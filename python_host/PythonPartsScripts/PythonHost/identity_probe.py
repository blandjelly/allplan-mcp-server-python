"""Read one explicit adapter identity, its ancestry and native representation."""
from .component_ownership import failure, observation, observe
from .query_contracts import SCHEMA, fingerprint
from .transport import BridgeError


def probe_identity(queries, doc, base, settings, request, trace, check):
    # Direct adapters are essential here: resolving to a terminal root would
    # hide a Slab tier's identity behind its MultiSlab parent.
    query = {"schema_version": SCHEMA, "action": "query",
             "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False,
                       "visibility": "api_select_all"},
             # Identity must not depend on property-owner agreement. Slab view
             # adapters can expose different organizational layers/names while
             # still having an exact readable model/view identity and lineage.
             "component_kind": "model_identity", "fields": ["file_state"],
             "max_adapters": 10000}
    live, owners = {}, []
    snapshot = trace.call("M1.direct_identity_scan", lambda: queries._scan(
        doc, base, settings, query, adapter_sink=live, adapter_owners=owners))
    check()
    if (not snapshot["coverage"]["requested_scope_complete"]
            or snapshot["scope"]["included_files"][0]["state"] != "active_foreground"):
        raise BridgeError("probe_scope_unavailable", "Identity probe needs one completely readable foreground drawing.", 409)
    matches = [item for item in snapshot["elements"] if item["ref"]["model_uuid"] == request["model_uuid"]]
    if (len(matches) != 1 or matches[0]["view_identity_not_checked"]
            or request["view_uuid"] not in matches[0]["view_uuids"]):
        raise BridgeError("probe_scope_unavailable", "Requested model/view identity is missing or conflicting.", 409)
    element = matches[0]
    wrappers = live.get((request["drawing_file"], request["model_uuid"]), {}).get(request["view_uuid"], [])
    # Keep every native wrapper alive and require consensus, never select an
    # arbitrary property owner from conflicting representations.
    unique = {id(adapter): adapter for adapter in wrappers}
    if not 1 <= len(unique) <= 64:
        raise BridgeError("probe_scope_unavailable", "Identity representation count is unavailable or over budget.", 409)
    evidence, represented = [], []
    def read(api, callback):
        try:
            return trace.call(api, callback)
        except BridgeError:
            raise
        except Exception as exc:
            raise BridgeError("probe_scope_unavailable", "Identity hierarchy or native representation is unavailable; no owner was chosen.", 409) from exc

    for adapter in unique.values():
        check()
        manifest = read("Adapter.component_ownership", lambda: observe(adapter, check))
        evidence.append(manifest)
        def native_representation():
            native = base.GetElement(adapter)
            if native is None:
                raise ValueError("Native representation unavailable")
            return {"python_type": type(native).__name__, "python_module": type(native).__module__,
                    "property_owner": "not_established"}
        represented.append(read("BaseElements.GetElement.identity", native_representation))
        check()
    if len({fingerprint(item) for item in evidence}) != 1 or len({fingerprint(item) for item in represented}) != 1:
        raise BridgeError("probe_scope_unavailable", "Exact identity wrappers disagree; no owner was chosen.", 409)
    return {"state": "observed", "scope": snapshot["scope"], "ref": element["ref"],
            "view_uuid": request["view_uuid"], "other_view_uuids": [view for view in element["view_uuids"] if view != request["view_uuid"]],
            "ownership": evidence[0], "native_representation": represented[0],
            "representation_count": len(unique), "source_fingerprint": snapshot["source_fingerprint"],
            "bounds_used_for_identity": False, "property_write_available": False,
            "physical_target_equivalence": "not_established"}


def probe_drawing_identity(queries, doc, base, settings, request, trace, check):
    """Explicit paginated structural inventory, never a writable target binding.

    Every page uses a new complete identity scan. The fingerprint is returned
    so callers can detect membership changes between pages. Read failures stay
    visible on their exact model/view entry; no geometry/name guessing is used.
    """
    query = {"schema_version": SCHEMA, "action": "query",
             "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False,
                       "visibility": "api_select_all"},
             "component_kind": "model_identity", "fields": ["file_state"], "max_adapters": 10000}
    live, owners = {}, []
    snapshot = trace.call("M1.drawing_identity_scan", lambda: queries._scan(
        doc, base, settings, query, adapter_sink=live, adapter_owners=owners))
    check()
    if (not snapshot["coverage"]["requested_scope_complete"]
            or len(snapshot["scope"]["included_files"]) != 1
            or snapshot["scope"]["included_files"][0]["state"] != "active_foreground"):
        raise BridgeError("probe_scope_unavailable", "Drawing identity requires a complete foreground scan.", 409)
    views = []
    for element in snapshot["elements"]:
        # An unreadable view must remain a visible row rather than vanish.
        for view in sorted(element["view_uuids"]) or [None]:
            views.append((element, view))
    views.sort(key=lambda pair: (pair[0]["ref"]["model_uuid"], pair[1] or ""))
    offset, limit = request.get("offset", 0), request.get("limit", 16)
    entries = []
    for element, view in views[offset:offset + limit]:
        check()
        wrappers = live.get((request["drawing_file"], element["ref"]["model_uuid"]), {}).get(view, [])
        unique = {id(adapter): adapter for adapter in wrappers}
        unavailable = {"status": "not_checked", "value": None, "reason": "identity_representation_unavailable"}
        entry = {"ref": element["ref"], "view_uuid": view,
                 "ownership": unavailable, "native_representation": unavailable,
                 "representation_count": len(unique)}
        if not element["view_identity_not_checked"] and view and 1 <= len(unique) <= 64:
            evidence, represented = [], []
            for adapter in unique.values():
                check()
                evidence.append(trace.call("Adapter.drawing_component_ownership", lambda: observation(adapter, check)))
                try:
                    native = trace.call("BaseElements.GetElement.drawing_identity", lambda: base.GetElement(adapter))
                    if native is None:
                        raise ValueError("Native representation unavailable")
                    represented.append({"status": "observed", "value": {
                        "python_type": type(native).__name__, "python_module": type(native).__module__,
                        "property_owner": "not_established"}})
                except BridgeError:
                    raise
                except Exception as exc:
                    represented.append(failure(exc, "native_representation"))
                check()
            for field, observations in (("ownership", evidence), ("native_representation", represented)):
                entry[field] = (observations[0] if len({fingerprint(item) for item in observations}) == 1 else
                                {"status": "not_checked", "value": None, "reason": "identity_representation_conflict"})
        entries.append(entry)
    observed = sum(entry["ownership"]["status"] == entry["native_representation"]["status"] == "observed"
                   for entry in entries)
    next_offset = offset + len(entries)
    check()
    return {"state": "observed" if observed == len(entries) else "not_checked",
            "scope": snapshot["scope"], "coverage": snapshot["coverage"], "entries": entries,
            "source_fingerprint": snapshot["source_fingerprint"],
            "pagination": {"offset": offset, "limit": limit, "total": len(views),
                           "next_offset": next_offset if next_offset < len(views) else None,
                           "has_more": next_offset < len(views)},
            "counts": {"model_identities": len(snapshot["elements"]), "view_identities": len(views),
                       "returned": len(entries), "observed": observed, "not_checked": len(entries) - observed},
            "bounds_used_for_identity": False, "property_write_available": False,
            "physical_target_equivalence": "not_established"}
