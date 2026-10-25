"""Narrow native attribute/layer adapter for the M4 model-edit path.

Native writes remain experimental: this module checks the planner's explicit
adapter version and does not claim that Allplan accepted or persisted a change.
"""
from __future__ import annotations

import math

from .model_context import boolean, guid, integer, observation, text
from .native_readers import COMPONENT_TYPES, adapter_ref, root_adapter
from .query_contracts import fingerprint
from .transport import BridgeError


_TYPES = {"text", "string", "integer", "real", "boolean", "enum"}
_READ_ALL = "ReadAll"
_READ_ALL_COMPUTABLE = "ReadAllAndComputable"
_ADD_EVIDENCE = "absent_from_ReadAllAndComputable"


def _explicitly_stale(adapter):
    for method in ("IsNull", "IsDeleted"):
        try:
            if boolean(getattr(adapter, method)()):
                return True
        except Exception:
            continue
    return False


def _conflict(message):
    raise BridgeError("repair_conflict", message, 409)


def _data_type(change):
    resource = change.get("resource") or {}
    value = resource.get("data_type")
    if value not in _TYPES:
        raise BridgeError("target_not_writable", "Attribute data type is unavailable or unsupported.", 409)
    return "text" if value == "string" else value


def _typed_value(value, data_type):
    if data_type in {"text", "enum"}:
        valid = isinstance(value, str) and len(value) <= 8192
    elif data_type == "integer":
        valid = type(value) is int
    elif data_type == "real":
        valid = type(value) in (int, float) and math.isfinite(value)
    else:
        valid = type(value) is bool
    if not valid:
        raise BridgeError("target_not_writable", "Attribute value does not match its explicitly bound data type.", 409)
    return value


def resolve(doc, base, queries, change, writable=False, diagnostics=None, adapter_owners=None,
            all_representations=False):
    """Resolve one exact native component root from the current M1 enumeration."""
    ref = change.get("ref") or {}
    native_type = change.get("native_type")
    if native_type not in COMPONENT_TYPES:
        _conflict("Target native type is not one of the supported component roots.")
    if (type(ref.get("drawing_file")) is not int or ref["drawing_file"] <= 0
            or not isinstance(ref.get("model_uuid"), str)
            or not isinstance(ref.get("type_uuid"), str)):
        _conflict("Target reference is incomplete.")

    started = queries.clock()
    seen_models, seen_roots = [], []

    def budget():
        if queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Edit resolution time budget exceeded.", 409)

    owner = base.ElementsSelectService.SelectAllElements(doc)
    if adapter_owners is not None:
        adapter_owners.append(owner)
    matches = {}
    for index, candidate in enumerate(owner):
        budget()
        if index >= 10000:
            raise BridgeError("scan_limit_exceeded", "Edit resolution adapter budget exceeded.", 409)
        candidate_model_uuid = None
        candidate_type = None
        try:
            signed_file = integer(candidate.GetDrawingfileNumber())
            if signed_file <= 0 or signed_file != ref["drawing_file"]:
                continue
            # Filter the enumeration by its direct model identity before
            # walking parent adapters. SelectAllElements can contain adapters
            # from unrelated element families whose hierarchy is unavailable;
            # an unrelated candidate must not poison an otherwise exact
            # target resolution.
            candidate_model_uuid = guid(candidate.GetModelElementUUID())
            if candidate_model_uuid not in seen_models and len(seen_models) < 8:
                seen_models.append(candidate_model_uuid)
            if candidate_model_uuid != ref["model_uuid"]:
                # The documented enumeration can contain child adapters
                # whose model UUID differs from their component root. Exact
                # component roots of other supported families can be excluded
                # directly; unsupported child wrappers still need the parent
                # walk to establish whether they belong to the target.
                candidate_type = text(candidate.GetElementAdapterType().GetTypeName())
                if candidate_type in COMPONENT_TYPES:
                    continue
            # Explicitly stale wrappers can coexist with a current wrapper in
            # the same enumeration. Their direct target identity is known;
            # skip only positive null/deleted evidence.
            if _explicitly_stale(candidate):
                continue
            root, _chain = root_adapter(candidate, budget, stop_types=COMPONENT_TYPES)
            current = adapter_ref(root)
        except BridgeError:
            raise
        except Exception as exc:
            # Allplan may retain an explicitly deleted/null adapter wrapper
            # during a write refresh. It cannot be a live target. Skip it only
            # after its direct model identity was proven to be this target;
            # unknown lifecycle or hierarchy failures remain conflicts.
            if candidate_model_uuid == ref["model_uuid"] and _explicitly_stale(candidate):
                continue
            detail = {"reason": "candidate_hierarchy_unavailable",
                      "candidate_model_uuid": candidate_model_uuid,
                      "candidate_type": candidate_type,
                      "expected_model_uuid": ref["model_uuid"],
                      "expected_type": native_type}
            if diagnostics is not None:
                diagnostics["resolution"] = detail
            raise BridgeError("repair_conflict", "Edit target resolution failed: " + str(detail), 409) from exc
        if current["model_uuid"] != ref["model_uuid"]:
            continue
        if len(seen_roots) < 8:
            seen_roots.append({"model_uuid": current["model_uuid"], "view_uuid": current["view_uuid"],
                               "type_name": current["type_name"]})
        if (current["type_name"] != native_type
                or guid(root.GetElementAdapterType().GetGuid()) != ref["type_uuid"]):
            _conflict("Resolved target type changed.")
        wrappers = matches.setdefault(current["view_uuid"], [])
        if all(root is not wrapper for wrapper in wrappers):
            wrappers.append(root)
    if all_representations and writable:
        _conflict("A consensus enumeration is read-only.")
    if matches and all_representations:
        return tuple(root for view in sorted(matches) for root in matches[view])
    selected_view = change.get("target_view_uuid")
    if selected_view is not None:
        try:
            valid_view = isinstance(selected_view, str) and guid(selected_view) == selected_view and selected_view in matches
        except Exception:
            valid_view = False
        if not valid_view:
            _conflict("The exact reviewed target view is missing or changed.")
        evidence = {}
        observed = read_consensus(base, queries,
            tuple(root for view in sorted(matches) for root in matches[view]), change, evidence)
        if observed.get("status") not in {"observed", "absent"}:
            _conflict("Reviewed target representations do not agree: " + str(evidence))
        if diagnostics is not None:
            diagnostics["representation_consensus"] = evidence
    elif len(matches) != 1:
        reason = "target_missing" if not matches else "multiple_views"
        detail = {"reason": reason, "expected_model_uuid": ref["model_uuid"],
                  "expected_type": native_type, "candidate_model_uuids": seen_models,
                  "matching_roots": seen_roots}
        if diagnostics is not None:
            diagnostics["resolution"] = detail
        _conflict("Edit target resolution failed: " + str(detail))
    selected = matches[selected_view] if selected_view is not None else next(iter(matches.values()))
    element = selected[0]
    if writable:
        for wrapper in selected:
            _writable(doc, base, queries, wrapper, change, diagnostics, budget)
    return element


