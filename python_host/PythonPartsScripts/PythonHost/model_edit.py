"""Typed criterion edits, independent of audit findings, using the M3 journal."""
from __future__ import annotations

import copy
import json
from collections import Counter
from uuid import uuid4

from .model_context import integer
from .model_metadata import bounded_text
from .model_properties import positive_id
from .model_edit_contracts import (DEFAULT_NATIVE_TYPES, SCHEMA, UNDEFINED_ATTRIBUTE_VALUES,
                                  is_undefined_attribute_value, validate_request)
from .query_contracts import evaluate, fingerprint, predicate_fields
from .repair_contracts import capability_probe
from .transport import BridgeError

KIND = "typed_model_edit"


def no_op_evidence(report, snapshot):
    """Publish bounded fresh destination reads without entering the executor."""
    matched = {fingerprint(check["ref"]) for check in report["checks"] if check["decision"] == "matched"}
    elements = [element for element in snapshot["elements"] if fingerprint(element["ref"]) in matched]
    fields = {bound["field"] for bound in report["binding"]}
    return {"status": "observed", "reason": "already_at_requested_values" if elements else "no_matching_targets",
            "matched_targets": len(elements), "setter_calls_started": 0,
            "source_fingerprint": report["source_fingerprint"],
            "observations": [{"ref": element["ref"], "fields": {
                field: copy.deepcopy(element["fields"][field]) for field in sorted(fields)}}
                for element in elements[:32]],
            "observations_complete": len(elements) <= 32, "observation_limit": 32}


