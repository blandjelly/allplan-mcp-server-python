"""Bounded single-tier Wall material adapter, with durable invariant evidence.

No definition enumeration, catalog creation, attribute or surface substitution.
Only the existing represented Wall object is submitted to ModifyElements.
"""
from __future__ import annotations

import hashlib
import json
import math

from .component_ownership import ComponentReadError, failure, identity, observe, same_model_identity
from .attribute_evidence import describe_value
from .model_context import boolean, integer, text
from .query_contracts import fingerprint
from .transport import BridgeError

_SCALARS = ("Thickness", "CalculationMode", "CircleDivision", "Factor", "Priority", "Trade",
            "Name", "Status", "Surface", "BitmapName", "FaceStyle", "Filling", "Hatch", "Pattern", "BackgroundColor")
_COMMON = ("Color", "ColorByLayer", "ConstructionLine", "DrawOrder", "ForceColor", "HelpConstruction",
           "InSpecialWindow", "Layer", "PageNumber", "Pen", "PenByLayer", "Printable", "Stroke", "StrokeByLayer",
           "Visible", "VisibleInsideZoomwindows", "VisibleOutsideZoomwindows")
_MAX_ATTRIBUTE_CONTAINERS = 64
_MAX_ATTRIBUTE_SNAPSHOT_BYTES = 256 * 1024


def _scalar(value):
    if type(value) in (str, bool, int) and (type(value) is not str or len(value) <= 8192):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    raise ValueError("Native material invariant is not a supported scalar")


def _representation(value):
    # These three documented complex properties have no portable scalar codec.
    # Their bounded native representations are additional drift evidence, not
    # a claim that every hidden SDK field was read or can be reconstructed.
    result = repr(value)
    if not result or len(result) > 16384 or " at 0x" in result:
        raise ValueError("Native property representation unavailable")
    return result


def _identity_key(ref):
    return tuple(ref[key] for key in ("drawing_file", "signed_drawing_file", "model_uuid", "type_name", "type_uuid"))


