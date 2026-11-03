"""Exact getter-only Beam/Slab evidence, independent of edit eligibility."""
from __future__ import annotations

import importlib

from .component_ownership import identity, same_model_identity
from .model_context import boolean
from .query_contracts import fingerprint
from .transport import BridgeError


_CLASSES = {
    "Beam_TypeUUID": ("BeamElement", "StructuralBeamElement"),
    "SkeletonBeam_TypeUUID": ("BeamElement", "StructuralBeamElement"),
    "Slab_TypeUUID": ("SlabElement",),
    "MultiSlab_TypeUUID": ("SlabElement",),
}


def resolve_slab_child(request, snapshot, live, owners, trace, check, details=None):
    """Resolve only an exact Slab under an explicitly named MultiSlab view.

    SelectAllElements need not expose every child. This separate read route
    never changes the query inventory or makes a child/parent a writable owner.
    Retain enumeration containers and all parent wrappers through later reads.
    """
    import NemAll_Python_IFW_ElementAdapter as adapters

    def unavailable(cause=None):
        # The cause names only identities already read; it never selects a
        # different view or owner for the caller.
        raise BridgeError("probe_scope_unavailable", "Exact Slab child/parent identity is unavailable or conflicting"
                          + (": %s." % cause if cause else "."), 409)

    def call(api, callback):
        check()
        value = trace.call(api, callback, drawing_file=request["drawing_file"],
                           model_uuid=request["model_uuid"], view_uuid=request["view_uuid"],
                           parent_model_uuid=request["parent_ref"]["model_uuid"],
                           parent_view_uuid=request["parent_ref"]["view_uuid"])
        check()
        return value

    hint = request["parent_ref"]
    parents = [e for e in snapshot["elements"] if e["ref"]["model_uuid"] == hint["model_uuid"]]
    direct = [e for e in snapshot["elements"] if e["ref"]["model_uuid"] == request["model_uuid"]]
    if (len(parents) != 1 or parents[0]["view_identity_not_checked"]
            or hint["view_uuid"] not in parents[0]["view_uuids"]
            or parents[0]["fields"]["type_name"].get("value") != "MultiSlab_TypeUUID"
            or len(direct) > 1 or (direct and direct[0]["view_identity_not_checked"])):
        unavailable()
    parent_wrappers = live.get((request["drawing_file"], hint["model_uuid"]), {}).get(hint["view_uuid"], [])
    unique_parents = {id(adapter): adapter for adapter in parent_wrappers}
    if not 1 <= len(unique_parents) <= 16:
        unavailable()
    candidates, inventory, edges = {}, [], []
    count = 0
    try:
        for parent in unique_parents.values():
            parent_ref = call("MaterialChild.parent_identity", lambda: identity(parent, trace=call))
            if (parent_ref["drawing_file"] != request["drawing_file"] or parent_ref["signed_drawing_file"] < 0
                    or any(parent_ref[key] != hint[key] for key in ("model_uuid", "view_uuid"))
                    or parent_ref["type_name"] != "MultiSlab_TypeUUID"
                    or parent_ref["type_uuid"] != parents[0]["ref"]["type_uuid"]):
                unavailable()
            for method in ("IsNull", "IsDeleted"):
                if boolean(call("MaterialChild.parent." + method, getattr(parent, method))):
                    unavailable()
            children = call("MaterialChild.GetChildModelElements", lambda:
                adapters.BaseElementAdapterChildElementsService.GetChildModelElements(parent, True))
            owners.append(children)
            refs, found = [], False
            for child in children:
                check()
                if count >= 256:
                    raise BridgeError("scan_limit_exceeded", "Material child resolution exceeded 256 child visits.", 409)
                count += 1
                ref = call("MaterialChild.child_identity", lambda: identity(child, trace=call))
                if ref["signed_drawing_file"] != parent_ref["signed_drawing_file"]:
                    unavailable()
                refs.append(ref)
                if ref["model_uuid"] == request["model_uuid"] and ref["view_uuid"] == request["view_uuid"]:
                    if ref["type_name"] != "Slab_TypeUUID":
                        unavailable()
                    candidates[id(child)] = child
                    found = True
            # A missing target on one parent wrapper is a conflict, not a vote
            # for the first wrapper which happened to expose it.
            if not found:
                views = sorted({ref["view_uuid"] for ref in refs if ref["model_uuid"] == request["model_uuid"]})
                unavailable(("the parent lists this child model under view(s) %s, not the requested view; "
                             "use the parent-edge child view" % views) if views
                            else "the parent does not list this child model")
            inventory.append({"parent": parent_ref, "children": sorted(refs, key=fingerprint)})
        for child in live.get((request["drawing_file"], request["model_uuid"]), {}).get(request["view_uuid"], []):
            candidates[id(child)] = child
        if not 1 <= len(candidates) <= 16:
            unavailable()
        target_refs = []
        for child in candidates.values():
            ref = call("MaterialChild.target_identity", lambda: identity(child, trace=call))
            if (ref["drawing_file"] != request["drawing_file"] or ref["signed_drawing_file"] < 0
                    or ref["type_name"] != "Slab_TypeUUID"
                    or any(ref[key] != request[key] for key in ("model_uuid", "view_uuid"))):
                unavailable()
            for method in ("IsNull", "IsDeleted"):
                if boolean(call("MaterialChild.target." + method, getattr(child, method))):
                    unavailable()
            parent = call("MaterialChild.GetParentElement", lambda:
                adapters.BaseElementAdapterParentElementService.GetParentElement(child))
            owners.append(parent)
            for method in ("IsNull", "IsDeleted"):
                if boolean(call("MaterialChild.edge_parent." + method, getattr(parent, method))):
                    unavailable()
            edge_ref = call("MaterialChild.edge_parent_identity", lambda: identity(parent, trace=call))
            if not same_model_identity(edge_ref, inventory[0]["parent"]):
                unavailable()
            edges.append({"child": ref, "parent": edge_ref})
            target_refs.append(ref)
        if len({fingerprint(ref) for ref in target_refs}) != 1:
            unavailable()
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("probe_scope_unavailable", "Exact Slab child/parent read failed; no native values were read.", 409) from exc
    ref = target_refs[0]
    element = {"ref": {**parents[0]["ref"], "model_uuid": ref["model_uuid"], "type_uuid": ref["type_uuid"]},
               "view_uuids": sorted(set([request["view_uuid"], *(direct[0]["view_uuids"] if direct else [])]))}
    resolution = {"method": "exact_parent_children", "parent_ref": inventory[0]["parent"],
                  "parent_representation_count": len(unique_parents), "child_visits": count,
                  "child_inventory_complete": True,
                  "target_in_direct_scan": bool(direct and request["view_uuid"] in direct[0]["view_uuids"]),
                  "child_parent_edges": sorted(edges, key=fingerprint),
                  "inventory_fingerprint": fingerprint(sorted(inventory, key=fingerprint))}
    if details is not None:
        # Diagnostic copy only; the fingerprinted resolution above is unchanged.
        details["inventory"] = sorted(inventory, key=fingerprint)
    return element, candidates, resolution


