"""Typed criterion edits, independent of audit findings, using the M3 journal."""
from __future__ import annotations

import copy
import json
from collections import Counter
from uuid import uuid4

from .model_context import integer
from .model_metadata import bounded_text
from .model_properties import positive_id
from .model_edit_contracts import DEFAULT_NATIVE_TYPES, SCHEMA, validate_request
from .query_contracts import evaluate, fingerprint, predicate_fields
from .repair_contracts import capability_probe
from .transport import BridgeError

KIND = "typed_model_edit"


def evaluate_criterion(node, fields):
    """Only a complete explicit presence read can prove an absent attribute."""
    if node is None:
        return True
    if "not" in node:
        value = evaluate_criterion(node["not"], fields)
        return None if value is None else not value
    for group in ("all", "any"):
        if group in node:
            values = [evaluate_criterion(child, fields) for child in node[group]]
            decisive = group == "any"
            return decisive if decisive in values else None if None in values else not decisive
    observed = fields[node["field"]]
    if observed.get("status") == "absent" and observed.get("presence_proven") is True:
        return False if node["op"] == "exists" else True if node["op"] == "is_unset" else None
    return evaluate(node, fields)


def bind_changes(doc, base, request, check, trace):
    """Resolve only explicitly requested resources; never enumerate definitions/enums."""
    bound, fields = [], set()

    def read(api, callback):
        check()
        result = trace.call(api, callback)
        check()
        return result

    for choice in request["changes"]:
        check()
        target = choice["target"]
        if target["kind"] == "layer":
            name = target["short_name"]
            ident = positive_id(read("LayerService.GetIDByShortName", lambda: base.LayerService.GetIDByShortName(name, doc)))
            doc_id = integer(read("DocumentAdapter.GetDocumentID", doc.GetDocumentID))
            actual = bounded_text(read("LayerService.GetShortNameByID", lambda: base.LayerService.GetShortNameByID(ident, doc_id)))
            if actual != name:
                raise ValueError("Layer name/ID round trip differs")
            item = {"field": "layer_id", "operation": "set_layer", "property_role": "layer",
                    "resource": {"layer_id": ident, "short_name": actual}, "new_value": ident}
        else:
            ident = target.get("attribute_id")
            if ident is None:
                ident = positive_id(read("AttributeService.GetAttributeID", lambda: base.AttributeService.GetAttributeID(doc, target["name"])))
            name = bounded_text(read("AttributeService.GetAttributeName", lambda: base.AttributeService.GetAttributeName(doc, ident)))
            if not name or (target.get("name") is not None and name != target["name"]):
                raise ValueError("Attribute name/ID round trip differs")
            if positive_id(read("AttributeService.GetAttributeID", lambda: base.AttributeService.GetAttributeID(doc, name))) != ident:
                raise ValueError("Attribute ID/name round trip differs")
            # Compare real enum members from the loaded SDK, never guessed codes.
            # A readable/computed field still does not imply native writability.
            type_value = read("AttributeService.GetAttributeType", lambda: base.AttributeService.GetAttributeType(doc, ident))
            type_name = {"text": "String", "integer": "Integer", "real": "Double", "boolean": "Boolean"}[choice["value_type"]]
            enum_type = base.AttributeService.AttributeType
            expected_type = getattr(enum_type, type_name, None)
            if expected_type is None or type_value != expected_type:
                raise ValueError("Declared value type differs from the project attribute type or SDK type is unsupported")
            item = {"field": f"attribute:{ident}", "operation": "set_attribute", "property_role": "attribute",
                    "resource": {"attribute_id": ident, "name": name,
                                 "data_type": {"text": "string"}.get(choice["value_type"], choice["value_type"]),
                                 "native_type_member": type_name,
                                 "read_mode": request.get("attribute_read_mode", "stored")},
                    "new_value": float(choice["value"]) if choice["value_type"] == "real" else choice["value"],
                    "mode": choice.get("mode", "replace")}
        if item["field"] in fields:
            raise BridgeError("property_binding_unavailable", "Two changes resolve to the same property.", 409)
        fields.add(item["field"])
        bound.append(item)
        check()
    return bound


