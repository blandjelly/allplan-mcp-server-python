"""Bounded adapter lineage evidence; geometry never establishes ownership."""
from __future__ import annotations

from .model_context import boolean, guid, integer, text
from .query_contracts import fingerprint
from .transport import BridgeError


def identity(adapter):
    signed = integer(adapter.GetDrawingfileNumber())
    if signed == 0:
        raise ValueError("Missing drawing-file identity")
    native_type = adapter.GetElementAdapterType()
    return {"drawing_file": abs(signed), "signed_drawing_file": signed,
            "model_uuid": guid(adapter.GetModelElementUUID()),
            "view_uuid": guid(adapter.GetElementUUID()),
            "type_name": text(native_type.GetTypeName()), "type_uuid": guid(native_type.GetGuid())}


class ComponentReadError(ValueError):
    """Bounded failure labels; native exception messages never enter reports."""
    def __init__(self, stage, reason, error_type="ValueError"):
        super().__init__(reason)
        self.stage, self.reason, self.error_type = stage, reason, error_type


def failure(exc, stage="component_ownership"):
    return {"status": "not_checked", "value": None,
            "reason": exc.reason if isinstance(exc, ComponentReadError) else type(exc).__name__,
            "diagnostic": {"stage": exc.stage if isinstance(exc, ComponentReadError) else stage,
                           "error_type": exc.error_type if isinstance(exc, ComponentReadError) else type(exc).__name__}}


def observe(adapter, check=lambda: None, *, include_children=True):
    """Read exact ancestry/direct children; no writable property owner is inferred."""
    import NemAll_Python_IFW_ElementAdapter as adapters

    def read(stage, callback):
        check()
        try:
            value = callback()
        except (BridgeError, ComponentReadError):
            raise
        except Exception as exc:
            raise ComponentReadError(stage, "component_read_unavailable", type(exc).__name__) from exc
        check()
        return value

    target = read("target_identity", lambda: identity(adapter))
    lineage, seen, retained = [target], {fingerprint(target)}, [adapter]
    current = adapter
    for _ in range(16):
        parent = read("parent", lambda: adapters.BaseElementAdapterParentElementService.GetParentElement(current))
        retained.append(parent)
        if read("parent", lambda: boolean(parent.IsNull())):
            break
        ref = read("parent_identity", lambda: identity(parent))
        if ref["signed_drawing_file"] != target["signed_drawing_file"]:
            raise ComponentReadError("parent_identity", "component_cross_file")
        if fingerprint(ref) in seen:
            raise ComponentReadError("parent_identity", "component_parent_cycle")
        seen.add(fingerprint(ref))
        lineage.append(ref)
        current = parent
    else:
        raise ComponentReadError("parent", "component_parent_limit")
    children = {}
    if include_children:
        owner = read("children", lambda: adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True))
        retained.append(owner)
        for index, child in enumerate(owner):
            check()
            if index >= 256:
                raise ComponentReadError("children", "component_child_limit")
            child_ref = read("child_identity", lambda: identity(child))
            if child_ref["signed_drawing_file"] != target["signed_drawing_file"]:
                raise ComponentReadError("child_identity", "component_cross_file")
            parent = read("child_parent", lambda: adapters.BaseElementAdapterParentElementService.GetParentElement(child))
            retained.append(parent)
            if read("child_parent", lambda: boolean(parent.IsNull())):
                raise ComponentReadError("child_parent_identity", "component_child_owner_mismatch")
            parent_ref = read("child_parent_identity", lambda: identity(parent))
            if parent_ref != target or child_ref == target:
                raise ComponentReadError("child_parent_identity", "component_child_owner_mismatch")
            children[fingerprint(child_ref)] = child_ref
    check()
    return {"schema_version": "m4-component-ownership-1", "target": target,
            "lineage": lineage, "terminal_root": lineage[-1],
            "parent_chain_complete": True, "children_complete": include_children,
            "children": sorted(children.values(), key=fingerprint),
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
