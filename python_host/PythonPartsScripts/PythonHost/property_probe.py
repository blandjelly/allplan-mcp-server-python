"""Isolated M4 reads with durable call boundaries; broad discovery stays blocked."""
from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from .model_context import integer
from .model_metadata import bounded_text, enum_code
from .model_properties import attribute_values, positive_id
from .query_contracts import SCHEMA, fingerprint
from .property_contracts import PROBE_SCHEMA, validate_probe
from .transport import BridgeError


class NativeProbeTrace:
    MAX_BYTES = 1024 * 1024

    def __init__(self, path, phase):
        self.path, self.phase, self.probe_id = Path(path), phase, uuid4().hex

    def record(self, api, state, **details):
        from datetime import datetime, timezone
        record = {"probe_id": self.probe_id, "phase": self.phase, "api": api, "state": state,
                  "at_utc": datetime.now(timezone.utc).isoformat(), **details}
        data = (json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n").encode()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("ab") as stream:
                if stream.tell() + len(data) > self.MAX_BYTES:
                    raise OSError("Trace capacity exceeded")
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as exc:
            raise BridgeError("probe_trace_unavailable", "M4 native trace is full or unwritable; no further native call may start. Preserve the trace.", 409) from exc

    def call(self, api, reader, **details):
        self.record(api, "started", **details)
        try:
            result = reader()
        except BaseException as exc:
            self.record(api, "failed", exception_type=type(exc).__name__, **details)
            raise
        self.record(api, "returned", **details)
        return result


class PropertyProbeService:
    def __init__(self, queries, trace_path=None):
        self.queries = queries
        self.trace_path = trace_path or Path(__file__).resolve().parents[2] / ".allplan-mcp/logs/m4-native-probe.jsonl"

    def handle(self, document_reader, base, settings, request):
        validate_probe(request)
        phase = request["phase"]
        trace = NativeProbeTrace(self.trace_path, phase)
        started = self.queries.clock()

        def budget():
            if self.queries.clock() - started >= self.queries.SCAN_SECONDS:
                raise BridgeError("scan_limit_exceeded", "Isolated property probe exceeded its read budget.", 409)

        def read(api, reader, **details):
            budget()
            try:
                value = trace.call(api, reader, **details)
                json.dumps(value, allow_nan=False)
                result = {"status": "observed", "value": value}
            except BridgeError:
                raise  # trace/budget failures forbid any following native call
            except Exception as exc:
                result = {"status": "not_checked", "value": None, "reason": type(exc).__name__}
            trace.record(api, "observation_recorded", observation_status=result["status"], **details)
            budget()
            return result

        doc = trace.call("CoordinateInput.GetInputViewDocument", document_reader)
        result = {"schema_version": PROBE_SCHEMA, "phase": phase, "probe_id": trace.probe_id,
                  "read_only": True, "model_data_changed": False, "usable_for_write": False,
                  "runtime_verified": False, "status": "ready_for_isolated_owner_probe",
                  "trace_file": "Local/.allplan-mcp/logs/m4-native-probe.jsonl",
                  "native_calls_not_automatically_retried": True, "native_selection": "not_requested"}
        if phase == "wall_sample":
            from .wall_probe import sample_wall
            result.update(sample_wall(self.queries, doc, base, settings, request, trace, budget))
        elif phase == "column_sample":
            query = {"schema_version": SCHEMA, "action": "query",
                     "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False, "visibility": "api_select_all"},
                     "component_kind": "top_level_component", "fields": ["layer_id", "file_state", "display_name"],
                     "predicate": {"field": "type_name", "op": "eq", "value": "Column_TypeUUID"}}
            live = {}
            native_owners = []
            snapshot = trace.call("M1.column_scan", lambda: self.queries._scan(doc, base, settings, query, adapter_sink=live, adapter_owners=native_owners))
            budget()
            if (not snapshot["coverage"]["requested_scope_complete"] or not snapshot["elements"]
                    or snapshot["scope"]["included_files"][0]["state"] != "active_foreground"):
                raise BridgeError("probe_scope_unavailable", "The isolated sample requires a readable Column root in one foreground drawing file.", 409)
            element = snapshot["elements"][0]
            ref = element["ref"]
            representations = live.get((ref["drawing_file"], ref["model_uuid"]), {})
            if element["view_identity_not_checked"] or not representations:
                raise BridgeError("probe_scope_unavailable", "Column view identity is unavailable.", 409)
            # One exact root adapter. Duplicate representations are not silently
            # used as property-owner evidence by this narrowly scoped probe.
            if len(representations) != 1:
                raise BridgeError("probe_scope_unavailable", "Isolated sample requires one unambiguous root view.", 409)
            adapter = next(iter(representations.values()))[0]
            if any(candidate is not adapter for candidate in next(iter(representations.values()))):
                raise BridgeError("probe_scope_unavailable", "The isolated root has ambiguous adapter representations; no attributes were read.", 409)
            attrs = read("BaseElementAdapter.GetAttributes(ReadAll)", lambda: attribute_values(adapter, base, budget),
                         drawing_file=ref["drawing_file"], model_uuid=ref["model_uuid"])
            result.update(scope=snapshot["scope"], counts=snapshot["counts"], sample={"ref": ref, "fields": element["fields"], "attributes": attrs},
                          owner="root_adapter_native_owner_not_verified", definition_reads="not_requested",
                          enum_reads="not_requested", presence_semantics="absence_from_ReadAll_not_proven_native_absence")
        elif phase == "element_attributes":
            # Locate one explicitly identified semantic component across the
            # documented/readable root families. Keep the M1 native container
            # alive until the exact root adapter has been read below.
            query = {"schema_version": SCHEMA, "action": "query",
                     "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False,
                               "visibility": "api_select_all"},
                     "component_kind": "semantic_component",
                     "fields": ["display_name", "file_state"], "max_adapters": 10000}
            live, native_owners = {}, []
            snapshot = trace.call("M1.semantic_component_scan",
                                  lambda: self.queries._scan(doc, base, settings, query,
                                                             adapter_sink=live, adapter_owners=native_owners))
            budget()
            if (not snapshot["coverage"]["requested_scope_complete"]
                    or snapshot["scope"]["included_files"][0]["state"] != "active_foreground"):
                raise BridgeError("probe_scope_unavailable", "Attribute listing requires a complete scan of one active foreground drawing.", 409)
            matches = [item for item in snapshot["elements"]
                       if item["ref"]["drawing_file"] == request["drawing_file"]
                       and item["ref"]["model_uuid"] == request["model_uuid"]
                       and request["view_uuid"] in item["view_uuids"]]
            if len(matches) != 1 or matches[0]["view_identity_not_checked"]:
                raise BridgeError("probe_scope_unavailable", "The requested model/view identity did not resolve to exactly one complete semantic component.", 409)
            element = matches[0]
            ref = element["ref"]
            representations = live.get((ref["drawing_file"], ref["model_uuid"]), {})
            views = representations.get(request["view_uuid"], [])
            # M1 has already grouped these adapters by root model/view identity
            # and rejected disagreement in the fields it reads. Distinct Python
            # wrappers can represent that same native root, so verify their
            # attributes too before choosing a representation.
            if (len(element["view_uuids"]) != 1
                    or element["view_uuids"] != [request["view_uuid"]]
                    or set(representations) != {request["view_uuid"]}
                    or not views):
                raise BridgeError("probe_scope_unavailable", "The requested component has ambiguous root adapter representations; no attributes were read.", 409)
            unique_views = []
            seen_adapter_objects = set()
            for adapter in views:
                if id(adapter) not in seen_adapter_objects:
                    seen_adapter_objects.add(id(adapter))
                    unique_views.append(adapter)
            adapter_attributes = [
                read("BaseElementAdapter.GetAttributes(ReadAll)",
                     lambda adapter=adapter: attribute_values(adapter, base, budget),
                     drawing_file=ref["drawing_file"], model_uuid=ref["model_uuid"],
                     view_uuid=request["view_uuid"], representation_index=index + 1,
                     representation_count=len(unique_views))
                for index, adapter in enumerate(unique_views)
            ]
            attrs = adapter_attributes[0]
            if any(item["status"] != "observed" for item in adapter_attributes):
                failed = next(item for item in adapter_attributes if item["status"] != "observed")
                attrs = {"status": "not_checked", "value": None,
                         "reason": "adapter_attributes_unavailable",
                         "representation_count": len(unique_views),
                         "failed_representation": failed.get("reason")}
                result.update(scope=snapshot["scope"], ref=ref, attributes=attrs,
                              adapter_attribute_consistency="not_checked",
                              listing_complete=False, presence_semantics="ReadAll_only_omissions_unknown",
                              writable="not_established")
            elif len({fingerprint(item["value"]) for item in adapter_attributes}) != 1:
                attrs = {"status": "not_checked", "value": None,
                         "reason": "conflicting_adapter_attributes",
                         "representation_count": len(unique_views)}
                result.update(scope=snapshot["scope"], ref=ref, attributes=attrs,
                              adapter_attribute_consistency="conflicting",
                              listing_complete=False,
                              presence_semantics="ReadAll_only_omissions_unknown",
                              writable="not_established")
            else:
                service = base.AttributeService
                sdk_types = getattr(service, "AttributeType", None)
                scalar_types = (("text", "String"), ("integer", "Integer"),
                                ("real", "Double"), ("boolean", "Boolean"))
                candidates, metadata_issues, unknown_filter_names = [], 0, 0
                name_filter = request.get("name_contains", "").casefold()
                for item in attrs["value"]:
                    ident = item["attribute_id"]
                    name = read("AttributeService.GetAttributeName",
                                lambda ident=ident: bounded_text(service.GetAttributeName(doc, ident)),
                                attribute_id=ident)
                    roundtrip = {"status": "not_checked", "value": None, "reason": "name_unavailable"}
                    if name["status"] == "observed":
                        roundtrip = read("AttributeService.GetAttributeID",
                                         lambda name=name["value"]: positive_id(service.GetAttributeID(doc, name)),
                                         attribute_id=ident)
                        if roundtrip["status"] == "observed" and roundtrip["value"] != ident:
                            roundtrip = {"status": "not_checked", "value": roundtrip["value"],
                                         "reason": "name_id_round_trip_mismatch"}
                    if name["status"] != "observed" or roundtrip["status"] != "observed":
                        metadata_issues += 1
                    row = {"attribute_id": ident, "name": name,
                           "name_id_round_trip": roundtrip, "value": item["value"]}
                    if not name_filter:
                        # ReadAll is the source of listing membership. Metadata
                        # failures must not erase an observed ID or raw value.
                        candidates.append(row)
                    elif name["status"] == "observed":
                        if name_filter in name["value"].casefold():
                            candidates.append(row)
                    else:
                        # We cannot determine whether this row matches a name
                        # filter, so disclose the gap in coverage below.
                        unknown_filter_names += 1
                total = len(candidates)
                page = candidates[request.get("offset", 0):request.get("offset", 0) + request.get("limit", 32)]
                for item in page:
                    ident = item["attribute_id"]
                    def inspect_type(ident=ident):
                        value = service.GetAttributeType(doc, ident)
                        supported = [value_type for value_type, member in scalar_types
                                     if sdk_types is not None and getattr(sdk_types, member, None) is not None
                                     and value == getattr(sdk_types, member)]
                        return {"type_code": enum_code(value), "supported_scalar_value_types": supported}
                    type_result = read("AttributeService.GetAttributeType", inspect_type, attribute_id=ident)
                    item["type"] = ({"status": "observed", "value": type_result["value"]["type_code"]}
                                    if type_result["status"] == "observed" else type_result)
                    item["supported_scalar_value_types"] = (type_result["value"]["supported_scalar_value_types"]
                                                             if type_result["status"] == "observed" else [])
                    if type_result["status"] != "observed":
                        metadata_issues += 1
                offset = request.get("offset", 0)
                result.update(scope=snapshot["scope"], counts=snapshot["counts"], ref=ref,
                              attributes=page, total_matches=total, offset=offset,
                              adapter_attribute_consistency="consistent",
                              adapter_attribute_representation_count=len(unique_views),
                              total_matches_status="not_checked" if unknown_filter_names else "observed",
                              next_offset=(offset + len(page) if offset + len(page) < total else None),
                              listing_complete=(offset + len(page) >= total and unknown_filter_names == 0),
                              metadata_complete=metadata_issues == 0,
                              metadata_not_checked_count=metadata_issues,
                              filter_unknown_name_count=unknown_filter_names,
                              presence_semantics="values_present_in_ReadAll_only; omissions_unknown",
                              writable="not_established", enum_values="not_read",
                              filter={"name_contains": request.get("name_contains", ""), "case_sensitive": False})
        elif phase == "attribute_name":
            name = request["attribute_name"]
            ident = read("AttributeService.GetAttributeID", lambda: positive_id(base.AttributeService.GetAttributeID(doc, name)))
            # A spelling miss is recoverable; a runtime/API failure is not an
            # invitation to retry native calls or broaden metadata discovery.
            if ident.get("reason") in {"ValueError", "TypeError"}:
                from .model_properties import resolve_attribute_name
                def lookup(api, callback):
                    budget()
                    value = trace.call(api, callback)
                    budget()
                    return value
                resolved = read("AttributeService.ResolveAttributeSpelling",
                                lambda: resolve_attribute_name(doc, base, name, lookup))
                if resolved["status"] == "observed":
                    ident = {"status": "observed", "value": resolved["value"][0]}
            result["requested_name"] = name
            result["attribute_id"] = ident
            if ident["status"] == "observed":
                actual = read("AttributeService.GetAttributeName", lambda: bounded_text(base.AttributeService.GetAttributeName(doc, ident["value"])), attribute_id=ident["value"])
                result["name"] = actual
                result["exact_name_round_trip"] = actual["status"] == "observed" and actual["value"] == name
                result["case_insensitive_name_round_trip"] = (actual["status"] == "observed"
                    and actual["value"].casefold() == name.strip().casefold())
            result["semantic_alias_verified"] = False
        elif phase == "attribute_definition":
            ident = request["attribute_id"]
            result["attribute_id"] = ident
            result["metadata"] = {}
            for method, convert in (("GetAttributeName", bounded_text), ("GetAttributeType", enum_code),
                                    ("GetAttributeUnit", bounded_text), ("GetAttributeControlType", enum_code)):
                value = read("AttributeService." + method, lambda method=method, convert=convert: convert(getattr(base.AttributeService, method)(doc, ident)), attribute_id=ident)
                result["metadata"][method] = value
                if value["status"] != "observed":
                    break  # stop this phase at the first unavailable API value
            result["enum_values"] = {"status": "not_checked", "value": None, "reason": "native_enum_probe_not_accepted"}
        elif phase in ("layer_name", "layer_catalog"):
            from .layer_names import resolve_direct_layer_name, scan_layer_name_page
            requested_name = request.get("layer_name", request.get("layer_short_name"))
            result["requested_layer_name"] = requested_name
            doc_id = read("DocumentAdapter.GetDocumentID", lambda: integer(doc.GetDocumentID()))
            if doc_id["status"] == "observed":
                def native_read(api, callback):
                    budget()
                    value = trace.call(api, callback)
                    budget()
                    return value

                if phase == "layer_catalog":
                    scan_started = self.queries.clock()
                    calls = [0]
                    def catalog_read(api, callback):
                        budget()
                        calls[0] += 1
                        return callback()
                    trace.record("LayerService.layer_catalog_page", "started",
                                 offset=request.get("offset", 0), limit=request.get("limit", 8192))
                    catalog = scan_layer_name_page(
                        base, doc, doc_id["value"], requested_name, request.get("offset", 0),
                        request.get("limit", 8192), catalog_read,
                        request.get("candidate_ids", []),
                        should_continue=lambda: self.queries.clock() - scan_started < min(3.0, self.queries.SCAN_SECONDS))
                    result["catalog"] = catalog
                    trace.record("LayerService.layer_catalog_page", "returned",
                                 offset=catalog["scan"]["start"], end_exclusive=catalog["scan"]["end_exclusive"],
                                 read_calls=calls[0], read_errors=catalog["scan"]["page_read_errors"],
                                 candidates=len(catalog["candidate_ids"]))
                    if catalog["status"] == "confirmation_required":
                        result["next_action"] = {"action": "ask_user_confirmation", "candidates": catalog["candidates"],
                                                  "prompt": "Confirm the intended layer by its exact full name and short_name. Do not substitute another candidate."}
                    elif catalog["scan"]["next_offset"] is not None:
                        result["next_action"] = {"tool": "model_property_probe", "request": {
                            "phase": "layer_catalog",
                            "layer_name": requested_name, "offset": catalog["scan"]["next_offset"],
                            "limit": request.get("limit", 8192),
                            "candidate_ids": catalog["candidate_ids"]}}
                    elif catalog["status"] == "scan_exhausted_no_match":
                        result["next_action"] = {"action": "ask_user_for_exact_short_name",
                                                  "prompt": "No exact layer candidate was found in the scanned ID range. Ask the user for the exact short name shown by Allplan before planning an edit."}
                    else:
                        result["next_action"] = None
                    result["catalog_policy"] = (
                        "A partial scan never authorizes an edit. Confirm an exact candidate with the user, then send its verified short_name to model_edit. "
                        "Read errors are counted per page and the lookup never proves absence; when the ID range is exhausted without a candidate, ask for the exact short name.")
                else:
                    result["resolution"] = resolve_direct_layer_name(
                        base, doc, doc_id["value"], requested_name, native_read)
                    if result["resolution"]["status"] == "catalog_scan_required":
                        result["next_action"] = {"tool": "model_property_probe", "request": {
                            "phase": "layer_catalog",
                            "layer_name": requested_name, "offset": 0, "limit": 8192}}
                    elif result["resolution"]["status"] == "ambiguous":
                        result["next_action"] = {"action": "ask_user_confirmation",
                                                  "candidates": result["resolution"]["candidates"],
                                                  "prompt": "Confirm the intended layer by its exact full name and short_name. Do not substitute another candidate."}
                    else:
                        result["next_action"] = None
            else:
                result["resolution"] = {"status": "not_checked", "reason": "document_id_unavailable"}
        result["probe_fingerprint"] = fingerprint(result)
        trace.record("probe", "completed")
        budget()
        return result
