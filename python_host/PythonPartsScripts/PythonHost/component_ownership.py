"""Bounded adapter lineage evidence; geometry never establishes ownership."""
from __future__ import annotations

from .model_context import boolean, guid, integer, text
from .query_contracts import fingerprint
from .transport import BridgeError


def identity(adapter, *, trace=None):
    def read(api, callback):
        return trace(api, callback) if trace is not None else callback()

    signed = integer(read("BaseElementAdapter.GetDrawingfileNumber", adapter.GetDrawingfileNumber))
    if signed == 0:
        raise ValueError("Missing drawing-file identity")
    native_type = read("BaseElementAdapter.GetElementAdapterType", adapter.GetElementAdapterType)
    return {"drawing_file": abs(signed), "signed_drawing_file": signed,
            "model_uuid": guid(read("BaseElementAdapter.GetModelElementUUID", adapter.GetModelElementUUID)),
            "view_uuid": guid(read("BaseElementAdapter.GetElementUUID", adapter.GetElementUUID)),
            "type_name": text(read("ElementAdapterType.GetTypeName", native_type.GetTypeName)),
            "type_uuid": guid(read("ElementAdapterType.GetGuid", native_type.GetGuid))}


def same_model_identity(left, right):
    """Compare a structural owner, without conflating its view wrappers.

    This is only for SDK parent/child edges. Exact target selection and the
    evidence fingerprint still include every observed view UUID.
    """
    keys = ("drawing_file", "signed_drawing_file", "model_uuid", "type_name", "type_uuid")
    return all(left[key] == right[key] for key in keys)


def model_identity_key(ref):
    return tuple(ref[key] for key in ("drawing_file", "signed_drawing_file", "model_uuid"))


class ComponentReadError(ValueError):
    """Bounded failure labels; native exception messages never enter reports."""
    def __init__(self, stage, reason, error_type="ValueError", *, evidence=None):
        super().__init__(reason)
        self.stage, self.reason, self.error_type = stage, reason, error_type
        self.evidence = evidence


def failure(exc, stage="component_ownership"):
    result = {"status": "not_checked", "value": None,
            "reason": exc.reason if isinstance(exc, ComponentReadError) else type(exc).__name__,
            "diagnostic": {"stage": exc.stage if isinstance(exc, ComponentReadError) else stage,
                           "error_type": exc.error_type if isinstance(exc, ComponentReadError) else type(exc).__name__}}
    if isinstance(exc, ComponentReadError) and exc.evidence is not None:
        result["diagnostic"]["evidence"] = exc.evidence
    return result


def observe(adapter, check=lambda: None, *, include_children=True, trace=None):
    """Read exact ancestry/direct children; no writable property owner is inferred."""
    import NemAll_Python_IFW_ElementAdapter as adapters

    def read(stage, callback, *, api=None):
        check()
        try:
            value = trace(api or "Component." + stage, callback) if trace is not None else callback()
        except (BridgeError, ComponentReadError):
            raise
        except Exception as exc:
            raise ComponentReadError(stage, "component_read_unavailable", type(exc).__name__) from exc
        check()
        return value

    target = read("target_identity", lambda: identity(adapter, trace=trace))
    lineage, seen, retained = [target], {model_identity_key(target)}, [adapter]
    current = adapter
    for _ in range(16):
        parent = read("parent", lambda: adapters.BaseElementAdapterParentElementService.GetParentElement(current),
                      api="BaseElementAdapterParentElementService.GetParentElement")
        retained.append(parent)
        if read("parent", lambda: boolean(parent.IsNull()), api="BaseElementAdapter.IsNull"):
            break
        ref = read("parent_identity", lambda: identity(parent, trace=trace))
        if ref["signed_drawing_file"] != target["signed_drawing_file"]:
            raise ComponentReadError("parent_identity", "component_cross_file")
        if model_identity_key(ref) in seen:
            raise ComponentReadError("parent_identity", "component_parent_cycle")
        seen.add(model_identity_key(ref))
        lineage.append(ref)
        current = parent
    else:
        raise ComponentReadError("parent", "component_parent_limit")
    children, child_parent_edges, child_models = {}, [], set()
    if include_children:
        owner = read("children", lambda: adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True),
                     api="BaseElementAdapterChildElementsService.GetChildModelElements")
        retained.append(owner)
        for index, child in enumerate(owner):
            check()
            if index >= 256:
                raise ComponentReadError("children", "component_child_limit")
            child_ref = read("child_identity", lambda: identity(child, trace=trace))
            if child_ref["signed_drawing_file"] != target["signed_drawing_file"]:
                raise ComponentReadError("child_identity", "component_cross_file")
            parent = read("child_parent", lambda: adapters.BaseElementAdapterParentElementService.GetParentElement(child),
                          api="BaseElementAdapterParentElementService.GetParentElement")
            retained.append(parent)
            if read("child_parent", lambda: boolean(parent.IsNull()), api="BaseElementAdapter.IsNull"):
                raise ComponentReadError("child_parent_identity", "component_child_owner_mismatch",
                                         evidence={"target": target, "child": child_ref, "observed_parent": None})
            parent_ref = read("child_parent_identity", lambda: identity(parent, trace=trace))
            if not same_model_identity(parent_ref, target) or model_identity_key(child_ref) in seen:
                raise ComponentReadError("child_parent_identity", "component_child_owner_mismatch",
                                         evidence={"target": target, "child": child_ref, "observed_parent": parent_ref})
            child_key = model_identity_key(child_ref)
            if child_key in child_models:
                raise ComponentReadError("child_identity", "component_child_identity_ambiguous")
            child_models.add(child_key)
            children[fingerprint(child_ref)] = child_ref
            child_parent_edges.append({"child": child_ref, "parent": parent_ref})
    check()
    return {"schema_version": "m4-component-ownership-1", "target": target,
            "lineage": lineage, "terminal_root": lineage[-1],
            "parent_chain_complete": True, "children_complete": include_children,
            "children": sorted(children.values(), key=fingerprint),
            "child_parent_edges": sorted(child_parent_edges, key=fingerprint),
            "property_owner": "not_established", "physical_target_equivalence": "not_established"}


