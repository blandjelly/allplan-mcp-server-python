"""Bounded wall-tier layer reads and writes for the Allplan 2026 adapter API.

Layer writes target the native wall tiers that own the layer values. The wall
root is used only to bind and revalidate hierarchy ownership.
"""
from __future__ import annotations

from .model_context import boolean, guid, integer
from .transport import BridgeError

SCHEMA = "m4-wall-layer-ownership-1"
MAX_CHILDREN = 256
MAX_TIERS = 32
_WALL = "Wall_TypeUUID"
_TIER = "WallTier_TypeUUID"


def _conflict(message):
    raise BridgeError("repair_conflict", message, 409)


def _identity(adapter):
    try:
        signed_file = integer(adapter.GetDrawingfileNumber())
        drawing_file = abs(signed_file)
        model_uuid = guid(adapter.GetModelElementUUID())
        view_uuid = guid(adapter.GetElementUUID())
        type_obj = adapter.GetElementAdapterType()
        type_name = type_obj.GetTypeName()
        type_uuid = guid(type_obj.GetGuid())
        if drawing_file <= 0 or not model_uuid or not view_uuid or not type_name or not type_uuid:
            _conflict("Wall layer ownership identity is incomplete.")
        return {"drawing_file": drawing_file, "signed_drawing_file": signed_file, "model_uuid": model_uuid,
                "view_uuid": view_uuid, "type_name": type_name, "type_uuid": type_uuid}
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("repair_conflict", "Wall layer ownership identity could not be read.", 409) from exc


def _layer(adapter):
    try:
        common = adapter.GetCommonProperties()
        value = integer(common.Layer)
        if value <= 0:
            _conflict("Wall layer value is not a positive native layer ID.")
        return value
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("repair_conflict", "Wall layer value could not be read.", 409) from exc


def _check_root(root):
    ident = _identity(root)
    if ident["type_name"] != _WALL:
        _conflict("Wall layer operation requires an exact Wall_TypeUUID root.")
    return ident


def _same_owner(child, root_ident, adapters, check):
    parent = child
    # A tier must have the exact wall root as its immediate parent.
    check()
    parent = adapters.BaseElementAdapterParentElementService.GetParentElement(child)
    check()
    parent_ident = _identity(parent)
    if (parent_ident["type_name"] != _WALL
            or parent_ident["drawing_file"] != root_ident["drawing_file"]
            or parent_ident["signed_drawing_file"] != root_ident["signed_drawing_file"]
            or parent_ident["model_uuid"] != root_ident["model_uuid"]
            or parent_ident["view_uuid"] != root_ident["view_uuid"]
            or parent_ident["type_uuid"] != root_ident["type_uuid"]):
        _conflict("Wall tier is not owned by the reviewed wall root representation.")
    return parent_ident


def _collect(root, adapters, check):
    """Return one root identity, observed tiers and their retained owner list."""
    check()
    root_ident = _check_root(root)
    check()
    children = adapters.BaseElementAdapterChildElementsService.GetChildModelElements(root, True)
    check()
    tiers_by_view, adapters_by_view, view_by_model = {}, {}, {}
    child_count = 0
    for child in children:
        check()
        child_count += 1
        if child_count > MAX_CHILDREN:
            raise BridgeError("scan_limit_exceeded", "Wall hierarchy exceeds the child read budget.", 409)
        child_type = child.GetElementAdapterType().GetTypeName()
        if child_type != _TIER:
            # Axes, openings, labels and all other child types are deliberately
            # outside the layer setter's target set.
            continue
        ident = _identity(child)
        if (ident["drawing_file"] != root_ident["drawing_file"]
                or ident["signed_drawing_file"] != root_ident["signed_drawing_file"]):
            _conflict("Wall tier crosses drawing-file scope.")
        parent_ident = _same_owner(child, root_ident, adapters, check)
        layer = _layer(child)
        record = {**ident, "parent_model_uuid": parent_ident["model_uuid"],
                  "parent_view_uuid": parent_ident["view_uuid"],
                  "parent_type_uuid": parent_ident["type_uuid"], "layer": layer}
        previous = tiers_by_view.get(ident["view_uuid"])
        if previous is not None and previous != record:
            _conflict("Duplicate wall tier representations disagree.")
        prior_view = view_by_model.get(ident["model_uuid"])
        if prior_view is not None and prior_view != ident["view_uuid"]:
            _conflict("Wall tier has multiple drawing-view representations.")
        view_by_model[ident["model_uuid"]] = ident["view_uuid"]
        tiers_by_view[ident["view_uuid"]] = record
        adapters_by_view.setdefault(ident["view_uuid"], child)
        if len(tiers_by_view) > MAX_TIERS:
            raise BridgeError("scan_limit_exceeded", "Wall exceeds the tier read/write budget.", 409)
    if not tiers_by_view:
        _conflict("Wall has no directly owned readable tiers.")
    tiers = [tiers_by_view[key] for key in sorted(tiers_by_view)]
    tier_adapters = [adapters_by_view[tier["view_uuid"]] for tier in tiers]
    return root_ident, tiers, tier_adapters, children