def _read_container_attributes(adapter, base, check):
    """Snapshot all stored metadata on one exact AttributeContainer leaf.

    Unknown SDK values are not coerced or omitted: they block preservation.
    This is preservation evidence only and does not establish field ownership.
    """
    raw = adapter.GetAttributes(base.eAttibuteReadState.ReadAll)
    result, seen, byte_count = [], set(), 0
    for index, pair in enumerate(raw):
        check()
        if index >= 4096 or type(pair) not in (list, tuple) or len(pair) != 2:
            raise ValueError("Invalid or over-budget attribute-container values")
        ident = pair[0]
        if type(ident) is not int or not 1 <= ident <= 2147483647 or ident in seen:
            raise ValueError("Invalid or duplicate attribute-container identity")
        seen.add(ident)
        value = describe_value(pair[1])
        if value.get("status") != "observed":
            raise ValueError("Attribute-container value has no bounded preservation codec")
        row = {"attribute_id": ident, **value}
        byte_count += len(json.dumps(row, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        if byte_count > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
            raise ComponentReadError("material_attribute_container_values", "wall_material_attribute_snapshot_limit")
        result.append(row)
    return sorted(result, key=lambda item: item["attribute_id"])


def _attribute_container_snapshot(adapter, base, owner, check, read):
    observed = read(lambda: observe(adapter, check), "material_attribute_container_hierarchy")
    lineage = observed["lineage"]
    if (len(lineage) != len(owner["lineage"]) + 1 or lineage[0] != observed["target"]
            or any(not same_model_identity(actual, expected)
                   for actual, expected in zip(lineage[1:], owner["lineage"]))
            or observed["children"]):
        raise ComponentReadError("material_attribute_container_hierarchy",
                                 "wall_material_attribute_container_hierarchy_unsupported")
    if observed["target"]["type_name"] != "AttributeContainer_TypeUUID":
        raise ComponentReadError("material_attribute_container_type",
                                 "wall_material_attribute_container_type_unsupported")
    attrs = read(lambda: _read_container_attributes(adapter, base, check),
                 "material_attribute_container_values")
    return {"ownership": observed, "stored_attributes": attrs}


def snapshot(base, adapter, check=lambda: None, *, material_observation=None):
    import NemAll_Python_ArchElements as arch
    import NemAll_Python_Geometry as geometry
    import NemAll_Python_IFW_ElementAdapter as adapters

    def read(callback, stage="wall_material"):
        check()
        try:
            result = callback()
        except (BridgeError, ComponentReadError):
            raise
        except Exception as exc:
            raise ComponentReadError(stage, "wall_material_read_unavailable", type(exc).__name__) from exc
        check()
        return result

    if text(read(lambda: adapter.GetElementAdapterType().GetTypeName())) != "Wall_TypeUUID":
        raise ValueError("Native material requires a Wall root")
    hierarchy = read(lambda: observe(adapter, check), "material_hierarchy")
    native = read(lambda: base.GetElement(adapter), "material_native_representation")
    if not isinstance(native, arch.WallElement):
        raise ValueError("Native representation is not WallElement")
    props = read(lambda: native.Properties, "material_properties")
    if integer(read(lambda: props.TierCount)) != 1:
        raise ComponentReadError("material_tier_count", "wall_material_single_tier_required")
    tier = read(lambda: props.GetWallTierProperties(1))
    material = read(lambda: tier.Material, "material_value")
    if type(material) is not str or len(material) > 255:
        raise ComponentReadError("material_value", "wall_material_string_unavailable")
    if material_observation is not None:
        material_observation.update(status="observed", value=material)
    if hierarchy["lineage"] != [hierarchy["target"]]:
        raise ComponentReadError("material_hierarchy", "wall_material_standalone_root_required")
    if not callable(getattr(tier, "SetMaterial", None)) or not callable(getattr(native, "SetProperties", None)):
        raise ComponentReadError("material_setters", "wall_material_setters_unavailable")
    children = read(lambda: adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True),
                    "material_children")
    tiers = []
    child_refs = []
    root_metadata = []
    for index, child in enumerate(children):
        check()
        if index >= 256:
            raise ComponentReadError("material_children", "wall_material_child_limit")
        kind = text(read(lambda: child.GetElementAdapterType().GetTypeName(), "material_child_type"))
        if kind == "WindowDoor_TypeUUID":
            raise ComponentReadError("material_children", "wall_material_openings_unsupported")
        if kind == "AttributeContainer_TypeUUID":
            if len(root_metadata) >= _MAX_ATTRIBUTE_CONTAINERS:
                raise ComponentReadError("material_children", "wall_material_attribute_container_limit")
            metadata = _attribute_container_snapshot(child, base, hierarchy, check, read)
            child_refs.append(metadata["ownership"]["target"])
            root_metadata.append(metadata)
            if len(json.dumps(root_metadata, ensure_ascii=False, allow_nan=False).encode("utf-8")) > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
                raise ComponentReadError("material_children", "wall_material_attribute_snapshot_limit")
            continue
        if kind != "WallTier_TypeUUID":
            raise ComponentReadError("material_children", "wall_material_child_type_unsupported",
                                     evidence={"owner": hierarchy["target"], "child": identity(child)})
        child_hierarchy = read(lambda: observe(child, check), "material_tier_hierarchy")
        lineage = child_hierarchy["lineage"]
        # A tier's parent can be another view wrapper of this same Wall.
        # Bind the observed wrappers below, but compare structural ownership
        # by drawing/model/type, as component_ownership.observe does.
        if (len(lineage) != 2 or lineage[0] != child_hierarchy["target"]
                or not same_model_identity(lineage[1], hierarchy["target"])):
            raise ComponentReadError("material_tier_hierarchy", "wall_material_tier_hierarchy_unsupported",
                                     evidence={"selected_wall": hierarchy["target"], "tier_lineage": lineage,
                                               "tier_child_count": len(child_hierarchy["children"]),
                                               "tier_children_sample": child_hierarchy["children"][:8]})
        child_refs.append(child_hierarchy["target"])
        # Wall tiers can own a direct AttributeContainer metadata leaf. Keep
        # this narrow: every other child type, nested container, incomplete
        # owner edge, or unrepresentable stored value remains blocked.
        metadata_children = []
        if child_hierarchy["children"]:
            if len(child_hierarchy["children"]) > _MAX_ATTRIBUTE_CONTAINERS:
                raise ComponentReadError("material_tier_children", "wall_material_attribute_container_limit")
            metadata_owner = read(lambda: adapters.BaseElementAdapterChildElementsService.GetChildModelElements(child, True),
                                  "material_tier_children")
            # Native child collections only need to support iteration. Keep
            # their owner alive and retain a bounded list of adapter wrappers.
            live_metadata = []
            for metadata_index, item in enumerate(metadata_owner):
                check()
                if metadata_index >= _MAX_ATTRIBUTE_CONTAINERS:
                    raise ComponentReadError("material_tier_children", "wall_material_attribute_container_limit")
                live_metadata.append(item)
            if len(live_metadata) != len(child_hierarchy["children"]):
                raise ComponentReadError("material_tier_children", "wall_material_attribute_container_changed")
            live_refs = [read(lambda item=item: identity(item), "material_attribute_container_identity")
                         for item in live_metadata]
            expected_refs = child_hierarchy["children"]
            if (len({_identity_key(ref) for ref in live_refs}) != len(live_refs)
                    or {_identity_key(ref) for ref in live_refs} != {_identity_key(ref) for ref in expected_refs}):
                raise ComponentReadError("material_tier_children", "wall_material_attribute_container_changed")
            for metadata_adapter, metadata_ref in zip(live_metadata, live_refs):
                check()
                if metadata_ref["type_name"] != "AttributeContainer_TypeUUID":
                    raise ComponentReadError("material_tier_children", "wall_material_tier_child_unsupported",
                                             evidence={"owner": child_hierarchy["target"], "child": metadata_ref})
                metadata_snapshot = _attribute_container_snapshot(
                    metadata_adapter, base, child_hierarchy, check, read)
                if not same_model_identity(metadata_snapshot["ownership"]["target"], metadata_ref):
                    raise ComponentReadError("material_tier_children", "wall_material_attribute_container_changed")
                metadata_children.append(metadata_snapshot)
                if len(json.dumps(metadata_children, ensure_ascii=False, allow_nan=False).encode("utf-8")) > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
                    raise ComponentReadError("material_tier_children", "wall_material_attribute_snapshot_limit")
            metadata_children.sort(key=fingerprint)
        solid = read(child.GetModelGeometry, "material_tier_geometry")
        if not isinstance(solid, geometry.Polyhedron3D) or not boolean(read(solid.IsValid)):
            raise ComponentReadError("material_tier_geometry", "wall_material_valid_tier_geometry_required")
        code, stream = read(solid.WriteToStream, "material_geometry_stream")
        if code != geometry.eGeometryErrorCode.eOK or type(stream) is not str or not stream or len(stream) > 524288:
            raise ComponentReadError("material_geometry_stream", "wall_material_geometry_stream_unavailable")
        tiers.append(hashlib.sha256(stream.encode("utf-8")).hexdigest())
    if (len(tiers) != 1 or len(child_refs) != len(hierarchy["children"])
            or len({_identity_key(ref) for ref in child_refs}) != len(child_refs)
            or {_identity_key(ref) for ref in child_refs} != {_identity_key(ref) for ref in hierarchy["children"]}):
        raise ComponentReadError("material_children", "wall_material_one_exact_tier_required")
    root_metadata.sort(key=fingerprint)
    if len(json.dumps(root_metadata + metadata_children, ensure_ascii=False, allow_nan=False).encode("utf-8")) > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
        raise ComponentReadError("material_children", "wall_material_attribute_snapshot_limit")
    state = {"hierarchy": hierarchy, "tier_hierarchy": child_hierarchy,
             "root_attribute_containers": root_metadata,
             "tier_attribute_containers": metadata_children, "tier_count": 1,
             "axis": read(lambda: _representation(props.Axis), "material_axis"),
             "path_axis_type": integer(read(lambda: props.PathElementAxisType)),
             "tier": {name: read(lambda name=name: _scalar(getattr(tier, name)), "material_tier_" + name) for name in _SCALARS},
             "common": {name: read(lambda name=name: _scalar(getattr(tier.CommonProperties, name)), "material_common_" + name) for name in _COMMON},
             "complex_properties": {name: read(lambda name=name: _representation(getattr(tier, name)), "material_" + name)
                                    for name in ("PlaneReferences", "SurfaceElementProperties")}}
    if type(state["tier"]["Thickness"]) not in (float, int) or state["tier"]["Thickness"] <= 0:
        raise ValueError("Wall thickness unavailable")
    state["geometry_stream_sha256"] = tiers[0]
    state["invariant_coverage"] = "serialized_tier_solid_explicit_scalars_bounded_complex_representations_and_attribute_container_values"
    check()
    return material, state, native, props


def observation(base, element, check=lambda: None):
    value, state, preservation = preview_observation(base, element, check)
    return (value, state) if state is not None else (preservation, None)


def preview_observation(base, element, check=lambda: None):
    """Separate a readable material string from eligibility to preserve the Wall.

    A material read alone never qualifies a setter or post-write readback.
    Native exception messages and representations are never returned on failure.
    """
    value = {}
    try:
        material, state, _, _ = snapshot(base, element, check, material_observation=value)
        return {"status": "observed", "value": material}, state, {"status": "observed", "value": True}
    except BridgeError:
        raise
    except Exception as exc:
        blocked = failure(exc, "wall_material_validation")
        return value or blocked, None, blocked


def valid_change(change):
    resource = change.get("resource") or {}
    evidence = resource.get("wall_material_state")
    target = (evidence or {}).get("hierarchy", {}).get("target", {})
    ref = change.get("ref") or {}
    return (change.get("operation") == "set_native_material" and change.get("native_type") == "Wall_TypeUUID"
            and change.get("field") == "wall.native_material" and change.get("property_role") == "native_material"
            and resource.get("tier_index") == 1 and resource.get("data_type") == "text"
            and type(change.get("new_value")) is str and 0 < len(change["new_value"]) <= 255
            and change.get("old_value", {}).get("status") == "observed"
            and type(change["old_value"].get("value")) is str
            and isinstance(evidence, dict) and evidence.get("tier_count") == 1
            and evidence.get("geometry_stream_sha256") is not None
            and all(target.get(key) == ref.get(key) for key in ("drawing_file", "model_uuid", "type_uuid"))
            and target.get("view_uuid") == change.get("target_view_uuid"))


def read(base, element, change, check=lambda: None):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Native material requires an exact reviewed single-tier Wall.", 409)
    value, state = observation(base, element, check)
    if fingerprint(state) != fingerprint(change["resource"]["wall_material_state"]):
        return {"status": "not_checked", "value": None, "reason": "wall_material_invariants_changed"}
    return value


def write(base, element, change, doc=None, check=lambda: None):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Native material change is not bound.", 409)
    material, state, native, props = snapshot(base, element, check)
    if state != change["resource"]["wall_material_state"] or material != change["old_value"]["value"]:
        raise BridgeError("repair_conflict", "Wall material or preservation evidence changed before setter.", 409)
    if doc is None:
        doc = element.GetDocument()
    from .model_delete import final_write_guard
    final_write_guard(base, element, change, doc, check)
    props.GetWallTierProperties(1).SetMaterial(change["new_value"])
    native.SetProperties(props)
    check()
    return base.ModifyElements(doc, [native])