def observation(adapter, check=lambda: None, *, include_children=True):
    try:
        return {"status": "observed", "value": observe(adapter, check, include_children=include_children)}
    except BridgeError:
        raise
    except Exception as exc:
        return failure(exc)


# 0.49.0 rename (owner decision 2026-11-04): the tier IS shown in the UI, in
# the slab palette's "Warstwa bieżąca" mode. A plain slab request targets
# "Cały obiekt" (the MultiSlab); the tier needs an explicit layer request
# through exact_target. The 0.47.0 name stated the wrong premise.
TIER_NOT_UI_OWNER = "slab_tier_requires_exact_layer_target"
TIER_BLOCKERS = frozenset({TIER_NOT_UI_OWNER, "slab_has_parent_requires_explicit_property_owner"})


def slab_ui_owner(evidence):
    """The MultiSlab ("Cały obiekt", the default slab owner) of a tier, or None.

    This is a hint for a separate preview, never a write redirection: the
    caller must request the MultiSlab itself. The tier is shown as
    "Warstwa bieżąca" and is changed only when the request names the layer.
    """
    value = evidence.get("value") if isinstance(evidence, dict) and evidence.get("status") == "observed" else None
    lineage = value.get("lineage") if isinstance(value, dict) else None
    if (not isinstance(lineage, list) or len(lineage) != 2 or not all(isinstance(ref, dict) for ref in lineage)
            or lineage[0].get("type_name") != "Slab_TypeUUID" or lineage[1].get("type_name") != "MultiSlab_TypeUUID"):
        return None
    parent = lineage[1]
    return {"drawing_file": parent.get("drawing_file"), "model_uuid": parent.get("model_uuid"),
            "view_uuid": parent.get("view_uuid"), "type_name": "MultiSlab_TypeUUID",
            "ui_mode": "Cały obiekt",
            "tier_ui_mode": "Warstwa bieżąca",
            "tier_route": "only when the request names the layer: exact_target with the tier's parent_ref",
            "next_preview": {"native_types": ["MultiSlab_TypeUUID"],
                             "target": {"property_owner": "selected_element"},
                             "check": "the plan change ref.model_uuid equals this model_uuid; "
                                      "exclude other MultiSlabs with exclude_model_uuids"}}


