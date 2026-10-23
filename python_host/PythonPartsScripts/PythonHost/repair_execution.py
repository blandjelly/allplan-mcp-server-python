"""Bounded disposable-copy execution, durable deduplication and read-only recovery."""
import copy
import json
import os
import re
from itertools import islice
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from . import native_repairs
from .query_contracts import fingerprint
from .transport import BridgeError


def _error_details(exc):
    # Include only host-generated BridgeError text. Native exception strings
    # can contain object representations or local paths, so expose their type.
    message = str(exc) if isinstance(exc, BridgeError) else type(exc).__name__
    return {"reason": getattr(exc, "code", type(exc).__name__),
            "message": message[:512]}


def same_observation(change, observed, expected):
    if change.get("adapter_version") == "m4-model-edit-1":
        if change.get("resource", {}).get("data_type") == "real":
            if (isinstance(observed, dict) and isinstance(expected, dict)
                    and type(observed.get("value")) in (int, float)
                    and type(expected.get("value")) in (int, float)):
                return _real_observation_equal(observed, expected)
        return fingerprint(observed) == fingerprint(expected)
    return observed == expected


def new_value_observed(change, observed):
    if observed.get("status") != "observed":
        return False
    if change.get("adapter_version") == "m4-model-edit-1":
        if change.get("resource", {}).get("data_type") == "real":
            return _finite_real_equal(observed.get("value"), change.get("new_value"))
        return (type(observed.get("value")) is type(change["new_value"])
                and observed.get("value") == change["new_value"])
    return observed.get("value") == change["new_value"]


def _finite_real_equal(left, right):
    import math
    return (type(left) in (int, float) and type(right) in (int, float)
            and math.isfinite(left) and math.isfinite(right) and left == right)


def _real_observation_equal(left, right):
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    if {k: v for k, v in left.items() if k != "value"} != {k: v for k, v in right.items() if k != "value"}:
        return False
    return _finite_real_equal(left.get("value"), right.get("value"))


def _model_edit_fields_match(actual, expected, changes):
    """Compare final fields with type-aware equality for explicitly bound Real attributes."""
    actual = copy.deepcopy(actual)
    expected = copy.deepcopy(expected)
    for change in changes:
        if change.get("resource", {}).get("data_type") != "real":
            continue
        model_uuid, field = change["ref"]["model_uuid"], change["field"]
        if model_uuid not in actual or model_uuid not in expected:
            return False
        if field not in actual[model_uuid] or field not in expected[model_uuid]:
            return False
        if not _real_observation_equal(actual[model_uuid][field], expected[model_uuid][field]):
            return False
        # Other unedited values and all observation metadata retain exact
        # fingerprint comparison below.
        actual[model_uuid][field] = copy.deepcopy(expected[model_uuid][field])
    return fingerprint(actual) == fingerprint(expected)


