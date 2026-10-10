"""Deterministic, non-destructive numbering over the same full audited snapshot."""
import copy

from .audit_contracts import normalized
from .model_audit import attribute_value, locator
from .query_contracts import fingerprint
from .transport import BridgeError

NUMBERING = {"policy_id": "preserve-valid-fill-gaps", "policy_version": "1.0.0",
             "prefix": "S", "start": 1, "width": 2,
             "order": ["center_y_mm", "center_x_mm", "center_z_mm", "model_uuid"],
             "required_rule_id": "QA-001", "unique_rule_id": "QA-002"}


def number_marks(snapshot, report, request, decisions, check_budget):
    policy = request["audit"]["profile"]["string_policies"]["mark"]
    metadata = {"definition": copy.deepcopy(NUMBERING), "state": "validated",
                "uses_full_snapshot": True, "preserves_unselected_peers": True,
                "assignments": [], "preserved_duplicate_keepers": []}
    if not report["coverage"]["audit_complete"]:
        metadata.update(state="not_checked", reason="audit_incomplete")
        return [], metadata
    groups, missing, order = {}, [], {}
    available = {(f["rule_id"], f["ref"]["model_uuid"]): f for f in report["findings"]}
    ids = request.get("finding_ids")
    def eligible(element, rule_id):
        finding = available.get((rule_id, element["ref"]["model_uuid"]))
        return (finding is not None and (ids is None or finding["finding_id"] in ids)
                and decisions.get(fingerprint(element["ref"]), "selected_elements") == "selected_elements")
    for element in snapshot["elements"]:
        check_budget()
        raw, state, value = attribute_value(element, report["profile_binding"], "mark", policy)
        ref = element["ref"]
        center = locator(element, report["profile_binding"])["center_mm"]
        if state == "not_checked" or center["status"] != "observed":
            metadata.update(state="not_checked", reason="mark_or_order_unavailable")
            return [], metadata
        x, y, z = center["value"]
        order[ref["model_uuid"]] = (y, x, z, ref["model_uuid"])
        if state == "missing":
            if eligible(element, NUMBERING["required_rule_id"]):
                # Attribute append/null conversion is outside this setter boundary.
                if raw.get("status") != "observed" or not isinstance(raw.get("value"), str):
                    metadata.update(state="not_checked", reason="existing_string_mark_required")
                    return [], metadata
                missing.append((element, NUMBERING["required_rule_id"]))
        else:
            group = (ref["drawing_file"], ref["type_uuid"], value)
            groups.setdefault(group, []).append(element)
    targets = missing
    occupied = {}
    for group, peers in sorted(groups.items()):
        check_budget()
        occupied.setdefault(group[:2], set()).add(group[2])
        if len(peers) > 1:
            peers.sort(key=lambda e: (eligible(e, NUMBERING["unique_rule_id"]), order[e["ref"]["model_uuid"]]))
            metadata["preserved_duplicate_keepers"].append(copy.deepcopy(peers[0]["ref"]))
            targets.extend((e, NUMBERING["unique_rule_id"]) for e in peers[1:]
                           if eligible(e, NUMBERING["unique_rule_id"]))
    if len(targets) + len(request["repairs"]) > 32:
        raise BridgeError("repair_scope_unavailable", "Numbering exceeds 32 reviewed choices; narrow proposals with selection.", 409)
    choices, next_number = [], {}
    for element, rule_id in sorted(targets, key=lambda item: order[item[0]["ref"]["model_uuid"]]):
        ref = element["ref"]
        group = (ref["drawing_file"], ref["type_uuid"])
        reserved = occupied.setdefault(group, set())
        number = next_number.get(group, NUMBERING["start"])
        while True:
            check_budget()
            value = NUMBERING["prefix"] + str(number).zfill(NUMBERING["width"])
            number += 1
            if normalized(value, policy) not in reserved:
                break
        reserved.add(normalized(value, policy))
        next_number[group] = number
        choice = {"rule_id": rule_id, "model_uuid": ref["model_uuid"], "value": value}
        choices.append(choice)
        metadata["assignments"].append(copy.deepcopy(choice))
    return choices, metadata