def native_material_evidence(base, adapter, ref, read):
    """Return JSON evidence while retaining native/props through Material read.

    Read access through a represented object is evidence about that accessor,
    not proof that submitting that object can persist a property edit.
    """
    def representation():
        native = base.GetElement(adapter)
        if native is None:
            raise ValueError("Native representation unavailable")
        return native

    native_result = read("BaseElements.GetElement.material_comparison", representation)
    if native_result["status"] != "observed":
        return native_result, {"status": "not_checked", "value": None,
                               "reason": "native_representation_unavailable"}
    native = native_result["value"]
    represented = {"status": "observed", "value": {
        "module": type(native).__module__, "name": type(native).__name__}}
    unavailable = {"status": "not_checked", "value": None,
                   "reason": "native_material_read_route_unsupported"}
    names = _CLASSES.get(ref["type_name"])
    if names is None:
        return represented, unavailable
    arch_result = read("Python.import.NemAll_Python_ArchElements.material_comparison",
                       lambda: importlib.import_module("NemAll_Python_ArchElements"))
    if arch_result["status"] != "observed":
        return represented, {"status": "not_checked", "value": None,
                             "reason": "native_material_module_unavailable"}
    arch = arch_result["value"]
    matches = [name for name in names if isinstance(getattr(arch, name, None), type)
               and isinstance(native, getattr(arch, name))]
    if len(matches) != 1:
        return represented, unavailable
    class_name = matches[0]
    accessor = "StructuralBeamProperties" if class_name == "StructuralBeamElement" else "Properties"
    path = class_name + "." + accessor
    props_result = read(path, lambda: getattr(native, accessor))
    binding = {"access_path": path + ".Material", "owner_ref": ref,
               "writable_owner": "not_established"}
    if props_result["status"] != "observed":
        return represented, {**props_result, **binding}
    props = props_result["value"]

    def material():
        value = props.Material
        if type(value) is not str or len(value) > 255:
            raise ValueError("Native Material must be a bounded string")
        return value

    value = read(class_name.replace("Element", "Properties") + ".Material", material)
    result = {**value, **binding}
    if class_name == "SlabElement":
        result["slab_tiers"] = slab_tier_evidence(props, read)
    return represented, result