def write_availability(plan, highlighted=False, valid=True):
    """Describe the executable route separately from its native acceptance."""
    available = valid and plan["evaluation_apply_available"]
    reasons = []
    if not valid:
        reasons.append("plan_conflict")
    if plan["state"] != "preview_ready":
        reasons.append(plan["state"])
    if plan.get("blocked"):
        reasons.append("blocked_properties")
    if not plan["coverage"].get("criteria_complete"):
        reasons.append("incomplete_criteria_or_fields")
    if len(plan["changes"]) > plan["limits"]["changes"]:
        reasons.append("change_limit_exceeded")
    files = plan["scope"]["included_files"]
    if len(files) != 1 or files[0]["state"] != "active_foreground":
        reasons.append("requires_one_active_foreground_drawing")
    if not available and not reasons:
        reasons.append("evaluation_scope_or_api_capability_unavailable")
    action = ("apply" if highlighted else "highlight") if available else None
    if valid and not highlighted and plan.get("evaluation_highlight_available"):
        action = "highlight"
    return {"apply_available": available, "evaluation_apply_available": available,
            "production_apply_available": False, "usable_for_write": available,
            "write_mode": "disposable_copy_evaluation", "write_blockers": reasons,
            "native_acceptance_blocks_evaluation": False,
            "required_steps": ["review_exact_plan_in_disposable_copy", "highlight_exact_plan",
                               "persist_apply_request_with_new_execution_id", "apply_with_acknowledgement"],
            "next_action": ({"tool": "model_edit", "request": {
                "schema_version": SCHEMA, "action": action, "plan_id": plan["plan_id"],
                **({"plan_hash": plan["plan_hash"]} if "plan_hash" in plan else {}),
                **({"acknowledgement": "disposable_copy_reviewed_plan"} if highlighted else {})},
                **({"required_request_fields": {"execution_id": "persist_new_uuid4_hex_before_sending"}}
                   if highlighted else {})} if action else None)}


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
        if target["kind"] == "delete":
            item = {"field": "element_exists", "operation": "delete_element", "property_role": "element",
                    "resource": {}, "new_value": False}
        elif target["kind"] == "native_material":
            item = {"field": "wall.native_material", "operation": "set_native_material", "property_role": "native_material",
                    "resource": {"tier_index": 1, "data_type": "text", "binding": "exact_native_material_string"},
                    "new_value": choice["value"]}
        elif target["kind"] == "layer":
            from .layer_names import bounded_layer_id
            doc_id = integer(read("DocumentAdapter.GetDocumentID", doc.GetDocumentID))
            if "name" in target:
                from .layer_names import resolve_direct_layer_name
                resolution = resolve_direct_layer_name(base, doc, doc_id, target["name"], read)
                if resolution["status"] != "resolved":
                    code = "layer_name_ambiguous" if resolution["status"] == "ambiguous" else "layer_name_catalog_required"
                    message = ("Exact layer name matches multiple layer IDs; use a unique exact short name."
                               if code == "layer_name_ambiguous" else
                               "Exact full layer name needs the paginated layer_catalog probe before it can be edited; use a verified unique short_name.")
                    raise BridgeError(code, message, 409)
                candidate = resolution["candidates"][0]
                ident = bounded_layer_id(candidate["layer_id"])
                actual = candidate["short_name"]
                requested_name = target["name"]
            else:
                requested_name = target["short_name"]
                ident = bounded_layer_id(read("LayerService.GetIDByShortName",
                                               lambda: base.LayerService.GetIDByShortName(requested_name, doc)))
                actual = bounded_text(read("LayerService.GetShortNameByID",
                                           lambda: base.LayerService.GetShortNameByID(ident, doc_id)))
                if actual != requested_name:
                    raise ValueError("Layer name/ID round trip differs")
            item = {"field": "layer_id", "operation": "set_layer", "property_role": "layer",
                    "resource": {"layer_id": ident, "short_name": actual,
                                 **({"requested_name": requested_name} if "name" in target else {})},
                    "new_value": ident}
            if "expected_layer_id" in target:
                current_name = bounded_text(read("LayerService.GetNameByID",
                    lambda: base.LayerService.GetNameByID(ident, doc_id)))
                if ident != target["expected_layer_id"] or current_name != target["expected_name"]:
                    raise BridgeError("layer_confirmation_stale", "The confirmed layer ID or name changed. Resolve and confirm the intended layer again.", 409)
                item["resource"]["confirmed_name"] = current_name
        else:
            ident = target.get("attribute_id")
            if ident is None:
                try:
                    from .model_properties import resolve_attribute_name
                    ident, _ = resolve_attribute_name(doc, base, target["name"], read)
                except BridgeError:
                    raise
                except Exception as exc:
                    raise BridgeError("attribute_name_unresolved", "Exact project attribute name was not resolved. Use model_property_probe phase=element_attributes on a known target to find its actual names/IDs; then bind the chosen ID. Do not guess an attribute or substitute native material.", 409) from exc
            name = bounded_text(read("AttributeService.GetAttributeName", lambda: base.AttributeService.GetAttributeName(doc, ident)))
            import unicodedata
            if not name or (target.get("name") is not None and
                            unicodedata.normalize("NFC", name).casefold() !=
                            unicodedata.normalize("NFC", target["name"].strip()).casefold()):
                raise BridgeError("attribute_name_mismatch", "Attribute name and ID do not agree exactly. Inspect element_attributes or an explicit attribute_definition, then use the verified ID/name.", 409)
            if positive_id(read("AttributeService.GetAttributeID", lambda: base.AttributeService.GetAttributeID(doc, name))) != ident:
                raise ValueError("Attribute ID/name round trip differs")
            # Compare real enum members from the loaded SDK, never guessed codes.
            # A readable/computed field still does not imply native writability.
            type_value = read("AttributeService.GetAttributeType", lambda: base.AttributeService.GetAttributeType(doc, ident))
            enum_type = base.AttributeService.AttributeType
            members = {"text": "String", "integer": "Integer", "real": "Double", "boolean": "Boolean"}
            from .attribute_codecs import supported_scalar_type, bind_enum_label
            scalar_binding = supported_scalar_type(base, type_value)
            requested_type = choice.get("value_type", "auto")
            value_type = requested_type
            if value_type == "auto":
                enum_member = getattr(enum_type, "Enum", None)
                value_type = (scalar_binding[0] if scalar_binding else
                              "enum" if (enum_member is not None and type_value == enum_member
                                         and isinstance(choice["value"], str) and choice["value"]) else None)
            from .native_model_edit import value_matches
            enum_binding = None
            boolean_binding = None
            new_value = choice["value"]
            # Some Allplan integer attributes expose a genuine checkbox
            # control. Only that SDK-bound metadata authorizes the documented
            # checkbox 0/1 representation; a field name or integer value alone
            # never turns JSON booleans into integers.
            if (isinstance(choice["value"], bool) and scalar_binding
                    and scalar_binding[0] == "integer"
                    and requested_type in {"auto", "boolean"}):
                from .attribute_codecs import checkbox_integer_boolean_binding
                control_type = read("AttributeService.GetAttributeControlType",
                                    lambda: base.AttributeService.GetAttributeControlType(doc, ident))
                boolean_binding = checkbox_integer_boolean_binding(base, control_type)
                if boolean_binding is not None:
                    boolean_binding = {**boolean_binding, "value": choice["value"],
                                       "encoded_value": int(choice["value"])}
                    value_type = "integer"
                    new_value = boolean_binding["encoded_value"]
            if value_type == "enum":
                compatible_members = [member for member in ("Enum", "Integer", "String")
                                      if getattr(enum_type, member, None) is not None
                                      and type_value == getattr(enum_type, member)]
                if not compatible_members:
                    raise BridgeError("attribute_type_unsupported", "Enum editing requires a runtime-bound Enum/Integer/String type and an exact project enum label.", 409)
                try:
                    enum_binding = bind_enum_label(base, ident, choice["value"], read)
                except BridgeError:
                    raise
                except Exception as exc:
                    raise BridgeError("attribute_enum_unresolved", "Enum label/key round trip failed. No value was guessed and no enum catalog was enumerated.", 409) from exc
                type_name = compatible_members[0]
            elif not scalar_binding or value_type != scalar_binding[0] or not value_matches(new_value, value_type):
                raise BridgeError("attribute_type_unsupported", "Requested value_type does not match the loaded SDK attribute type. Inspect attribute_definition or element_attributes; use a supported metadata-bound codec, without coercing display text.", 409)
            else:
                type_name = members[value_type]
            item = {"field": f"attribute:{ident}", "operation": "set_attribute", "property_role": "attribute",
                    "resource": {"attribute_id": ident, "name": name,
                                 "data_type": {"text": "string"}.get(value_type, value_type),
                                 "native_type_member": type_name,
                                 "read_mode": request.get("attribute_read_mode", "stored")},
                    "new_value": float(new_value) if value_type == "real" else new_value,
                    "mode": choice.get("mode", "replace")}
            if enum_binding is not None:
                item["resource"]["enum_binding"] = enum_binding
            if boolean_binding is not None:
                item["resource"]["boolean_binding"] = boolean_binding
                item["resource"]["value_codec"] = "integer_checkbox_boolean"
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
    layer_requested = any(b["operation"] == "set_layer" for b in binding)
    delete_requested = any(b["operation"] == "delete_element" for b in binding)
    material_requested = any(b["operation"] == "set_native_material" for b in binding)
    query["fields"] = [field for field in query["fields"] if field not in {"element_exists", "wall.native_material"}]
    if layer_requested or "layer_id" in predicate_fields(request.get("predicate")):
        query["layer_resolution"] = "component"
    live, owners = {}, []
    snapshot = trace.call("M1.semantic_component_scan", lambda: plans.queries._scan(
        doc, base, settings, query, adapter_sink=live, adapter_owners=owners))
    check()
    if material_requested:
        from .wall_material import preview_observation as material_observation
        for element in snapshot["elements"]:
            representations = live.get((element["ref"]["drawing_file"], element["ref"]["model_uuid"]), {})
            values = [trace.call("Wall.native_material_preservation", lambda adapter=adapter:
                      material_observation(base, adapter, check))
                      for wrappers in representations.values() for adapter in wrappers]
            if values and len({fingerprint(value) for value in values}) == 1 and not element["view_identity_not_checked"]:
                (element["fields"]["wall.native_material"], element["wall_material_state"],
                 element["wall_material_preservation"]) = values[0]
            else:
                element["fields"]["wall.native_material"] = {"status": "not_checked", "value": None,
                                                            "reason": "native_material_representation_conflict"}
                element["wall_material_preservation"] = {
                    "status": "not_checked", "value": None, "reason": "native_material_representation_conflict",
                    "diagnostic": {"stage": "material_representation_consensus", "error_type": "RepresentationConflict"}}
    if delete_requested:
        from .model_delete import ownership as delete_ownership
        for element in snapshot["elements"]:
            representations = live.get((element["ref"]["drawing_file"], element["ref"]["model_uuid"]), {})
            evidence = [trace.call("Component.delete_ownership", lambda adapter=adapter:
                        delete_ownership(adapter, check))
                        for wrappers in representations.values() for adapter in wrappers]
            element["delete_ownership"] = (evidence[0] if evidence and len({fingerprint(e) for e in evidence}) == 1
                and not element["view_identity_not_checked"] else
                {"status": "not_checked", "value": None, "reason": "delete_ownership_representation_conflict"})
            element["fields"]["element_exists"] = {"status": "observed", "value": True}
    # Semantic enumeration intentionally retains a Slab and its MultiSlab as
    # distinct identities. Observe ancestry before deciding which can be edited;
    # equal geometry is never a reason to merge or redirect them.
    from .component_ownership import observation as ownership_observation
    for element in snapshot["elements"]:
        if element["fields"]["type_name"].get("value") not in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}:
            continue
        representations = live.get((element["ref"]["drawing_file"], element["ref"]["model_uuid"]), {})
        evidence = [trace.call("Slab.component_ownership", lambda adapter=adapter:
                    ownership_observation(adapter, check))
                    for adapters in representations.values() for adapter in adapters]
        element["component_ownership"] = (evidence[0] if evidence and len({fingerprint(e) for e in evidence}) == 1
            and not element["view_identity_not_checked"] else
            {"status": "not_checked", "value": None, "reason": "slab_ownership_representation_conflict"})
    if layer_requested:
        from .wall_layer import observe as observe_wall_layer
        import NemAll_Python_IFW_ElementAdapter as native_adapters
        for element in snapshot["elements"]:
            if element["fields"]["type_name"].get("value") != "Wall_TypeUUID":
                continue
            representations = live.get((element["ref"]["drawing_file"], element["ref"]["model_uuid"]), {})
            observations = []
            try:
                for adapters in representations.values():
                    for adapter in adapters:
                        check()
                        observations.append(trace.call("WallTier.layer_ownership", lambda:
                            observe_wall_layer(adapter, native_adapters, check),
                            drawing_file=element["ref"]["drawing_file"], model_uuid=element["ref"]["model_uuid"]))
                if (not observations or len({fingerprint(o) for o in observations}) != 1
                        or element["view_identity_not_checked"]):
                    raise ValueError("Wall layer representations disagree")
                element["wall_layer_ownership"] = observations[0]
            except BridgeError as exc:
                if exc.code in {"scan_limit_exceeded", "probe_trace_unavailable"}:
                    raise
                element["fields"]["layer_id"] = {"status": "not_checked", "value": None, "reason": exc.code}
            except Exception as exc:
                element["fields"]["layer_id"] = {"status": "not_checked", "value": None, "reason": type(exc).__name__}
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
    # A decisive false criterion does not require destination properties on
    # non-targets (e.g. wall thickness on a Column). Keep every peer in the
    # source fingerprint so a newly matching peer still invalidates Apply.
    decisions = {fingerprint(c["ref"]): c["decision"] for c in checks}
    destination_fields = {item["field"] for item in binding}
    required_failures = [
        {"ref": element["ref"], "field": field, "observation": copy.deepcopy(value)}
        for element in snapshot["elements"]
        for field, value in element["fields"].items()
        if decisions[fingerprint(element["ref"])] == "matched"
        and field in destination_fields
        and value.get("status") not in {"observed", "absent", "missing"}
    ]
    field_complete = not required_failures
    complete = snapshot["coverage"]["requested_scope_complete"] and field_complete and not any(c["decision"] == "unknown" for c in checks)
    snapshot["coverage"]["returned_fields_not_checked"] = sum(
        value.get("status") == "not_checked"
        for element in snapshot["elements"] for value in element["fields"].values())
    snapshot["coverage"]["returned_fields_complete"] = snapshot["coverage"]["returned_fields_not_checked"] == 0
    snapshot["coverage"]["required_destination_fields_complete"] = field_complete
    snapshot["source_fingerprint"] = fingerprint({"m1_source": snapshot["source_fingerprint"],
                                                   "elements": snapshot["elements"], "binding": binding})
    report = {"schema_version": SCHEMA, "read_only": True, "checks": checks, "binding": binding,
              "source_fingerprint": snapshot["source_fingerprint"], "scope": snapshot["scope"],
              "coverage": {**snapshot["coverage"], "criteria_complete": complete},
              "counts": dict(Counter(c["decision"] for c in checks)), "omissions": snapshot["omissions"],
              "attribute_read_mode": request.get("attribute_read_mode", "stored"),
              "required_field_failures": required_failures,
              "operation_eligibility_failures": [
                  {"ref": element["ref"], "field": "wall.native_material",
                   "old_value": copy.deepcopy(element["fields"]["wall.native_material"]),
                   "observation": copy.deepcopy(element["wall_material_preservation"])}
                  for element in snapshot["elements"]
                  if decisions[fingerprint(element["ref"])] == "matched"
                  and element.get("wall_material_preservation", {}).get("status") == "not_checked"],
              "component_ownership": [{"ref": element["ref"], "observation": element["component_ownership"]}
                                      for element in snapshot["elements"] if "component_ownership" in element],
              "criterion_failures": [
                  {"ref": element["ref"], "fields": {
                      field: copy.deepcopy(element["fields"][field])
                      for field in predicate_fields(request.get("predicate"))
                      if element["fields"][field].get("status") != "observed"}}
                  for element in snapshot["elements"]
                  if decisions[fingerprint(element["ref"])] == "unknown"],
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
            if bound["operation"] == "set_native_material" and not element.get("wall_material_state"):
                blocked.append({"ref": element["ref"], "field": bound["field"],
                                "reason": ("native_material_preservation_unavailable"
                                           if old.get("status") == "observed" else "old_value_unknown"),
                                "old_value": copy.deepcopy(old),
                                "observation": copy.deepcopy(element["wall_material_preservation"])})
                continue
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
            elif observed and bound["operation"] not in {"set_layer", "delete_element"} and old.get("value") is not None and not value_matches(old["value"], bound["resource"]["data_type"]):
                data_type = bound["resource"].get("data_type")
                undefined_numeric_or_boolean = (
                    data_type in {"integer", "real", "boolean"}
                    and old.get("computed_only") is not True
                    and is_undefined_attribute_value(old.get("value"))
                )
                if not undefined_numeric_or_boolean:
                    reason = "old_value_type_differs"
            if reason:
                blocked.append({"ref": element["ref"], "field": bound["field"], "reason": reason,
                                "observation": copy.deepcopy(old)})
                continue
            change = {**copy.deepcopy(bound), "ref": copy.deepcopy(element["ref"]),
                      "adapter_version": SCHEMA, "native_type": element["fields"]["type_name"]["value"],
                      "old_value": copy.deepcopy(old), "source_fingerprint": element["source_fingerprint"],
                      "locator": {"drawing_file": element["ref"]["drawing_file"], "model_uuid": element["ref"]["model_uuid"]}}
            if (bound["operation"] != "set_layer"
                    and bound["resource"].get("data_type") in {"integer", "real", "boolean"}
                    and is_undefined_attribute_value(old.get("value"))):
                change["old_value_state"] = "undefined"
            if absent:
                change["operation"] = "add_attribute"
            if bound["operation"] == "set_layer" and change["native_type"] == "Wall_TypeUUID":
                ownership = element.get("wall_layer_ownership")
                if ownership is None:
                    blocked.append({"ref": element["ref"], "field": "layer_id", "reason": "wall_layer_ownership_unavailable"})
                    continue
                change["operation"] = "set_wall_layer"
                change["resource"]["wall_layer_ownership"] = copy.deepcopy(ownership)
            if element.get("view_identity_not_checked") or not element.get("view_uuids"):
                blocked.append({"ref": element["ref"], "field": bound["field"], "reason": "target_view_unavailable"})
                continue
            change["target_view_uuid"] = sorted(element["view_uuids"])[0]
            if bound["operation"] == "delete_element":
                from .model_delete import blocker as delete_blocker
                ownership = element.get("delete_ownership")
                reason = delete_blocker(ownership)
                if reason:
                    blocked.append({"ref": element["ref"], "field": bound["field"], "reason": reason,
                                    "observation": copy.deepcopy(ownership)})
                    continue
                descendant_ids = {item["model_uuid"] for item in ownership["value"]["descendants"]}
                if descendant_ids & set(request.get("exclude_model_uuids", [])):
                    blocked.append({"ref": element["ref"], "field": bound["field"], "reason": "delete_contains_excluded_descendant"})
                    continue
                change["resource"]["delete_ownership"] = copy.deepcopy(ownership)
            elif bound["operation"] == "set_native_material":
                change["resource"]["wall_material_state"] = copy.deepcopy(element["wall_material_state"])
            elif change["native_type"] in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}:
                from .component_ownership import slab_write_blocker
                ownership = element.get("component_ownership")
                reason = slab_write_blocker(ownership)
                if reason:
                    blocked.append({"ref": element["ref"], "field": bound["field"], "reason": reason})
                    continue
                change["resource"]["component_ownership"] = copy.deepcopy(ownership)
            changes.append(change)
    if any(change["operation"] == "delete_element" for change in changes):
        descendants = {item["model_uuid"] for change in changes
                       for item in change["resource"]["delete_ownership"]["value"]["descendants"]}
        blocked = [item for item in blocked if not (item["reason"] == "delete_parent_requires_explicit_owner"
                                                   and item["ref"]["model_uuid"] in descendants)]
        targets = [target for target in targets if target["model_uuid"] not in descendants]
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
                       "native_material_update": "experimental_single_tier_Wall_without_openings",
                       "deletion": "exact_component_roots_or_Wall_owned_openings_with_reviewed_subtrees"}}
    plan["undefined_policy"] = {
        "recognized_raw_values": sorted(UNDEFINED_ATTRIBUTE_VALUES),
        "allowed_metadata_types": ["integer", "real", "boolean"],
        "raw_old_value_preserved": True,
    }
    plan["setter_calls_started"] = 0
    if plan["state"] == "no_op":
        plan["no_op_evidence"] = no_op_evidence(report, snapshot)
    plan["evaluation_apply_available"] = plans.executor.evaluation_scope(plan)
    plan["evaluation_highlight_available"] = ready
    # Symbol inspection is not a production gate and must not contradict the
    # route's actual evaluation eligibility in a nested capability flag.
    plan["capabilities"]["production_apply_available"] = plan["capabilities"].pop("apply_available", False)
    plan.update(write_availability(plan))
    plan["capabilities"]["apply_available"] = plan["apply_available"]
    plan["capabilities"]["durable_retry_deduplication"] = "execution_id_journal_replay_without_setters"
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
    response = copy.deepcopy(plan)
    # The action hint carries the final hash without creating a hash cycle.
    response.update(write_availability(plan))
    return response


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
    report, snapshot, _ = observe(plans, doc, base, settings, entry["request"])
    if plans.queries.clock() - entry["created"] >= plans.TTL_SECONDS:
        del cache[ident]
        raise BridgeError("plan_expired", "Model edit plan expired during revalidation.", 409)
    valid = report["report_fingerprint"] == plan["evidence_fingerprint"] and not invalidated
    if not valid:
        del cache[ident]
    return {"schema_version": SCHEMA, "action": "revalidate", "read_only": True,
            "state": "unchanged" if valid else "conflict", "plan_id": ident, "plan_hash": plan["plan_hash"],
            "setter_calls_started": 0,
            **({"no_op_evidence": no_op_evidence(report, snapshot)} if valid and plan["state"] == "no_op" else {}),
            **write_availability(plan, highlighted=entry.get("presentation", {}).get("state") == "submitted", valid=valid)}


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
    return {**result, "plan_id": request["plan_id"], "plan_hash": request["plan_hash"],
            **write_availability(entry["plan"], highlighted=result["state"] == "submitted")}
