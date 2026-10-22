"""Exact component deletion; absence requires a complete fresh native scan."""
from __future__ import annotations

from .component_ownership import ComponentReadError, failure, identity, observe
from .model_context import boolean, guid, integer
from .native_readers import COMPONENT_TYPES
from .query_contracts import fingerprint
from .transport import BridgeError


def ownership(adapter, check=lambda: None):
    """Bind a component and its bounded entire subtree, retaining native owners."""
    try:
        root = observe(adapter, check)
        descendants, seen = [], {fingerprint(root["target"])}
        import NemAll_Python_IFW_ElementAdapter as adapters
        retained = [adapter]
        pending = [adapter]
        while pending:
            parent = pending.pop()
            check()
            owner = adapters.BaseElementAdapterChildElementsService.GetChildModelElements(parent, True)
            retained.append(owner)
            for child in owner:
                check()
                ref = identity(child)
                key = fingerprint(ref)
                if key in seen or len(seen) >= 256:
                    raise ValueError("Deletion subtree cyclic or over budget")
                child_evidence = observe(child, check)
                if child_evidence["lineage"][1:] != [identity(parent)] + observe(parent, check)["lineage"][1:]:
                    raise ValueError("Deletion child hierarchy changed")
                if ref["signed_drawing_file"] != root["target"]["signed_drawing_file"]:
                    raise ValueError("Deletion subtree crosses scope")
                seen.add(key)
                descendants.append(ref)
                pending.append(child)
                retained.append(child)
        root["descendants"] = sorted(descendants, key=fingerprint)
        root["descendants_complete"] = True
        return {"status": "observed", "value": root}
    except BridgeError:
        raise
    except Exception as exc:
        if isinstance(exc, ComponentReadError):
            return failure(exc)
        return failure(ComponentReadError("deletion_descendants", "delete_subtree_unavailable", type(exc).__name__))


def blocker(evidence):
    if not isinstance(evidence, dict) or evidence.get("status") != "observed":
        return "delete_ownership_unavailable"
    value = evidence.get("value")
    if (not isinstance(value, dict) or value.get("parent_chain_complete") is not True
            or value.get("children_complete") is not True or value.get("descendants_complete") is not True
            or not isinstance(value.get("target"), dict) or value["target"].get("type_name") not in COMPONENT_TYPES
            or not isinstance(value.get("descendants"), list) or len(value["descendants"]) > 255):
        return "delete_ownership_unavailable"
    lineage = value.get("lineage")
    opening_owner = (value["target"].get("type_name") == "WindowDoor_TypeUUID"
                     and isinstance(lineage, list) and len(lineage) == 2 and lineage[0] == value["target"]
                     and lineage[1].get("type_name") == "Wall_TypeUUID" and value.get("terminal_root") == lineage[1])
    if not opening_owner and (lineage != [value["target"]] or value.get("terminal_root") != value["target"]):
        return "delete_parent_requires_explicit_owner"
    return None


def valid_change(change):
    resource = change.get("resource") or {}
    evidence = resource.get("delete_ownership")
    if blocker(evidence):
        return False
    target = evidence["value"]["target"]
    ref = change.get("ref") or {}
    return (change.get("operation") == "delete_element" and change.get("field") == "element_exists"
            and change.get("property_role") == "element" and change.get("new_value") is False
            and change.get("old_value") == {"status": "observed", "value": True}
            and all(target.get(key) == ref.get(key) for key in ("drawing_file", "model_uuid", "type_uuid"))
            and target.get("view_uuid") == change.get("target_view_uuid")
            and target.get("type_name") == change.get("native_type"))


def preflight(element, change, check=lambda: None):
    if not valid_change(change):
        raise BridgeError("target_not_writable", "Deletion requires a reviewed component root or Wall-owned opening and full subtree.", 409)
    current = ownership(element, check)
    if current != change["resource"]["delete_ownership"]:
        raise BridgeError("repair_conflict", "Deletion ownership or descendants changed since preview.", 409)


