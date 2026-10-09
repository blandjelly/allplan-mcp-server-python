"""Bounded plans over fresh M2 evidence; explicit evaluation execution is separate."""
import copy
import json
from collections import OrderedDict
from uuid import uuid4

from .model_audit import run_audit
from .query_contracts import evaluate, fingerprint
from .repair_contracts import SCHEMA, capability_probe, validate_repair_request
from .transport import BridgeError


class RepairPlanService:
    TTL_SECONDS = 300
    MAX_PLANS = 8
    MAX_PLAN_BYTES = 4 * 1024 * 1024
    MAX_CACHE_BYTES = 8 * 1024 * 1024

    def __init__(self, queries, journal_path=None):
        self.queries = queries
        self.plans = OrderedDict()
        from pathlib import Path
        from .repair_execution import RepairExecutor
        self.executor = RepairExecutor(self, journal_path or Path(__file__).resolve().parents[2] / ".allplan-mcp" / "repairs")

    def handle(self, doc, base, settings, request):
        validate_repair_request(request)
        if request["action"] in {"apply", "recover"}:
            return self.executor.handle(doc, base, settings, request)
        now = self.queries.clock()
        for ident, entry in list(self.plans.items()):
            if now - entry["created"] >= self.TTL_SECONDS:
                del self.plans[ident]
        if request["action"] == "revalidate":
            return self._revalidate(doc, base, settings, request)
        decisions, selection_result = {}, None
        if "selection" in request:
            report, snapshot = run_audit(self.queries, doc, base, settings, request["audit"], with_snapshot=True)
            selection = request["selection"]
            exceptions = set(selection.get("exclude_model_uuids", []))
            if not exceptions <= {e["ref"]["model_uuid"] for e in snapshot["elements"]}:
                raise BridgeError("finding_stale", "An exception is absent from the full audited scope. Review the current model UUIDs.", 409)
            selection_result = {"selected_elements": 0, "predicate_false": 0,
                                "excluded_elements": 0, "predicate_not_checked": 0}
            selection_started = self.queries.clock()
            for element in snapshot["elements"]:
                if self.queries.clock() - selection_started >= self.queries.SCAN_SECONDS:
                    raise BridgeError("scan_limit_exceeded", "Repair selection exceeded its time budget; no plan was stored.", 409)
                if element["ref"]["model_uuid"] in exceptions:
                    decision = "excluded_elements"
                else:
                    value = evaluate(selection["where"], element["fields"])
                    decision = "selected_elements" if value is True else "predicate_false" if value is False else "predicate_not_checked"
                decisions[fingerprint(element["ref"])] = decision
                selection_result[decision] += 1
        else:
            report = run_audit(self.queries, doc, base, settings, request["audit"])
        choices = {c["rule_id"]: c["value"] for c in request["repairs"]}
        rules = {r["rule_id"]: r for r in request["audit"]["profile"]["rules"]}
        ids = request.get("finding_ids")
        available = {f["finding_id"] for f in report["findings"] if f["rule_id"] in choices}
        if ids is not None and not set(ids) <= available:
            raise BridgeError("finding_stale", "Selected findings are absent or outside the chosen repair rules. Read a fresh audit.", 409)
        changes, exclusions, targets = [], [], set()
        complete = report["coverage"]["audit_complete"]
        active = {f["drawing_file"] for f in report["scope"]["included_files"]
                  if f["state"] in {"active_foreground", "active_background"}}
        for finding in report["findings"]:
            rule_id = finding["rule_id"]
            reason = ("rule_not_selected" if rule_id not in choices else
                      "finding_not_selected" if ids is not None and finding["finding_id"] not in ids else
                      "selection_exception" if decisions.get(fingerprint(finding["ref"])) == "excluded_elements" else
                      "selection_predicate_false" if decisions.get(fingerprint(finding["ref"])) == "predicate_false" else
                      "selection_not_checked" if decisions.get(fingerprint(finding["ref"])) == "predicate_not_checked" else
                      "audit_incomplete" if not complete else
                      "file_not_active" if finding["ref"]["drawing_file"] not in active else
                      "old_value_unavailable" if finding["evidence"]["raw"]["status"] != "observed" else None)
            if reason:
                exclusions.append({"finding_id": finding["finding_id"], "rule_id": rule_id,
                                   "ref": copy.deepcopy(finding["ref"]), "reason": reason})
                continue
            rule = rules[rule_id]
            if rule["kind"] == "required_layer":
                operation = "set_layer"
                resource = copy.deepcopy(report["profile_binding"]["layers"][choices[rule_id]]["value"])
                new_value = resource["layer_id"]
                field = "layer_id"
            else:
                operation = "set_attribute"
                resource = copy.deepcopy(report["profile_binding"]["attributes"]["status"]["value"])
                new_value = choices[rule_id]
                field = f"attribute:{resource['attribute_id']}"
            key = (fingerprint(finding["ref"]), field)
            if key in targets:
                raise BridgeError("repair_conflict", "Multiple repair rules target the same element/property. Choose one explicit rule.", 409)
            targets.add(key)
            changes.append({"finding_id": finding["finding_id"], "rule_id": rule_id,
                            "ref": copy.deepcopy(finding["ref"]), "locator": copy.deepcopy(finding["locator"]),
                            "operation": operation, "field": field, "resource": resource,
                            "old_value": copy.deepcopy(finding["evidence"]["raw"]), "new_value": new_value,
                            "source_fingerprint": finding["source_fingerprint"], "write_eligibility": "not_checked"})
        changes.sort(key=lambda c: (c["ref"]["drawing_file"], c["ref"]["model_uuid"], c["field"]))
        plan_complete = (complete and not any(e["reason"] in {"file_not_active", "old_value_unavailable"} for e in exclusions)
                         and not (selection_result and selection_result["predicate_not_checked"]))
        created = self.queries.clock()
        plan = {"schema_version": SCHEMA, "action": "preview", "read_only": True,
                "state": "preview_ready" if plan_complete else "not_checked", "plan_id": uuid4().hex,
                "query_session_id": self.queries.session_id, "profile_id": report["profile_id"],
                "profile_version": report["profile_version"], "profile_fingerprint": report["profile_fingerprint"],
                "source_fingerprint": report["source_fingerprint"], "audit_report_fingerprint": report["report_fingerprint"],
                "scope": copy.deepcopy(report["scope"]), "coverage": copy.deepcopy(report["coverage"]),
                "changes": changes, "exclusions": exclusions,
                "counts": {"changes": len(changes), "excluded_findings": len(exclusions), "audit_findings": len(report["findings"])},
                "capabilities": capability_probe(base), "apply_available": False, "usable_for_write": False,
                "allplan_acceptance": "not_run", "runtime_verified": False,
                "expires_after_seconds": self.TTL_SECONDS,
                "reference_lifetime": "host_session_project_document_snapshot; no persistence or authorization",
                "report_text": self._text(changes, exclusions, complete)}
        if selection_result is not None:
            plan["selection"] = copy.deepcopy(request["selection"])
            plan["selection_result"] = selection_result
            plan["report_text"] += (f"\nSelection: {selection_result['selected_elements']} selected; "
                                    f"{selection_result['excluded_elements']} explicit exceptions; "
                                    f"{selection_result['predicate_not_checked']} unchecked predicates.")
        if "workflow" in request:
            plan["workflow"] = copy.deepcopy(request["workflow"])
            workflow = request["workflow"]
            if workflow["kind"] == "office_standard_preview":
                plan["report_text"] += f"\nStandard: {workflow['standard_id']} {workflow['standard_version']}. Preview only."
        plan["evaluation_apply_available"] = self.executor.evaluation_scope(plan)
        plan["evaluation_apply_limit"] = "disposable_copy_reviewed_two_repairs; native acceptance pending"
        if "selection" in plan or "workflow" in plan:
            plan["evaluation_apply_limit"] = "Selected/standard workflows are preview-only; no native apply authorization."
        plan["plan_hash"] = fingerprint({"plan": plan, "request": request})
        entry = {"created": created, "request": copy.deepcopy(request), "plan": plan}
        size = len(json.dumps(entry, ensure_ascii=False, allow_nan=False).encode())
        if size > self.MAX_PLAN_BYTES:
            raise BridgeError("scan_limit_exceeded", "Repair plan exceeds the 4 MiB budget; no plan was stored.", 409)
        entry["size"] = size
        while self.plans and (len(self.plans) >= self.MAX_PLANS or sum(e["size"] for e in self.plans.values()) + size > self.MAX_CACHE_BYTES):
            self.plans.popitem(last=False)
        self.plans[plan["plan_id"]] = entry
        return copy.deepcopy(plan)

    def _revalidate(self, doc, base, settings, request):
        entry = self.plans.get(request["plan_id"])
        if entry is None:
            raise BridgeError("plan_expired", "Plan expired, was evicted or belongs to another host session. Preview again.", 409)
        plan = entry["plan"]
        if request["plan_hash"] != plan["plan_hash"]:
            raise BridgeError("plan_hash_mismatch", "Use the exact hash returned with the reviewed plan.", 409)
        report = run_audit(self.queries, doc, base, settings, entry["request"]["audit"])
        # A blocked native read may finish after the plan's lifetime.
        if self.queries.clock() - entry["created"] >= self.TTL_SECONDS:
            del self.plans[request["plan_id"]]
            raise BridgeError("plan_expired", "Plan expired during revalidation. Preview again.", 409)
        valid = (report["source_fingerprint"] == plan["source_fingerprint"]
                 and report["report_fingerprint"] == plan["audit_report_fingerprint"])
        if not valid:
            del self.plans[request["plan_id"]]
        return {"schema_version": SCHEMA, "action": "revalidate", "read_only": True,
                "plan_id": request["plan_id"], "plan_hash": plan["plan_hash"],
                "state": "unchanged" if valid else "conflict", "source_unchanged": valid,
                "current_source_fingerprint": report["source_fingerprint"],
                "current_audit_report_fingerprint": report["report_fingerprint"],
                "expires_in_seconds": max(0, int(self.TTL_SECONDS - (self.queries.clock() - entry["created"]))),
                "apply_available": False, "usable_for_write": False,
                "evaluation_apply_available": valid and plan["evaluation_apply_available"],
                "report_text": "Plan evidence unchanged; bounded disposable-copy evaluation apply requires explicit acknowledgement." if valid else
                               "Plan conflict: identity, resources, scope or audited source changed. Preview again."}

    @staticmethod
    def _text(changes, exclusions, complete):
        lines = [f"Repair preview: {len(changes)} proposed changes; {len(exclusions)} excluded findings.",
                 f"Audit complete: {complete}. Preview requests no writes; evaluation apply requires a reviewed disposable copy."]
        for change in changes:
            loc = change["locator"]
            lines.append(f"{change['rule_id']}: file {loc['drawing_file']}, mark {loc['mark'].get('value')!r}, "
                         f"model {loc['model_uuid']}, center {loc['center_mm'].get('value')} mm: "
                         f"{change['field']} {change['old_value'].get('value')!r} -> {change['new_value']!r}.")
        return "\n".join(lines)
