"""Runtime-bound codecs for Allplan scalar attribute values.

Allplan's generated API reference does not publish AttributeType enum values.
Resolve against members exposed by the installed SDK and fail closed when the
runtime cannot bind one of the explicitly supported scalar families.
"""
from __future__ import annotations


_SCALAR_MEMBERS = {
    "text": "String",
    "integer": "Integer",
    "real": "Double",
    "boolean": "Boolean",
}


def supported_scalar_type(base, native_type):
    """Return ``(value_type, SDK member name)`` for a known scalar type.

    ``native_type`` must be the result of a targeted ``GetAttributeType`` call.
    Numeric enum values are never encoded here. A runtime with duplicate/equal
    enum members is treated as ambiguous rather than choosing by order.
    """
    enum_type = base.AttributeService.AttributeType
    matches = []
    for value_type, member_name in _SCALAR_MEMBERS.items():
        member = getattr(enum_type, member_name, None)
        if member is not None and native_type == member:
            matches.append((value_type, member_name))
    if len(matches) != 1:
        return None
    return matches[0]


def bind_enum_label(base, attribute_id, label, read):
    """Resolve an exact enum label through targeted SDK helpers and round-trip it.

    `read` is the caller's traced/check-wrapped function accepting `(api,
    callback)`. The setter payload remains the label: Allplan's
    `ChangeAttributes` manual demonstrates that pair shape for enum fields.
    The key is retained as binding evidence and is never used as the payload.
    """
    if (type(attribute_id) is not int or not 1 <= attribute_id <= 2147483647
            or not isinstance(label, str) or not label or len(label) > 8192):
        raise ValueError("Invalid enum attribute ID or label")
    service = base.AttributeService
    key = read("AttributeService.GetEnumIDFromValueString",
               lambda: service.GetEnumIDFromValueString(attribute_id, label))
    if type(key) is not int or not 0 <= key <= 2147483647:
        raise ValueError("Enum label did not resolve to a supported key")
    resolved_label = read("AttributeService.GetEnumValueStringFromID",
                          lambda: service.GetEnumValueStringFromID(attribute_id, key))
    if not isinstance(resolved_label, str) or resolved_label != label:
        raise ValueError("Enum label/key round trip differs")
    resolved_key = read("AttributeService.GetEnumIDFromValueString",
                        lambda: service.GetEnumIDFromValueString(attribute_id, resolved_label))
    if type(resolved_key) is not int or resolved_key != key:
        raise ValueError("Enum key/label round trip differs")
    return {"enum_id": key, "value": resolved_label}