def observe_deleted(doc, base, queries, change, diagnostics=None):
    """Never infer deletion from a filtered query, stale wrapper or failed scan."""
    if not valid_change(change):
        raise BridgeError("repair_conflict", "Deletion evidence is unavailable.", 409)
    ref = change["ref"]
    if integer(doc.GetDocumentID()) != ref["document_id"]:
        raise BridgeError("repair_conflict", "Deletion document changed.", 409)
    if integer(base.DrawingFileService.GetActiveFileNumber()) != ref["drawing_file"]:
        raise BridgeError("repair_conflict", "Deletion active drawing changed.", 409)
    started = queries.clock()
    identities = [change["resource"]["delete_ownership"]["value"]["target"]]
    identities += change["resource"]["delete_ownership"]["value"]["descendants"]
    expected = {item["model_uuid"] for item in identities}
    preserved_parents = {item["model_uuid"] for item in change["resource"]["delete_ownership"]["value"]["lineage"][1:]}
    present, parent_present = set(), set()
    owner = base.ElementsSelectService.SelectAllElements(doc)
    for index, adapter in enumerate(owner):
        if index >= 10000 or queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Deletion absence scan exceeded budget.", 409)
        # Unreadable candidate identities/lifecycle abort rather than proving absence.
        signed = integer(adapter.GetDrawingfileNumber())
        if signed == 0 or signed == -ref["drawing_file"]:
            raise BridgeError("repair_conflict", "Deletion absence scan has unavailable or conflicting drawing-file identity.", 409)
        if abs(signed) != ref["drawing_file"]:
            continue
        model = guid(adapter.GetModelElementUUID())
        if model not in expected | preserved_parents:
            continue
        deleted, null = boolean(adapter.IsDeleted()), boolean(adapter.IsNull())
        if deleted or null:
            # A stale wrapper alone cannot prove absence. Continue the entire scan.
            continue
        if not boolean(adapter.IsValid()) or signed <= 0:
            raise BridgeError("repair_conflict", "Deletion target lifecycle or scope is unreadable.", 409)
        if model in expected:
            present.add(model)
        else:
            parent_present.add(model)
    if queries.clock() - started >= queries.SCAN_SECONDS:
        raise BridgeError("scan_limit_exceeded", "Deletion absence scan exceeded budget.", 409)
    if diagnostics is not None:
        diagnostics.update(method="complete_fresh_native_identity_scan", complete=True,
                           expected_model_uuids=sorted(expected), present_model_uuids=sorted(present),
                           preserved_parent_model_uuids=sorted(preserved_parents),
                           observed_parent_model_uuids=sorted(parent_present))
    if parent_present != preserved_parents:
        return {"status": "not_checked", "value": None, "reason": "deletion_parent_preservation_unproven"}
    if not present:
        return {"status": "observed", "value": False}
    if present == expected:
        return {"status": "observed", "value": True}
    return {"status": "not_checked", "value": None, "reason": "deletion_subtree_partially_present"}


def final_write_guard(base, element, change, doc, check):
    check()
    if (integer(doc.GetDocumentID()) != change["ref"]["document_id"]
            or integer(base.DrawingFileService.GetActiveFileNumber()) != change["ref"]["drawing_file"]
            or integer(element.GetDrawingfileNumber()) != change["ref"]["drawing_file"]):
        raise BridgeError("target_not_writable", "Native mutation scope does not match the plan.", 409)
    for method, expected in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                             ("IsInActiveDocument", True), ("IsInActiveLayer", True), ("IsLabelElement", False)):
        if boolean(getattr(element, method)()) is not expected:
            raise BridgeError("target_not_writable", "Native mutation target fails " + method, 409)
    check()


def write(base, element, change, doc=None, check=lambda: None):
    preflight(element, change, check)
    import NemAll_Python_IFW_ElementAdapter as adapters
    targets = adapters.BaseElementAdapterList()
    targets.append(element)
    if doc is None:
        doc = element.GetDocument()
    final_write_guard(base, element, change, doc, check)
    return base.DeleteElements(doc, targets)
