"""Bounded read evidence for exact adapters; never infers a writable owner."""
from __future__ import annotations

import math
import json

from .component_ownership import identity, observation
from .model_context import boolean, integer
from .query_contracts import SCHEMA, fingerprint
from .transport import BridgeError


def describe_value(value):
    """Preserve JSON values and type identity without invoking unknown objects.

    A date-shaped string remains a string. SDK objects are reported by type,
    never repr/str, property introspection, iteration or guessed conversion.
    """
    kind = type(value)
    result = {"runtime_type": {"module": kind.__module__, "name": kind.__name__}}
    if (value is None or kind is bool or kind is int and abs(value) <= 2 ** 63 - 1
            or kind is float and math.isfinite(value) or kind is str and len(value) <= 8192):
        return {**result, "status": "observed", "value": value, "encoding": "json_scalar"}
    if kind in (list, tuple) and len(value) <= 64:
        members = [describe_value(item) for item in value if type(item) not in (list, tuple)]
        if len(members) == len(value) and all(item["status"] == "observed" for item in members):
            return {**result, "status": "observed", "value": [item["value"] for item in members],
                    "encoding": "json_sequence", "member_types": [item["runtime_type"] for item in members]}
    return {**result, "status": "not_checked", "value": None,
            "reason": "unsupported_or_over_budget_native_value"}


def _attributes(adapter, base, ids, mode, check):
    values = {}
    raw = adapter.GetAttributes(getattr(base.eAttibuteReadState, mode))
    for index, pair in enumerate(raw):
        check()
        if index >= 4096 or type(pair) not in (list, tuple) or len(pair) != 2:
            raise ValueError("Invalid or over-budget attribute response")
        ident = integer(pair[0])
        if not 1 <= ident <= 2147483647:
            raise ValueError("Invalid native attribute identity")
        if ident not in ids:
            continue
        if ident in values:
            raise ValueError("Duplicate requested attribute identity")
        values[ident] = describe_value(pair[1])
    return [{"attribute_id": ident, **values.get(ident, {
        "status": "not_returned", "value": None, "absence_proven": False})} for ident in ids]


