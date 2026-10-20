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


def observe(adapter, check=lambda: None, *, include_children=True):
    """Read exact ancestry and direct children, retaining native containers locally.

    A complete hierarchy is structural evidence only. It does not establish
    which adapter owns a native material, attribute or organizational layer.
    """
    import NemAll_Python_IFW_ElementAdapter as adapters
    check()
    target = identity(adapter)
    lineage, seen, retained = [target], {fingerprint(target)}, [adapter]
    current = adapter
    for _ in range(16):
        check()
        parent = adapters.BaseElementAdapterParentElementService.GetParentElement(current)
        retained.append(parent)
        if boolean(parent.IsNull()):
            break
        ref = identity(parent)
        if (ref["signed_drawing_file"] != target["signed_drawing_file"]
                or fingerprint(ref) in seen):
            raise ValueError("Cyclic or cross-file hierarchy")
        seen.add(fingerprint(ref))
        lineage.append(ref)
        current = parent
    else:
        raise ValueError("Hierarchy exceeds 16 parents")
    children = {}
    if include_children:
        owner = adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True)
        retained.append(owner)
        for index, child in enumerate(owner):
            check()
            if index >= 256:
                raise ValueError("Direct child budget exceeded")
            child_ref = identity(child)
            if child_ref["signed_drawing_file"] != target["signed_drawing_file"]:
                raise ValueError("Child crosses drawing-file scope")
            parent = adapters.BaseElementAdapterParentElementService.GetParentElement(child)
            retained.append(parent)
            if boolean(parent.IsNull()) or identity(parent) != target or child_ref == target:
                raise ValueError("Direct child owner differs")
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
        return {"status": "not_checked", "value": None, "reason": type(exc).__name__}


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
