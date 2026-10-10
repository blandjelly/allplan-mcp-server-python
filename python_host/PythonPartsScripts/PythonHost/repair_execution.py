"""Bounded disposable-copy execution, durable deduplication and read-only recovery."""
import copy
import json
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from . import native_repairs
from .audit_contracts import query_request
from .model_audit import run_audit
from .query_contracts import fingerprint
from .transport import BridgeError


class RepairExecutor:
    MAX_RECORDS = 128
    MAX_RECORD_BYTES = 1024 * 1024
    MAX_CHANGES = 32

    def __init__(self, plans, path):
        self.plans = plans
        self.path = Path(path)

    @contextmanager
    def locked(self):
        """OS lock survives multiple handlers and releases automatically on crash."""
        try:
            self.path.mkdir(parents=True, exist_ok=True)
            stream = (self.path / "writer.lock").open("a+b")
            stream.seek(0)
            if stream.read(1) == b"":
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if "stream" in locals():
                stream.close()
            raise BridgeError("repair_journal_unavailable", "Mutation journal unavailable or another writer is active. No write requested.", 409) from exc
        try:
            yield
        finally:
            stream.close()

    def load(self, execution_id):
        file = self.path / (execution_id + ".json")
        if not file.exists():
            return None
        try:
            if file.stat().st_size > self.MAX_RECORD_BYTES:
                raise ValueError("oversize record")
            record = json.loads(file.read_text(encoding="utf-8"))
            content = record.pop("record_hash")
            if (content != fingerprint(record) or record["execution_id"] != execution_id
                    or record["schema_version"] != "m3-execution-1"):
                raise ValueError("invalid record")
            return record
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise BridgeError("repair_journal_unavailable", "Mutation record cannot be verified; do not retry writes.", 409) from exc

    def save(self, record):
        payload = json.dumps({**record, "record_hash": fingerprint(record)}, ensure_ascii=False, allow_nan=False).encode()
        if len(payload) > self.MAX_RECORD_BYTES:
            raise BridgeError("repair_journal_unavailable", "Mutation journal size budget exceeded.", 409)
        temporary = self.path / (record["execution_id"] + "." + uuid4().hex + ".tmp")
        try:
            with temporary.open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path / (record["execution_id"] + ".json"))
            if os.name != "nt":
                descriptor = os.open(self.path, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        except OSError as exc:
            raise BridgeError("repair_journal_unavailable", "Mutation journal persistence failed. Inspect/recover before any further write.", 503) from exc
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def evaluation_scope(plan):
        """Existing string mark/status and layer writes in one foreground file."""
        changes = plan["changes"]
        files = plan["scope"]["included_files"]
        validation = plan.get("mark_validation")
        if ((validation is not None and (validation.get("state") != "validated"
                                        or validation.get("uses_full_snapshot") is not True
                                        or validation.get("collision_groups") != 0
                                        or validation.get("not_checked_elements") != 0))
                or plan["state"] != "preview_ready"
                or not 1 <= len(changes) <= RepairExecutor.MAX_CHANGES
                or len(files) != 1 or files[0]["state"] != "active_foreground"
                or not all(plan["coverage"].get(key) is True for key in
                           ("audit_complete", "requested_scope_complete", "returned_fields_complete"))):
            return False
        fields = set()
        for change in changes:
            ref, resource = change["ref"], change["resource"]
            symbol = ("ElementsLayerService.ChangeLayer" if change["operation"] == "set_layer"
                      else "ElementsAttributeService.ChangeAttributes")
            capability = plan["capabilities"]["symbols"].get(symbol, {})
            if capability.get("status") != "observed" or capability.get("callable") is not True:
                return False
            key = (ref["model_uuid"], change["field"])
            if (key in fields or ref["drawing_file"] != files[0]["drawing_file"]
                    or ref["type_uuid"] != "ac9415e3-4337-4860-8cd4-2f0d48596f12"
                    or change["old_value"].get("status") != "observed"):
                return False
            fields.add(key)
            if change["operation"] == "set_layer":
                if (change["field"] != "layer_id" or change.get("property_role") != "layer"
                        or type(resource.get("layer_id")) is not int
                        or change["new_value"] != resource["layer_id"]
                        or not isinstance(resource.get("short_name"), str) or not resource["short_name"]):
                    return False
            elif change["operation"] == "set_attribute":
                if (change.get("property_role") not in {"status", "mark"} or resource.get("data_type") != "string"
                        or (change.get("property_role") == "mark" and validation is None)
                        or type(resource.get("attribute_id")) is not int
                        or change["field"] != f"attribute:{resource['attribute_id']}"
                        or not isinstance(change["old_value"].get("value"), str)
                        or not isinstance(change["new_value"], str)):
                    return False
            else:
                return False
        return True

    @staticmethod
    def legacy_evaluation_scope(plan):
        """Keep the old acknowledgement restricted to its accepted two-target gate."""
        changes = plan["changes"]
        return ("selection" not in plan and "workflow" not in plan and "mark_validation" not in plan
                and plan["state"] == "preview_ready" and len(changes) == 2
                and plan["counts"] == {"changes": 2, "excluded_findings": 3, "audit_findings": 5}
                and all(c["ref"]["drawing_file"] == 101 and c["ref"]["type_uuid"] == "ac9415e3-4337-4860-8cd4-2f0d48596f12" for c in changes)
                and sum(c["operation"] == "set_layer" and c["locator"]["mark"].get("value") == "S05"
                        and c["resource"].get("short_name") == "SZ_OGÓ01" for c in changes) == 1
                and sum(c["operation"] == "set_attribute" and c["locator"]["mark"].get("value") == "S06"
                        and c["resource"].get("name") == "MCP_QA_STATUS"
                        and c["old_value"].get("value") == "NWE" and c["new_value"] == "NEW" for c in changes) == 1
                and all(f["state"] == "active_foreground" for f in plan["scope"]["included_files"]))

    def handle(self, doc, base, settings, request):
        with self.locked():
            record = self.load(request["execution_id"])
            if request["action"] == "recover":
                if record is None:
                    raise BridgeError("execution_not_found", "No mutation record exists for this execution ID.", 404)
                return self.recover(doc, base, settings, record)
            if record is not None:
                if record["request_hash"] != fingerprint(request):
                    raise BridgeError("execution_id_conflict", "Execution ID belongs to a different apply request.", 409)
                # Even after restart or UI Undo, a retry never invokes setters.
                return self.result(record, replayed=True)
            files = list(self.path.glob("*.json"))
            if len(files) >= self.MAX_RECORDS:
                raise BridgeError("repair_journal_full", "Journal is full; records are never automatically evicted.", 409)
            for file in files:
                previous = self.load(file.stem)
                if previous["state"] == "running" or any(o["state"] == "unknown" for o in previous["outcomes"]):
                    raise BridgeError("repair_recovery_required", "An unresolved mutation exists. Recover its execution ID before new writes.", 409)
            return self.apply(doc, base, settings, request)

    def apply(self, doc, base, settings, request):
        started = self.plans.queries.clock()
        # Retained invalidated evidence is exclusively for read-only inspection.
        # Reject before scanning and leave it available for a revalidate request.
        if request["plan_id"] not in self.plans.plans:
            raise BridgeError("plan_expired", "Plan expired or was invalidated by execution. Preview again.", 409)
        check = self.plans._revalidate(doc, base, settings, request)
        if check["state"] != "unchanged":
            raise BridgeError("repair_conflict", "Reviewed source changed; preview again.", 409)
        entry = self.plans.plans[request["plan_id"]]
        plan = entry["plan"]
        expected_workflow = request.get("workflow_kind")
        if (not self.evaluation_scope(plan)
                or (expected_workflow is not None and plan.get("workflow", {}).get("kind") != expected_workflow)
                or (request["acknowledgement"] == "disposable_copy_reviewed_two_repairs"
                    and not self.legacy_evaluation_scope(plan))):
            raise BridgeError("repair_scope_unavailable", "Apply requires a reviewed supported Column mark/status/layer plan in one foreground file; new plans require disposable_copy_reviewed_plan.", 409)
        before = self.plans.queries._scan(doc, base, settings, query_request(entry["request"]["audit"]))
        if before["source_fingerprint"] != plan["source_fingerprint"]:
            raise BridgeError("repair_conflict", "Audited source changed during preflight.", 409)
        expected = {e["ref"]["model_uuid"]: copy.deepcopy(e["fields"]) for e in before["elements"]}
        for change in plan["changes"]:
            fields = expected[change["ref"]["model_uuid"]]
            fields[change["field"]] = {"status": "observed", "value": change["new_value"]}
            role = change.get("property_role")
            if role in {"status", "mark"} and role in fields:
                fields[role] = copy.deepcopy(fields[change["field"]])
        # Resolve and check every target before recording or invoking any setter.
        target_preflight = []
        for change in plan["changes"]:
            diagnostics = {"ref": copy.deepcopy(change["ref"])}
            element = native_repairs.resolve(doc, base, self.plans.queries, change, writable=True, diagnostics=diagnostics)
            target_preflight.append(diagnostics)
            if native_repairs.read(base, self.plans.queries, element, change) != change["old_value"]:
                raise BridgeError("repair_conflict", "Target old value differs from the reviewed plan.", 409)
        if self.plans.queries.clock() - entry["created"] >= self.plans.TTL_SECONDS:
            raise BridgeError("plan_expired", "Plan expired during target preflight.", 409)
        record = {"schema_version": "m3-execution-1", "execution_id": request["execution_id"],
                  "request_hash": fingerprint(request), "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
                  "state": "running", "audit_request": entry["request"]["audit"],
                  "changes": copy.deepcopy(plan["changes"]),
                  "target_preflight": target_preflight,
                  "outcomes": [{"state": "skipped", "reason": "not_attempted"} for _ in plan["changes"]]}
        self.save(record)
        self.plans.invalidate_for_execution()
        self.plans.queries.selections.clear()
        for index, change in enumerate(record["changes"]):
            outcome = record["outcomes"][index]
            if self.plans.queries.clock() - started >= 20:
                outcome["reason"] = "execution_time_budget"
                break
            try:
                element = native_repairs.resolve(doc, base, self.plans.queries, change, writable=True)
                old = native_repairs.read(base, self.plans.queries, element, change)
                if old != change["old_value"]:
                    outcome.update(state="conflict", reason="old_value_changed", readback=old)
                    break
                if self.plans.queries.clock() - started >= 20:
                    outcome["reason"] = "execution_time_budget"
                    break
            except Exception as exc:
                outcome.update(state="conflict", reason=getattr(exc, "code", type(exc).__name__))
                break
            outcome.update(state="unknown", reason="setter_may_have_run")
            self.save(record)  # Write-ahead marker: a crash cannot authorize replay.
            try:
                native_repairs.write(base, element, change)
                # Never trust returned/stale adapters or setter return values as success.
                fresh = native_repairs.resolve(doc, base, self.plans.queries, change)
                observed = native_repairs.read(base, self.plans.queries, fresh, change)
                outcome["readback"] = observed
                if observed.get("status") == "observed" and observed.get("value") == change["new_value"]:
                    outcome.update(state="applied", reason="readback_matches")
                elif observed == change["old_value"]:
                    outcome.update(state="failed", reason="readback_unchanged")
                else:
                    outcome.update(state="unknown", reason="readback_differs_or_unavailable")
            except Exception as exc:
                outcome.update(state="unknown", reason=getattr(exc, "code", type(exc).__name__))
            self.save(record)
            if outcome["state"] != "applied":
                break
        record["state"] = "completed" if all(o["state"] == "applied" for o in record["outcomes"]) else "stopped"
        try:
            record["audit_after"] = run_audit(self.plans.queries, doc, base, settings, record["audit_request"])
            after = self.plans.queries._scan(doc, base, settings, query_request(record["audit_request"]))
            actual = {e["ref"]["model_uuid"]: e["fields"] for e in after["elements"]}
            record["audited_fields_match_plan"] = (after["coverage"]["requested_scope_complete"]
                                                    and after["scope"] == before["scope"] and actual == expected)
            if record["state"] == "completed" and (not record["audited_fields_match_plan"]
                    or not record["audit_after"]["coverage"]["audit_complete"]):
                record["state"] = "verification_failed"
        except Exception as exc:
            record["audit_after"] = {"state": "not_checked", "reason": getattr(exc, "code", type(exc).__name__)}
            record["audited_fields_match_plan"] = False
            if record["state"] == "completed":
                record["state"] = "verification_failed"
        self.save(record)
        return self.result(record)

    def recover(self, doc, base, settings, record):
        # Recovery is observation only; session-local refs are never resumed.
        report = run_audit(self.plans.queries, doc, base, settings, record["audit_request"])
        if not report["coverage"]["audit_complete"]:
            raise BridgeError("repair_recovery_unavailable", "Recovery audit is incomplete.", 409)
        current = report["checks"][0]["ref"] if report["checks"] else None
        reference = record["changes"][0]["ref"]
        if current is None or any(current[k] != reference[k] for k in ("project_key", "document_id")):
            raise BridgeError("repair_conflict", "Open the original disposable project/document for recovery.", 409)
        observations = []
        for index, change in enumerate(record["changes"]):
            try:
                element = native_repairs.resolve(doc, base, self.plans.queries, change)
                value = native_repairs.read(base, self.plans.queries, element, change)
                state = ("new_value_observed" if value.get("status") == "observed" and value.get("value") == change["new_value"]
                         else "old_value_observed" if value == change["old_value"] else "conflict")
            except Exception as exc:
                value, state = {"status": "not_checked", "reason": getattr(exc, "code", type(exc).__name__)}, "unknown"
            observations.append({"state": state, "readback": value})
            if record["outcomes"][index]["state"] == "unknown" and state in {"new_value_observed", "old_value_observed"}:
                record["outcomes"][index].update(state="reconciled", reason=state, readback=value)
        record["state"] = "stopped" if record["state"] == "running" else record["state"]
        record["recovery"] = {"observations": observations, "audit": report,
                              "identity_limit": "project/document/model match; copy identity and mutation causality not proven"}
        self.save(record)
        result = self.result(record)
        result.update(action="recover", read_only=True)
        return result

    @staticmethod
    def result(record, replayed=False):
        return copy.deepcopy({**record, "action": "apply", "read_only": replayed,
                              "replayed": replayed, "automatic_retry": False,
                              "undo": "not_checked; observe native UI Undo on disposable copy; no automatic rollback",
                              "allplan_acceptance": "not_run", "runtime_verified": False,
                              "report_text": "Repair execution " + record["state"] + ": " +
                              ", ".join(o["state"] for o in record["outcomes"]) + ". No automatic rollback or retry."})