def probe_attribute_evidence(queries, doc, base, settings, request, trace, check):
    """Read requested IDs on target wrappers and optionally immediate parents.

    Ancestry and child inventory are independent. A failed child inventory
    must not erase the exact target, readable ancestry or targeted raw values.
    None of those reads establishes field ownership or setter payloads.
    """
    compare_material = request["phase"] == "material_comparison"
    query = {"schema_version": SCHEMA, "action": "query",
             "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False,
                       "visibility": "api_select_all"},
             "component_kind": "model_identity", "fields": ["file_state"], "max_adapters": 10000}
    live, owners = {}, []
    snapshot = trace.call("M1.attribute_evidence_identity_scan", lambda: queries._scan(
        doc, base, settings, query, adapter_sink=live, adapter_owners=owners))
    check()
    if (not snapshot["coverage"]["requested_scope_complete"]
            or len(snapshot["scope"]["included_files"]) != 1
            or snapshot["scope"]["included_files"][0]["state"] != "active_foreground"):
        raise BridgeError("probe_scope_unavailable", "Attribute evidence requires one complete foreground drawing.", 409)
    resolution = None
    if compare_material and "parent_ref" in request:
        from .material_probe import resolve_slab_child
        element, unique, resolution = resolve_slab_child(request, snapshot, live, owners, trace, check)
    else:
        matches = [item for item in snapshot["elements"] if item["ref"]["model_uuid"] == request["model_uuid"]]
        if (len(matches) != 1 or matches[0]["view_identity_not_checked"]
                or request["view_uuid"] not in matches[0]["view_uuids"]):
            raise BridgeError("probe_scope_unavailable", "Exact model/view identity is missing or conflicting.", 409)
        element = matches[0]
        wrappers = live.get((request["drawing_file"], request["model_uuid"]), {}).get(request["view_uuid"], [])
        unique = {id(adapter): adapter for adapter in wrappers}
    if not 1 <= len(unique) <= 16:
        raise BridgeError("probe_scope_unavailable", "Attribute evidence supports at most 16 exact-view wrappers.", 409)

    def call(api, callback):
        check()
        value = trace.call(api, callback)
        check()
        return value

    def read(api, callback):
        check()
        try:
            value = call(api, callback)
            result = {"status": "observed", "value": value}
        except BridgeError:
            raise
        except Exception as exc:
            result = {"status": "not_checked", "value": None, "reason": type(exc).__name__}
        check()
        return result

    ids = request["attribute_ids"]
    metadata = []
    for ident in ids:
        def type_binding(ident=ident):
            native_type = base.AttributeService.GetAttributeType(doc, ident)
            enum = base.AttributeService.AttributeType
            # Names are compared to actual loaded SDK members, never numbers.
            names = [name for name in ("String", "Integer", "Double", "Boolean", "Enum", "Date",
                                      "DoubleVec", "IntegerVec", "StringVec", "Vector", "Byte", "Object")
                     if getattr(enum, name, None) is not None and native_type == getattr(enum, name)]
            return {"matching_sdk_members": names,
                    "binding_status": "matched" if len(names) == 1 else "ambiguous" if names else "unresolved",
                    "runtime_type": {"module": type(native_type).__module__, "name": type(native_type).__name__},
                    "writable_codec": "not_established"}
        row = {"attribute_id": ident, "type_binding": read("AttributeService.GetAttributeType.evidence", type_binding)}
        if compare_material:
            from .model_metadata import bounded_text
            from .model_properties import positive_id
            name = read("AttributeService.GetAttributeName.material_comparison",
                        lambda ident=ident: bounded_text(base.AttributeService.GetAttributeName(doc, ident)))
            roundtrip = {"status": "not_checked", "value": None, "reason": "name_unavailable"}
            if name["status"] == "observed":
                roundtrip = read("AttributeService.GetAttributeID.material_comparison",
                                 lambda: positive_id(base.AttributeService.GetAttributeID(doc, name["value"])))
                if roundtrip["status"] == "observed" and roundtrip["value"] != ident:
                    roundtrip = {**roundtrip, "status": "not_checked", "reason": "name_id_round_trip_mismatch"}
            row.update(name=name, name_id_round_trip=roundtrip)
        metadata.append(row)

    def adapter_evidence(adapter, *, exact_target=False):
        ref = call("Adapter.attribute_evidence_identity", lambda: identity(adapter, trace=call if compare_material else None))
        if ref["drawing_file"] != request["drawing_file"] or ref["signed_drawing_file"] < 0:
            raise ValueError("Parent is outside the foreground drawing")
        if exact_target and (ref["model_uuid"] != request["model_uuid"] or ref["view_uuid"] != request["view_uuid"]):
            raise ValueError("Target identity changed after enumeration")
        if compare_material:
            from .component_ownership import failure, observe
            def ownership(include_children):
                try:
                    return {"status": "observed", "value": observe(
                        adapter, check, include_children=include_children, trace=call)}
                except BridgeError:
                    raise
                except Exception as exc:
                    return failure(exc)
            ancestry, children = ownership(False), ownership(True)
        else:
            ancestry = call("Adapter.attribute_evidence_ancestry", lambda: observation(adapter, check, include_children=False))
            children = call("Adapter.attribute_evidence_children", lambda: observation(adapter, check))
        def representation():
            native = base.GetElement(adapter)
            if native is None:
                raise ValueError("Native representation unavailable")
            return {"module": type(native).__module__, "name": type(native).__name__}
        material = None
        if compare_material:
            from .material_probe import native_material_evidence
            native, material = native_material_evidence(base, adapter, ref, read)
        else:
            native = read("BaseElements.GetElement.attribute_evidence", representation)
        values = {mode: read("BaseElementAdapter.GetAttributes.evidence." + mode,
                            lambda mode=mode: _attributes(adapter, base, ids, mode, check))
                  for mode in ("ReadAll", "ReadAllAndComputable")}
        evidence = {"ref": ref, "ancestry": ancestry, "children": children,
                    "native_representation": native, "read_modes": values,
                    "property_owner": "not_established", "setter_payload": "not_established"}
        if compare_material:
            evidence["native_material"] = material
        return evidence

    import NemAll_Python_IFW_ElementAdapter as adapters
    representations = []
    for adapter in unique.values():
        target = read("Adapter.attribute_evidence_target", lambda: adapter_evidence(adapter, exact_target=True))
        parent = {"status": "not_requested", "value": None}
        if request.get("include_parent", False):
            def parent_evidence():
                owner = call("Adapter.attribute_evidence_parent", lambda:
                    adapters.BaseElementAdapterParentElementService.GetParentElement(adapter))
                owners.append(owner)
                if boolean(call("Adapter.attribute_evidence_parent.IsNull", owner.IsNull)):
                    return {"parent_present": False}
                return {"parent_present": True, "evidence": adapter_evidence(owner)}
            parent = read("Adapter.attribute_evidence_parent_values", parent_evidence)
        representations.append({"target": target, "parent": parent})
        if len(json.dumps(representations, ensure_ascii=False, allow_nan=False).encode()) > 512 * 1024:
            raise BridgeError("scan_limit_exceeded", "Attribute evidence exceeded its 512 KiB result budget.", 409)
    consensus = len({fingerprint(item) for item in representations}) == 1
    def complete_adapter(value):
        return (all(value[field]["status"] == "observed" for field in ("ancestry", "children", "native_representation"))
                and (not compare_material or value["native_material"]["status"] == "observed")
                and all(mode["status"] == "observed" and all(row["status"] == "observed" for row in mode["value"])
                        for mode in value["read_modes"].values()))

    def complete_representation(item):
        target, parent = item["target"], item["parent"]
        if target["status"] != "observed" or not complete_adapter(target["value"]):
            return False
        if parent["status"] == "not_requested":
            return True
        if parent["status"] != "observed":
            return False
        return not parent["value"]["parent_present"] or complete_adapter(parent["value"]["evidence"])

    complete = consensus and all(complete_representation(item) for item in representations)
    complete = complete and all(item["type_binding"]["status"] == "observed"
                                and item["type_binding"]["value"]["binding_status"] == "matched" for item in metadata)
    if compare_material:
        complete = complete and all(item["name"]["status"] == item["name_id_round_trip"]["status"] == "observed"
                                    for item in metadata)
    check()
    report = {"state": "observed" if complete else "not_checked", "evidence_complete": complete, "scope": snapshot["scope"],
            "ref": element["ref"], "view_uuid": request["view_uuid"], "attribute_ids": ids,
            "metadata": metadata, "representations": representations, "representation_count": len(unique),
            "representation_consensus": consensus, "source_fingerprint": snapshot["source_fingerprint"],
            "presence_semantics": "read_modes_separate; ReadAll_omission_does_not_prove_absence",
            "property_write_available": False, "property_owner": "not_established",
            "date_vector_setter_available": False, "setter_calls_started": 0,
            "bounds_used_for_identity": False, "physical_target_equivalence": "not_established"}
    if compare_material:
        report.update(coverage=snapshot["coverage"], counts=snapshot["counts"],
                      other_view_uuids=[view for view in element["view_uuids"] if view != request["view_uuid"]],
                      storage_coupling="not_established", persistence="not_checked")
    if resolution is not None:
        report["identity_resolution"] = resolution
        report["source_fingerprint"] = fingerprint({"scan": snapshot["source_fingerprint"], "resolution": resolution})
        if len(json.dumps(report, ensure_ascii=False, allow_nan=False).encode()) > 512 * 1024:
            raise BridgeError("scan_limit_exceeded", "Material child evidence exceeded its 512 KiB result budget.", 409)
    return report
