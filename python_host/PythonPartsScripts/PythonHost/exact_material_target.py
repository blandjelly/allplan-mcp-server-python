"""Opt-in exact Slab enumeration; locating a wrapper never authorizes mutation."""
import json
from types import SimpleNamespace

from .component_ownership import identity
from .material_probe import resolve_slab_child
from .query_contracts import fingerprint
from .transport import BridgeError


# Every key of the resolution returned by resolve_slab_child. A section digest
# names which bound evidence changed; it is diagnostic, never authorization.
SECTIONS = ("method", "parent_ref", "parent_representation_count", "child_visits",
            "child_inventory_complete", "target_in_direct_scan", "child_parent_edges",
            "inventory_fingerprint")
DIAGNOSTIC_LIMIT = 16384


def sections(resolution):
    return {key: fingerprint(resolution.get(key)) for key in SECTIONS}


def valid_sections(value):
    return (isinstance(value, dict) and set(value) == set(SECTIONS)
            and all(isinstance(item, str) and len(item) == 64 for item in value.values()))


def conflict_details(resolution, expected=None, expected_sections=None, inventory=None):
    """Bounded identity-only comparison; contains no native property values."""
    current = sections(resolution)
    details = {"schema_version": "m4-exact-inventory-diff-1",
               "expected_fingerprint": expected, "current_fingerprint": fingerprint(resolution),
               "current_sections": current,
               "changed_sections": (sorted(k for k in SECTIONS if current[k] != expected_sections[k])
                                    if valid_sections(expected_sections) else "not_checked_legacy_binding")}
    for key, value in (("current_resolution", resolution), ("current_inventory", inventory)):
        if value is None:
            continue
        size = len(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                              separators=(",", ":")).encode())
        details[key] = (value if size <= DIAGNOSTIC_LIMIT else
                        {"status": "omitted", "reason": "diagnostic_size_limit", "size": size})
    return details


class ScopedBase:
    def __init__(self, base, wrappers, owners):
        self._base = base
        self._owners = owners
        self.ElementsSelectService = SimpleNamespace(SelectAllElements=lambda doc: wrappers)

    def __getattr__(self, name):
        return getattr(self._base, name)


def locate(doc, base, target, check, trace=None, expected=None, expected_sections=None, sink=None):
    """Retain a complete direct inventory plus one explicitly enumerated child.

    This facade lives only for the enclosing operation. Ordinary query and edit
    callers keep their original enumeration and all downstream write guards.
    """
    def call(api, callback, **details):
        check()
        value = trace.call(api, callback, **details) if trace else callback()
        check()
        return value
    try:
        owner = call("ExactMaterial.SelectAllElements", lambda: base.ElementsSelectService.SelectAllElements(doc))
        owners, wrappers, live, models = [owner], [], {}, {}
        for index, adapter in enumerate(owner):
            check()
            if index >= 10000:
                raise BridgeError("scan_limit_exceeded", "Exact material inventory exceeds 10000 wrappers.", 409)
            wrappers.append(adapter)
            ref = call("ExactMaterial.identity", lambda: identity(adapter, trace=call))
            if ref["drawing_file"] != target["drawing_file"]:
                continue
            row = models.setdefault(ref["model_uuid"], {"ref": {"type_uuid": ref["type_uuid"]},
                "view_identity_not_checked": False, "view_uuids": [],
                "fields": {"type_name": {"value": ref["type_name"]}}})
            if (row["ref"]["type_uuid"] != ref["type_uuid"]
                    or row["fields"]["type_name"]["value"] != ref["type_name"]):
                row["view_identity_not_checked"] = True
            row["ref"]["model_uuid"] = ref["model_uuid"]
            row["view_uuids"].append(ref["view_uuid"])
            live.setdefault((ref["drawing_file"], ref["model_uuid"]), {}).setdefault(ref["view_uuid"], []).append(adapter)
        inventory = []
        _, found, resolution = resolve_slab_child(target, {"elements": list(models.values())}, live, owners,
                                                  SimpleNamespace(call=call), check, inventory)
        if any(edge["parent"][k] != target["parent_ref"][k]
               for edge in resolution["child_parent_edges"] for k in ("model_uuid", "view_uuid")):
            raise BridgeError("repair_conflict", "Exact child parent view changed.", 409,
                              details=conflict_details(resolution, expected, expected_sections, inventory))
        digest = fingerprint(resolution)
        if expected is not None and digest != expected:
            raise BridgeError("repair_conflict", "Exact child inventory or parent edge changed.", 409,
                              details=conflict_details(resolution, expected, expected_sections, inventory))
        if sink is not None:
            sink["inventory_sections"] = sections(resolution)
        for adapter in found.values():
            if all(adapter is not existing for existing in wrappers):
                wrappers.append(adapter)
        return ScopedBase(base, wrappers, owners), digest
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("repair_conflict", "Exact material target could not be resolved.", 409) from exc
