"""Bounded project-local definitions and sampled values; no setters or live cache."""
from __future__ import annotations

import json

from .model_context import integer, observation
from .model_metadata import bounded_text, enum_code
from .property_contracts import PROPERTIES_SCHEMA, validate_properties
from .query_contracts import SCHEMA, fingerprint, scalar
from .runtime_info import runtime_info
from .transport import BridgeError


def resolve_attribute_name(doc, base, name, read):
    """Try bounded spelling variants, verifying each ID against project metadata.

    No aliases, transliteration or definition enumeration: an English label
    must not silently resolve to a different Polish/native property.
    """
    import unicodedata
    normalized = unicodedata.normalize("NFC", name.strip())
    variants = dict.fromkeys((name, normalized, normalized[:1].upper() + normalized[1:],
                              normalized.upper(), normalized.lower()))
    resolved = {}
    for spelling in variants:
        try:
            ident = positive_id(read("AttributeService.GetAttributeID",
                                     lambda: base.AttributeService.GetAttributeID(doc, spelling)))
        except BridgeError:
            raise
        except (ValueError, TypeError):
            continue
        actual = bounded_text(read("AttributeService.GetAttributeName",
                                   lambda: base.AttributeService.GetAttributeName(doc, ident)))
        if unicodedata.normalize("NFC", actual).casefold() != normalized.casefold():
            raise ValueError("Resolved attribute name differs from the requested spelling")
        if positive_id(read("AttributeService.GetAttributeID",
                            lambda: base.AttributeService.GetAttributeID(doc, actual))) != ident:
            raise ValueError("Attribute ID/name round trip differs")
        resolved[ident] = actual
    if len(resolved) > 1:
        raise ValueError("Case variants resolve to different project attribute IDs")
    if resolved:
        return next(iter(resolved.items()))
    raise ValueError("Attribute name was not found; inspect element_attributes")


def attribute_values(adapter, base, check):
    check()
    result = []
    seen = set()
    for index, (ident, value) in enumerate(adapter.GetAttributes(base.eAttibuteReadState.ReadAll)):
        check()
        ident = integer(ident)
        if index >= 256 or not 1 <= ident <= 2147483647 or ident in seen or not scalar(value):
            raise ValueError("Unsupported, ambiguous or over-budget attribute response")
        seen.add(ident)
        result.append({"attribute_id": ident, "value": value})
    return sorted(result, key=lambda item: item["attribute_id"])


def positive_id(value):
    value = integer(value)
    if not 1 <= value <= 2147483647:
        raise ValueError("No positive resource ID")
    return value


