"""Dependency-free M3 plan validation; run before accessing native context."""
import re

from .audit_contracts import bounded_string, normalized, selected_rules, validate_audit_request
from .query_contracts import invalid, keys
from .transport import BridgeError

SCHEMA = "m3-repair-1"


def validate_repair_request(request):
    if isinstance(request, dict) and request.get("action") == "apply":
        raise BridgeError("repair_apply_unavailable", "Native repair apply is unavailable in this preview package. Verify the M3 owner gate first.", 409)
    if not isinstance(request, dict):
        invalid("Repair request must be an object.")
    action = request.get("action")
    if action == "revalidate":
        required = {"schema_version", "action", "plan_id", "plan_hash"}
        keys(request, required, required)
        for key, size in (("plan_id", 32), ("plan_hash", 64)):
            if not isinstance(request[key], str) or not re.fullmatch(r"[0-9a-f]{" + str(size) + "}", request[key]):
                invalid(f"Invalid {key}.")
    elif action == "preview":
        required = {"schema_version", "action", "audit", "repairs"}
        keys(request, required | {"finding_ids"}, required)
        validate_audit_request(request["audit"])
        scope = request["audit"]["scope"]
        if scope["include_passive"] or len(scope["drawing_files"]) != 1:
            invalid("Repair preview requires one explicit drawing file and include_passive=false.")
        choices = request["repairs"]
        if not isinstance(choices, list) or not 1 <= len(choices) <= 32:
            invalid("repairs must contain 1..32 explicit choices.")
        rules = {r["rule_id"]: r for r in selected_rules(request["audit"])}
        seen = set()
        for choice in choices:
            keys(choice, {"rule_id", "value"}, {"rule_id", "value"})
            ident = choice["rule_id"]
            if not isinstance(ident, str) or ident not in rules or ident in seen:
                invalid("Repair choices must reference distinct selected rule IDs.")
            seen.add(ident)
            bounded_string(choice["value"], 128, "Repair value")
            rule = rules[ident]
            if rule["kind"] == "required_layer":
                if choice["value"] != rule["expected_layer"]:
                    invalid("Layer repair must use the rule's explicit expected layer role.")
            elif rule["kind"] == "allowed_attribute_values" and rule["attribute"] == "status":
                policy = request["audit"]["profile"]["string_policies"]["status"]
                if normalized(choice["value"], policy) not in {normalized(v, policy) for v in rule["allowed_values"]}:
                    invalid("Status repair value must satisfy the selected rule.")
            else:
                invalid("This slice supports required-layer and allowed-status repair previews only.")
        if "finding_ids" in request:
            ids = request["finding_ids"]
            if (not isinstance(ids, list) or not 1 <= len(ids) <= 100
                    or any(not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v) for v in ids)
                    or len(set(ids)) != len(ids)):
                invalid("finding_ids must contain 1..100 distinct finding hashes.")
    else:
        invalid("Repair action must be preview or revalidate.")
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
