"""Native architectural material edits with optional preservation evidence.

No definition enumeration, catalog creation, attribute or surface substitution.
Only the existing represented object is submitted to ModifyElements.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import math

from .component_ownership import ComponentReadError, failure, identity, observe, same_model_identity
from .attribute_evidence import describe_value
from .model_context import integer, text
from .native_readers import OPENING_TYPES
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
_STATE_SCHEMA = "m4-native-material-state-3"
_NATIVE_CLASSES = {
    "Wall_TypeUUID": ("WallElement",),
    "Column_TypeUUID": ("ColumnElement",),
    "Beam_TypeUUID": ("BeamElement", "StructuralBeamElement"),
    "SkeletonBeam_TypeUUID": ("BeamElement", "StructuralBeamElement"),
    "Slab_TypeUUID": ("SlabElement",),
    "MultiSlab_TypeUUID": ("SlabElement",),
}
_MATERIAL_OWNERS = {"WallElement": "wall_tier_1", "ColumnElement": "column_properties",
                    "BeamElement": "beam_properties", "StructuralBeamElement": "structural_beam_properties",
                    "SlabElement": "slab_properties"}
_PROPERTY_ACCESSORS = {"StructuralBeamElement": ("StructuralBeamProperties", "SetStructuralBeamProperties")}

# 0.49.0: the native Material route also carries one CalculationMode write
# (plan item 5 step 2). SDK 2026 documents the closed code set below; the
# label is the SDK's. Only the field itself and its observed attribute mirror
# candidate are excluded from the bound preservation evidence.
MATERIAL_OPERATION = "set_native_material"
CALCULATION_MODE_OPERATION = "set_native_calculation_mode"
NATIVE_PROPERTY_OPERATIONS = frozenset({MATERIAL_OPERATION, CALCULATION_MODE_OPERATION})
CALCULATION_MODE_CODES = {0: "m3", 1: "m2", 2: "m", 3: "Pcs", 4: "kg"}
CALCULATION_MODE_MIRROR_ATTRIBUTE = 120
# Native trial 0.48.0: native code, attribute 120 and UI agree on these
# families. The MultiSlab's native SlabProperties is not the UI owner, so the
# slab calculation mode goes through attribute 120 on the MultiSlab instead.
CALCULATION_MODE_TYPES = frozenset({"Wall_TypeUUID", "Column_TypeUUID", "Beam_TypeUUID"})
SLAB_CALCULATION_MODE_BLOCK = "slab_calculation_mode_uses_multislab_attribute_120"
_CALCULATION_STATE_SCHEMA = "m4-native-calculation-mode-state-1"
_FIELDS = {
    "Material": {"operation": MATERIAL_OPERATION, "field": "native.material", "setter": "SetMaterial",
                 "excluded_attribute": 508, "state_key": "native_material_state"},
    "CalculationMode": {"operation": CALCULATION_MODE_OPERATION, "field": "native.calculation_mode",
                        "setter": "SetCalculationMode",
                        "excluded_attribute": CALCULATION_MODE_MIRROR_ATTRIBUTE,
                        "state_key": "native_property_state"},
}
_OPERATION_FIELDS = {spec["operation"]: name for name, spec in _FIELDS.items()}


def field_for(change):
    """Native SDK property name bound by a native property change, or None."""
    return _OPERATION_FIELDS.get((change or {}).get("operation"))


def state_key(change):
    return _FIELDS[field_for(change) or "Material"]["state_key"]


def _preserved_scalars(field):
    # Material is not an invariant of its own write; every other edit must
    # preserve it together with the remaining scalar set.
    return _SCALARS if field == "Material" else tuple(name for name in _SCALARS if name != field) + ("Material",)


def _property_accessors(class_name):
    return _PROPERTY_ACCESSORS.get(class_name, ("Properties", "SetProperties"))


def _supported_lineage(hierarchy):
    if not isinstance(hierarchy, dict):
        return False
    lineage = hierarchy.get("lineage", [])
    target = hierarchy.get("target")
    return (isinstance(target, dict) and isinstance(lineage, list)
            and all(isinstance(ref, dict) for ref in lineage) and (lineage == [target]
            or (len(lineage) == 2 and lineage[0] == hierarchy["target"]
                and lineage[0]["type_name"] == "Slab_TypeUUID"
                and lineage[1].get("type_name") == "MultiSlab_TypeUUID")))


def _reader(check, trace=None, trace_ref=None, *, reason="wall_material_read_unavailable"):
    # Identities come from the completed M1 scan; do not make untraced SDK
    # identity calls to enrich the diagnostic. Values and SDK reprs stay out.
    details = {key: trace_ref[key] for key in ("drawing_file", "model_uuid", "view_uuid")
               if trace_ref is not None and key in trace_ref}

    def native(api, callback):
        return trace.call(api, callback, **details) if trace is not None else callback()

    def read(callback, stage="wall_material", *, api=None):
        check()
        try:
            return native(api or "Native.material." + stage, callback)
        except (BridgeError, ComponentReadError):
            raise
        except Exception as exc:
            raise ComponentReadError(stage, reason, type(exc).__name__) from exc
        finally:
            check()

    read.native = native
    return read


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


def _read_container_attributes(adapter, base, check, read, excluded=508):
    """Snapshot all stored metadata on one exact AttributeContainer.

    Unknown SDK values are not coerced: they make this optional snapshot unavailable.
    This is preservation evidence only and does not establish field ownership.
    """
    raw = read.native("BaseElementAdapter.GetAttributes(ReadAll)",
                      lambda: adapter.GetAttributes(base.eAttibuteReadState.ReadAll))
    result, seen, byte_count = [], set(), 0
    for index, pair in enumerate(raw):
        check()
        if index >= 4096 or type(pair) not in (list, tuple) or len(pair) != 2:
            raise ValueError("Invalid or over-budget attribute-container values")
        ident = pair[0]
        if type(ident) is not int or not 1 <= ident <= 2147483647 or ident in seen:
            raise ValueError("Invalid or duplicate attribute-container identity")
        seen.add(ident)
        # The SDK's standard Material attribute (508) can reflect the very native
        # property being changed; for CalculationMode the candidate mirror is
        # attribute 120. It must not be hashed as an unrelated invariant.
        if ident == excluded:
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
                      "material_component_children", api="BaseElementAdapterChildElementsService.GetChildModelElements")
    live = []
    for index, child in enumerate(collection):
        check()
        if index >= _MAX_AUXILIARY_COMPONENTS:
            raise ComponentReadError("material_component_children", "wall_material_component_limit")
        live.append(child)
    refs = [read(lambda child=child: identity(child, trace=read.native), "material_component_identity") for child in live]
    # A shared opening tier (0.51.1) is enumerated here but owned and
    # snapshotted by its opening; it is bound by its observed edge instead.
    shared = {_identity_key(edge["child"]) for edge in observed.get("shared_children", [])}
    if (len({_identity_key(ref) for ref in refs}) != len(refs)
            or {_identity_key(ref) for ref in refs}
            != {_identity_key(ref) for ref in observed["children"]} | shared):
        raise ComponentReadError("material_component_children", "wall_material_component_children_changed")
    # Some native collections own the wrapper lifetimes; callers must retain it.
    return collection, [(child, ref) for child, ref in zip(live, refs) if _identity_key(ref) not in shared]


def _auxiliary_geometry(adapter, check, read=None):
    """Keep stream evidence when available, without requiring every child to be a solid.

    Axis and other auxiliary SDK geometries need not expose WriteToStream.
    A bounded not_checked result is explicit coverage information, not proof
    that hidden geometry or other native properties have been preserved.
    """
    import NemAll_Python_Geometry as geometry_api

    check()
    try:
        native_read = read.native if read is not None else lambda api, callback: callback()
        geometry = native_read("BaseElementAdapter.GetModelGeometry", adapter.GetModelGeometry)
        serializer = getattr(geometry, "WriteToStream", None)
        if not callable(serializer):
            return {"status": "not_checked", "reason": "geometry_stream_unsupported"}
        code, stream = native_read("Geometry.WriteToStream", serializer)
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
    observed = read(lambda: observe(adapter, check, trace=read.native), "material_component_hierarchy")
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
        attrs = read(lambda: _read_container_attributes(adapter, base, check, read,
                                                        budget.get("excluded_attribute", 508)),
                     "material_attribute_container_values")
        result["stored_attributes"] = attrs
        budget["attribute_bytes"] += len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        if budget["attribute_bytes"] > _MAX_ATTRIBUTE_SNAPSHOT_BYTES:
            raise ComponentReadError("material_children", "wall_material_attribute_snapshot_limit")
    result["geometry"] = _auxiliary_geometry(adapter, check, read)
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


def _child_preservation(adapter, base, hierarchy, check, read, excluded=508):
    budget = {"count": 0, "attribute_bytes": 0, "snapshot_bytes": 0, "excluded_attribute": excluded,
              "seen": {(hierarchy["target"]["signed_drawing_file"], hierarchy["target"]["model_uuid"])}}
    retained_children, children = _live_children(adapter, hierarchy, check, read)
    return sorted([_auxiliary_snapshot(child, base, hierarchy, check, read, budget, ref)
                   for child, ref in children], key=fingerprint)


def _bind_shared_opening_children(tier_hierarchy, root_auxiliary):
    """Each tier-listed opening child must be a snapshotted child of that opening.

    The opening's own subtree (geometry, metadata, identities) is the
    preservation evidence; the tier keeps only the exact observed edge.
    """
    for edge in tier_hierarchy.get("shared_children", []):
        owners = [component["ownership"] for component in root_auxiliary
                  if same_model_identity(component["ownership"]["target"], edge["parent"])]
        if (len(owners) != 1 or owners[0]["target"] != edge["parent"]
                or _identity_key(edge["child"]) not in {_identity_key(ref) for ref in owners[0]["children"]}):
            raise ComponentReadError("material_tier_children", "wall_material_shared_opening_child_unbound",
                                     evidence={"tier": tier_hierarchy["target"], "child": edge["child"],
                                               "observed_parent": edge["parent"]})


def _detailed_snapshot(base, adapter, check=lambda: None, *, material_observation=None, captured=None,
                       trace=None, trace_ref=None, field="Material"):
    read = _reader(check, trace, trace_ref)
    arch = read(lambda: importlib.import_module("NemAll_Python_ArchElements"), "material_native_module",
                api="Python.import.NemAll_Python_ArchElements")
    adapters = read(lambda: importlib.import_module("NemAll_Python_IFW_ElementAdapter"), "material_adapter_module",
                    api="Python.import.NemAll_Python_IFW_ElementAdapter")

    if text(read(lambda: adapter.GetElementAdapterType().GetTypeName())) != "Wall_TypeUUID":
        raise ValueError("Native material requires a Wall root")
    state = captured if captured is not None else {}
    hierarchy = read(lambda: observe(adapter, check, trace=read.native), "material_hierarchy")
    state["hierarchy"] = hierarchy
    native = read(lambda: base.GetElement(adapter), "material_native_representation", api="BaseElements.GetElement")
    if not isinstance(native, arch.WallElement):
        raise ValueError("Native representation is not WallElement")
    props = read(lambda: native.Properties, "material_properties", api="WallElement.Properties")
    if integer(read(lambda: props.TierCount, api="WallProperties.TierCount")) != 1:
        raise ComponentReadError("material_tier_count", "wall_material_single_tier_required")
    tier = read(lambda: props.GetWallTierProperties(1), api="WallProperties.GetWallTierProperties(1)")
    material = read(lambda: tier.Material, "material_value", api="WallTierProperties.Material")
    if type(material) is not str or len(material) > 255:
        raise ComponentReadError("material_value", "wall_material_string_unavailable")
    primary = material if field == "Material" else _field_value(read, tier, field, "WallTierProperties")
    if material_observation is not None:
        material_observation.update(status="observed", value=primary)
    if hierarchy["lineage"] != [hierarchy["target"]]:
        raise ComponentReadError("material_hierarchy", "wall_material_standalone_root_required")
    if (not callable(getattr(tier, _FIELDS[field]["setter"], None))
            or not callable(getattr(native, "SetProperties", None))):
        raise ComponentReadError("material_setters", "wall_material_setters_unavailable")
    children = read(lambda: adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True),
                    "material_children", api="BaseElementAdapterChildElementsService.GetChildModelElements")
    tiers = []
    child_refs = []
    root_metadata = []
    root_auxiliary, tier_auxiliary = [], []
    state.update(root_attribute_containers=root_metadata,
                 auxiliary_components={"root": root_auxiliary, "tier": tier_auxiliary})
    # Openings that are direct children of this Wall may also be listed under
    # its tier through their own tier (Window, 0.51.0 trial); see observe.
    openings = [ref for ref in hierarchy["children"] if ref["type_name"] in OPENING_TYPES]
    budget = {"count": 0, "attribute_bytes": 0, "snapshot_bytes": 0,
              "excluded_attribute": _FIELDS[field]["excluded_attribute"],
              "seen": {(hierarchy["target"]["signed_drawing_file"], hierarchy["target"]["model_uuid"])}}
    for index, child in enumerate(children):
        check()
        if index >= 256:
            raise ComponentReadError("material_children", "wall_material_child_limit")
        kind = text(read(lambda: child.GetElementAdapterType().GetTypeName(), "material_child_type"))
        if kind != "WallTier_TypeUUID":
            if kind == "AttributeContainer_TypeUUID" and len(root_metadata) >= _MAX_ATTRIBUTE_CONTAINERS:
                raise ComponentReadError("material_children", "wall_material_attribute_container_limit")
            ref = read(lambda: identity(child, trace=read.native), "material_component_identity")
            component = _auxiliary_snapshot(child, base, hierarchy, check, read, budget, ref)
            child_refs.append(component["ownership"]["target"])
            (root_metadata if kind == "AttributeContainer_TypeUUID" else root_auxiliary).append(component)
            continue
        child_hierarchy = read(lambda: observe(child, check, trace=read.native, shared_parents=openings),
                               "material_tier_hierarchy")
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
        tiers.append(_auxiliary_geometry(child, check, read))
        state["tier_geometry"] = tiers[-1]
    if len(tiers) == 1:
        _bind_shared_opening_children(child_hierarchy, root_auxiliary)
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
             "axis": read(lambda: _representation(props.Axis), "material_axis", api="WallProperties.Axis.repr"),
             "path_axis_type": integer(read(lambda: props.PathElementAxisType, api="WallProperties.PathElementAxisType")),
             "tier": {name: read(lambda name=name: _scalar(getattr(tier, name)), "material_tier_" + name,
                                  api="WallTierProperties." + name) for name in _preserved_scalars(field)},
             "common": {name: read(lambda name=name: _scalar(getattr(tier.CommonProperties, name)), "material_common_" + name,
                                    api="WallTierProperties.CommonProperties." + name) for name in _COMMON},
             "complex_properties": {name: read(lambda name=name: _representation(getattr(tier, name)), "material_" + name)
                                    for name in ("PlaneReferences", "SurfaceElementProperties")}})
    if type(state["tier"]["Thickness"]) not in (float, int) or state["tier"]["Thickness"] <= 0:
        raise ValueError("Wall thickness unavailable")
    state["tier_geometry"] = tiers[0]
    state["geometry_stream_sha256"] = tiers[0].get("stream_sha256")
    state["invariant_coverage"] = "explicit_properties_metadata_and_bounded_auxiliary_tree_with_optional_geometry_streams"
    if field != "Material":
        state.update(schema_version=_CALCULATION_STATE_SCHEMA, native_field=field)
    check()
    return primary, state, native, props, tier


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


def _field_value(read, owner, field, owner_name):
    """Read the bound native field; CalculationMode must be a documented code."""
    if field == "Material":
        value = read(lambda: owner.Material, "material_value", api=owner_name + ".Material")
        if type(value) is not str or len(value) > 255:
            raise ComponentReadError("material_value", "native_material_string_unavailable")
        return value
    value = read(lambda: getattr(owner, field), "calculation_mode_value", api=owner_name + "." + field)
    if type(value) is not int or value not in CALCULATION_MODE_CODES:
        raise ComponentReadError("calculation_mode_value", "native_calculation_mode_code_unavailable")
    return value


def snapshot(base, adapter, check=lambda: None, *, material_observation=None, trace=None, trace_ref=None,
             preservation=True, field="Material"):
    """Require the field owner and material, not geometry or hidden metadata.

    Available invariant evidence is still bound into revalidation/readback.
    Unsupported preservation reads remain explicit and never authorize a
    different target, an automatic setter retry or a claim of full coverage.
    """
    read = _reader(check, trace, trace_ref, reason="native_material_read_unavailable")
    arch = read(lambda: importlib.import_module("NemAll_Python_ArchElements"), "material_native_module",
                api="Python.import.NemAll_Python_ArchElements")

    hierarchy = read(lambda: observe(adapter, check, include_children=False, trace=read.native), "material_hierarchy")
    kind = hierarchy["target"]["type_name"]
    class_names = _NATIVE_CLASSES.get(kind)
    if class_names is None:
        raise ComponentReadError("material_native_type", "native_material_type_unsupported")
    if field != "Material" and kind not in CALCULATION_MODE_TYPES:
        raise ComponentReadError("native_property_type", SLAB_CALCULATION_MODE_BLOCK
                                 if kind in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}
                                 else "native_calculation_mode_family_unsupported")
    if not _supported_lineage(hierarchy):
        raise ComponentReadError("material_hierarchy", "native_material_standalone_root_required")
    native = read(lambda: base.GetElement(adapter), "material_native_representation", api="BaseElements.GetElement")
    # Adapter names alone do not prove the represented SDK class (notably
    # SkeletonBeam). Dispatch only after checking the live native instance.
    matching_classes = [name for name in class_names if isinstance(getattr(arch, name, None), type)
                        and isinstance(native, getattr(arch, name))]
    if len(matching_classes) != 1:
        raise ComponentReadError("material_native_representation", "native_material_representation_unsupported")
    class_name = matching_classes[0]
    property_name, setter_name = _property_accessors(class_name)
    props = read(lambda: getattr(native, property_name), "material_properties", api=class_name + "." + property_name)
    is_wall = kind == "Wall_TypeUUID"
    if is_wall and integer(read(lambda: props.TierCount, "material_tier_count", api="WallProperties.TierCount")) != 1:
        raise ComponentReadError("material_tier_count", "wall_material_single_tier_required")
    tier = read(lambda: props.GetWallTierProperties(1), "material_tier_properties",
                api="WallProperties.GetWallTierProperties(1)") if is_wall else props
    owner_name = "WallTierProperties" if is_wall else class_name.replace("Element", "Properties")
    material = _field_value(read, tier, field, owner_name)
    if material_observation is not None:
        material_observation.update(status="observed", value=material)
    if (not callable(getattr(tier, _FIELDS[field]["setter"], None))
            or not callable(getattr(native, setter_name, None))):
        raise ComponentReadError("material_setters", "native_material_setters_unavailable"
                                 if field == "Material" else "native_calculation_mode_setters_unavailable")

    def identify(state):
        # The Material state keeps its historical schema and keys unchanged so
        # existing journals compare byte-for-byte; another field is explicit.
        state.update(schema_version=_STATE_SCHEMA, native_class=class_name,
                     material_owner=_MATERIAL_OWNERS[class_name])
        if field != "Material":
            state.update(schema_version=_CALCULATION_STATE_SCHEMA, native_field=field)
        return state

    state = {"hierarchy": hierarchy, "tier_count": 1 if is_wall else None}
    if not preservation:
        identify(state)
        check()
        return material, state, native, props
    detailed = None
    if is_wall:
        # Boost.Python may expose borrowed children. Retain the first owner
        # graph through all reads, including replacement by the detailed read.
        retained_core = native, props, tier
        captured = {}
        detailed = _optional(lambda: _detailed_snapshot(base, adapter, check, captured=captured,
                             trace=trace, trace_ref=trace_ref, field=field), check, "material_preservation")
        if isinstance(detailed, tuple):
            current_material, state, native, props, tier = detailed
            if current_material != material:
                raise BridgeError("repair_conflict", "Material changed during observation."
                                  if field == "Material" else "CalculationMode changed during observation.", 409)
        else:
            # Keep completed observations even if a later auxiliary read fails.
            # Only the core root identity establishes the mutation target.
            state["partial_preservation"] = captured
            state["preservation_diagnostic"] = detailed
    else:
        state["component_tree"] = _optional(lambda: observe(adapter, check, trace=read.native), check, "material_component_tree")
        state["geometry"] = _auxiliary_geometry(adapter, check, read)
        if class_name == "SlabElement" and state["component_tree"].get("children_complete") is True:
            # Aggregate Slab geometry may live on its child tiers. Bind those
            # exact children and available geometry/metadata without treating
            # any child's adapter as the selected native property owner.
            state["child_components"] = _optional(lambda: _child_preservation(
                adapter, base, state["component_tree"], check, read, _FIELDS[field]["excluded_attribute"]),
                check, "material_child_preservation")

    # Read each unrelated property independently: one unsupported field must
    # not discard all the other available drift evidence.
    if isinstance(detailed, tuple):
        # These values already belong to the final retained property owners.
        # Reuse them instead of repeating every SDK getter and durable trace.
        state["optional_properties"] = {"tier": dict(state["tier"]), "common": dict(state["common"]),
                                        "complex": dict(state["complex_properties"]), "axis": state["axis"]}
    else:
        state["optional_properties"] = {
            "tier": {name: _optional(lambda name=name: read.native(owner_name + "." + name,
                                      lambda: _scalar(getattr(tier, name))), check,
                                      "material_tier_" + name) for name in _preserved_scalars(field)},
            "common": {name: _optional(lambda name=name: read.native(owner_name + ".CommonProperties." + name,
                                        lambda: _scalar(getattr(tier.CommonProperties, name))), check,
                                        "material_common_" + name) for name in _COMMON},
            "complex": {name: _optional(lambda name=name: read.native(owner_name + "." + name + ".repr",
                                         lambda: _representation(getattr(tier, name))), check,
                                         "material_" + name) for name in ("PlaneReferences", "SurfaceElementProperties")}}
    if is_wall and not isinstance(detailed, tuple):
        state["optional_properties"]["axis"] = _optional(lambda: read.native("WallProperties.Axis.repr",
                                                          lambda: _representation(props.Axis)), check, "material_axis")
    identify(state)
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


def preview_observation(base, element, check=lambda: None, *, trace=None, trace_ref=None, preservation=True,
                        field="Material"):
    """Separate a readable material string from eligibility to preserve the Wall.

    Eligibility requires the native property owner and available setters.
    Native exception messages and representations are never returned on failure.
    """
    value = {}
    try:
        material, state, _, _ = snapshot(base, element, check, material_observation=value,
                                       trace=trace, trace_ref=trace_ref, preservation=preservation, field=field)
        return {"status": "observed", "value": material}, state, {"status": "observed", "value": True}
    except BridgeError:
        raise
    except Exception as exc:
        blocked = failure(exc, "wall_material_validation")
        return value or blocked, None, blocked


def _valid_calculation_change(change):
    """CalculationMode: one documented code to another on a reviewed owner (0.49.0)."""
    resource = change.get("resource") or {}
    evidence = resource.get("native_property_state")
    if (not isinstance(evidence, dict) or not _supported_lineage(evidence.get("hierarchy"))
            or "native_material_state" in resource or "exact_target_binding" in resource):
        return False
    target = evidence["hierarchy"]["target"]
    ref = change.get("ref") or {}
    kind = change.get("native_type")
    class_name = evidence.get("native_class")
    old, new = change.get("old_value") or {}, change.get("new_value")
    return (change.get("field") == "native.calculation_mode" and change.get("property_role") == "native_property"
            and kind in CALCULATION_MODE_TYPES and class_name in _NATIVE_CLASSES[kind]
            and resource.get("data_type") == "integer"
            and resource.get("binding") == "sdk_calculation_mode_code"
            and resource.get("mirror_attribute_id") == CALCULATION_MODE_MIRROR_ATTRIBUTE
            and type(new) is int and new in CALCULATION_MODE_CODES
            and resource.get("new_label") == CALCULATION_MODE_CODES[new]
            and old.get("status") == "observed" and type(old.get("value")) is int
            and old["value"] in CALCULATION_MODE_CODES and old["value"] != new
            and evidence.get("schema_version") == _CALCULATION_STATE_SCHEMA
            and evidence.get("native_field") == "CalculationMode"
            and evidence.get("material_owner") == _MATERIAL_OWNERS[class_name]
            and evidence["hierarchy"]["lineage"] == [target]
            and (kind != "Wall_TypeUUID" or evidence.get("tier_count") == 1)
            and all(target.get(key) == ref.get(key) for key in ("drawing_file", "model_uuid", "type_uuid"))
            and target.get("type_name") == kind
            and target.get("view_uuid") == change.get("target_view_uuid"))


def valid_change(change):
    if change.get("operation") == CALCULATION_MODE_OPERATION:
        return _valid_calculation_change(change)
    resource = change.get("resource") or {}
    evidence = resource.get("native_material_state")
    if not isinstance(evidence, dict) or not _supported_lineage(evidence.get("hierarchy")):
        return False
    target = evidence["hierarchy"]["target"]
    ref = change.get("ref") or {}
    kind = change.get("native_type")
    class_name = (evidence or {}).get("native_class")
    exact = resource.get("exact_target_binding")
    if exact is not None:
        # 0.43.0 adds an optional bounded inventory summary for post-setter
        # drift diagnosis; journals from 0.42.x carry only the fingerprint.
        if (not isinstance(exact, dict)
                or set(exact) - {"inventory_summary"} != {"target", "inventory_fingerprint"}):
            return False
        if "inventory_summary" in exact:
            from .exact_material_target import valid_inventory_summary
            if not valid_inventory_summary(exact["inventory_summary"]):
                return False
        hint = exact.get("target")
        if not isinstance(hint, dict) or not isinstance(hint.get("parent_ref"), dict):
            return False
        lineage = evidence["hierarchy"]["lineage"]
        if (kind != "Slab_TypeUUID" or len(lineage) != 2
                or any(hint.get(key) != target.get(key) for key in ("drawing_file", "model_uuid", "view_uuid"))
                or any(hint["parent_ref"].get(key) != lineage[1].get(key) for key in ("model_uuid", "view_uuid"))
                or not isinstance(exact["inventory_fingerprint"], str)
                or len(exact["inventory_fingerprint"]) != 64):
            return False
    return (change.get("operation") == "set_native_material" and kind in _NATIVE_CLASSES
            and change.get("field") == "native.material" and change.get("property_role") == "native_material"
            and resource.get("tier_index") == 1 and resource.get("data_type") == "text"
            and type(resource.get("tier_index")) is int
            and type(change.get("new_value")) is str and 0 < len(change["new_value"]) <= 255
            and bool(change["new_value"].strip()) and not any(ord(c) < 32 for c in change["new_value"])
            and change.get("old_value", {}).get("status") == "observed"
            and type(change["old_value"].get("value")) is str
            and isinstance(evidence, dict) and evidence.get("schema_version") == _STATE_SCHEMA
            and class_name in _NATIVE_CLASSES[kind]
            and evidence.get("material_owner") == _MATERIAL_OWNERS[class_name]
            and _supported_lineage(evidence["hierarchy"])
            and (kind != "Wall_TypeUUID" or evidence.get("tier_count") == 1)
            and all(target.get(key) == ref.get(key) for key in ("drawing_file", "model_uuid", "type_uuid"))
            and target.get("type_name") == kind
            and target.get("view_uuid") == change.get("target_view_uuid"))


def bound_owner(state, change):
    """Required ownership must match independently of optional preservation."""
    expected = change["resource"][state_key(change)]
    return (state is not None and _supported_lineage(state.get("hierarchy"))
            and state.get("schema_version") == expected.get("schema_version")
            and state.get("native_field") == expected.get("native_field")
            and state.get("native_class") == expected.get("native_class")
            and state.get("material_owner") == expected.get("material_owner")
            and state.get("tier_count") == expected.get("tier_count")
            and [_identity_key(ref) for ref in state["hierarchy"]["lineage"]]
                == [_identity_key(ref) for ref in expected["hierarchy"]["lineage"]])


def read(base, element, change, check=lambda: None, *, preservation=True,
         post_setter=False, accepted=None):
    """Read the bound native material and compare preservation evidence.

    ``post_setter`` is set only by the fresh readback/recovery path after a
    setter. Only there may the family-specific regeneration of auxiliary
    children be accepted; ``accepted`` then receives the bounded report.
    Preflight and the final setter boundary stay byte-exact.
    """
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Native material requires an exact reviewed architectural property owner.", 409)
    field = field_for(change)
    material = field == "Material"
    expected = change["resource"][state_key(change)]
    value, state, _ = preview_observation(base, element, check, preservation=preservation, field=field)
    if not bound_owner(state, change):
        return {"status": "not_checked", "value": None,
                "reason": "native_material_owner_unavailable" if material else "native_property_owner_unavailable"}
    if preservation and fingerprint(state) != fingerprint(expected):
        sections = sorted(key for key in set(expected) | set(state) if expected.get(key) != state.get(key))
        report = {"before_sha256": fingerprint(expected), "current_sha256": fingerprint(state),
                  "changed_sections": sections}
        if "component_tree" in sections:
            report["component_tree_diff"] = component_tree_diff(expected.get("component_tree"),
                                                                state.get("component_tree"))
            # The Beam native Material acceptance keeps its 0.44.2 rule.
            if post_setter and material and regenerated_auxiliary_children(change["native_type"], expected, state):
                if accepted is not None:
                    accepted.update(report, accepted=REGENERATED_CHILDREN_ACCEPTANCE)
                return value
        report["identity_diff"] = identity_diff(expected, state)
        # 0.50.0 (CalculationMode), 0.51.0 (Material): accept only a renaming
        # of the family's observed regenerated identities; every other byte
        # of the bound evidence must be equal after that renaming.
        regeneration = (identity_regeneration(change["native_type"], field, expected, state)
                        if post_setter else None)
        if regeneration is not None:
            if accepted is not None:
                accepted.update(report, accepted=IDENTITY_REGENERATION_ACCEPTANCE, **regeneration)
            return value
        if post_setter and report["identity_diff"].get("status") == "observed" and (
                report["identity_diff"]["removed"]["count"] or report["identity_diff"]["added"]["count"]):
            # 0.51.1: the 0.51.0 window-Wall trial renamed only listed types
            # yet stayed unknown; name what else differs for the next review.
            report["regeneration_residual"] = identity_regeneration_residual(expected, state)
        # The Wall-specific reason predates Beam/Column/Slab support; keep it
        # for Walls so earlier journals and reports read the same.
        if not material:
            return {"status": "not_checked", "value": None, "reason": "native_property_invariants_changed",
                    "native_readback": value, "preservation": report}
        reason = ("wall_material_invariants_changed" if change["native_type"] == "Wall_TypeUUID"
                  else "native_material_invariants_changed")
        return {"status": "not_checked", "value": None, "reason": reason,
                "material_readback": value, "preservation": report}
    return value


def mirror_crosscheck(base, element, change, ident=CALCULATION_MODE_MIRROR_ATTRIBUTE):
    """Read the candidate attribute mirror of a native property (no setter).

    Reported next to the native readback, never folded into it: a diverging
    attribute 120 (or 508 beside native Material, 0.51.0) is review evidence
    and is not accepted automatically in either direction.
    """
    from .native_model_edit import attribute_fields
    observation = attribute_fields(element, base, [ident], "all_and_computable")[f"attribute:{ident}"]
    return {"attribute_id": ident, "observation": observation}


def mirror_summary(change, rows):
    """Bounded verdict over per-view attribute 120 reads; review evidence only."""
    old, new = change["old_value"]["value"], change["new_value"]
    labels = {"old_label": CALCULATION_MODE_CODES.get(old), "new_label": CALCULATION_MODE_CODES.get(new)}
    values = [row["observation"].get("value") for row in rows
              if isinstance(row, dict) and row.get("observation", {}).get("status") == "observed"]
    if not rows or len(values) != len(rows):
        verdict = "unavailable"
    elif len({json.dumps(value, sort_keys=True) for value in values}) != 1:
        verdict = "representations_disagree"
    elif values[0] == labels["new_label"]:
        verdict = "matches_new_label"
    elif values[0] == labels["old_label"]:
        verdict = "matches_old_label"
    else:
        verdict = "other_value"
    return {"attribute_id": CALCULATION_MODE_MIRROR_ATTRIBUTE, **labels,
            "values": values[:8], "verdict": verdict,
            "acceptance": "owner_review_required_not_part_of_readback",
            "decides": "whether_attribute_120_mirrors_native_calculation_mode"}


MAX_TREE_DIFF_ITEMS = 4


def _tree_key(ref):
    return "|".join(str(ref.get(key)) for key in ("type_name", "model_uuid", "view_uuid"))


def component_tree_diff(expected, current):
    """Name what changed in a bounded component tree; never judge benignness.

    ModifyElements may regenerate auxiliary children (0.43.0 Slab, 0.44.1
    Beam trials). This diff is review evidence for the existing reconciliation
    path only: it does not verify preservation or authorize a setter.
    """
    def tree(value):
        return value if isinstance(value, dict) and isinstance(value.get("target"), dict) else None

    expected, current = tree(expected), tree(current)
    if expected is None or current is None:
        return {"status": "not_checked", "expected_observed": expected is not None,
                "current_observed": current is not None}

    def refs(value, name):
        return {_tree_key(ref) for ref in value.get(name) or [] if isinstance(ref, dict)}

    def edges(value):
        return {_tree_key(edge.get("child") or {}) + ">" + _tree_key(edge.get("parent") or {})
                for edge in value.get("child_parent_edges") or [] if isinstance(edge, dict)}

    def listed(values):
        values = sorted(values)
        return {"count": len(values), "items": values[:MAX_TREE_DIFF_ITEMS],
                "truncated": len(values) > MAX_TREE_DIFF_ITEMS}

    def by_type(values):
        counts = {}
        for value in values:
            name = value.split("|", 1)[0]
            counts[name] = counts.get(name, 0) + 1
        return counts

    before, after = refs(expected, "children"), refs(current, "children")
    removed, added = by_type(before - after), by_type(after - before)
    root = {name: {"expected": _tree_key(expected[name]), "current": _tree_key(current[name])}
            for name in ("target", "terminal_root")
            if isinstance(expected.get(name), dict) and isinstance(current.get(name), dict)
            and _tree_key(expected[name]) != _tree_key(current[name])}
    flags = {name: {"expected": expected.get(name), "current": current.get(name)}
             for name in ("parent_chain_complete", "children_complete")
             if expected.get(name) != current.get(name)}
    return {"status": "observed", "root_changes": root, "flag_changes": flags,
            "lineage_changed": refs(expected, "lineage") != refs(current, "lineage"),
            "child_type_changes": {name: {"removed": removed.get(name, 0), "added": added.get(name, 0)}
                                   for name in sorted(set(removed) | set(added))},
            "children_removed": listed(before - after), "children_added": listed(after - before),
            "edges_removed": listed(edges(expected) - edges(current)),
            "edges_added": listed(edges(current) - edges(expected))}


REGENERATED_CHILDREN_ACCEPTANCE = "auxiliary_children_regenerated"

# Child types that ModifyElements replaces with new model UUIDs when the
# native Material setter runs, per family. Native evidence: Beam 0.44.1 and
# 0.44.2 (only these children regenerated, readback and UI showed the new
# value, UI Undo restored the original children). No other family is listed
# without equivalent evidence.
REGENERABLE_CHILD_TYPES = {
    "Beam_TypeUUID": frozenset({"AttributeContainer_TypeUUID", "WallAxis_TypeUUID"}),
}


def regenerated_auxiliary_children(native_type, expected, current):
    """True only if the sole drift is a one-for-one regeneration of listed children.

    Every other state section, the root, lineage, completeness flags and the
    per-type child counts must be identical, and every removed/added child
    must hang directly off the unchanged target root.
    """
    allowed = REGENERABLE_CHILD_TYPES.get(native_type)
    if not allowed or not isinstance(expected, dict) or not isinstance(current, dict):
        return False
    if set(expected) != set(current) or any(expected[key] != current[key]
                                            for key in expected if key != "component_tree"):
        return False
    before, after = expected.get("component_tree"), current.get("component_tree")
    if not isinstance(before, dict) or not isinstance(after, dict) or set(before) != set(after):
        return False
    if any(before[key] != after[key] for key in before if key not in ("children", "child_parent_edges")):
        return False
    if before.get("children_complete") is not True or before.get("parent_chain_complete") is not True:
        return False

    def children(tree):
        items = tree.get("children")
        if not isinstance(items, list) or not all(isinstance(ref, dict) for ref in items):
            return None
        return items

    def edges(tree):
        items = tree.get("child_parent_edges")
        if not isinstance(items, list) or not all(
                isinstance(edge, dict) and isinstance(edge.get("child"), dict)
                and isinstance(edge.get("parent"), dict) for edge in items):
            return None
        return {(_tree_key(edge["child"]), _tree_key(edge["parent"])) for edge in items}

    old_children, new_children = children(before), children(after)
    old_edges, new_edges = edges(before), edges(after)
    if None in (old_children, new_children, old_edges, new_edges):
        return False
    old_keys = {_tree_key(ref) for ref in old_children}
    new_keys = {_tree_key(ref) for ref in new_children}
    if len(old_keys) != len(old_children) or len(new_keys) != len(new_children):
        return False
    removed, added = old_keys - new_keys, new_keys - old_keys
    if not removed or not added:
        return False

    def types(keys):
        counts = {}
        for key in keys:
            name = key.split("|", 1)[0]
            counts[name] = counts.get(name, 0) + 1
        return counts

    if types(removed) != types(added) or not set(types(removed)) <= allowed:
        return False
    root = _tree_key(before["target"])
    changed = removed | added
    # Unchanged children keep their exact edges; each regenerated child has
    # exactly one edge, to the unchanged reviewed root.
    if {edge for edge in old_edges if edge[0] not in changed} != {
            edge for edge in new_edges if edge[0] not in changed}:
        return False
    return ({edge for edge in old_edges if edge[0] in changed} == {(key, root) for key in removed}
            and {edge for edge in new_edges if edge[0] in changed} == {(key, root) for key in added})


IDENTITY_REGENERATION_ACCEPTANCE = "identities_regenerated_evidence_otherwise_equal"

# Identities that ModifyElements replaced after a native property setter,
# per family. The renaming is a property of the family's ModifyElements, not
# of the written field: the same sets appear for both bound native fields.
# - Column (CalculationMode, 0.49.0/0.50.0): the AttributeContainer child and
#   the reviewed root view (cc752bda… -> 8f88036e…, restored by UI Undo);
#   model UUID unchanged.
# - Beam: the AttributeContainer and WallAxis children (CalculationMode
#   0.50.0; the same pair as the Beam Material regeneration of 0.44.1/0.44.2).
# - Wall: root/tier attribute containers and the tier's WallAxis/WallAxisLine
#   (CalculationMode 0.50.0, Wall 240).
# - Wall with a door (CalculationMode 0.50.0, execution bd30912a…): also the
#   Door and its DoorSill; the DoorTier and DoorReveal kept their identities
#   and geometry streams. The bound evidence with exactly these four UUID
#   pairs renamed hashed to the post-setter evidence, and UI Undo restored the
#   preflight evidence byte for byte.
# - Wall Material (0.50.1 trial, executions 9ed2e229… on Wall 240 and
#   37196703… on the Wall with door): the native value was reached (owner UI
#   check, UI Undo) and the changed sections were exactly those of the
#   accepted CalculationMode renamings of the same walls; 0.50.1 did not log
#   the Material identity_diff, so 0.51.0 applies the same rule to Material.
# - Wall with a window (0.51.0, not yet observed natively): by analogy with
#   the door, the Window, its Sill and the WindowOpeningSmartPart (child of
#   the WindowReveal, 0.50.1 query) may be renamed; the WindowTier and
#   WindowReveal must keep their identities.
# Column Material uses the Column rule (not yet observed natively). Every
# other byte of the bound evidence must be equal after the renaming, so an
# unlisted or wrong regeneration stays `unknown` with identity_diff.
_WALL_REGENERATED = frozenset({"AttributeContainer_TypeUUID", "WallAxis_TypeUUID", "WallAxisLine_TypeUUID",
                               "Door_TypeUUID", "DoorSill_TypeUUID",
                               "Window_TypeUUID", "Sill_TypeUUID", "WindowOpeningSmartPart_TypeUUID"})
_FAMILY_REGENERATION = {
    "Column_TypeUUID": {"children": frozenset({"AttributeContainer_TypeUUID"}), "root_view": True},
    "Beam_TypeUUID": {"children": frozenset({"AttributeContainer_TypeUUID", "WallAxis_TypeUUID"}),
                      "root_view": False},
    "Wall_TypeUUID": {"children": _WALL_REGENERATED, "root_view": False},
}
IDENTITY_REGENERATION = {(field, family): rule for family, rule in _FAMILY_REGENERATION.items()
                         for field in ("CalculationMode", "Material")}
_MAX_IDENTITY_REFS = 4096
_MAX_REGENERATED_PER_TYPE = 4
_MAX_PAIRINGS = 64


def _identity_refs(value, found=None, depth=0):
    """Every ref-shaped dict (type_name, model_uuid, view_uuid) in bounded state evidence."""
    found = set() if found is None else found
    if depth > 32 or len(found) > _MAX_IDENTITY_REFS:
        raise ValueError("identity evidence over limit")
    if isinstance(value, dict):
        if all(isinstance(value.get(key), str) for key in ("type_name", "model_uuid", "view_uuid")):
            found.add((value["type_name"], value["model_uuid"], value["view_uuid"]))
        for item in value.values():
            _identity_refs(item, found, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _identity_refs(item, found, depth + 1)
    return found


def identity_diff(expected, current):
    """Bounded report of identities that disappeared/appeared; review evidence only."""
    try:
        before, after = _identity_refs(expected), _identity_refs(current)
    except ValueError:
        return {"status": "not_checked", "reason": "identity_evidence_over_limit"}

    def listed(values):
        values = sorted("|".join(item) for item in values)
        return {"count": len(values), "items": values[:MAX_TREE_DIFF_ITEMS * 2],
                "truncated": len(values) > MAX_TREE_DIFF_ITEMS * 2}

    return {"status": "observed", "removed": listed(before - after), "added": listed(after - before)}


def _rename(value, mapping):
    if isinstance(value, dict):
        return {_rename(key, mapping): _rename(item, mapping) for key, item in value.items()}
    if isinstance(value, list):
        return [_rename(item, mapping) for item in value]
    if isinstance(value, str):
        for old, new in mapping.items():
            if old in value:
                value = value.replace(old, new)
        return value
    return value


def _canonical(value, key=None):
    """Order-normalize identity-sorted collections after a renaming.

    Producers sort children, edges and container snapshots by identity, so a
    renamed identity can move. Lineage keeps its order (child -> root).
    """
    if isinstance(value, dict):
        return {name: _canonical(item, name) for name, item in value.items()}
    if isinstance(value, list):
        items = [_canonical(item) for item in value]
        if key != "lineage" and items and all(isinstance(item, dict) for item in items):
            items.sort(key=fingerprint)
        return items
    return value


def identity_regeneration(native_type, field, expected, current):
    """Accept drift that is only a renaming of listed regenerated identities.

    Returns the renaming report, or None. The reviewed root model UUID and
    type never change; a root view may change only where the family lists it.
    Each removed identity pairs one-for-one with an added identity of the
    same type, and the expected evidence with every such UUID renamed must be
    byte-identical to the current evidence (fingerprint).
    """
    from itertools import permutations, product

    rule = IDENTITY_REGENERATION.get((field, native_type))
    if rule is None or not isinstance(expected, dict) or not isinstance(current, dict):
        return None
    try:
        before, after = _identity_refs(expected), _identity_refs(current)
    except ValueError:
        return None
    removed, added = before - after, after - before
    if not removed or len(removed) != len(added):
        return None
    groups = {}
    for side, items in (("removed", removed), ("added", added)):
        for item in items:
            groups.setdefault(item[0], {"removed": [], "added": []})[side].append(item)
    for type_name, group in groups.items():
        group["removed"].sort()
        group["added"].sort()
        if len(group["removed"]) != len(group["added"]) or len(group["removed"]) > _MAX_REGENERATED_PER_TYPE:
            return None
        if type_name == native_type:
            if (not rule["root_view"] or len(group["removed"]) != 1
                    or group["removed"][0][1] != group["added"][0][1]):
                return None
        elif type_name not in rule["children"]:
            return None
    names = sorted(groups)
    options = [list(permutations(groups[name]["added"])) for name in names]
    combinations = 1
    for choice in options:
        combinations *= len(choice)
    if combinations > _MAX_PAIRINGS:
        return None
    target = fingerprint(_canonical(current))
    remaining = {value for ref in after for value in ref[1:]}
    for selection in product(*options):
        mapping, pairs, valid = {}, [], True
        for name, chosen in zip(names, selection):
            for old, new in zip(groups[name]["removed"], chosen):
                pairs.append({"type_name": name, "old_model_uuid": old[1], "new_model_uuid": new[1],
                              "old_view_uuid": old[2], "new_view_uuid": new[2]})
                for old_id, new_id in ((old[1], new[1]), (old[2], new[2])):
                    if old_id == new_id:
                        continue
                    if mapping.get(old_id, new_id) != new_id or old_id in remaining:
                        valid = False
                    mapping[old_id] = new_id
        if not valid or not mapping:
            continue
        if fingerprint(_canonical(_rename(expected, mapping))) == target:
            root_views = {pair["old_view_uuid"]: pair["new_view_uuid"]
                          for pair in pairs if pair["type_name"] == native_type}
            return {"regenerated_identities": sorted(pairs, key=lambda p: (p["type_name"], p["old_model_uuid"]))[:16],
                    "view_map": root_views}
    return None


_MAX_RESIDUAL_PATHS = 8
_MAX_RESIDUAL_SCALAR = 96


def _keyed(items):
    """Identity-keyed list items (component snapshots, refs, edges), or None."""
    keyed = {}
    for item in items:
        if not isinstance(item, dict):
            return None
        ref = (item.get("ownership") or {}).get("target") if isinstance(item.get("ownership"), dict) else None
        ref = ref or item.get("target") or item.get("child") or item
        if not isinstance(ref, dict) or not isinstance(ref.get("type_name"), str) \
                or not isinstance(ref.get("model_uuid"), str):
            return None
        key = ref["type_name"] + "|" + ref["model_uuid"]
        if "parent" in item and isinstance(item["parent"], dict):
            key += ">" + str(item["parent"].get("model_uuid"))
        if key in keyed:
            return None
        keyed[key] = item
    return keyed


def _residual_paths(before, after, path, found):
    if len(found) > _MAX_RESIDUAL_PATHS:
        return
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before) | set(after)):
            if key not in before or key not in after:
                found.append({"path": path + "/" + str(key),
                              "difference": "added" if key not in before else "removed"})
            elif before[key] != after[key]:
                _residual_paths(before[key], after[key], path + "/" + str(key), found)
        return
    if isinstance(before, list) and isinstance(after, list):
        left, right = _keyed(before), _keyed(after)
        if left is not None and right is not None:
            # Pair components by identity so one difference is not reported
            # as a shifted list position.
            for key in sorted(set(left) | set(right)):
                if key not in left or key not in right:
                    found.append({"path": path + "/[" + key + "]",
                                  "difference": "added" if key not in left else "removed"})
                elif left[key] != right[key]:
                    _residual_paths(left[key], right[key], path + "/[" + key + "]", found)
            return
        if len(before) != len(after):
            found.append({"path": path, "difference": "length", "before": len(before), "after": len(after)})
            return
        for index, (left, right) in enumerate(zip(before, after)):
            if left != right:
                _residual_paths(left, right, path + "/" + str(index), found)
        return
    row = {"path": path, "difference": "value"}
    for name, value in (("before", before), ("after", after)):
        if value is None or isinstance(value, (bool, int, float)) or (
                isinstance(value, str) and len(value) <= _MAX_RESIDUAL_SCALAR):
            row[name] = value
    found.append(row)


def identity_regeneration_residual(expected, current):
    """Where the evidence still differs after renaming same-type identities.

    Review evidence for an `unknown` outcome only (0.51.1): identities of one
    type are paired in sorted order, the expected evidence is renamed and the
    first differing paths are listed. It never accepts drift.
    """
    if not isinstance(expected, dict) or not isinstance(current, dict):
        return {"status": "not_checked", "reason": "evidence_unavailable"}
    try:
        before, after = _identity_refs(expected), _identity_refs(current)
    except ValueError:
        return {"status": "not_checked", "reason": "identity_evidence_over_limit"}
    groups = {}
    for side, items in (("removed", before - after), ("added", after - before)):
        for item in sorted(items):
            groups.setdefault(item[0], {"removed": [], "added": []})[side].append(item)
    mapping, unpaired = {}, []
    for name in sorted(groups):
        removed, added = groups[name]["removed"], groups[name]["added"]
        if len(removed) != len(added):
            unpaired.append({"type_name": name, "removed": len(removed), "added": len(added)})
        for old, new in zip(removed, added):
            for old_id, new_id in ((old[1], new[1]), (old[2], new[2])):
                if old_id != new_id:
                    mapping.setdefault(old_id, new_id)
    found = []
    _residual_paths(_canonical(_rename(expected, mapping)), _canonical(current), "", found)
    return {"status": "observed", "pairing": "same_type_sorted_order", "unpaired_types": unpaired[:8],
            "paths": found[:_MAX_RESIDUAL_PATHS], "truncated": len(found) > _MAX_RESIDUAL_PATHS,
            "acceptance": "review_evidence_only"}


def write(base, element, change, doc=None, check=lambda: None, *, trace=None):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Native material change is not bound.", 409)
    exact = (change.get("resource") or {}).get("exact_target_binding")
    if exact is not None:
        from .exact_material_target import locate
        # Repeat inventory/edge validation at the final mutation boundary.
        # The facade retains enumeration containers through snapshot/setter.
        base, _ = locate(doc if doc is not None else element.GetDocument(), base,
                         exact["target"], check, trace, expected=exact["inventory_fingerprint"])
    field = field_for(change)
    material, state, native, props = snapshot(base, element, check, field=field)
    if state != change["resource"][state_key(change)] or material != change["old_value"]["value"]:
        raise BridgeError("repair_conflict", "Wall material or preservation evidence changed before setter."
                          if field == "Material" else
                          "CalculationMode or preservation evidence changed before setter.", 409)
    if doc is None:
        doc = element.GetDocument()
    from .model_delete import final_write_guard
    final_write_guard(base, element, change, doc, check)
    owner = props.GetWallTierProperties(1) if change["native_type"] == "Wall_TypeUUID" else props
    getattr(owner, _FIELDS[field]["setter"])(change["new_value"])
    _, setter_name = _property_accessors(state["native_class"])
    getattr(native, setter_name)(props)
    check()
    return base.ModifyElements(doc, [native])