def _writable(doc, base, queries, element, change, diagnostics, budget):
    ref = change["ref"]
    flags = {}
    if diagnostics is not None:
        diagnostics.update(resolved_root=adapter_ref(element), native_flags=flags,
                           hierarchy_check="terminal_component_root_matches_reviewed_model_and_type")
    flags["IsInMacro"] = observation(lambda: boolean(element.IsInMacro()))
    flags["active_drawing_file"] = observation(
        lambda: integer(base.DrawingFileService.GetActiveFileNumber()))
    if (flags["active_drawing_file"].get("status") != "observed"
            or flags["active_drawing_file"].get("value") != ref["drawing_file"]):
        raise BridgeError("target_not_writable", "Target is outside the active foreground drawing.", 409)
    for method, expected in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                             ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                             ("IsLabelElement", False)):
        flags[method] = observation(lambda method=method: boolean(getattr(element, method)()))
        if flags[method].get("status") != "observed" or flags[method].get("value") != expected:
            raise BridgeError("target_not_writable", f"Target fails {method}; no write requested.", 409)
    if integer(element.GetDrawingfileNumber()) != ref["drawing_file"]:
        raise BridgeError("target_not_writable", "Passive target cannot be changed.", 409)
    if (change.get("native_type") in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}
            and change.get("operation") not in {"delete_element", "set_native_material"}):
        _slab_ownership(element, change, budget)
    if change.get("operation") == "set_wall_layer":
        import NemAll_Python_IFW_ElementAdapter as native_adapters
        from .wall_layer import preflight
        preflight(base, element, change, native_adapters, budget)
    if change.get("operation") == "delete_element":
        from .model_delete import preflight
        preflight(element, change, budget)
    if change.get("operation") == "set_native_material":
        from .wall_material import read as read_material
        if read_material(base, element, change, budget) != change["old_value"]:
            _conflict("Native material or observed evidence changed before write.")