def observe(adapter, adapters, check=lambda: None):
    """Build a JSON-safe manifest from one freshly resolved wall adapter."""
    root_ident, tiers, _tier_adapters, _children_owner = _collect(adapter, adapters, check)
    root_layer = _layer(adapter)
    return {"schema_version": SCHEMA,
            "root": {**root_ident, "layer": root_layer},
            "tiers": tiers,
            "complete": True}


def layer_value(evidence):
    """Return the effective wall layer only when every tier agrees."""
    tiers = evidence.get("tiers") if isinstance(evidence, dict) else None
    if (not isinstance(evidence, dict) or evidence.get("schema_version") != SCHEMA
            or evidence.get("complete") is not True or not isinstance(tiers, list) or not tiers):
        return {"status": "not_checked", "value": None, "reason": "wall_tier_ownership_unavailable"}
    values = [tier.get("layer") for tier in tiers]
    if any(type(value) is not int or value <= 0 for value in values):
        return {"status": "not_checked", "value": None, "reason": "wall_tier_layer_unavailable"}
    if len(set(values)) != 1:
        return {"status": "not_checked", "value": None, "reason": "mixed_wall_tier_layers"}
    return {"status": "observed", "value": values[0]}


def same_owners(left, right):
    """Compare wall/tier ownership identities while ignoring mutable layers."""
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    def identity(manifest):
        if (manifest.get("schema_version") != SCHEMA or manifest.get("complete") is not True
                or not isinstance(manifest.get("root"), dict) or not isinstance(manifest.get("tiers"), list)):
            return None
        root = {key: manifest["root"].get(key) for key in
                ("drawing_file", "signed_drawing_file", "model_uuid", "view_uuid", "type_name", "type_uuid")}
        tiers = [{key: tier.get(key) for key in
                  ("drawing_file", "signed_drawing_file", "model_uuid", "view_uuid", "type_name", "type_uuid",
                   "parent_model_uuid", "parent_view_uuid", "parent_type_uuid")}
                 for tier in manifest["tiers"] if isinstance(tier, dict)]
        if len(tiers) != len(manifest["tiers"]) or not tiers:
            return None
        return root, sorted(tiers, key=lambda tier: (str(tier["view_uuid"]), str(tier["model_uuid"])))
    return identity(left) is not None and identity(left) == identity(right)


def read(base, wall_root, change, adapters, check=lambda: None):
    """Read a wall's effective layer and verify tier membership after a write."""
    try:
        current = observe(wall_root, adapters, check)
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("repair_conflict", "Wall tier layer readback could not be verified.", 409) from exc
    reviewed = (change.get("resource") or {}).get("wall_layer_ownership")
    if reviewed is not None and not same_owners(reviewed, current):
        raise BridgeError("repair_conflict", "Wall or tier identity changed during readback.", 409)
    return layer_value(current)


