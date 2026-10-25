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


def slab_write_blocker(evidence):
    """No automatic redirection from slab tiers or aggregates to a field owner."""
    if not isinstance(evidence, dict) or evidence.get("status") != "observed":
        return "slab_ownership_unavailable"
    value = evidence.get("value")
    if not isinstance(value, dict):
        return "slab_ownership_unavailable"
    lineage, target = value.get("lineage"), value.get("target")
    if (value.get("parent_chain_complete") is not True or not isinstance(lineage, list) or not lineage
            or not isinstance(target, dict) or target.get("type_name") not in {"Slab_TypeUUID", "MultiSlab_TypeUUID"}
            or lineage[0] != target or value.get("terminal_root") != lineage[-1]):
        return "slab_ownership_unavailable"
    if len(lineage) != 1:
        return "slab_has_parent_requires_explicit_property_owner"
    if target["type_name"] == "MultiSlab_TypeUUID":
        return "aggregate_slab_requires_explicit_property_owner"
    return None
