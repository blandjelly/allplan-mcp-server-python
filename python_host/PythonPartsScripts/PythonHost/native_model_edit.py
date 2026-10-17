"""Narrow native attribute/layer adapter for the M4 model-edit path.

Native writes remain experimental: this module checks the planner's explicit
adapter version and does not claim that Allplan accepted or persisted a change.
"""
from __future__ import annotations

import math

from .model_context import boolean, guid, integer, observation
from .native_readers import COMPONENT_TYPES, adapter_ref, root_adapter
from .transport import BridgeError


_TYPES = {"text", "string", "integer", "real", "boolean"}
_READ_ALL = "ReadAll"
_READ_ALL_COMPUTABLE = "ReadAllAndComputable"
_ADD_EVIDENCE = "absent_from_ReadAllAndComputable"


def _conflict(message):
    raise BridgeError("repair_conflict", message, 409)


def _data_type(change):
    resource = change.get("resource") or {}
    value = resource.get("data_type")
    if value not in _TYPES:
        raise BridgeError("target_not_writable", "Attribute data type is unavailable or unsupported.", 409)
    return "text" if value == "string" else value


def _typed_value(value, data_type):
    if data_type == "text":
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


def resolve(doc, base, queries, change, writable=False, diagnostics=None, adapter_owners=None):
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
        try:
            signed_file = integer(candidate.GetDrawingfileNumber())
            if signed_file <= 0 or signed_file != ref["drawing_file"]:
                continue
            root, _chain = root_adapter(candidate, budget, stop_types=COMPONENT_TYPES)
            current = adapter_ref(root)
        except BridgeError:
            raise
        except Exception as exc:
            raise BridgeError("repair_conflict", "Target identity or component hierarchy could not be resolved.", 409) from exc
        if current["model_uuid"] != ref["model_uuid"]:
            continue
        if (current["type_name"] != native_type
                or guid(root.GetElementAdapterType().GetGuid()) != ref["type_uuid"]):
            _conflict("Resolved target type changed.")
        matches[current["view_uuid"]] = root
    if len(matches) != 1:
        _conflict("Edit target is missing or has multiple root representations; no arbitrary representation selected.")
    element = next(iter(matches.values()))
    if writable:
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
        if change.get("operation") == "set_wall_layer":
            import NemAll_Python_IFW_ElementAdapter as native_adapters
            from .wall_layer import preflight
            preflight(base, element, change, native_adapters, budget)
    return element


def read(base, queries, element, change):
    """Read old layer/attribute state, preserving missing vs unreadable.

    For add_attribute, a caller may explicitly request the documented complete
    attribute read including computed attributes. Missing from ReadAll alone is
    deliberately reported as unknown, because ReadAll omits computed values.
    """
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


def write(base, element, change):
    """Invoke an established setter only for the explicit evaluation adapter."""
    if change.get("adapter_version") != "m4-model-edit-1":
        raise BridgeError("target_not_writable", "Native model edit adapter version is not enabled.", 409)
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