def discover_properties(service, doc, base, settings, request):
    validate_properties(request)
    started = service.clock()

    def check():
        if service.clock() - started >= service.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Property discovery exceeded its 5-second budget; no complete report was returned.", 409)

    def read(reader):
        check()
        result = observation(reader)
        check()
        return result

    query = {"schema_version": SCHEMA, "action": "query", "scope": request.get("scope", "open_drawings"),
             "component_kind": "top_level_component", "fields": ["display_name", "layer_id", "file_state"],
             "predicate": {"field": "type_name", "op": "in", "value": request.get("native_types", ["Column_TypeUUID", "Wall_TypeUUID"])},
             "max_adapters": request.get("max_adapters", 5000)}
    live = {}
    native_owners = []
    snapshot = service._scan(doc, base, settings, query, adapter_sink=live, adapter_owners=native_owners)
    check()
    samples = []
    discovered = set()
    for element in snapshot["elements"][:request.get("sample_limit", 10)]:
        ref = element["ref"]
        representations = live.get((ref["drawing_file"], ref["model_uuid"]), {})
        # Compare all resolved representations; don't hide differing attributes
        # behind a first-view choice. All adapter references die with this call.
        def values():
            if not representations or element["view_identity_not_checked"]:
                raise ValueError("Sample representation identity unavailable")
            results = [attribute_values(adapter, base, check) for adapters in representations.values() for adapter in adapters]
            if len({fingerprint(result) for result in results}) != 1:
                raise ValueError("Attribute representations disagree")
            return results[0]
        attributes = read(values)
        if attributes["status"] == "observed":
            discovered.update(item["attribute_id"] for item in attributes["value"])
        samples.append({"ref": ref, "fields": element["fields"], "attributes": attributes,
                        "presence_semantics": "absent_from_ReadAll_response_is_not_proven_native_absence",
                        "owner": "sampled_root_adapter_native_property_owner_not_verified",
                        "usable_for_write": False})

    name_resolution = []
    requested_ids = set()
    for name in request.get("attribute_names", []):
        def resolve(name=name):
            ident = positive_id(base.AttributeService.GetAttributeID(doc, name))
            actual = bounded_text(base.AttributeService.GetAttributeName(doc, ident))
            if actual != name:
                raise ValueError("Exact attribute-name round trip failed")
            return {"attribute_id": ident, "name": actual}
        resolved = read(resolve)
        if resolved["status"] == "observed":
            requested_ids.add(resolved["value"]["attribute_id"])
        name_resolution.append({"requested_name": name, "resolution": resolved,
                                "semantic_alias_verified": False})
    limit = request.get("metadata_limit", 64)
    ids = sorted(requested_ids) + sorted(discovered - requested_ids)[:max(0, limit - len(requested_ids))]
    attributes = []
    for ident in ids:
        attributes.append({"property_key": f"attribute:{ident}", "attribute_id": ident,
                           "name": read(lambda: bounded_text(base.AttributeService.GetAttributeName(doc, ident))),
                           "type_code": read(lambda: enum_code(base.AttributeService.GetAttributeType(doc, ident))),
                           "unit_label": read(lambda: bounded_text(base.AttributeService.GetAttributeUnit(doc, ident))),
                           "control_type_code": read(lambda: enum_code(base.AttributeService.GetAttributeControlType(doc, ident))),
                           "enum_values": {"status": "not_checked", "value": None, "reason": "native_enum_probe_not_accepted"},
                           "enum_encoding": "not_checked_no_unconditional_GetEnumValues_calls",
                           "unit_conversion": "not_checked", "native_owner": "not_checked",
                           "replace": "unsupported_by_this_tool", "add": "unsupported_by_this_tool"})
    doc_id = read(lambda: integer(doc.GetDocumentID()))
    layer_resolution = []
    layer_ids = {item["fields"]["layer_id"]["value"] for item in samples if item["fields"]["layer_id"]["status"] == "observed"}
    for name in request.get("layer_short_names", []):
        def resolve_layer(name=name):
            if doc_id["status"] != "observed":
                raise ValueError("Document ID unavailable")
            ident = positive_id(base.LayerService.GetIDByShortName(name, doc))
            actual = bounded_text(base.LayerService.GetShortNameByID(ident, doc_id["value"]))
            if actual != name:
                raise ValueError("Layer short-name round trip failed")
            return {"layer_id": ident, "short_name": actual}
        resolved = read(resolve_layer)
        if resolved["status"] == "observed":
            layer_ids.add(resolved["value"]["layer_id"])
        layer_resolution.append({"requested_short_name": name, "resolution": resolved})
    named_layer_resolution = []
    if doc_id["status"] == "observed":
        from .layer_names import resolve_direct_layer_name
        def layer_read(api, callback):
            result = read(callback)
            if result["status"] != "observed":
                raise ValueError("Layer lookup API did not return a verified value")
            return result["value"]
        for name in request.get("layer_names", []):
            resolution = read(lambda name=name: resolve_direct_layer_name(
                base, doc, doc_id["value"], name, layer_read))
            if resolution["status"] == "observed" and resolution["value"]["status"] == "resolved":
                layer_ids.add(resolution["value"]["candidates"][0]["layer_id"])
            named_layer_resolution.append({"requested_name": name, "resolution": resolution,
                                           "catalog_scan_required": resolution.get("value", {}).get("status") == "catalog_scan_required"})
    else:
        named_layer_resolution = [{"requested_name": name, "resolution": {
            "status": "not_checked", "value": None, "reason": "document_id_unavailable"},
            "catalog_scan_required": True} for name in request.get("layer_names", [])]
    layers = []
    for ident in sorted(layer_ids):
        def layer_field(method):
            if doc_id["status"] != "observed":
                return {"status": "not_checked", "value": None, "reason": "document_id_unavailable"}
            return read(lambda: bounded_text(getattr(base.LayerService, method)(ident, doc_id["value"])))
        from .layer_names import _long_name
        name_read = layer_field("GetNameByID")
        short_read = layer_field("GetShortNameByID")
        long_read = {"status": "not_checked", "value": None, "reason": "layer_name_unavailable"}
        if name_read["status"] == "observed" and short_read["status"] == "observed":
            long_read = {"status": "observed", "value": _long_name(name_read["value"], short_read["value"])}
        layers.append({"layer_id": ident, "name": name_read, "short_name": short_read, "long_name": long_read,
                       "write_eligibility": "not_checked", "create": "unsupported_by_this_tool"})

    registry = []
    for family in query["predicate"]["value"]:
        family_samples = [item for item in samples if item["fields"]["type_name"]["value"] == family]
        for definition in attributes:
            present = [item for item in family_samples if item["attributes"]["status"] == "observed"
                       and any(value["attribute_id"] == definition["attribute_id"] for value in item["attributes"]["value"])]
            registry.append({"native_type": family, "property_key": definition["property_key"],
                             "read": "observed_in_sample" if present else "unknown",
                             "replace": "unsupported_by_this_tool", "add": "unsupported_by_this_tool",
                             "native_update": "unsupported_by_this_tool", "sampled_owner_refs": [item["ref"] for item in present],
                             "accepted_on_build": None})
        for key in ("organizational.layer", "native.material", "visual.surface", "wall.total_thickness"):
            registry.append({"native_type": family, "property_key": key,
                             "read": "observed_in_sample" if key == "organizational.layer" and any(
                                 item["fields"]["layer_id"]["status"] == "observed" for item in family_samples) else "unsupported_by_this_probe",
                             "replace": "unsupported_by_this_tool", "add": "unsupported_by_this_tool",
                             "native_update": "unsupported_by_this_tool", "accepted_on_build": None})
    observations = [value for record in attributes + layers for value in record.values() if isinstance(value, dict)]
    observations += [item["resolution"] for item in name_resolution + layer_resolution]
    observations += [item["attributes"] for item in samples]
    failed = sum(item["status"] == "not_checked" for item in observations)
    result = {"schema_version": PROPERTIES_SCHEMA, "adapter_version": PROPERTIES_SCHEMA, "read_only": True, "model_data_changed": False,
              "runtime_verified": False, "status": "ready_for_owner_test", "usable_for_write": False,
              "query_session_id": service.session_id, "runtime": runtime_info(settings.AllplanVersion),
              "scope_mode": request.get("scope", "open_drawings"), "scope": snapshot["scope"],
              "counts": snapshot["counts"], "coverage": {**snapshot["coverage"],
                  "property_catalog": "sampled_attributes_and_explicit_names_not_all_project_definitions",
                  "metadata_complete_for_discovered_ids": set(ids) == discovered | requested_ids,
                  "metadata_reads_complete": failed == 0, "metadata_reads_not_checked": failed,
                  "attribute_ids_without_metadata": sorted(discovered - set(ids)),
                  "native_ownership": "not_checked", "writability": "not_checked"},
              "omissions": snapshot["omissions"], "not_checked_samples": snapshot["not_checked_samples"],
              "sample": {"limit": request.get("sample_limit", 10), "returned": len(samples),
                         "is_full_selection": len(samples) == len(snapshot["elements"]), "elements": samples},
              "attribute_name_resolution": name_resolution, "attribute_metadata": attributes,
              "layer_name_resolution": layer_resolution, "layer_full_name_resolution": named_layer_resolution,
              "layer_metadata": layers,
              "support_registry": registry, "source_fingerprint": snapshot["source_fingerprint"],
              "api_symbols": {name: callable(getattr(base.AttributeService, name, None)) for name in (
                  "GetAttributeID", "GetAttributeName", "GetAttributeType", "GetAttributeUnit", "GetEnumValues")},
              "layer_api_symbols": {name: callable(getattr(base.LayerService, name, None)) for name in (
                  "GetIDByShortName", "GetNameByID", "GetShortNameByID", "GetAllLayerNames", "GetIDByName")},
              "semantics": {"attribute_material": "separate_binding_may_reflect_native_material_requires_live_readback",
                            "organizational.layer": "separate_from_wall_tier_and_visual.surface",
                            "concrete_class": "requires_actual_project_catalog_no_C35_substitution",
                            "api_symbol_presence": "not_native_acceptance"}}
    result["probe_fingerprint"] = fingerprint(result)
    if len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode()) > service.MAX_SNAPSHOT_BYTES:
        raise BridgeError("scan_limit_exceeded", "Property discovery exceeded its 4 MiB report budget.", 409)
    check()
    return result