_MAX_MEMBERS = 128
_MAX_TIERS = 16


def _members(kind):
    """List public binding member names of a class without invoking getters."""
    names = sorted(name for name in dir(kind) if not name.startswith("_"))
    return {"names": names[:_MAX_MEMBERS], "complete": len(names) <= _MAX_MEMBERS}


def _bounded_material(owner):
    value = owner.Material
    if type(value) is not str or len(value) > 255:
        raise ValueError("Native Material must be a bounded string")
    return value


def slab_tier_evidence(props, read):
    """Read-only API study of Slab tier storage; never a writable owner.

    The setter on SlabProperties.Material has left the observed value blank,
    so this records which members the installed binding exposes and reads
    the tier Material values through GetSlabTierProperties when present.
    Native 0.44.0 observation (Allplan 2026.1): TierCount=1 and index 1
    raised IndexError, so tiers are zero-based. Tier 0 is read without a
    count; further tiers only within an observed, bounded TierCount.
    Nothing here establishes ownership or persistence.
    """
    evidence = {"properties_members": read("SlabProperties.members", lambda: _members(type(props))),
                "tier_api": "absent", "tier_index_base": 0,
                "tier_count": {"status": "not_checked", "value": None,
                               "reason": "tier_count_member_absent"},
                "variable_tier": {"status": "not_checked", "value": None,
                                  "reason": "variable_tier_member_absent"},
                "tiers": [], "writable_owner": "not_established"}
    if not callable(getattr(type(props), "GetSlabTierProperties", None)):
        return evidence
    evidence["tier_api"] = "present"
    if hasattr(type(props), "VariableTier"):
        def variable_tier():
            value = props.VariableTier
            if type(value) not in (bool, int):
                raise ValueError("VariableTier must be a boolean scalar")
            return value
        evidence["variable_tier"] = read("SlabProperties.VariableTier", variable_tier)
    count = 1
    if hasattr(type(props), "TierCount"):
        def tier_count():
            value = props.TierCount
            if type(value) is not int or not 1 <= value <= _MAX_TIERS:
                raise ValueError("TierCount outside the bounded range")
            return value
        evidence["tier_count"] = read("SlabProperties.TierCount", tier_count)
        if evidence["tier_count"]["status"] == "observed":
            count = evidence["tier_count"]["value"]
    for index in range(count):
        api = f"SlabProperties.GetSlabTierProperties({index})"
        tier = read(api, lambda index=index: props.GetSlabTierProperties(index))
        row = {"tier_index": index, "access_path": api + ".Material"}
        if tier["status"] != "observed":
            row.update(status=tier["status"], value=None, reason=tier.get("reason"))
        else:
            owner = tier["value"]
            row.update(read("SlabTierProperties.Material", lambda owner=owner: _bounded_material(owner)))
            row["members"] = read("SlabTierProperties.members", lambda owner=owner: _members(type(owner)))
        evidence["tiers"].append(row)
    return evidence