def observe(plans, doc, base, settings, request):
    validate_request(request)
    started = plans.queries.clock()
    from .property_probe import NativeProbeTrace
    trace = NativeProbeTrace(plans.trace_path, "model_edit")

    def check():
        if plans.queries.clock() - started >= plans.queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Model edit evidence exceeded its read budget.", 409)

    try:
        binding = bind_changes(doc, base, request, check, trace)
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("property_binding_unavailable", "An explicit attribute/layer binding could not be verified; no resource was guessed or created.", 409) from exc
    from .native_readers import COMPONENT_TYPES
    native_types = request.get("native_types", DEFAULT_NATIVE_TYPES)
    family_predicate = {"field": "type_name", "op": "in", "value": native_types or sorted(COMPONENT_TYPES)}
    fields = predicate_fields(request.get("predicate")) | {b["field"] for b in binding}
    attribute_ids = sorted(set(request.get("attribute_ids", [])) |
                           {int(f.split(":")[1]) for f in fields if f.startswith("attribute:")})
    if len(attribute_ids) > 32:
        raise BridgeError("invalid_payload", "At most 32 bound/criterion attributes may be read.")
    # Keep all peers, including nonmatches, in the source to detect new matches.
    query = {"schema_version": "m1-query-1", "action": "query", "scope": request.get("scope", "open_drawings"),
             "component_kind": "semantic_component", "predicate": family_predicate,
             "fields": sorted((fields - {f for f in fields if f.startswith("attribute:")}) |
                              {"display_name", "layer_id", "file_state", "family"}),
             "attribute_ids": attribute_ids, "max_adapters": request.get("max_adapters", 5000)}
    live, owners = {}, []
    snapshot = trace.call("M1.semantic_component_scan", lambda: plans.queries._scan(
        doc, base, settings, query, adapter_sink=live, adapter_owners=owners))
    check()
    # A new opt-in reader can establish absence; legacy ReadAll paths stay intact.
    if request.get("attribute_read_mode", "stored") == "all_and_computable" and attribute_ids:
        from .native_model_edit import attribute_fields
        for element in snapshot["elements"]:
            representations = live.get((element["ref"]["drawing_file"], element["ref"]["model_uuid"]), {})
            results = []
            for adapters in representations.values():
                for adapter in adapters:
                    check()
                    results.append(trace.call("BaseElementAdapter.GetAttributes.ReadAllAndComputable", lambda:
                        attribute_fields(adapter, base, attribute_ids, "all_and_computable"),
                        drawing_file=element["ref"]["drawing_file"], model_uuid=element["ref"]["model_uuid"]))
            if not results or len({fingerprint(r) for r in results}) != 1 or element["view_identity_not_checked"]:
                values = {f"attribute:{i}": {"status": "not_checked", "value": None,
                                             "reason": "attribute_representation_conflict"} for i in attribute_ids}
            else:
                values = results[0]
            element["fields"].update(values)
    excluded = set(request.get("exclude_model_uuids", []))
    if excluded - {e["ref"]["model_uuid"] for e in snapshot["elements"]}:
        raise BridgeError("selection_stale", "An explicit exception is absent from the complete family scope.", 409)
    checks = []
    for element in snapshot["elements"]:
        values = element["fields"]
        match = evaluate_criterion(request.get("predicate"), values)
        decision = ("excluded" if element["ref"]["model_uuid"] in excluded else
                    "unknown" if match is None else "matched" if match else "nonmatching")
        checks.append({"ref": element["ref"], "decision": decision})
    field_complete = all(v.get("status") in {"observed", "absent", "missing"}
                         for e in snapshot["elements"] for v in e["fields"].values())
    complete = snapshot["coverage"]["requested_scope_complete"] and field_complete and not any(c["decision"] == "unknown" for c in checks)
    snapshot["coverage"]["returned_fields_complete"] = field_complete
    snapshot["source_fingerprint"] = fingerprint({"m1_source": snapshot["source_fingerprint"],
                                                   "elements": snapshot["elements"], "binding": binding})
    report = {"schema_version": SCHEMA, "read_only": True, "checks": checks, "binding": binding,
              "source_fingerprint": snapshot["source_fingerprint"], "scope": snapshot["scope"],
              "coverage": {**snapshot["coverage"], "criteria_complete": complete},
              "counts": dict(Counter(c["decision"] for c in checks)), "omissions": snapshot["omissions"],
              "attribute_read_mode": request.get("attribute_read_mode", "stored"),
              "native_acceptance": "not_run", "runtime_verified": False}
    report["report_fingerprint"] = fingerprint(report)
    check()
    return report, snapshot, query


