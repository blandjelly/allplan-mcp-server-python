"""Criterion-based Column layer plans, sharing the M3 executor and journal.

Only exact resource-name round trips and established Column reads are used.
Broad property definitions/enums are deliberately outside this workflow.
"""
from __future__ import annotations

import copy
import json
import re
from collections import Counter
from uuid import uuid4

from .model_context import integer
from .model_metadata import bounded_text
from .model_properties import positive_id
from .property_probe import NativeProbeTrace
from .query_contracts import bounded_int, fingerprint, invalid, keys
from .repair_contracts import capability_probe, validate_repair_request
from .transport import BridgeError

SCHEMA = "m4-column-layer-1"
KIND = "column_missing_fire_layer"
# Fire resistance *classification* (F30/F60), not the separate fire-risk field
# resolved as "Odporność ogniowa" / 1398 in the 0.17.0 native report. Resolve
# project IDs by exact names; do not replace missing bindings with a guessed ID.
DEFAULT_NAMES = ["Klasa odporności ogniowej", "Fire resistance classification"]
DEFAULT_UNDEFINED = ["<niezdefiniowany>", "<undefined>"]


def validate_request(request):
    if not isinstance(request, dict) or request.get("schema_version") != SCHEMA:
        invalid("Expected m4-column-layer-1 request.")
    action = request.get("action")
    if action == "preview":
        keys(request, {"schema_version", "action", "drawing_file", "attribute_names", "layer_short_name",
                       "undefined_values", "exclude_model_uuids"}, {"schema_version", "action", "drawing_file"})
        bounded_int(request["drawing_file"], 1, 2147483647, "drawing_file")
        for key, default, maximum, length in (("attribute_names", DEFAULT_NAMES, 4, 128),
                                             ("undefined_values", DEFAULT_UNDEFINED, 8, 128)):
            values = request.get(key, default)
            if (not isinstance(values, list) or not 1 <= len(values) <= maximum
                    or any(not isinstance(v, str) or not v.strip() or len(v) > length for v in values)
                    or len(set(values)) != len(values)):
                invalid(f"Invalid {key}; use distinct, bounded nonempty strings.")
        name = request.get("layer_short_name", "W1")
        if not isinstance(name, str) or not name.strip() or len(name) > 16:
            invalid("Invalid layer short name.")
        ids = request.get("exclude_model_uuids", [])
        if (not isinstance(ids, list) or len(ids) > 100 or any(not isinstance(v, str) or not re.fullmatch(
                r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", v) for v in ids) or len(set(ids)) != len(ids)):
            invalid("Invalid model UUID exceptions.")
    elif action in {"highlight", "revalidate", "apply", "recover"}:
        converted = {**request, "schema_version": "m3-repair-1"}
        if action == "highlight":
            converted["action"] = "revalidate"
        validate_repair_request(converted)
        if "workflow_kind" in request or "evaluation_stop" in request:
            invalid("No alternate workflow or diagnostic interruption on this route.")
        if action == "apply" and request["acknowledgement"] != "disposable_copy_reviewed_plan":
            invalid("Use disposable_copy_reviewed_plan for the new Column layer workflow.")
    else:
        invalid("Action must be preview, highlight, revalidate, apply or recover.")


def value_state(raw, undefined_values):
    # ReadAll explicitly omits computed attributes. Omission is not evidence of
    # native absence; it must never become a write target by a negated predicate.
    if raw["status"] == "missing":
        return "absent_from_readall_unknown"
    if raw["status"] != "observed":
        return "unreadable"
    value = raw.get("value")
    if value is None:
        return "null"
    if not isinstance(value, str):
        return "unsupported_value_type"
    if not value.strip():
        return "empty"
    if value.strip() in undefined_values:
        return "undefined"
    return "present"


def observe(plans, doc, base, settings, request):
    """Fresh JSON evidence for *all* Columns, including peers outside the match."""
    validate_request(request)
    trace = NativeProbeTrace(plans.trace_path, "column_layer")
    started = plans.queries.clock()

    def call(api, reader, **details):
        if plans.queries.clock() - started >= plans.queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Column layer evidence exceeded its read budget.", 409)
        result = trace.call(api, reader, **details)
        if plans.queries.clock() - started >= plans.queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Column layer evidence exceeded its read budget.", 409)
        return result

    resolutions = []
    for name in request.get("attribute_names", DEFAULT_NAMES):
        ident = call("AttributeService.GetAttributeID", lambda: integer(base.AttributeService.GetAttributeID(doc, name)), name=name)
        if ident <= 0:
            continue
        ident = positive_id(ident)
        actual = call("AttributeService.GetAttributeName", lambda: bounded_text(base.AttributeService.GetAttributeName(doc, ident)), attribute_id=ident)
        if actual != name:
            raise BridgeError("property_binding_unavailable", "Attribute name/ID round trip differs; no field was guessed.", 409)
        resolutions.append({"attribute_id": ident, "name": actual})
    if len({r["attribute_id"] for r in resolutions}) != 1:
        raise BridgeError("property_binding_unavailable", "Expected exactly one fire-resistance classification field (F30/F60): "
                          + ", ".join(request.get("attribute_names", DEFAULT_NAMES))
                          + ". Exact names were absent or ambiguous; no alternative fire-risk field was substituted.", 409)
    attribute = resolutions[0]
    name = request.get("layer_short_name", "W1")
    ident = call("LayerService.GetIDByShortName", lambda: positive_id(base.LayerService.GetIDByShortName(name, doc)), short_name=name)
    doc_id = call("DocumentAdapter.GetDocumentID", lambda: integer(doc.GetDocumentID()))
    actual = call("LayerService.GetShortNameByID", lambda: bounded_text(base.LayerService.GetShortNameByID(ident, doc_id)), layer_id=ident)
    if actual != name:
        raise BridgeError("property_binding_unavailable", "Layer short name/ID round trip differs; no layer was created.", 409)
    layer = {"layer_id": ident, "short_name": actual}
    query = {"schema_version": "m1-query-1", "action": "query",
             "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False, "visibility": "api_select_all"},
             "component_kind": "top_level_component", "predicate": {"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
             "fields": ["display_name", "layer_id", "file_state", "bounding_box_mm"],
             "attribute_ids": [attribute["attribute_id"]]}
    snapshot = call("M1.column_criterion_scan", lambda: plans.queries._scan(doc, base, settings, query, native_type_gate="Column_TypeUUID"))
    excluded = set(request.get("exclude_model_uuids", []))
    if excluded - {e["ref"]["model_uuid"] for e in snapshot["elements"]}:
        raise BridgeError("selection_stale", "An explicit exception is absent from the Column scope.", 409)
    checks = []
    for e in snapshot["elements"]:
        raw = e["fields"][f"attribute:{attribute['attribute_id']}"]
        state = value_state(raw, request.get("undefined_values", DEFAULT_UNDEFINED))
        match = state in {"null", "empty", "undefined"}
        decision = ("excluded" if e["ref"]["model_uuid"] in excluded else
                    "unknown" if state in {"absent_from_readall_unknown", "unreadable", "unsupported_value_type"} else
                    "nonmatching" if not match else
                    "unknown" if e["fields"]["layer_id"]["status"] != "observed" else
                    "no_op" if e["fields"]["layer_id"]["value"] == layer["layer_id"] else "change")
        checks.append({"ref": e["ref"], "fire_resistance": raw, "value_state": state, "decision": decision})
    complete = (snapshot["coverage"]["requested_scope_complete"] and snapshot["coverage"]["returned_fields_complete"]
                and not any(c["decision"] == "unknown" for c in checks)
                and snapshot["scope"]["included_files"] == [{"drawing_file": request["drawing_file"], "state": "active_foreground", "write_eligibility": "not_checked"}])
    report = {"schema_version": SCHEMA, "read_only": True, "checks": checks,
              "binding": {"attribute": attribute, "layer": layer, "name_resolutions": resolutions},
              "source_fingerprint": snapshot["source_fingerprint"], "scope": snapshot["scope"],
              "coverage": {**snapshot["coverage"], "criteria_complete": complete},
              "counts": dict(Counter(c["decision"] for c in checks)),
              "missing_policy": {"matches": ["null", "empty", "undefined"],
                                 "undefined_values": request.get("undefined_values", DEFAULT_UNDEFINED),
                                 "absent_from_readall": "unknown_never_selected"},
              "omissions": snapshot["omissions"], "runtime_verified": False}
    report["report_fingerprint"] = fingerprint(report)
    trace.record("column_layer", "completed")
    return report, snapshot, query


def preview(plans, doc, base, settings, request):
    report, snapshot, query = observe(plans, doc, base, settings, request)
    decisions = {c["ref"]["model_uuid"]: c["decision"] for c in report["checks"]}
    changes = []
    for e in snapshot["elements"]:
        if decisions[e["ref"]["model_uuid"]] != "change":
            continue
        changes.append({"ref": copy.deepcopy(e["ref"]), "operation": "set_layer", "field": "layer_id",
                        "property_role": "layer", "resource": copy.deepcopy(report["binding"]["layer"]),
                        "old_value": copy.deepcopy(e["fields"]["layer_id"]),
                        "new_value": report["binding"]["layer"]["layer_id"], "source_fingerprint": e["source_fingerprint"],
                        "locator": {"drawing_file": e["ref"]["drawing_file"], "model_uuid": e["ref"]["model_uuid"],
                                    "bounding_box_mm": e["fields"]["bounding_box_mm"]}})
    ident = uuid4().hex
    ready = report["coverage"]["criteria_complete"] and len(changes) <= plans.executor.MAX_CHANGES
    plan = {"schema_version": SCHEMA, "action": "preview", "read_only": True, "plan_id": ident,
            "state": ("preview_ready" if changes else "no_op") if ready else "not_checked",
            "source_kind": KIND, "source_fingerprint": snapshot["source_fingerprint"],
            "evidence_fingerprint": report["report_fingerprint"], "scope": report["scope"], "coverage": report["coverage"],
            "changes": changes, "criteria": report, "capabilities": capability_probe(base),
            "counts": {**report["counts"], "changes": len(changes), "columns": len(snapshot["elements"])},
            "requires_highlight": True, "native_selection": "not_requested_owner_accepts_highlight",
            "runtime_verified": False, "allplan_acceptance": "not_run", "usable_for_write": False,
            "expires_after_seconds": plans.TTL_SECONDS}
    plan["evaluation_apply_available"] = plans.executor.evaluation_scope(plan)
    plan["plan_hash"] = fingerprint({"plan": plan, "request": request})
    entry = {"created": plans.queries.clock(), "request": copy.deepcopy(request), "plan": plan}
    entry["size"] = len(json.dumps(entry, ensure_ascii=False, allow_nan=False).encode())
    if entry["size"] > plans.MAX_PLAN_BYTES:
        raise BridgeError("scan_limit_exceeded", "Column plan exceeded its size budget.", 409)
    while (len(plans.plans) + len(plans.invalidated_plans) >= plans.MAX_PLANS
           or sum(e["size"] for c in (plans.plans, plans.invalidated_plans) for e in c.values()) + entry["size"] > plans.MAX_CACHE_BYTES):
        cache = min((c for c in (plans.plans, plans.invalidated_plans) if c), key=lambda c: next(iter(c.values()))["created"])
        cache.popitem(last=False)
    plans.plans[ident] = entry
    return copy.deepcopy(plan)


def revalidate(plans, doc, base, settings, request):
    ident = request["plan_id"]
    invalidated = ident not in plans.plans
    cache = plans.invalidated_plans if invalidated else plans.plans
    entry = cache.get(ident)
    if not entry or entry["plan"].get("source_kind") != KIND:
        raise BridgeError("plan_expired", "Column plan expired or belongs to another session/workflow.", 409)
    plan = entry["plan"]
    if request["plan_hash"] != plan["plan_hash"]:
        raise BridgeError("plan_hash_mismatch", "Use the exact reviewed Column plan hash.", 409)
    report, _, _ = observe(plans, doc, base, settings, entry["request"])
    if plans.queries.clock() - entry["created"] >= plans.TTL_SECONDS:
        del cache[ident]
        raise BridgeError("plan_expired", "Column plan expired during revalidation.", 409)
    valid = report["report_fingerprint"] == plan["evidence_fingerprint"] and not invalidated
    if not valid:
        del cache[ident]
    return {"schema_version": SCHEMA, "action": "revalidate", "read_only": True,
            "state": "unchanged" if valid else "conflict", "plan_id": ident, "plan_hash": plan["plan_hash"]}


def highlight(plans, doc, base, settings, ifw, request):
    if revalidate(plans, doc, base, settings, request)["state"] != "unchanged":
        raise BridgeError("repair_conflict", "Column criteria changed before highlight; preview again.", 409)
    entry = plans.plans[request["plan_id"]]
    for pending in plans.plans.values():
        pending.pop("presentation", None)
    if not entry["plan"]["evaluation_apply_available"]:
        raise BridgeError("repair_scope_unavailable", "Only a complete applicable Column plan may be highlighted for Apply.", 409)
    report, snapshot, query = observe(plans, doc, base, settings, entry["request"])
    if report["report_fingerprint"] != entry["plan"]["evidence_fingerprint"]:
        raise BridgeError("repair_conflict", "Column evidence changed before highlight.", 409)
    from .model_selection import present_selection
    ident = uuid4().hex
    queries = plans.queries
    queries._expire()
    if len(queries.selections) >= queries.MAX_SELECTIONS:
        queries.selections.popitem(last=False)
    queries.selections[ident] = {"created": entry["created"], "request": query, "snapshot": snapshot, "cursors": {}, "native_type_gate": "Column_TypeUUID"}
    targets = {c["ref"]["model_uuid"] for c in entry["plan"]["changes"]}
    try:
        trace = NativeProbeTrace(plans.trace_path, "column_layer_highlight")
        result = trace.call("M4.present_selection", lambda: present_selection(queries, doc, base, settings, ifw,
            {"schema_version": "m4-selection-1", "action": "highlight", "selection_id": ident}, target_model_uuids=targets))
    finally:
        queries.selections.pop(ident, None)
    if result["state"] == "submitted":
        entry["presentation"] = {"state": "submitted", "plan_hash": entry["plan"]["plan_hash"]}
    return {**result, "plan_id": request["plan_id"], "plan_hash": request["plan_hash"]}
