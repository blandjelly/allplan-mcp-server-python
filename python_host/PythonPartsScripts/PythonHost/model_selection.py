"""Explicit UI presentation of a full fresh selection; never authorizes a write."""
from __future__ import annotations

import copy

from .model_context import integer
from .property_contracts import SELECTION_SCHEMA, validate_selection
from .transport import BridgeError


def present_selection(service, doc, base, settings, ifw, request):
    validate_selection(request)
    result = {"schema_version": SELECTION_SCHEMA, "action": request["action"],
              "model_data_changed": False, "usable_for_write": False, "runtime_verified": False,
              "native_selection": {"status": "unsupported", "reason": "no_verified_programmatic_UI_selection_in_current_interactor"},
              "ui_visibility": "requires_owner_observation", "status": "ready_for_owner_test"}
    # Never silently substitute a highlight when native selection was requested.
    if request["action"] == "select":
        return {**result, "state": "unsupported", "ui_calls_started": False}
    highlight = getattr(ifw, "HighlightService", None)
    cancel = getattr(highlight, "CancelAllHighlightedElements", None)
    apply = getattr(highlight, "HighlightElements", None)
    if not callable(cancel) or (request["action"] == "highlight" and not callable(apply)):
        raise BridgeError("presentation_unavailable", "Highlight API symbols are unavailable in the loaded build.", 409)
    doc_id = integer(doc.GetDocumentID())
    result["clear_scope"] = "all_highlights_in_current_document_including_other_sources"
    if request["action"] == "clear_highlight":
        try:
            cancel(doc_id)
        except Exception as exc:
            return {**result, "state": "unknown", "ui_calls_started": True, "error": type(exc).__name__}
        return {**result, "state": "submitted", "ui_calls_started": True}
    started = service.clock()
    service._expire()
    ident = request["selection_id"]
    entry = service.selections.get(ident)
    if entry is None:
        raise BridgeError("selection_unavailable", "Selection expired or belongs to another host session. Query again.", 409)
    live = {}
    try:
        snapshot = service._scan(doc, base, settings, entry["request"], adapter_sink=live)
    except BridgeError as exc:
        service.selections.pop(ident, None)
        raise BridgeError("selection_unverifiable", "No UI call started; the full selection could not be revalidated.", 409) from exc
    if snapshot["source_fingerprint"] != entry["snapshot"]["source_fingerprint"]:
        service.selections.pop(ident, None)
        raise BridgeError("selection_stale", "No UI call started; full query evidence changed. Query again.", 409)
    if service.clock() - entry["created"] >= service.TTL_SECONDS:
        service.selections.pop(ident, None)
        raise BridgeError("selection_unavailable", "Selection expired during revalidation; query again.", 409)
    from NemAll_Python_IFW_ElementAdapter import BaseElementAdapterList
    adapters = BaseElementAdapterList()
    excluded = set(request.get("exclude_model_uuids", []))
    all_ids = {item["ref"]["model_uuid"] for item in snapshot["elements"]}
    if excluded - all_ids:
        raise BridgeError("invalid_payload", "Every exception must name a member of the full selection.")
    targets = [item for item in snapshot["elements"] if item["ref"]["model_uuid"] not in excluded]
    states = {item["drawing_file"]: item["state"] for item in snapshot["scope"]["included_files"]}
    for item in targets:
        refs = live.get((item["ref"]["drawing_file"], item["ref"]["model_uuid"]), {})
        if item["view_identity_not_checked"] or set(refs) != set(item["view_uuids"]) or not refs:
            raise BridgeError("selection_unverifiable", "No UI call started; a presentation adapter is unresolved.", 409)
        for view in sorted(refs):
            adapters.append(refs[view][0])
    if service.clock() - started >= service.SCAN_SECONDS or service.clock() - entry["created"] >= service.TTL_SECONDS:
        raise BridgeError("selection_unverifiable", "No UI call started; presentation read budget or selection lifetime elapsed.", 409)
    result.update({"selection_id": ident, "source_fingerprint": snapshot["source_fingerprint"],
                   "scope": copy.deepcopy(snapshot["scope"]), "coverage": copy.deepcopy(snapshot["coverage"]),
                   "omissions": copy.deepcopy(snapshot["omissions"]), "exclude_model_uuids": sorted(excluded),
                   "counts": {"matched": len(snapshot["elements"]), "excluded": len(snapshot["elements"]) - len(targets),
                              "requested_model_identities": len(targets), "requested_adapters": len(adapters),
                              "submitted_model_identities": None, "submitted_adapters": None,
                              "selected": None, "highlighted": None, "not_visible": None,
                              "unreadable": sum(snapshot["counts"][key] for key in (
                                  "predicate_not_checked", "identity_not_checked", "conflicting_model_identities", "hierarchy_not_checked")),
                              "not_editable": sum(states[item["ref"]["drawing_file"]] == "passive_background" for item in targets),
                              "other_editability": "not_checked"}})
    # The documented API has no visibility/readback result. Success means only
    # submission; do not publish invented highlighted/selected counts.
    try:
        cancel(doc_id)
        if targets:
            apply(adapters)
    except Exception as exc:
        return {**result, "state": "unknown", "ui_calls_started": True, "error": type(exc).__name__}
    result["counts"].update(submitted_model_identities=len(targets), submitted_adapters=len(adapters))
    return {**result, "state": "submitted", "ui_calls_started": True}