def read_consensus(base, queries, elements, change, diagnostics=None):
    """Observe every exact live root, preserving read evidence and never setting values."""
    from .repair_execution import same_observation
    started = queries.clock()
    evidence = {"method": "all_exact_live_root_representations", "representations": [],
                "complete": False, "agreed": False}
    if diagnostics is not None:
        diagnostics.update(evidence)
    if not elements or len(elements) > 64:
        return {"status": "not_checked", "value": None, "reason": "representation_count_unavailable_or_over_limit"}
    observations = []
    for element in elements:
        if queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Consensus read time budget exceeded.", 409)
        lifecycle = {method: observation(lambda method=method: boolean(getattr(element, method)()))
                     for method in ("IsNull", "IsDeleted", "IsValid")}
        valid = all(lifecycle[method].get("status") == "observed"
                    and lifecycle[method].get("value") is expected
                    for method, expected in (("IsNull", False), ("IsDeleted", False), ("IsValid", True)))
        # Optional preservation belongs to the exact reviewed view. Other
        # live views must agree on the required native material/owner only.
        if (valid and change.get("operation") == "set_native_material"
                and guid(element.GetElementUUID()) != change.get("target_view_uuid")):
            from .wall_material import preview_observation
            value, material_state, eligibility = preview_observation(base, element)
            if material_state is None:
                value = eligibility
        else:
            value = (read(base, queries, element, change) if valid else
                 {"status": "not_checked", "value": None, "reason": "representation_lifecycle_unavailable"})
        # Retain raw agreed readback in the outcome, but do not duplicate up to
        # 8192 characters per view into the bounded durable journal.
        evidence["representations"].append({"view_uuid": guid(element.GetElementUUID()),
            "lifecycle": {key: item["value"] if item.get("status") == "observed" else item
                          for key, item in lifecycle.items()},
            "readback_status": value.get("status"), "readback_sha256": fingerprint(value)})
        observations.append(value)
        if queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Consensus read time budget exceeded.", 409)
    evidence["complete"] = True
    first = observations[0]
    readable = all(value.get("status") == "observed" or (
        value.get("status") == "absent" and value.get("presence_proven") is True
        and value.get("evidence") == _ADD_EVIDENCE) for value in observations)
    evidence["agreed"] = readable and all(same_observation(change, first, value) for value in observations[1:])
    if diagnostics is not None:
        diagnostics.update(evidence)
    if not evidence["agreed"]:
        return {"status": "not_checked", "value": None,
                "reason": "representation_values_disagree" if readable else "representation_read_unavailable"}
    return first


def read(base, queries, element, change):
    """Read old layer/attribute state, preserving missing vs unreadable.

    For add_attribute, a caller may explicitly request the documented complete
    attribute read including computed attributes. Missing from ReadAll alone is
    deliberately reported as unknown, because ReadAll omits computed values.
    """
    if change.get("operation") == "set_native_material":
        from .wall_material import read as read_material
        return read_material(base, element, change)
    if change.get("operation") == "delete_element":
        from .model_delete import preflight
        preflight(element, change)
        return {"status": "observed", "value": True}
    if change.get("native_type") in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}:
        try:
            _slab_ownership(element, change)
        except BridgeError as exc:
            return {"status": "not_checked", "value": None, "reason": exc.code}
    operation = change.get("operation")
    if operation == "set_wall_layer":
        import NemAll_Python_IFW_ElementAdapter as native_adapters
        from .wall_layer import read as read_wall_layer
        return read_wall_layer(base, element, change, native_adapters)
    if operation == "set_layer":
        return queries._fields(element, base, {"layer_id"}, change["ref"]["drawing_file"],
                               "active_foreground")["layer_id"]
    if operation not in {"set_attribute", "add_attribute"}:
        return {"status": "not_checked", "value": None, "reason": "unsupported_operation"}
    resource = change.get("resource") or {}
    ident = resource.get("attribute_id")
    if type(ident) is not int or not 1 <= ident <= 2147483647:
        return {"status": "not_checked", "value": None, "reason": "attribute_id_unavailable"}

    mode = resource.get("read_mode") or "stored"
    return attribute_fields(element, base, [ident], mode).get(
        f"attribute:{ident}", {"status": "not_checked", "value": None, "reason": "attribute_not_returned"})


