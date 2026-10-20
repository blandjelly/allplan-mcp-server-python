"""Read one explicit adapter identity, its ancestry and native representation."""
from .component_ownership import observe
from .query_contracts import SCHEMA, fingerprint
from .transport import BridgeError


def probe_identity(queries, doc, base, settings, request, trace, check):
    # Direct adapters are essential here: resolving to a terminal root would
    # hide a Slab tier's identity behind its MultiSlab parent.
    query = {"schema_version": SCHEMA, "action": "query",
             "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False,
                       "visibility": "api_select_all"},
             "component_kind": "model_identity", "fields": ["display_name", "layer_id", "file_state"],
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