def preview(plans, doc, base, settings, request):
    from .native_model_edit import value_matches
    report, snapshot, _ = observe(plans, doc, base, settings, request)
    decisions = {fingerprint(c["ref"]): c["decision"] for c in report["checks"]}
    changes, blocked, targets = [], [], []
    for element in snapshot["elements"]:
        if decisions[fingerprint(element["ref"])] != "matched":
            continue
        targets.append(copy.deepcopy(element["ref"]))
        for bound in report["binding"]:
            old = element["fields"][bound["field"]]
            mode = bound.get("mode", "replace")
            absent = old.get("status") == "absent" and old.get("presence_proven") is True
            observed = old.get("status") == "observed"
            real_equal = (bound["resource"].get("data_type") == "real"
                          and value_matches(old.get("value"), "real") and old.get("value") == bound["new_value"])
            if mode != "add" and observed and (real_equal or type(old.get("value")) is type(bound["new_value"]) and old["value"] == bound["new_value"]):
                continue
            reason = None
            if old.get("computed_only") is True:
                reason = "computed_attribute_is_read_only"
            elif not observed and not absent:
                reason = "old_value_unknown"
            elif absent and mode == "replace":
                reason = "replace_requires_existing_attribute"
            elif observed and mode == "add":
                reason = "add_requires_proven_absence"
            elif observed and bound["operation"] != "set_layer" and old.get("value") is not None and not value_matches(old["value"], bound["resource"]["data_type"]):
                reason = "old_value_type_differs"
            if reason:
                blocked.append({"ref": element["ref"], "field": bound["field"], "reason": reason})
                continue
            change = {**copy.deepcopy(bound), "ref": copy.deepcopy(element["ref"]),
                      "adapter_version": SCHEMA, "native_type": element["fields"]["type_name"]["value"],
                      "old_value": copy.deepcopy(old), "source_fingerprint": element["source_fingerprint"],
                      "locator": {"drawing_file": element["ref"]["drawing_file"], "model_uuid": element["ref"]["model_uuid"]}}
            if absent:
                change["operation"] = "add_attribute"
            changes.append(change)
    ready = report["coverage"]["criteria_complete"] and not blocked and len(changes) <= plans.executor.MAX_CHANGES
    plan = {"schema_version": SCHEMA, "action": "preview", "read_only": True, "plan_id": uuid4().hex,
            "state": ("preview_ready" if changes else "no_op") if ready else "not_checked",
            "source_kind": KIND, "source_fingerprint": snapshot["source_fingerprint"],
            "evidence_fingerprint": report["report_fingerprint"], "scope": report["scope"], "coverage": report["coverage"],
            "changes": changes, "blocked": blocked, "highlight_targets": targets, "criteria": report,
            "capabilities": capability_probe(base), "counts": {**report["counts"], "changes": len(changes), "blocked": len(blocked),
                                                                "highlight_targets": len(targets)},
            "requires_highlight": True, "native_selection": "unsupported_use_explicit_highlight",
            "runtime_verified": False, "allplan_acceptance": "not_run", "usable_for_write": False,
            "expires_after_seconds": plans.TTL_SECONDS,
            "limits": {"changes": plans.executor.MAX_CHANGES, "write_scope": "one_active_foreground_drawing",
                       "native_material_update": "unsupported_use_explicit_attribute_target"}}
    plan["evaluation_apply_available"] = plans.executor.evaluation_scope(plan)
    plan["evaluation_highlight_available"] = ready
    plan["plan_hash"] = fingerprint({"plan": plan, "request": request})
    entry = {"created": plans.queries.clock(), "request": copy.deepcopy(request), "plan": plan}
    entry["size"] = len(json.dumps(entry, ensure_ascii=False, allow_nan=False).encode())
    if entry["size"] > plans.MAX_PLAN_BYTES:
        raise BridgeError("scan_limit_exceeded", "Model edit plan exceeded its size budget.", 409)
    while (len(plans.plans) + len(plans.invalidated_plans) >= plans.MAX_PLANS
           or sum(e["size"] for c in (plans.plans, plans.invalidated_plans) for e in c.values()) + entry["size"] > plans.MAX_CACHE_BYTES):
        cache = min((c for c in (plans.plans, plans.invalidated_plans) if c), key=lambda c: next(iter(c.values()))["created"])
        cache.popitem(last=False)
    plans.plans[plan["plan_id"]] = entry
    return copy.deepcopy(plan)