def attribute_fields(adapter, base, needed_ids, read_mode="stored"):
    """Read a bounded set of attributes with explicit stored/computed semantics."""
    ids = set(needed_ids)
    result = {f"attribute:{ident}": {"status": "not_checked", "value": None,
                                      "reason": "attribute_read_failed"} for ident in ids}
    if (not ids or len(ids) > 32 or any(type(ident) is not int or not 1 <= ident <= 2147483647 for ident in ids)
            or read_mode not in {"stored", "all_and_computable"}):
        return {f"attribute:{ident}": {"status": "not_checked", "value": None,
                                        "reason": "invalid_attribute_read_request"} for ident in ids}
    try:
        stored = _read_requested_attributes(adapter, base, ids, _READ_ALL)
        if read_mode == "stored":
            for ident in ids:
                key = f"attribute:{ident}"
                if ident in stored:
                    result[key] = {"status": "observed", "value": stored[ident]}
                else:
                    result[key] = {"status": "missing", "value": None, "presence_proven": False,
                                   "evidence": "absent_from_ReadAll_not_proven_native_absence"}
            return result

        # A successful computed-inclusive read does not reveal whether a
        # value is computed. Compare it with ReadAll so computed-only values
        # remain useful evidence but cannot be treated as editable attributes.
        complete = _read_requested_attributes(adapter, base, ids, _READ_ALL_COMPUTABLE)
        for ident in ids:
            key = f"attribute:{ident}"
            if ident in stored:
                if ident not in complete or not _same_scalar(stored[ident], complete[ident]):
                    result[key] = {"status": "not_checked", "value": None,
                                   "reason": "attribute_read_modes_disagree"}
                else:
                    result[key] = {"status": "observed", "value": stored[ident]}
            elif ident in complete:
                result[key] = {"status": "observed", "value": complete[ident],
                               "computed_only": True, "presence_proven": False}
            else:
                result[key] = {"status": "absent", "value": None, "presence_proven": True,
                               "evidence": _ADD_EVIDENCE}
    except Exception as exc:
        result = {f"attribute:{ident}": {"status": "not_checked", "value": None,
                                          "reason": type(exc).__name__} for ident in ids}
    return result


def _read_requested_attributes(adapter, base, ids, mode_name):
    raw = adapter.GetAttributes(getattr(base.eAttibuteReadState, mode_name))
    values = {}
    for index, pair in enumerate(raw):
        if index >= 4096 or not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("Unsupported or over-budget attribute response")
        ident = integer(pair[0])
        if not 1 <= ident <= 2147483647:
            raise ValueError("Invalid attribute ID")
        if ident not in ids:
            continue
        if ident in values or not _scalar(pair[1]):
            raise ValueError("Ambiguous or unsupported requested attribute")
        values[ident] = pair[1]
    return values


def _same_scalar(left, right):
    # Avoid Python's bool/int equality when comparing two native read modes.
    return type(left) is type(right) and left == right


def _scalar(value):
    if value is None or isinstance(value, (bool, str)):
        return not isinstance(value, str) or len(value) <= 8192
    return type(value) in (int, float) and math.isfinite(value)


def value_matches(value, data_type):
    """Return whether a JSON scalar matches the explicitly bound attribute type."""
    if data_type not in _TYPES:
        return False
    data_type = "text" if data_type == "string" else data_type
    try:
        _typed_value(value, data_type)
        return True
    except BridgeError:
        return False


def valid_enum_binding(change):
    resource = change.get("resource") or {}
    if resource.get("data_type") != "enum":
        return True
    bound = resource.get("enum_binding") or {}
    return (resource.get("native_type_member") in {"Enum", "Integer", "String"}
            and type(bound.get("enum_id")) is int and 0 <= bound["enum_id"] <= 2147483647
            and isinstance(bound.get("value"), str) and bool(bound["value"])
            and bound["value"] == change.get("new_value"))


def valid_boolean_binding(change):
    """Validate optional SDK-bound CheckBox-to-Integer encoding evidence."""
    resource = change.get("resource") or {}
    marker = "boolean_binding" in resource
    codec = resource.get("value_codec")
    if not marker and codec is None:
        return True
    bound = resource.get("boolean_binding")
    if (codec != "integer_checkbox_boolean" or not marker
            or resource.get("data_type") != "integer"
            or resource.get("native_type_member") != "Integer"
            or not isinstance(bound, dict)
            or set(bound) != {"control_type_member", "false_value", "true_value", "value", "encoded_value"}):
        return False
    if (bound.get("control_type_member") != "CheckBox"
            or type(bound.get("false_value")) is not int or bound["false_value"] != 0
            or type(bound.get("true_value")) is not int or bound["true_value"] != 1
            or type(bound.get("value")) is not bool
            or type(bound.get("encoded_value")) is not int):
        return False
    encoded = 1 if bound["value"] else 0
    return bound["encoded_value"] == encoded and type(change.get("new_value")) is int and change["new_value"] == encoded