class RepairExecutor:
    # Keep enough resolved history for multiple interactive batches before
    # requiring the existing confirmed archival workflow.
    MAX_RECORDS = 512
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
        from .journal_maintenance import archive_path
        if not isinstance(execution_id, str) or not re.fullmatch(r"[0-9a-f]{32}", execution_id):
            raise BridgeError("repair_journal_unavailable", "Invalid stored execution ID; no write requested.", 409)
        active = self.path / (execution_id + ".json")
        archived = archive_path(self) / active.name
        for file in (active, archived):
            if file.is_symlink():
                raise BridgeError("repair_journal_unavailable", "Mutation record is a symbolic link; no write requested.", 409)
        existing = [file for file in (active, archived) if file.exists()]
        if not existing:
            return None
        records = [self._load_file(file, execution_id) for file in existing]
        for file, record in zip(existing, records):
            if file == archived and (record["state"] == "running" or any(
                    outcome["state"] == "unknown" for outcome in record["outcomes"])):
                raise BridgeError("repair_journal_unavailable", "Archived execution is unresolved; preserve it for inspection.", 409)
        if len(records) == 2 and fingerprint(records[0]) != fingerprint(records[1]):
            raise BridgeError("repair_journal_unavailable", "Active and archived execution records disagree.", 409)
        return records[0]

    def _load_file(self, file, execution_id):
        try:
            if not file.is_file() or file.stat().st_size > self.MAX_RECORD_BYTES:
                raise ValueError("oversize or nonregular record")
            record = json.loads(file.read_text(encoding="utf-8"))
            content = record.pop("record_hash")
            if (content != fingerprint(record) or record["execution_id"] != execution_id
                    or record["schema_version"] != "m3-execution-1"):
                raise ValueError("invalid record")
            self.validate_record(record)
            return record
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            raise BridgeError("repair_journal_unavailable", "Mutation record cannot be verified; do not retry writes.", 409) from exc

    def archived(self, execution_id):
        from .journal_maintenance import archive_path
        return (not (self.path / (execution_id + ".json")).exists()
                and (archive_path(self) / (execution_id + ".json")).exists())

    def journal_maintenance(self, request):
        from .journal_maintenance import preview, cleanup
        if request["action"] == "preview_journal_cleanup":
            return preview(self, request["target"])
        return cleanup(self, request)

    @staticmethod
    def validate_record(record):
        """Hashes alone do not establish a usable execution/recovery record."""
        for key, size in (("execution_id", 32), ("request_hash", 64), ("plan_id", 32), ("plan_hash", 64)):
            if not isinstance(record.get(key), str) or not re.fullmatch(r"[0-9a-f]{" + str(size) + "}", record[key]):
                raise ValueError("invalid identity")
        if ("audit_request" in record) == ("criterion_request" in record):
            raise ValueError("exactly one source request is required")
        if "criterion_request" in record:
            if record["criterion_request"].get("schema_version") == "m4-model-edit-1":
                from .model_edit_contracts import validate_request
            else:
                from .column_layer import validate_request
            try:
                validate_request(record["criterion_request"])
                if record["criterion_request"]["action"] != "preview":
                    raise ValueError("journal criterion must be a preview")
            except BridgeError as exc:
                raise ValueError("invalid journal criterion") from exc
        changes, outcomes = record.get("changes"), record.get("outcomes")
        if (record.get("state") not in {"running", "stopped", "completed", "verification_failed"}
                or (not isinstance(record.get("audit_request"), dict)
                    and not isinstance(record.get("criterion_request"), dict))
                or not isinstance(changes, list) or not 1 <= len(changes) <= RepairExecutor.MAX_CHANGES
                or not isinstance(outcomes, list) or len(outcomes) != len(changes)):
            raise ValueError("invalid execution structure")
        for change, outcome in zip(changes, outcomes):
            if (not isinstance(change, dict) or not isinstance(change.get("ref"), dict)
                    or not isinstance(outcome, dict) or outcome.get("state") not in
                    {"skipped", "unknown", "applied", "failed", "conflict", "reconciled"}):
                raise ValueError("invalid target/outcome")
            if any(key not in change["ref"] for key in
                   ("project_key", "document_id", "drawing_file", "model_uuid", "type_uuid")):
                raise ValueError("invalid target identity")
            ref = change["ref"]
            if (not isinstance(ref["project_key"], str) or not re.fullmatch(r"[0-9a-f]{64}", ref["project_key"])
                    or type(ref["document_id"]) is not int or type(ref["drawing_file"]) is not int
                    or any(not isinstance(ref[k], str) or not re.fullmatch(
                        r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", ref[k]) for k in ("model_uuid", "type_uuid"))):
                raise ValueError("invalid target identity types")

    def inspect_journal(self):
        """Bounded, locked history inspection; no native read, reconciliation or pruning."""
        with self.locked():
            files = sorted(islice(self.path.glob("*.json"), self.MAX_RECORDS + 1))
            records, blockers = [], []
            if len(files) > self.MAX_RECORDS:
                blockers.append("capacity_exceeded")
            for file in files[:self.MAX_RECORDS]:
                try:
                    record = self.load(file.stem)
                    if record is None:
                        raise BridgeError("repair_journal_unavailable", "Record disappeared during inspection.", 409)
                    states = [o["state"] for o in record["outcomes"]]
                    unresolved = record["state"] == "running" or "unknown" in states
                    ref = record["changes"][0]["ref"]
                    records.append({"execution_id": record["execution_id"], "plan_id": record["plan_id"],
                                    "plan_hash": record["plan_hash"], "state": record["state"],
                                    "integrity": "verified", "requires_recovery": unresolved,
                                    "changes": len(states), "outcome_counts": {s: states.count(s) for s in sorted(set(states))},
                                    "source_identity": {k: ref[k] for k in ("project_key", "document_id", "drawing_file")}})
                    if unresolved and "recovery_required" not in blockers:
                        blockers.append("recovery_required")
                except BridgeError:
                    records.append({"execution_id": file.stem[:128], "integrity": "unverifiable",
                                    "requires_recovery": None})
                    if "invalid_record" not in blockers:
                        blockers.append("invalid_record")
            if len(files) >= self.MAX_RECORDS and "capacity_exceeded" not in blockers:
                blockers.append("journal_full")
            result = {"schema_version": "m3-journal-inspection-1", "action": "inspect_journal",
                    "state": "blocked" if blockers else "available", "read_only": True,
                    "native_model_access": False, "records_modified": False,
                    "complete": len(files) <= self.MAX_RECORDS, "record_limit": self.MAX_RECORDS,
                    "record_count": len(files) if len(files) <= self.MAX_RECORDS else None,
                    "remaining_slots": max(0, self.MAX_RECORDS - len(files)),
                    "new_execution_blockers": blockers, "records": records,
                    "current_model_values": "not_checked", "copy_identity": "not_proven",
                    "automatic_pruning": False,
                    "report_text": "Repair journal: " + str(len(records)) + " inspected records; " +
                                   (", ".join(blockers) if blockers else "storage checks passed") +
                                   ". Historical records only; model values and write eligibility are not checked."}
            from .property_probe import NativeProbeTrace
            try:
                result["native_trace"] = NativeProbeTrace.inspect_storage(self.plans.trace_path)
            except BridgeError as exc:
                result["native_trace"] = {"state": "unavailable", "reason": exc.code}
            result["cleanup_options"] = [
                {"tool": "fix_model_issues", "request": {"action": "preview_journal_cleanup", "target": target},
                 "user_confirmation_required": True} for target in ("native_trace", "repair_records")]
            result["record_byte_limit"] = self.MAX_RECORD_BYTES
            result["archive_replay_preserved"] = True
            return result

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
        if plan.get("source_kind") == "typed_model_edit":
            return RepairExecutor.model_edit_scope(plan)
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
                           ("criteria_complete" if plan.get("source_kind") == "column_missing_fire_layer" else "audit_complete",
                            "requested_scope_complete", "returned_fields_complete"))):
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
    def model_edit_scope(plan):
        """Separate evaluation contract; does not broaden historical M3 permissions."""
        from .native_model_edit import (replaceable_attribute_value, value_matches,
                                        valid_boolean_binding, valid_enum_binding)
        from .native_readers import COMPONENT_TYPES
        changes, files = plan["changes"], plan["scope"]["included_files"]
        if (plan.get("schema_version") != "m4-model-edit-1" or plan["state"] != "preview_ready"
                or plan.get("blocked") or not 1 <= len(changes) <= RepairExecutor.MAX_CHANGES
                or len(files) != 1 or files[0]["state"] != "active_foreground"
                or not all(plan["coverage"].get(k) is True for k in
                           ("criteria_complete", "requested_scope_complete"))
                or plan["coverage"].get("required_destination_fields_complete",
                                        plan["coverage"].get("returned_fields_complete")) is not True):
            return False
        seen = set()
        for change in changes:
            ref, resource, old = change["ref"], change["resource"], change["old_value"]
            key = (ref["drawing_file"], ref["model_uuid"], change["field"])
            if (key in seen or ref["drawing_file"] != files[0]["drawing_file"]
                    or change.get("adapter_version") != "m4-model-edit-1"
                    or change.get("native_type") not in COMPONENT_TYPES):
                return False
            seen.add(key)
            if change.get("operation") == "set_native_material":
                from .wall_material import valid_change
                capability = plan["capabilities"]["symbols"].get("ModifyElements", {})
                if (not valid_change(change) or capability.get("status") != "observed"
                        or capability.get("callable") is not True
                        or any(item.get("operation") != "set_native_material" for item in changes)):
                    return False
                continue
            if change.get("operation") == "delete_element":
                from .model_delete import valid_change
                capability = plan["capabilities"]["symbols"].get("DeleteElements", {})
                if (not valid_change(change) or capability.get("status") != "observed"
                        or capability.get("callable") is not True
                        or any(item.get("operation") != "delete_element" for item in changes)):
                    return False
                continue
            if change.get("native_type") in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}:
                from .component_ownership import slab_write_blocker
                if slab_write_blocker(resource.get("component_ownership")):
                    return False
            symbol = ("ElementsLayerService.ChangeLayer" if change["operation"] in {"set_layer", "set_wall_layer"}
                      else "ElementsAttributeService.ChangeAttributes")
            capability = plan["capabilities"]["symbols"].get(symbol, {})
            if capability.get("status") != "observed" or capability.get("callable") is not True:
                return False
            if change["operation"] in {"set_layer", "set_wall_layer"}:
                if (old.get("status") != "observed" or change["field"] != "layer_id"
                        or change.get("property_role") != "layer" or type(resource.get("layer_id")) is not int
                        or change["new_value"] != resource["layer_id"]
                        or not isinstance(resource.get("short_name"), str) or not resource["short_name"]):
                    return False
                if change["operation"] == "set_wall_layer":
                    from .wall_layer import valid_change
                    if not valid_change(change):
                        return False
            elif change["operation"] in {"set_attribute", "add_attribute"}:
                if (change.get("property_role") != "attribute" or type(resource.get("attribute_id")) is not int
                        or change["field"] != f"attribute:{resource['attribute_id']}"
                        or old.get("computed_only") is True
                        or not valid_enum_binding(change)
                        or not valid_boolean_binding(change)
                        or not value_matches(change["new_value"], resource.get("data_type"))):
                    return False
                if change["operation"] == "add_attribute":
                    if (old.get("status") != "absent" or old.get("presence_proven") is not True
                            or old.get("evidence") != "absent_from_ReadAllAndComputable"
                            or resource.get("read_mode") != "all_and_computable"
                            or change.get("mode") not in {"add", "upsert"}):
                        return False
                elif not replaceable_attribute_value(change) or change.get("mode") not in {"replace", "upsert"}:
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

    @staticmethod
    def recovery_evaluation_scope(plan):
        """A diagnostic stop may only use the retained two-mark numbering fixture."""
        workflow = plan.get("workflow", {})
        changes = plan["changes"]
        if (workflow.get("kind") != "office_standard_preview"
                or workflow.get("standard_id") != "native-model-qa-demo-mark-numbering"
                or workflow.get("standard_version") != "1.0.0"
                or "selection" in plan or len(changes) != 2
                or plan["counts"]["audit_findings"] != 3
                or plan.get("numbering", {}).get("state") != "validated"):
            return False
        for change, rule, old, new, center in zip(changes,
                ("QA-001", "QA-002"), ("<niezdefiniowany>", "S02"), ("S03", "S04"),
                ([12000, 0, 1500], [0, 6000, 1500])):
            observed = change["locator"]["center_mm"]
            if (change["operation"] != "set_attribute" or change.get("property_role") != "mark"
                    or change["rule_id"] != rule or change["ref"]["drawing_file"] != 101
                    or change["old_value"].get("value") != old or change["new_value"] != new
                    or observed.get("status") != "observed" or len(observed["value"]) != 3
                    or any(abs(a - b) > 1 for a, b in zip(observed["value"], center))):
                return False
        return changes[0]["resource"] == changes[1]["resource"]

    def handle(self, doc, base, settings, request):
        with self.locked():
            record = self.load(request["execution_id"])
            if request["action"] == "recover":
                if record is None:
                    raise BridgeError("execution_not_found", "No mutation record exists for this execution ID.", 404)
                if self.archived(request["execution_id"]):
                    return {**self.result(record, replayed=True), "action": "recover", "archived": True,
                            "current_model_values": "not_checked", "recovery_required": False,
                            "report_text": "Archived resolved execution; history only. No current model values read or setters repeated."}
                return self.recover(doc, base, settings, record)
            if record is not None:
                if record["request_hash"] != fingerprint(request):
                    raise BridgeError("execution_id_conflict", "Execution ID belongs to a different apply request.", 409)
                # Even after restart or UI Undo, a retry never invokes setters.
                return {**self.result(record, replayed=True), "archived": self.archived(request["execution_id"])}
            files = list(self.path.glob("*.json"))
            if len(files) >= self.MAX_RECORDS:
                raise BridgeError("repair_journal_full", "Journal is full. Use fix_model_issues preview_journal_cleanup target=repair_records; ask the user to confirm archival. No records are silently evicted.", 409)
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
        if ((plan.get("source_kind") == "typed_model_edit") != (request.get("schema_version") == "m4-model-edit-1")):
            raise BridgeError("repair_scope_unavailable", "Typed model edit plans require their own route and acknowledgement.", 409)
        if request.get("schema_version") == "m4-column-layer-1" and plan.get("source_kind") != "column_missing_fire_layer":
            raise BridgeError("repair_scope_unavailable", "This route requires a Column criterion plan.", 409)
        if plan.get("requires_highlight") and entry.get("presentation") != {"state": "submitted", "plan_hash": plan["plan_hash"]}:
            raise BridgeError("presentation_required", "Highlight the exact reviewed Column plan before Apply.", 409)
        expected_workflow = request.get("workflow_kind")
        if (not self.evaluation_scope(plan)
                or (expected_workflow is not None and plan.get("workflow", {}).get("kind") != expected_workflow)
                or (request["acknowledgement"] == "disposable_copy_reviewed_two_repairs"
                    and not self.legacy_evaluation_scope(plan))):
            raise BridgeError("repair_scope_unavailable", "Apply requires a reviewed supported Column mark/status/layer plan in one foreground file; new plans require disposable_copy_reviewed_plan.", 409)
        if request.get("evaluation_stop") and not self.recovery_evaluation_scope(plan):
            raise BridgeError("repair_scope_unavailable", "Recovery-test stop requires the retained unselected two-mark numbering fixture.", 409)
        before_report, before = self.plans.source_observation(doc, base, settings, entry["request"])
        if plan.get("source_kind") in {"column_missing_fire_layer", "typed_model_edit"} and before_report["report_fingerprint"] != plan["evidence_fingerprint"]:
            raise BridgeError("repair_conflict", "Column resource or criterion evidence changed during preflight.", 409)
        if before["source_fingerprint"] != plan["source_fingerprint"]:
            raise BridgeError("repair_conflict", "Audited source changed during preflight.", 409)
        expected = {e["ref"]["model_uuid"]: copy.deepcopy(e["fields"]) for e in before["elements"]}
        for change in plan["changes"]:
            if change.get("operation") == "delete_element":
                ownership = change["resource"]["delete_ownership"]["value"]
                for target in [ownership["target"], *ownership["descendants"]]:
                    expected.pop(target["model_uuid"], None)
                continue
            fields = expected[change["ref"]["model_uuid"]]
            fields[change["field"]] = {"status": "observed", "value": change["new_value"]}
            role = change.get("property_role")
            if role in {"status", "mark"} and role in fields:
                fields[role] = copy.deepcopy(fields[change["field"]])
        # Resolve and check every target before recording or invoking any setter.
        target_preflight = []
        for change in plan["changes"]:
            diagnostics = {"ref": copy.deepcopy(change["ref"])}
            native_owners = []
            element = native_repairs.resolve(doc, base, self.plans.queries, change, writable=True, diagnostics=diagnostics, adapter_owners=native_owners)
            target_preflight.append(diagnostics)
            if not same_observation(change, native_repairs.read(base, self.plans.queries, element, change), change["old_value"]):
                raise BridgeError("repair_conflict", "Target old value differs from the reviewed plan.", 409)
        if self.plans.queries.clock() - entry["created"] >= self.plans.TTL_SECONDS:
            raise BridgeError("plan_expired", "Plan expired during target preflight.", 409)
        record = {"schema_version": "m3-execution-1", "execution_id": request["execution_id"],
                  "request_hash": fingerprint(request), "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
                  "state": "running",
                  "changes": copy.deepcopy(plan["changes"]),
                  "target_preflight": target_preflight,
                  "outcomes": [{"state": "skipped", "reason": "not_attempted"} for _ in plan["changes"]]}
        if plan.get("source_kind") in {"column_missing_fire_layer", "typed_model_edit"}:
            record["criterion_request"] = copy.deepcopy(entry["request"])
        else:
            record["audit_request"] = entry["request"]["audit"]
        if "evaluation_stop" in request:
            record["evaluation_control"] = {"stop": request["evaluation_stop"],
                                            "controlled_interruption": True,
                                            "not_a_native_crash": True}
        self.save(record)
        self.plans.invalidate_for_execution()
        self.plans.queries.selections.clear()
        if all(change.get("operation") == "delete_element" for change in record["changes"]):
            self._apply_delete_batch(doc, base, record, started)
        else:
            for index, change in enumerate(record["changes"]):
                outcome = record["outcomes"][index]
                if self.plans.queries.clock() - started >= 20:
                    outcome["reason"] = "execution_time_budget"
                    break
                stage = "pre_set_resolve"
                try:
                    native_owners = []
                    element = native_repairs.resolve(doc, base, self.plans.queries, change, writable=True, adapter_owners=native_owners)
                    stage = "pre_set_read"
                    old = native_repairs.read(base, self.plans.queries, element, change)
                    if not same_observation(change, old, change["old_value"]):
                        outcome.update(state="conflict", reason="old_value_changed", readback=old)
                        break
                    if self.plans.queries.clock() - started >= 20:
                        outcome["reason"] = "execution_time_budget"
                        break
                except Exception as exc:
                    outcome.update(state="conflict", **_error_details(exc), stage=stage)
                    break
                outcome.update(state="unknown", reason="setter_may_have_run")
                self.save(record)  # Write-ahead marker: a crash cannot authorize replay.
                stage = "setter"
                try:
                    if change.get("operation") in {"delete_element", "set_native_material"}:
                        def write_budget():
                            if self.plans.queries.clock() - started >= 20:
                                raise BridgeError("scan_limit_exceeded", "Native mutation preflight exceeded execution budget.", 409)
                        native_repairs.write(base, element, change, doc=doc, check=write_budget)
                    else:
                        native_repairs.write(base, element, change)
                    if index == 0 and request.get("evaluation_stop"):
                        # Leave the actual durable write-ahead marker unchanged. No
                        # readback, final save, second setter or fabricated failure.
                        # Exact-ID replay and Recover use the normal journal route.
                        return self.result(record)
                    # Never trust returned/stale adapters or setter return values as success.
                    stage = "fresh_resolve"
                    resolution = {}
                    observed = native_repairs.observe(doc, base, self.plans.queries, change, resolution)
                    stage = "readback"
                    if resolution:
                        outcome["representation_consensus"] = resolution
                    outcome["readback"] = observed
                    if new_value_observed(change, observed):
                        outcome.update(state="applied", reason="readback_matches")
                    elif same_observation(change, observed, change["old_value"]):
                        outcome.update(state="failed", reason="readback_unchanged")
                    else:
                        outcome.update(state="unknown", reason="readback_differs_or_unavailable")
                except Exception as exc:
                    outcome.update(state="unknown", **_error_details(exc), stage=stage)
                self.save(record)
                if outcome["state"] != "applied":
                    break
        record["state"] = "completed" if all(o["state"] == "applied" for o in record["outcomes"]) else "stopped"
        try:
            report_key = "criteria_after" if "criterion_request" in record else "audit_after"
            record[report_key], after = self.plans.source_observation(doc, base, settings,
                record.get("criterion_request", record.get("audit_request")))
            actual = {e["ref"]["model_uuid"]: e["fields"] for e in after["elements"]}
            fields_match = (_model_edit_fields_match(actual, expected, record["changes"])
                            if plan.get("source_kind") == "typed_model_edit" else actual == expected)
            record["audited_fields_match_plan"] = (after["coverage"]["requested_scope_complete"]
                                                    and after["scope"] == before["scope"] and fields_match)
            if record["state"] == "completed" and (not record["audited_fields_match_plan"]
                    or not record[report_key]["coverage"]["criteria_complete" if "criterion_request" in record else "audit_complete"]):
                record["state"] = "verification_failed"
        except Exception as exc:
            record[report_key] = {"state": "not_checked", "reason": getattr(exc, "code", type(exc).__name__)}
            record["audited_fields_match_plan"] = False
            if record["state"] == "completed":
                record["state"] = "verification_failed"
        self.save(record)
        return self.result(record)

    def _apply_delete_batch(self, doc, base, record, started):
        """One delete command is one native submission for all reviewed roots."""
        from .model_delete import write_batch

        def write_budget():
            if self.plans.queries.clock() - started >= 20:
                raise BridgeError("scan_limit_exceeded", "Native deletion batch exceeded execution budget.", 409)

        elements, native_owners = [], []
        stage = "pre_set_resolve"
        try:
            # Keep all enumerations alive until the one native call completes.
            for index, change in enumerate(record["changes"]):
                write_budget()
                stage = "pre_set_resolve"
                element = native_repairs.resolve(doc, base, self.plans.queries, change,
                    writable=True, adapter_owners=native_owners)
                stage = "pre_set_read"
                old = native_repairs.read(base, self.plans.queries, element, change)
                if not same_observation(change, old, change["old_value"]):
                    record["outcomes"][index].update(state="conflict", reason="old_value_changed", readback=old)
                    self.save(record)
                    return
                elements.append(element)
            write_budget()
        except Exception as exc:
            record["outcomes"][index].update(state="conflict", **_error_details(exc), stage=stage)
            self.save(record)
            return
        record["native_delete_batch"] = {"method": "DeleteElements", "target_count": len(elements),
            "submission": "may_have_run", "native_undo": "not_checked"}
        for outcome in record["outcomes"]:
            outcome.update(state="unknown", reason="setter_may_have_run")
        # Every root can be affected by the next call. Persist all write-ahead
        # markers together; a crash or partial exception must never permit retry.
        self.save(record)
        try:
            write_batch(base, elements, record["changes"], doc, write_budget)
        except Exception as exc:
            for outcome in record["outcomes"]:
                outcome.update(state="unknown", **_error_details(exc), stage="setter")
            self.save(record)
            return
        record["native_delete_batch"]["submission"] = "returned"
        # The whole list was submitted, so observe every root even if another
        # root has failed readback. No result implies native batch atomicity.
        for change, outcome in zip(record["changes"], record["outcomes"]):
            stage = "fresh_resolve"
            try:
                resolution = {}
                observed = native_repairs.observe(doc, base, self.plans.queries, change, resolution)
                stage = "readback"
                if resolution:
                    outcome["representation_consensus"] = resolution
                outcome["readback"] = observed
                if new_value_observed(change, observed):
                    outcome.update(state="applied", reason="readback_matches")
                elif same_observation(change, observed, change["old_value"]):
                    outcome.update(state="failed", reason="readback_unchanged")
                else:
                    outcome.update(state="unknown", reason="readback_differs_or_unavailable")
            except Exception as exc:
                outcome.update(state="unknown", **_error_details(exc), stage=stage)
            self.save(record)

    def recover(self, doc, base, settings, record):
        # Recovery is observation only; session-local refs are never resumed.
        reference = record["changes"][0]["ref"]
        criterion_request = record.get("criterion_request", {})
        if criterion_request.get("schema_version") == "m4-model-edit-1":
            # A global criterion scan can be incomplete because Allplan still
            # exposes stale/unrelated wrappers after a setter. Recovery only
            # needs to prove project/document identity, then read each exact
            # journal target. This remains read-only and cannot authorize a
            # retry or bypass the original project/document guard.
            from .model_context import context_probe
            context = context_probe(doc, base, settings, {})
            project = context.get("project", {})
            document = context.get("document_id", {})
            if (project.get("status") != "observed"
                    or project.get("value", {}).get("key_status") != "observed"
                    or document.get("status") != "observed"):
                raise BridgeError("repair_recovery_unavailable", "Current project/document identity is unavailable.", 409)
            current = {"project_key": project["value"]["key"],
                       "document_id": document["value"]}
            identity = {"state": "observed", "project_key": current["project_key"],
                        "document_id": current["document_id"],
                        "method": "context_probe_no_model_scan"}
            report = {"state": "identity_verified", "coverage": "exact_journal_targets_only"}
        else:
            report, _ = self.plans.source_observation(doc, base, settings,
                record.get("criterion_request", record.get("audit_request")))
            if not report["coverage"]["criteria_complete" if "criterion_request" in record else "audit_complete"]:
                raise BridgeError("repair_recovery_unavailable", "Recovery audit is incomplete.", 409)
            current = report["checks"][0]["ref"] if report["checks"] else None
            identity = {"state": "observed" if current else "not_checked",
                        "method": "recovery_audit"}
        if current is None or any(current[k] != reference[k] for k in ("project_key", "document_id")):
            raise BridgeError("repair_conflict", "Open the original disposable project/document for recovery.", 409)
        observations = []
        for index, change in enumerate(record["changes"]):
            stage = "recovery_resolve"
            resolution = {}
            try:
                value = native_repairs.observe(doc, base, self.plans.queries, change, resolution)
                stage = "recovery_read"
                state = ("new_value_observed" if new_value_observed(change, value)
                         else "old_value_observed" if same_observation(change, value, change["old_value"]) else "conflict")
            except Exception as exc:
                details = _error_details(exc)
                value, state = {"status": "not_checked", **details}, "unknown"
            else:
                details = {}
            observations.append({"state": state, "readback": value, "stage": stage,
                                 **({"representation_consensus": resolution} if resolution else {}), **details})
            if record["outcomes"][index]["state"] == "unknown" and state in {"new_value_observed", "old_value_observed"}:
                record["outcomes"][index].update(state="reconciled", reason=state, readback=value)
        record["state"] = "stopped" if record["state"] == "running" else record["state"]
        record["recovery"] = {"observations": observations, ("criteria" if "criterion_request" in record else "audit"): report,
                              "identity": identity,
                              "identity_limit": "project/document/model match; copy identity and mutation causality not proven"}
        self.save(record)
        result = self.result(record)
        result.update(action="recover", read_only=True)
        blockers, blocking_ids = [], []
        journal_files = sorted(self.path.glob("*.json"))
        if len(journal_files) > self.MAX_RECORDS:
            blockers.append("capacity_exceeded")
        for file in journal_files[:self.MAX_RECORDS]:
            try:
                saved = self.load(file.stem)
            except BridgeError:
                if "invalid_record" not in blockers:
                    blockers.append("invalid_record")
                continue
            if saved is not None and (saved["state"] == "running"
                    or any(o["state"] == "unknown" for o in saved["outcomes"])):
                blocking_ids.append(saved["execution_id"])
        if blocking_ids:
            blockers.insert(0, "recovery_required")
        if "capacity_exceeded" in blockers and "journal_full" not in blockers:
            blockers.append("journal_full")
        if blocking_ids:
            next_action = {"action": "recover", "execution_id": blocking_ids[0]}
        elif blockers:
            next_action = {"action": "inspect_journal"}
        else:
            next_action = {"action": "preview", "reason": "fresh_preview_required_before_apply"}
        result.update(write_blocked=bool(blockers), blockers=blockers,
                      blocking_execution_ids=blocking_ids, next_action=next_action)
        return result

    @staticmethod
    def result(record, replayed=False):
        return copy.deepcopy({**record, "action": "apply", "read_only": replayed,
                              "replayed": replayed, "automatic_retry": False,
                              "undo": "not_checked; observe native UI Undo on disposable copy; no automatic rollback",
                              "allplan_acceptance": "not_run", "runtime_verified": False,
                              "report_text": "Repair execution " + record["state"] + ": " +
                              ", ".join(o["state"] for o in record["outcomes"]) + ". No automatic rollback or retry."})
