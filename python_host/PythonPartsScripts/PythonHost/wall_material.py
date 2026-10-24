"""Native Wall/Column material edits with optional preservation evidence.

No definition enumeration, catalog creation, attribute or surface substitution.
Only the existing represented object is submitted to ModifyElements.
"""
from __future__ import annotations

import hashlib
import json
import math

from .component_ownership import ComponentReadError, failure, identity, observe, same_model_identity
from .attribute_evidence import describe_value
from .model_context import integer, text
from .query_contracts import fingerprint
from .transport import BridgeError

_SCALARS = ("Thickness", "CalculationMode", "CircleDivision", "Factor", "Priority", "Trade",
            "Name", "Status", "Surface", "BitmapName", "FaceStyle", "Filling", "Hatch", "Pattern", "BackgroundColor")
_COMMON = ("Color", "ColorByLayer", "ConstructionLine", "DrawOrder", "ForceColor", "HelpConstruction",
           "InSpecialWindow", "Layer", "PageNumber", "Pen", "PenByLayer", "Printable", "Stroke", "StrokeByLayer",
           "Visible", "VisibleInsideZoomwindows", "VisibleOutsideZoomwindows")
_MAX_ATTRIBUTE_CONTAINERS = 64
_MAX_ATTRIBUTE_SNAPSHOT_BYTES = 256 * 1024
_MAX_AUXILIARY_COMPONENTS = 256
_MAX_COMPONENT_SNAPSHOT_BYTES = 1024 * 1024
_STATE_SCHEMA = "m4-native-material-state-2"


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
    """Snapshot all stored metadata on one exact AttributeContainer.

    Unknown SDK values are not coerced: they make this optional snapshot unavailable.
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
        # The SDK's standard Material attribute can reflect the very native
        # property being changed. It must not be hashed as an unrelated invariant.
        if ident == 508:
            continue
        value = describe_value(pair[1])
        if value.get("status") != "observed":
            raise ValueError("Attribute-container value has no bounded preservation codec")
        row = {"attribute_id": ident, **value}
        byte_count += len(json.dumps(row, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        if byte_count > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
            raise ComponentReadError("material_attribute_container_values", "wall_material_attribute_snapshot_limit")
        result.append(row)
    return sorted(result, key=lambda item: item["attribute_id"])


def _live_children(adapter, observed, check, read):
    """Re-enumerate bounded live wrappers without requiring an indexable SDK collection."""
    import NemAll_Python_IFW_ElementAdapter as adapters

    collection = read(lambda: adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True),
                      "material_component_children")
    live = []
    for index, child in enumerate(collection):
        check()
        if index >= _MAX_AUXILIARY_COMPONENTS:
            raise ComponentReadError("material_component_children", "wall_material_component_limit")
        live.append(child)
    refs = [read(lambda child=child: identity(child), "material_component_identity") for child in live]
    if (len({_identity_key(ref) for ref in refs}) != len(refs)
            or {_identity_key(ref) for ref in refs} != {_identity_key(ref) for ref in observed["children"]}):
        raise ComponentReadError("material_component_children", "wall_material_component_children_changed")
    # Some native collections own the wrapper lifetimes; callers must retain it.
    return collection, list(zip(live, refs))


def _auxiliary_geometry(adapter, check):
    """Keep stream evidence when available, without requiring every child to be a solid.

    Axis and other auxiliary SDK geometries need not expose WriteToStream.
    A bounded not_checked result is explicit coverage information, not proof
    that hidden geometry or other native properties have been preserved.
    """
    import NemAll_Python_Geometry as geometry_api

    check()
    try:
        geometry = adapter.GetModelGeometry()
        serializer = getattr(geometry, "WriteToStream", None)
        if not callable(serializer):
            return {"status": "not_checked", "reason": "geometry_stream_unsupported"}
        code, stream = serializer()
        if code != geometry_api.eGeometryErrorCode.eOK or type(stream) is not str or not stream or len(stream) > 524288:
            return {"status": "not_checked", "reason": "geometry_stream_unavailable"}
        return {"status": "observed", "stream_sha256": hashlib.sha256(stream.encode("utf-8")).hexdigest()}
    except (BridgeError, ComponentReadError):
        raise
    except Exception as exc:
        return {"status": "not_checked", "reason": "geometry_stream_unavailable", "error_type": type(exc).__name__}
    finally:
        check()


def _auxiliary_snapshot(adapter, base, owner, check, read, budget, expected):
    check()
    if budget["count"] >= _MAX_AUXILIARY_COMPONENTS:
        raise ComponentReadError("material_component_children", "wall_material_component_limit")
    budget["count"] += 1
    observed = read(lambda: observe(adapter, check), "material_component_hierarchy")
    lineage = observed["lineage"]
    if (not same_model_identity(observed["target"], expected)
            or len(lineage) != len(owner["lineage"]) + 1 or lineage[0] != observed["target"]
            or any(not same_model_identity(actual, expected)
                   for actual, expected in zip(lineage[1:], owner["lineage"]))):
        raise ComponentReadError("material_component_hierarchy", "wall_material_component_hierarchy_changed",
                                 evidence={"owner": owner["target"], "child": observed["target"]})
    key = (observed["target"]["signed_drawing_file"], observed["target"]["model_uuid"])
    if key in budget["seen"]:
        raise ComponentReadError("material_component_hierarchy", "wall_material_component_identity_ambiguous")
    budget["seen"].add(key)
    result = {"ownership": observed, "children": []}
    if observed["target"]["type_name"] == "AttributeContainer_TypeUUID":
        attrs = read(lambda: _read_container_attributes(adapter, base, check),
                     "material_attribute_container_values")
        result["stored_attributes"] = attrs
        budget["attribute_bytes"] += len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        if budget["attribute_bytes"] > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
            raise ComponentReadError("material_children", "wall_material_attribute_snapshot_limit")
    result["geometry"] = _auxiliary_geometry(adapter, check)
    # Count each node once, including empty child-list framing and a comma
    # allowance, before its descendants are attached to the serialized tree.
    budget["snapshot_bytes"] += len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")) + 2
    if budget["snapshot_bytes"] > _MAX_COMPONENT_SNAPSHOT_BYTES:
        raise ComponentReadError("material_component_children", "wall_material_component_snapshot_limit")
    children_owner, children = _live_children(adapter, observed, check, read)
    if sum(ref["type_name"] == "AttributeContainer_TypeUUID" for ref in observed["children"]) > _MAX_ATTRIBUTE_CONTAINERS:
        raise ComponentReadError("material_component_children", "wall_material_attribute_container_limit")
    result["children"] = sorted(
        [_auxiliary_snapshot(child, base, observed, check, read, budget, ref) for child, ref in children], key=fingerprint)
    return result


def _detailed_snapshot(base, adapter, check=lambda: None, *, material_observation=None, captured=None):
    import NemAll_Python_ArchElements as arch
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
    state = captured if captured is not None else {}
    hierarchy = read(lambda: observe(adapter, check), "material_hierarchy")
    state["hierarchy"] = hierarchy
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
    root_auxiliary, tier_auxiliary = [], []
    state.update(root_attribute_containers=root_metadata,
                 auxiliary_components={"root": root_auxiliary, "tier": tier_auxiliary})
    budget = {"count": 0, "attribute_bytes": 0, "snapshot_bytes": 0,
              "seen": {(hierarchy["target"]["signed_drawing_file"], hierarchy["target"]["model_uuid"])}}
    for index, child in enumerate(children):
        check()
        if index >= 256:
            raise ComponentReadError("material_children", "wall_material_child_limit")
        kind = text(read(lambda: child.GetElementAdapterType().GetTypeName(), "material_child_type"))
        if kind != "WallTier_TypeUUID":
            if kind == "AttributeContainer_TypeUUID" and len(root_metadata) >= _MAX_ATTRIBUTE_CONTAINERS:
                raise ComponentReadError("material_children", "wall_material_attribute_container_limit")
            ref = read(lambda: identity(child), "material_component_identity")
            component = _auxiliary_snapshot(child, base, hierarchy, check, read, budget, ref)
            child_refs.append(component["ownership"]["target"])
            (root_metadata if kind == "AttributeContainer_TypeUUID" else root_auxiliary).append(component)
            continue
        child_hierarchy = read(lambda: observe(child, check), "material_tier_hierarchy")
        state["tier_hierarchy"] = child_hierarchy
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
        # Auxiliary shape alone does not disqualify material edits. Preserve
        # bounded ownership trees, supported geometry streams and metadata.
        metadata_children = []
        state["tier_attribute_containers"] = metadata_children
        tier_children_owner, live_children = _live_children(child, child_hierarchy, check, read)
        for auxiliary, ref in live_children:
            if ref["type_name"] == "AttributeContainer_TypeUUID" and len(metadata_children) >= _MAX_ATTRIBUTE_CONTAINERS:
                raise ComponentReadError("material_tier_children", "wall_material_attribute_container_limit")
            component = _auxiliary_snapshot(auxiliary, base, child_hierarchy, check, read, budget, ref)
            (metadata_children if ref["type_name"] == "AttributeContainer_TypeUUID" else tier_auxiliary).append(component)
        metadata_children.sort(key=fingerprint)
        # Material is a property edit; a tier need not expose a valid
        # Polyhedron3D (or any serializable geometry) to accept it.
        tiers.append(_auxiliary_geometry(child, check))
        state["tier_geometry"] = tiers[-1]
    if (len(tiers) != 1 or len(child_refs) != len(hierarchy["children"])
            or len({_identity_key(ref) for ref in child_refs}) != len(child_refs)
            or {_identity_key(ref) for ref in child_refs} != {_identity_key(ref) for ref in hierarchy["children"]}):
        raise ComponentReadError("material_children", "wall_material_one_exact_tier_required")
    root_metadata.sort(key=fingerprint)
    state.update({"hierarchy": hierarchy, "tier_hierarchy": child_hierarchy,
             "root_attribute_containers": root_metadata,
             "tier_attribute_containers": metadata_children, "tier_count": 1,
             "auxiliary_components": {"root": sorted(root_auxiliary, key=fingerprint),
                                      "tier": sorted(tier_auxiliary, key=fingerprint)},
             "axis": read(lambda: _representation(props.Axis), "material_axis"),
             "path_axis_type": integer(read(lambda: props.PathElementAxisType)),
             "tier": {name: read(lambda name=name: _scalar(getattr(tier, name)), "material_tier_" + name) for name in _SCALARS},
             "common": {name: read(lambda name=name: _scalar(getattr(tier.CommonProperties, name)), "material_common_" + name) for name in _COMMON},
             "complex_properties": {name: read(lambda name=name: _representation(getattr(tier, name)), "material_" + name)
                                    for name in ("PlaneReferences", "SurfaceElementProperties")}})
    if type(state["tier"]["Thickness"]) not in (float, int) or state["tier"]["Thickness"] <= 0:
        raise ValueError("Wall thickness unavailable")
    state["tier_geometry"] = tiers[0]
    state["geometry_stream_sha256"] = tiers[0].get("stream_sha256")
    state["invariant_coverage"] = "explicit_properties_metadata_and_bounded_auxiliary_tree_with_optional_geometry_streams"
    check()
    return material, state, native, props


def _optional(callback, check, stage):
    check()
    try:
        return callback()
    except BridgeError:
        raise
    except Exception as exc:
        return failure(exc, stage)
    finally:
        check()


def snapshot(base, adapter, check=lambda: None, *, material_observation=None):
    """Require the field owner and material, not geometry or hidden metadata.

    Available invariant evidence is still bound into revalidation/readback.
    Unsupported preservation reads remain explicit and never authorize a
    different target, an automatic setter retry or a claim of full coverage.
    """
    import NemAll_Python_ArchElements as arch

    def read(callback, stage):
        check()
        try:
            return callback()
        except (BridgeError, ComponentReadError):
            raise
        except Exception as exc:
            raise ComponentReadError(stage, "native_material_read_unavailable", type(exc).__name__) from exc
        finally:
            check()

    hierarchy = read(lambda: observe(adapter, check, include_children=False), "material_hierarchy")
    kind = hierarchy["target"]["type_name"]
    class_name = {"Wall_TypeUUID": "WallElement", "Column_TypeUUID": "ColumnElement"}.get(kind)
    if class_name is None:
        raise ComponentReadError("material_native_type", "native_material_type_unsupported")
    if hierarchy["lineage"] != [hierarchy["target"]]:
        raise ComponentReadError("material_hierarchy", "native_material_standalone_root_required")
    native = read(lambda: base.GetElement(adapter), "material_native_representation")
    if not isinstance(native, getattr(arch, class_name)):
        raise ComponentReadError("material_native_representation", "native_material_representation_unsupported")
    props = read(lambda: native.Properties, "material_properties")
    is_wall = kind == "Wall_TypeUUID"
    if is_wall and integer(read(lambda: props.TierCount, "material_tier_count")) != 1:
        raise ComponentReadError("material_tier_count", "wall_material_single_tier_required")
    tier = read(lambda: props.GetWallTierProperties(1), "material_tier_properties") if is_wall else props
    material = read(lambda: tier.Material, "material_value")
    if type(material) is not str or len(material) > 255:
        raise ComponentReadError("material_value", "native_material_string_unavailable")
    if material_observation is not None:
        material_observation.update(status="observed", value=material)
    if not callable(getattr(tier, "SetMaterial", None)) or not callable(getattr(native, "SetProperties", None)):
        raise ComponentReadError("material_setters", "native_material_setters_unavailable")

    state = {"hierarchy": hierarchy, "tier_count": 1 if is_wall else None}
    if is_wall:
        captured = {}
        detailed = _optional(lambda: _detailed_snapshot(base, adapter, check, captured=captured), check, "material_preservation")
        if isinstance(detailed, tuple):
            current_material, state, native, props = detailed
            if current_material != material:
                raise BridgeError("repair_conflict", "Material changed during observation.", 409)
        else:
            # Keep completed observations even if a later auxiliary read fails.
            # Only the core root identity establishes the mutation target.
            state["partial_preservation"] = captured
            state["preservation_diagnostic"] = detailed
    else:
        state["component_tree"] = _optional(lambda: observe(adapter, check), check, "material_component_tree")
        state["geometry"] = _auxiliary_geometry(adapter, check)

    # Read each unrelated property independently: one unsupported field must
    # not discard all the other available drift evidence.
    state["optional_properties"] = {
        "tier": {name: _optional(lambda name=name: _scalar(getattr(tier, name)), check,
                                  "material_tier_" + name) for name in _SCALARS},
        "common": {name: _optional(lambda name=name: _scalar(getattr(tier.CommonProperties, name)), check,
                                    "material_common_" + name) for name in _COMMON},
        "complex": {name: _optional(lambda name=name: _representation(getattr(tier, name)), check,
                                     "material_" + name) for name in ("PlaneReferences", "SurfaceElementProperties")}}
    if is_wall:
        state["optional_properties"]["axis"] = _optional(lambda: _representation(props.Axis), check, "material_axis")
    state.update(schema_version=_STATE_SCHEMA,
                 material_owner="wall_tier_1" if is_wall else "column_properties")
    check()
    return material, state, native, props


def consensus_key(result):
    """Compare required native values across views, not optional view evidence."""
    value, state, eligibility = result
    if state is None:
        return fingerprint((value, eligibility))
    target = state["hierarchy"]["target"]
    return fingerprint({"value": value, "owner": state["material_owner"],
                        "tier_count": state["tier_count"],
                        "target": {key: target[key] for key in (
                            "drawing_file", "signed_drawing_file", "model_uuid", "type_name", "type_uuid")}})


def observation(base, element, check=lambda: None):
    value, state, preservation = preview_observation(base, element, check)
    return (value, state) if state is not None else (preservation, None)


def preview_observation(base, element, check=lambda: None):
    """Separate a readable material string from eligibility to preserve the Wall.

    Eligibility requires the native property owner and available setters.
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
    evidence = resource.get("native_material_state")
    target = (evidence or {}).get("hierarchy", {}).get("target", {})
    ref = change.get("ref") or {}
    kind = change.get("native_type")
    return (change.get("operation") == "set_native_material" and kind in {"Wall_TypeUUID", "Column_TypeUUID"}
            and change.get("field") == "native.material" and change.get("property_role") == "native_material"
            and resource.get("tier_index") == 1 and resource.get("data_type") == "text"
            and type(resource.get("tier_index")) is int
            and type(change.get("new_value")) is str and 0 < len(change["new_value"]) <= 255
            and bool(change["new_value"].strip()) and not any(ord(c) < 32 for c in change["new_value"])
            and change.get("old_value", {}).get("status") == "observed"
            and type(change["old_value"].get("value")) is str
            and isinstance(evidence, dict) and evidence.get("schema_version") == _STATE_SCHEMA
            and evidence.get("material_owner") == ("wall_tier_1" if kind == "Wall_TypeUUID" else "column_properties")
            and (kind != "Wall_TypeUUID" or evidence.get("tier_count") == 1)
            and all(target.get(key) == ref.get(key) for key in ("drawing_file", "model_uuid", "type_uuid"))
            and target.get("type_name") == kind
            and target.get("view_uuid") == change.get("target_view_uuid"))


def read(base, element, change, check=lambda: None):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Native material requires an exact reviewed Wall or Column.", 409)
    value, state = observation(base, element, check)
    if fingerprint(state) != fingerprint(change["resource"]["native_material_state"]):
        return {"status": "not_checked", "value": None, "reason": "wall_material_invariants_changed"}
    return value


def write(base, element, change, doc=None, check=lambda: None):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Native material change is not bound.", 409)
    material, state, native, props = snapshot(base, element, check)
    if state != change["resource"]["native_material_state"] or material != change["old_value"]["value"]:
        raise BridgeError("repair_conflict", "Wall material or preservation evidence changed before setter.", 409)
    if doc is None:
        doc = element.GetDocument()
    from .model_delete import final_write_guard
    final_write_guard(base, element, change, doc, check)
    owner = props.GetWallTierProperties(1) if change["native_type"] == "Wall_TypeUUID" else props
    owner.SetMaterial(change["new_value"])
    native.SetProperties(props)
    check()
    return base.ModifyElements(doc, [native])