def replaceable_attribute_value(change):
    """A typed replacement may start from a known native undefined marker."""
    from .model_edit_contracts import is_undefined_attribute_value
    old = change.get("old_value") or {}
    data_type = (change.get("resource") or {}).get("data_type")
    if old.get("status") != "observed" or old.get("computed_only") is True:
        return False
    undefined = (data_type in {"integer", "real", "boolean"}
                 and is_undefined_attribute_value(old.get("value")))
    if undefined:
        return change.get("old_value_state") == "undefined"
    if "old_value_state" in change:
        return False
    return old.get("value") is None or value_matches(old.get("value"), data_type)


def _slab_ownership(element, change, check=lambda: None):
    from .component_ownership import observation, slab_write_blocker
    reviewed = (change.get("resource") or {}).get("component_ownership")
    if slab_write_blocker(reviewed, change):
        raise BridgeError("target_not_writable", "Slab needs a reviewed, standalone field owner; use component_identity read-only.", 409)
    current = observation(element, check)
    if slab_write_blocker(current, change) or current != reviewed:
        _conflict("Slab ownership changed or became unavailable since preview.")


def write(base, element, change, doc=None, check=lambda: None):
    """Invoke an established setter only for the explicit evaluation adapter."""
    if change.get("adapter_version") != "m4-model-edit-1":
        raise BridgeError("target_not_writable", "Native model edit adapter version is not enabled.", 409)
    if change.get("operation") == "delete_element":
        from .model_delete import write as delete
        return delete(base, element, change, doc, check)
    if change.get("operation") == "set_native_material":
        from .wall_material import write as set_material
        return set_material(base, element, change, doc, check)
    # Also guard the final native boundary, including a missing native_type in
    # a malformed change. No legacy plan can bypass the new slab owner gate.
    try:
        actual_type = text(element.GetElementAdapterType().GetTypeName())
    except Exception as exc:
        raise BridgeError("target_not_writable", "Native target type is unavailable.", 409) from exc
    if actual_type in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}:
        _slab_ownership(element, change)
    operation = change.get("operation")
    if operation == "set_wall_layer":
        import NemAll_Python_IFW_ElementAdapter as native_adapters
        from .wall_layer import write as write_wall_layer
        return write_wall_layer(base, element, change, native_adapters)
    if operation not in {"set_attribute", "add_attribute", "set_layer"}:
        raise BridgeError("target_not_writable", "Native model edit operation is unsupported.", 409)
    import NemAll_Python_IFW_ElementAdapter as adapters
    targets = adapters.BaseElementAdapterList()
    targets.append(element)
    if operation == "set_layer":
        resource = change.get("resource") or {}
        short_name = resource.get("short_name")
        if not isinstance(short_name, str) or not short_name or len(short_name) > 255:
            raise BridgeError("target_not_writable", "Bound layer short name is unavailable.", 409)
        return base.ElementsLayerService.ChangeLayer(targets, short_name)

    resource = change.get("resource") or {}
    ident = resource.get("attribute_id")
    if type(ident) is not int or not 1 <= ident <= 2147483647:
        raise BridgeError("target_not_writable", "Bound attribute ID is unavailable.", 409)
    value = _typed_value(change.get("new_value"), _data_type(change))
    if not valid_enum_binding(change):
        raise BridgeError("target_not_writable", "Enum change requires the reviewed exact label/key binding.", 409)
    if not valid_boolean_binding(change):
        raise BridgeError("target_not_writable", "Integer checkbox change requires the reviewed CheckBox zero/one binding.", 409)
    if operation == "add_attribute":
        old = change.get("old_value") or {}
        if (old.get("status") != "absent" or old.get("presence_proven") is not True
                or old.get("evidence") != _ADD_EVIDENCE
                or (resource.get("read_mode") or "stored") != "all_and_computable"):
            raise BridgeError("target_not_writable", "Attribute addition requires explicit ReadAllAndComputable absence evidence.", 409)
    elif (change.get("old_value") or {}).get("status") != "observed":
        raise BridgeError("target_not_writable", "Attribute replacement requires an observed old value.", 409)
    elif (change.get("old_value") or {}).get("computed_only") is True:
        raise BridgeError("target_not_writable", "Computed-only attributes cannot be edited through the element attribute setter.", 409)
    elif not replaceable_attribute_value(change):
        raise BridgeError("target_not_writable", "Attribute old value is neither type-compatible nor an explicitly bound undefined value.", 409)
    # The 2026 API documents ChangeAttributes as appending an attribute when it
    # is absent and replacing it when present. Flags remain False: no deletion
    # and no undefined-value operation is exposed here.
    return base.ElementsAttributeService.ChangeAttributes([(ident, value)], targets, False, False)