def revalidate(plans, doc, base, settings, request):
    ident = request["plan_id"]
    invalidated = ident not in plans.plans
    cache = plans.invalidated_plans if invalidated else plans.plans
    entry = cache.get(ident)
    if not entry or entry["plan"].get("source_kind") != KIND:
        raise BridgeError("plan_expired", "Model edit plan expired or belongs to another workflow.", 409)
    plan = entry["plan"]
    if request["plan_hash"] != plan["plan_hash"]:
        raise BridgeError("plan_hash_mismatch", "Use the exact reviewed model edit plan hash.", 409)
    report, _, _ = observe(plans, doc, base, settings, entry["request"])
    if plans.queries.clock() - entry["created"] >= plans.TTL_SECONDS:
        del cache[ident]
        raise BridgeError("plan_expired", "Model edit plan expired during revalidation.", 409)
    valid = report["report_fingerprint"] == plan["evidence_fingerprint"] and not invalidated
    if not valid:
        del cache[ident]
    return {"schema_version": SCHEMA, "action": "revalidate", "read_only": True,
            "state": "unchanged" if valid else "conflict", "plan_id": ident, "plan_hash": plan["plan_hash"]}


def highlight(plans, doc, base, settings, ifw, request):
    if revalidate(plans, doc, base, settings, request)["state"] != "unchanged":
        raise BridgeError("repair_conflict", "Model edit criteria changed before highlight.", 409)
    entry = plans.plans[request["plan_id"]]
    for pending in plans.plans.values():
        pending.pop("presentation", None)
    if not entry["plan"]["evaluation_highlight_available"]:
        raise BridgeError("repair_scope_unavailable", "Only a complete model edit plan may be highlighted.", 409)
    report, snapshot, query = observe(plans, doc, base, settings, entry["request"])
    if report["report_fingerprint"] != entry["plan"]["evidence_fingerprint"]:
        raise BridgeError("repair_conflict", "Model edit evidence changed before highlight.", 409)
    # model_selection compares M1 source, whereas the plan also binds presence/resource evidence.
    raw_snapshot = plans.queries._scan(doc, base, settings, query)
    ident = uuid4().hex
    if len(plans.queries.selections) >= plans.queries.MAX_SELECTIONS:
        plans.queries.selections.popitem(last=False)
    plans.queries.selections[ident] = {"created": entry["created"], "request": query, "snapshot": raw_snapshot, "cursors": {}}
    try:
        from .model_selection import present_selection
        result = present_selection(plans.queries, doc, base, settings, ifw,
                                   {"schema_version": "m4-selection-1", "action": "highlight", "selection_id": ident},
                                   target_model_uuids={r["model_uuid"] for r in entry["plan"]["highlight_targets"]})
    finally:
        plans.queries.selections.pop(ident, None)
    if result["state"] == "submitted":
        entry["presentation"] = {"state": "submitted", "plan_hash": entry["plan"]["plan_hash"]}
    return {**result, "plan_id": request["plan_id"], "plan_hash": request["plan_hash"]}
