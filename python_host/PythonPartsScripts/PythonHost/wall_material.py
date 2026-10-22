"""Bounded single-tier Wall material adapter, with durable invariant evidence.

No definition enumeration, catalog creation, attribute or surface substitution.
Only the existing represented Wall object is submitted to ModifyElements.
"""
from __future__ import annotations

import hashlib
import math

from .component_ownership import ComponentReadError, failure, observe
from .model_context import boolean, integer, text
from .query_contracts import fingerprint
from .transport import BridgeError

_SCALARS = ("Thickness", "CalculationMode", "CircleDivision", "Factor", "Priority", "Trade",
            "Name", "Status", "Surface", "BitmapName", "FaceStyle", "Filling", "Hatch", "Pattern", "BackgroundColor")
_COMMON = ("Color", "ColorByLayer", "ConstructionLine", "DrawOrder", "ForceColor", "HelpConstruction",
           "InSpecialWindow", "Layer", "PageNumber", "Pen", "PenByLayer", "Printable", "Stroke", "StrokeByLayer",
           "Visible", "VisibleInsideZoomwindows", "VisibleOutsideZoomwindows")


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
    for index, child in enumerate(children):
        check()
        if index >= 256:
            raise ComponentReadError("material_children", "wall_material_child_limit")
        kind = text(read(lambda: child.GetElementAdapterType().GetTypeName(), "material_child_type"))
        if kind == "WindowDoor_TypeUUID":
            raise ComponentReadError("material_children", "wall_material_openings_unsupported")
        if kind != "WallTier_TypeUUID":
            raise ComponentReadError("material_children", "wall_material_child_type_unsupported")
        child_hierarchy = read(lambda: observe(child, check), "material_tier_hierarchy")
        if (child_hierarchy["lineage"] != [child_hierarchy["target"], hierarchy["target"]]
                or child_hierarchy["children"]):
            raise ComponentReadError("material_tier_hierarchy", "wall_material_tier_hierarchy_unsupported")
        child_refs.append(child_hierarchy["target"])
        solid = read(child.GetModelGeometry, "material_tier_geometry")
        if not isinstance(solid, geometry.Polyhedron3D) or not boolean(read(solid.IsValid)):
            raise ComponentReadError("material_tier_geometry", "wall_material_valid_tier_geometry_required")
        code, stream = read(solid.WriteToStream, "material_geometry_stream")
        if code != geometry.eGeometryErrorCode.eOK or type(stream) is not str or not stream or len(stream) > 524288:
            raise ComponentReadError("material_geometry_stream", "wall_material_geometry_stream_unavailable")
        tiers.append(hashlib.sha256(stream.encode("utf-8")).hexdigest())
    if len(tiers) != 1 or child_refs != hierarchy["children"]:
        raise ComponentReadError("material_children", "wall_material_one_exact_tier_required")
    state = {"hierarchy": hierarchy, "tier_count": 1,
             "axis": read(lambda: _representation(props.Axis), "material_axis"),
             "path_axis_type": integer(read(lambda: props.PathElementAxisType)),
             "tier": {name: read(lambda name=name: _scalar(getattr(tier, name)), "material_tier_" + name) for name in _SCALARS},
             "common": {name: read(lambda name=name: _scalar(getattr(tier.CommonProperties, name)), "material_common_" + name) for name in _COMMON},
             "complex_properties": {name: read(lambda name=name: _representation(getattr(tier, name)), "material_" + name)
                                    for name in ("PlaneReferences", "SurfaceElementProperties")}}
    if type(state["tier"]["Thickness"]) not in (float, int) or state["tier"]["Thickness"] <= 0:
        raise ValueError("Wall thickness unavailable")
    state["geometry_stream_sha256"] = tiers[0]
    state["invariant_coverage"] = "serialized_tier_solid_explicit_scalars_bounded_complex_representations"
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
