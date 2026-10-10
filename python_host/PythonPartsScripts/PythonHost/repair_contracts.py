"""Dependency-free M3 plan validation; run before accessing native context."""
import re

from .audit_contracts import bounded_string, is_missing_string, normalized, selected_rules, validate_audit_request
from .query_contracts import invalid, keys, predicate_fields
from .transport import BridgeError

SCHEMA = "m3-repair-1"


def validate_repair_request(request):
    if not isinstance(request, dict):
        invalid("Repair request must be an object.")
    action = request.get("action")
    if action in {"revalidate", "apply", "recover"}:
        required = {"schema_version", "action", "plan_id", "plan_hash"}
        if action == "recover":
            required = {"schema_version", "action", "execution_id"}
        elif action == "apply":
            required |= {"execution_id", "acknowledgement"}
        optional = {"workflow_kind"} if action == "apply" else set()
        keys(request, required | optional, required)
        for key, size in (("plan_id", 32), ("plan_hash", 64), ("execution_id", 32)):
            if key not in required:
                continue
            if not isinstance(request[key], str) or not re.fullmatch(r"[0-9a-f]{" + str(size) + "}", request[key]):
                invalid(f"Invalid {key}.")
        if action == "apply":
            if (not isinstance(request["acknowledgement"], str)
                    or request["acknowledgement"] not in {"disposable_copy_reviewed_two_repairs", "disposable_copy_reviewed_plan"}):
                invalid("Apply requires acknowledgement of the reviewed repairs on a disposable project copy.")
            if "workflow_kind" in request and (not isinstance(request["workflow_kind"], str)
                    or request["workflow_kind"] not in {"office_standard_preview", "rule_based_edit_preview"}):
                invalid("Unknown apply workflow.")
    elif action == "preview":
        required = {"schema_version", "action", "audit", "repairs"}
        keys(request, required | {"finding_ids", "selection", "workflow"}, required)
        validate_audit_request(request["audit"])
        scope = request["audit"]["scope"]
        if scope["include_passive"] or len(scope["drawing_files"]) != 1:
            invalid("Repair preview requires one explicit drawing file and include_passive=false.")
        if "selection" in request:
            selection = request["selection"]
            keys(selection, {"where", "exclude_model_uuids"}, {"where"})
            if not isinstance(selection["where"], dict):
                invalid("Repair selection requires an explicit predicate.")
            fields = predicate_fields(selection["where"])
            allowed = {"mark", "status", "layer_id", "file_state"}
            allowed.update(r["field"] for r in selected_rules(request["audit"]) if r["kind"] == "dimension_range")
            if not fields <= allowed:
                invalid("Repair selection may use only mark/status/layer_id/file_state and selected audit dimension fields.")
            ids = selection.get("exclude_model_uuids", [])
            if (not isinstance(ids, list) or len(ids) > 100
                    or any(not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", v) for v in ids)
                    or len(set(ids)) != len(ids)):
                invalid("Exceptions must contain at most 100 distinct canonical model UUIDs.")
        if "workflow" in request:
            workflow = request["workflow"]
            if not isinstance(workflow, dict):
                invalid("workflow must be an object.")
            if workflow.get("kind") == "office_standard_preview":
                keys(workflow, {"kind", "standard_id", "standard_version", "standard_fingerprint"},
                     {"kind", "standard_id", "standard_version", "standard_fingerprint"})
                bounded_string(workflow["standard_id"], 64, "Standard ID")
                bounded_string(workflow["standard_version"], 32, "Standard version")
                if not isinstance(workflow["standard_fingerprint"], str) or not re.fullmatch(r"[0-9a-f]{64}", workflow["standard_fingerprint"]):
                    invalid("Invalid standard fingerprint.")
            elif workflow.get("kind") == "rule_based_edit_preview":
                keys(workflow, {"kind"}, {"kind"})
                if "selection" not in request:
                    invalid("Rule-based preview requires selection.")
            else:
                invalid("Unknown preview workflow.")
        choices = request["repairs"]
        if not isinstance(choices, list) or not 1 <= len(choices) <= 32:
            invalid("repairs must contain 1..32 explicit choices.")
        rules = {r["rule_id"]: r for r in selected_rules(request["audit"])}
        seen, mark_targets = set(), set()
        for choice in choices:
            keys(choice, {"rule_id", "value", "model_uuid"}, {"rule_id", "value"})
            ident = choice["rule_id"]
            target = choice.get("model_uuid")
            if target is not None and (not isinstance(target, str) or not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", target)):
                invalid("Mark targets require canonical model UUIDs.")
            if not isinstance(ident, str) or ident not in rules or (ident, target) in seen:
                invalid("Repair choices must reference distinct selected rule/target pairs.")
            seen.add((ident, target))
            bounded_string(choice["value"], 128, "Repair value")
            rule = rules[ident]
            if rule["kind"] in {"required_attribute", "unique_attribute"} and rule["attribute"] == "mark":
                if target is None or target in mark_targets:
                    invalid("Each mark repair requires one distinct explicit model UUID.")
                mark_targets.add(target)
                if not {"required_attribute", "unique_attribute"} <= {
                        r["kind"] for r in rules.values() if r.get("attribute") == "mark"}:
                    invalid("Mark repairs require selected required-mark and unique-mark rules.")
                policy = request["audit"]["profile"]["string_policies"]["mark"]
                value = choice["value"]
                if (not value.strip() or is_missing_string(value, policy)
                        or any(ord(c) < 32 or ord(c) == 127 for c in value)):
                    invalid("Mark repairs require a nonmissing string without control characters.")
            elif "model_uuid" in choice:
                invalid("Explicit model UUID choices are supported only for mark repairs.")
            elif rule["kind"] == "required_layer":
                if choice["value"] != rule["expected_layer"]:
                    invalid("Layer repair must use the rule's explicit expected layer role.")
            elif rule["kind"] == "allowed_attribute_values" and rule["attribute"] == "status":
                policy = request["audit"]["profile"]["string_policies"]["status"]
                if normalized(choice["value"], policy) not in {normalized(v, policy) for v in rule["allowed_values"]}:
                    invalid("Status repair value must satisfy the selected rule.")
            else:
                invalid("Supported previews are required-layer, allowed-status and explicit mark repairs.")
        if "finding_ids" in request:
            ids = request["finding_ids"]
            if (not isinstance(ids, list) or not 1 <= len(ids) <= 100
                    or any(not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v) for v in ids)
                    or len(set(ids)) != len(ids)):
                invalid("finding_ids must contain 1..100 distinct finding hashes.")
    else:
        invalid("Repair action must be preview, revalidate, apply or recover.")
    if request["schema_version"] != SCHEMA:
        invalid(f"schema_version must be {SCHEMA}.")


def capability_probe(base):
    """Inspect documented API symbols only; never invoke a setter or Undo."""
    symbols = {}
    for service, method in (("ElementsAttributeService", "ChangeAttributes"),
                            ("ElementsLayerService", "ChangeLayer")):
        name = service + "." + method
        try:
            member = getattr(getattr(base, service), method)
            symbols[name] = {"status": "observed", "callable": callable(member),
                             "doc": (getattr(member, "__doc__", None) or "")[:2048]}
        except Exception as exc:
            symbols[name] = {"status": "not_checked", "reason": type(exc).__name__}
    return {"method": "symbol_inspection_without_invocation", "symbols": symbols,
            "per_element_writability": "not_checked", "native_write_readback": "not_checked",
            "undo": "not_checked", "durable_retry_deduplication": "not_implemented",
            "apply_available": False}