def slab_write_blocker(evidence, change=None):
    """No automatic redirection from slab tiers or aggregates to a field owner."""
    if not isinstance(evidence, dict) or evidence.get("status") != "observed":
        return "slab_ownership_unavailable"
    value = evidence.get("value")
    if not isinstance(value, dict):
        return "slab_ownership_unavailable"
    lineage, target = value.get("lineage"), value.get("target")
    if (value.get("parent_chain_complete") is not True or not isinstance(lineage, list) or not lineage
            or any(not isinstance(ref, dict) for ref in lineage)
            or not isinstance(target, dict) or target.get("type_name") not in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}
            or lineage[0] != target or value.get("terminal_root") != lineage[-1]):
        return "slab_ownership_unavailable"
    resource = (change or {}).get("resource") or {}
    if resource.get("property_owner") == "selected_element":
        # This is an explicit adapter target for ChangeAttributes, not an
        # inference that the aggregate and its tiers are interchangeable.
        ref = change.get("ref") or {}
        if (change.get("operation") not in {"set_attribute", "add_attribute"}
                or change.get("native_type") != target["type_name"]
                or any(target.get(key) != ref.get(key) for key in ("drawing_file", "model_uuid", "type_uuid"))
                or target.get("view_uuid") != change.get("target_view_uuid")
                or value.get("children_complete") is not True
                or (len(lineage) != 1 and not (len(lineage) == 2
                    and target["type_name"] == "Slab_TypeUUID"
                    and lineage[1].get("type_name") == "MultiSlab_TypeUUID"))):
            return "slab_explicit_property_owner_invalid"
        if len(lineage) == 2:
            # The tier stores its own attributes (0.46.0) and the UI shows them
            # in the "Warstwa bieżąca" palette mode (owner, 2026-11-04). Plain
            # slab requests target the MultiSlab ("Cały obiekt"); a tier write
            # needs an explicit layer request with exact_target on the tier's
            # parent-edge view (0.47.0 route).
            exact = resource.get("exact_target_binding")
            target_binding = exact.get("target") if isinstance(exact, dict) else None
            parent = lineage[1]
            if (not isinstance(target_binding, dict)
                    or target_binding.get("model_uuid") != target.get("model_uuid")
                    or target_binding.get("view_uuid") != target.get("view_uuid")
                    or target_binding.get("parent_ref") != {"model_uuid": parent.get("model_uuid"),
                                                            "view_uuid": parent.get("view_uuid")}):
                return TIER_NOT_UI_OWNER
        return None
    if "property_owner" in resource:
        return "slab_explicit_property_owner_invalid"
    if len(lineage) != 1:
        return "slab_has_parent_requires_explicit_property_owner"
    if target["type_name"] == "MultiSlab_TypeUUID":
        return "aggregate_slab_requires_explicit_property_owner"
    return None


def overlapping_slab_owners(changes):
    """Reject separate edits of an aggregate and its selected tier in one plan."""
    selected = {(c["ref"]["drawing_file"], c["ref"]["model_uuid"]) for c in changes}
    for change in changes:
        resource = change.get("resource") or {}
        material = resource.get("native_material_state") or {}
        ownership = resource.get("component_ownership") or {}
        hierarchy = material.get("hierarchy") if isinstance(material, dict) else None
        if not isinstance(hierarchy, dict):
            hierarchy = ownership.get("value") if isinstance(ownership, dict) else None
        if not isinstance(hierarchy, dict):
            continue  # The field-specific validator rejects malformed evidence.
        lineage = hierarchy.get("lineage", [])
        if not isinstance(lineage, list) or any(not isinstance(ref, dict) for ref in lineage):
            continue
        if any((ref["drawing_file"], ref["model_uuid"]) in selected for ref in lineage[1:]):
            return True
    return False


MAX_REPORTED_TIERS = 16


def multislab_tier_values(adapter, base, attribute_ids, read_mode="stored", check=lambda: None):
    """Read the same attributes on a MultiSlab's Slab tiers; informational only.

    A MultiSlab preview shows that the layer ("Warstwa bieżąca") keeps its own
    value. No tier is selected, bound or written by this read.
    """
    import NemAll_Python_IFW_ElementAdapter as adapters
    from .native_model_edit import attribute_fields

    try:
        children = adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True)
        tiers = []
        for index, child in enumerate(children):
            check()
            if index >= 256:
                return {"status": "not_checked", "value": None, "reason": "tier_child_limit"}
            if text(child.GetElementAdapterType().GetTypeName()) != "Slab_TypeUUID":
                continue
            if len(tiers) >= MAX_REPORTED_TIERS:
                return {"status": "not_checked", "value": None, "reason": "tier_report_limit"}
            ref = identity(child)
            tiers.append({"model_uuid": ref["model_uuid"], "view_uuid": ref["view_uuid"],
                          "fields": attribute_fields(child, base, list(attribute_ids), read_mode)})
        check()
        return {"status": "observed", "value": sorted(tiers, key=fingerprint)}
    except BridgeError:
        raise
    except Exception as exc:
        return failure(exc, "multislab_tier_values")