def _validate_reviewed(change):
    resource = change.get("resource") or {}
    reviewed = resource.get("wall_layer_ownership")
    short_name = resource.get("short_name")
    ref = change.get("ref") or {}
    old_value = change.get("old_value") or {}
    target_layer = resource.get("layer_id")
    if (change.get("operation") != "set_wall_layer"
            or change.get("native_type") != _WALL
            or change.get("adapter_version") != "m4-model-edit-1"
            or change.get("property_role") != "layer"
            or change.get("field") != "layer_id"
            or type(ref.get("drawing_file")) is not int or ref["drawing_file"] <= 0
            or ref.get("type_name", _WALL) != _WALL
            or not isinstance(ref.get("model_uuid"), str)
            or not isinstance(ref.get("type_uuid"), str)
            or not isinstance(short_name, str) or not 1 <= len(short_name) <= 16
            or type(target_layer) is not int or target_layer <= 0
            or type(change.get("new_value")) is not int or change["new_value"] != target_layer
            or old_value.get("status") != "observed"
            or type(old_value.get("value")) is not int or old_value["value"] <= 0
            or not isinstance(reviewed, dict) or reviewed.get("schema_version") != SCHEMA
            or reviewed.get("complete") is not True):
        raise BridgeError("target_not_writable", "Wall tier layer ownership was not explicitly reviewed.", 409)
    root, tiers = reviewed.get("root"), reviewed.get("tiers")
    if (not isinstance(root, dict) or not isinstance(tiers, list) or not tiers
            or len(tiers) > MAX_TIERS):
        raise BridgeError("target_not_writable", "Reviewed wall tier manifest is incomplete or exceeds its bounds.", 409)
    identity_keys = ("drawing_file", "signed_drawing_file", "model_uuid", "view_uuid", "type_name", "type_uuid")
    try:
        for record, expected_type in [(root, _WALL), *((tier, _TIER) for tier in tiers)]:
            if (any(key not in record for key in (*identity_keys, "layer"))
                    or type(record.get("drawing_file")) is not int or record["drawing_file"] != ref["drawing_file"]
                    or type(record.get("signed_drawing_file")) is not int or record["signed_drawing_file"] <= 0
                    or record["signed_drawing_file"] != record["drawing_file"]
                    or record.get("type_name") != expected_type
                    or not isinstance(record.get("model_uuid"), str)
                    or not isinstance(record.get("view_uuid"), str)
                    or not isinstance(record.get("type_uuid"), str)
                    or guid(record["model_uuid"]) != record["model_uuid"]
                    or guid(record["view_uuid"]) != record["view_uuid"]
                    or guid(record["type_uuid"]) != record["type_uuid"]
                    or type(record.get("layer")) is not int or record["layer"] <= 0):
                raise BridgeError("target_not_writable", "Reviewed wall tier manifest contains an invalid identity or layer.", 409)
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("target_not_writable", "Reviewed wall tier manifest contains an invalid identity or layer.", 409) from exc
    try:
        ref_model_uuid, ref_type_uuid = guid(ref["model_uuid"]), guid(ref["type_uuid"])
    except Exception as exc:
        raise BridgeError("target_not_writable", "Requested wall reference is malformed.", 409) from exc
    if (root["model_uuid"] != ref_model_uuid or root["type_uuid"] != ref_type_uuid
            or len({tier["model_uuid"] for tier in tiers}) != len(tiers)
            or len({tier["view_uuid"] for tier in tiers}) != len(tiers)
            or any(tier["signed_drawing_file"] != root["signed_drawing_file"] for tier in tiers)
            or any(tier.get("parent_model_uuid") != root["model_uuid"]
                   or tier.get("parent_view_uuid") != root["view_uuid"]
                   or tier.get("parent_type_uuid") != root["type_uuid"] for tier in tiers)
            or len({tier["layer"] for tier in tiers}) != 1
            or old_value["value"] != tiers[0]["layer"]
            or target_layer == old_value["value"]):
        raise BridgeError("target_not_writable", "Reviewed wall tier manifest does not match the requested wall.", 409)
    return reviewed, short_name


def valid_change(change):
    """Pure, bounded validation for the root executor's pre-journal guard."""
    try:
        _validate_reviewed(change)
    except Exception:
        return False
    return True


def _fresh_targets(base, adapter, change, adapters, check):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Wall tier layer change is malformed or was not explicitly reviewed.", 409)
    reviewed, short_name = _validate_reviewed(change)
    root_ident, tiers, tier_adapters, children_owner = _collect(adapter, adapters, check)
    current = {"schema_version": SCHEMA,
               "root": {**root_ident, "layer": _layer(adapter)},
               "tiers": tiers, "complete": True}
    if current != reviewed:
        raise BridgeError("selection_stale", "Wall or tier ownership/layer state changed since preview.", 409)
    if root_ident["signed_drawing_file"] <= 0:
        raise BridgeError("target_not_writable", "Passive wall cannot be changed.", 409)
    for tier_adapter in tier_adapters:
        check()
        _writable(tier_adapter, root_ident, base)
    return short_name, tier_adapters, children_owner


def preflight(base, adapter, change, adapters, check=lambda: None):
    """Revalidate wall-tier owners and writability without requesting a setter."""
    _short_name, _tier_adapters, _children_owner = _fresh_targets(base, adapter, change, adapters, check)
    return True


def _writable(adapter, root_ident, base):
    try:
        if integer(base.DrawingFileService.GetActiveFileNumber()) != root_ident["drawing_file"]:
            raise BridgeError("target_not_writable", "Wall is outside the active foreground drawing.", 409)
        for method, expected in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                                 ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                                 ("IsLabelElement", False)):
            if boolean(getattr(adapter, method)()) is not expected:
                raise BridgeError("target_not_writable", f"Wall tier fails {method}; no write requested.", 409)
        if integer(adapter.GetDrawingfileNumber()) != root_ident["drawing_file"]:
            raise BridgeError("target_not_writable", "Wall tier is passive; no write requested.", 409)
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("target_not_writable", "Wall tier writability could not be verified.", 409) from exc


def write(base, adapter, change, adapters, check=lambda: None):
    """Change only reviewed, directly owned WallTier adapters, exactly once."""
    short_name, tier_adapters, children_owner = _fresh_targets(base, adapter, change, adapters, check)
    targets = adapters.BaseElementAdapterList()
    # Keep fresh child adapter owners alive through the one setter call; never
    # pass the wall root, axis, opening, label or stale preview adapters.
    for tier_adapter in tier_adapters:
        targets.append(tier_adapter)
    check()
    try:
        return base.ElementsLayerService.ChangeLayer(targets, short_name)
    finally:
        # Keep both the native child container and its adapter wrappers alive
        # across the API call; CLR proxy ownership may be tied to the container.
        _ = children_owner, tier_adapters, targets
