"""UI-dispatched read-only queries; snapshots contain JSON and no live adapters."""
from __future__ import annotations

import copy
import json
import time
from collections import Counter, OrderedDict
from uuid import uuid4

from .model_context import context_probe, guid, integer, observation, text
from .query_contracts import SCHEMA, attribute_id, evaluate, fingerprint, predicate_fields, scalar, validate_request
from .transport import BridgeError


class ModelQueryService:
    TTL_SECONDS = 300
    MAX_SELECTIONS = 8
    SCAN_SECONDS = 5
    MAX_SNAPSHOT_BYTES = 4 * 1024 * 1024

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.session_id = uuid4().hex
        self.selections = OrderedDict()

    def handle(self, doc, base, settings, request):
        validate_request(request)
        self._expire()
        if request["action"] == "query":
            snapshot = self._scan(doc, base, settings, request)
            ident = uuid4().hex
            if len(self.selections) >= self.MAX_SELECTIONS:
                self.selections.popitem(last=False)
            entry = {"request": copy.deepcopy(request), "snapshot": snapshot,
                     "created": self.clock(), "cursors": {}}
            self.selections[ident] = entry
            return self._page(ident, entry, 0, request.get("page_size", 100))
        ident = request["selection_id"]
        entry = self.selections.get(ident)
        if entry is None:
            raise BridgeError("selection_unavailable", "Selection expired, was evicted or belongs to a previous host session. Run a new query.", 409)
        cursor = request.get("cursor")
        if cursor is not None and cursor not in entry["cursors"]:
            raise BridgeError("invalid_cursor", "Cursor does not belong to this selection.")
        try:
            current = self._scan(doc, base, settings, entry["request"])
        except BridgeError as exc:
            del self.selections[ident]
            raise BridgeError("selection_unverifiable", "Selection could not be revalidated. Run a new query in the current scope.", 409) from exc
        if current["source_fingerprint"] != entry["snapshot"]["source_fingerprint"]:
            del self.selections[ident]
            raise BridgeError("selection_stale", "Project, document, file state, identity or a queried field changed. Run a new query.", 409)
        if request["action"] == "summary":
            result = self._metadata(ident, entry)
            items = entry["snapshot"]["elements"]
            result["summary"] = {"drawing_files": dict(sorted(Counter(str(e["ref"]["drawing_file"]) for e in items).items())),
                                 "type_names": dict(sorted(Counter(e["fields"]["type_name"]["value"] for e in items).items()))}
            result["summary_uses_full_selection"] = True
            return result
        return self._page(ident, entry, entry["cursors"].get(cursor, 0), request.get("page_size", 100))

    def _expire(self):
        for ident, entry in list(self.selections.items()):
            if self.clock() - entry["created"] >= self.TTL_SECONDS:
                del self.selections[ident]

    def _metadata(self, ident, entry):
        snapshot = entry["snapshot"]
        return {"schema_version": SCHEMA, "read_only": True, "runtime_verified": False,
                "selection_id": ident, "query_session_id": self.session_id,
                "expires_in_seconds": max(0, int(self.TTL_SECONDS - (self.clock() - entry["created"]))),
                "source_fingerprint": snapshot["source_fingerprint"],
                "scope": copy.deepcopy(snapshot["scope"]), "counts": copy.deepcopy(snapshot["counts"]),
                "coverage": copy.deepcopy(snapshot["coverage"]), "omissions": copy.deepcopy(snapshot["omissions"]),
                "not_checked_samples": copy.deepcopy(snapshot["not_checked_samples"]),
                "usable_for_write": False}

    def _page(self, ident, entry, offset, size):
        result = self._metadata(ident, entry)
        items = entry["snapshot"]["elements"]
        end = min(len(items), offset + size)
        cursor = None
        if end < len(items):
            cursor = next((key for key, index in entry["cursors"].items() if index == end), None)
            if cursor is None:
                cursor = uuid4().hex
                entry["cursors"][cursor] = end
        result.update({"elements": copy.deepcopy(items[offset:end]),
                       "page": {"offset": offset, "returned": end - offset, "next_cursor": cursor,
                                "complete": end == len(items), "is_full_selection": offset == 0 and end == len(items)}})
        return result

    def _scan(self, doc, base, settings, request):
        started = self.clock()
        context = context_probe(doc, base, settings, {})
        project = context["project"]
        if (project["status"] != "observed" or project["value"]["key_status"] != "observed"
                or context["document_id"]["status"] != "observed" or context["loaded_drawing_files"]["status"] != "observed"):
            raise BridgeError("context_unavailable", "Project key, document identity and loaded-file inventory must be readable before querying.", 409)
        scope = request["scope"]
        states = {f["number"]: f["state"] for f in context["loaded_drawing_files"]["value"]}
        included, omitted = [], []
        for number in sorted(scope["drawing_files"]):
            state = states.get(number)
            reason = ("unloaded_or_unavailable" if state is None else
                      "unknown_file_state" if state not in {"active_foreground", "active_background", "passive_background"} else
                      "passive_excluded" if state == "passive_background" and not scope["include_passive"] else None)
            if reason:
                omitted.append({"drawing_file": number, "reason": reason})
            else:
                included.append({"drawing_file": number, "state": state, "write_eligibility": "not_checked"})
        binding = {"query_session_id": self.session_id, "project_key": project["value"]["key"],
                   "document_id": context["document_id"]["value"]}
        needed = predicate_fields(request.get("predicate")) | set(request.get("fields", ["display_name", "layer_id"]))
        needed.update({"type_name", "type_uuid"})
        needed.update(f"attribute:{number}" for number in request.get("attribute_ids", []))
        files = {f["drawing_file"] for f in included}
        groups, source, samples = {}, [], []
        source_bytes = 0
        def add_source(record):
            nonlocal source_bytes
            source_bytes += len(json.dumps(record, ensure_ascii=False, allow_nan=False).encode())
            if source_bytes > self.MAX_SNAPSHOT_BYTES:
                raise BridgeError("scan_limit_exceeded", "Query exceeded the 4 MiB snapshot budget; no selection was created. Narrow the scope or requested fields.", 409)
            source.append(record)
        def sample(reason, record):
            if len(samples) < 10:
                samples.append({"reason": reason, **record})
        counts = Counter({"raw_adapters_visited": 0, "in_scope_adapters": 0, "matched_model_identities": 0,
                          "nonmatching_model_identities": 0, "predicate_not_checked": 0,
                          "identity_not_checked": 0, "conflicting_model_identities": 0,
                          "duplicate_representations": 0, "file_identity_not_checked": 0, "file_state_conflicts": 0})
        try:
            adapters = base.ElementsSelectService.SelectAllElements(doc) if files else []
            for adapter in adapters:
                if counts["raw_adapters_visited"] >= request.get("max_adapters", 5000) or self.clock() - started >= self.SCAN_SECONDS:
                    raise BridgeError("scan_limit_exceeded", "Query exceeded the adapter/time budget; no selection or complete count was created. Narrow loaded files or use max_adapters up to 10000.", 409)
                counts["raw_adapters_visited"] += 1
                signed = observation(lambda: integer(adapter.GetDrawingfileNumber()))
                if signed["status"] != "observed" or signed["value"] == 0:
                    counts["file_identity_not_checked"] += 1
                    add_source({"file_identity": signed})
                    sample("file_identity_not_checked", {"file_identity": signed})
                    continue
                number = abs(signed["value"])
                if number not in files:
                    continue
                if signed["value"] < 0 and states[number] != "passive_background":
                    counts["file_state_conflicts"] += 1
                    record = {"signed_drawing_file_number": signed["value"], "inventory_state": states[number]}
                    add_source(record)
                    sample("file_state_conflict", record)
                    continue
                counts["in_scope_adapters"] += 1
                values = self._fields(adapter, base, needed, number, states[number])
                model = observation(lambda: guid(adapter.GetModelElementUUID()))
                view = observation(lambda: guid(adapter.GetElementUUID()))
                record = {"signed_drawing_file_number": signed["value"], "model_uuid": model,
                          "view_uuid": view, "fields": values}
                add_source(record)
                if (model["status"] != "observed" or values["type_uuid"]["status"] != "observed"
                        or values["type_name"]["status"] != "observed"):
                    counts["identity_not_checked"] += 1
                    sample("identity_not_checked", record)
                    continue
                key = (number, model["value"])
                groups.setdefault(key, []).append(record)
        except BridgeError:
            raise
        except Exception as exc:
            raise BridgeError("query_read_failed", "Allplan element enumeration failed; no selection was created.", 503) from exc
        if self.clock() - started >= self.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Query exceeded its time budget; no selection was created.", 409)
        elements = []
        for (number, model_uuid), records in sorted(groups.items()):
            records.sort(key=fingerprint)
            counts["duplicate_representations"] += len(records) - 1
            # Representation disagreement is explicit: never pick the first view's values.
            if len({fingerprint(r["fields"]) for r in records}) != 1:
                counts["conflicting_model_identities"] += 1
                sample("representation_conflict", {"drawing_file": number, "model_uuid": model_uuid})
                continue
            values = records[0]["fields"]
            match = evaluate(request.get("predicate"), values)
            if match is None:
                counts["predicate_not_checked"] += 1
                sample("predicate_not_checked", {"drawing_file": number, "model_uuid": model_uuid, "fields": values})
                continue
            if not match:
                counts["nonmatching_model_identities"] += 1
                continue
            counts["matched_model_identities"] += 1
            elements.append({"ref": {**binding, "drawing_file": number, "model_uuid": model_uuid,
                                     "type_uuid": values["type_uuid"]["value"], "durable_identity_verified": False},
                             "signed_drawing_file_numbers": sorted({r["signed_drawing_file_number"] for r in records}),
                             "view_uuids": sorted({r["view_uuid"]["value"] for r in records if r["view_uuid"]["status"] == "observed"}),
                             "view_identity_not_checked": any(r["view_uuid"]["status"] != "observed" for r in records),
                             "fields": values, "source_fingerprint": fingerprint(records), "usable_for_write": False})
        # Source includes rejected candidates so additions and changes into the result are detected.
        source.sort(key=fingerprint)
        complete = not omitted and not any(counts[key] for key in ("predicate_not_checked", "identity_not_checked", "conflicting_model_identities", "file_identity_not_checked", "file_state_conflicts"))
        failed_fields = sum(v["status"] == "not_checked" for e in elements for v in e["fields"].values())
        return {"scope": {"requested": copy.deepcopy(scope), "included_files": included},
                "counts": dict(counts), "elements": elements, "omissions": omitted, "not_checked_samples": samples,
                "coverage": {"scan_complete": True, "requested_scope_complete": complete,
                             "returned_fields_complete": failed_fields == 0, "returned_fields_not_checked": failed_fields,
                             "whole_project": False, "unloaded_files": "not_enumerated",
                             "visibility": "api_select_all_screen_and_occlusion_not_checked",
                             "count_kind": "unique_file_model_uuid_not_top_level_components",
                             "native_component_counts": "not_checked", "geometry_units_offset": "not_checked"},
                "source_fingerprint": fingerprint({"binding": binding, "included": included, "omissions": omitted, "source": source})}

    @staticmethod
    def _fields(adapter, base, needed, number, state):
        result = {}
        def bounded_text(value):
            value = text(value)
            if len(value) > 8192:
                raise ValueError("Text exceeds the query field budget")
            return value
        readers = {"display_name": lambda: bounded_text(adapter.GetDisplayName()),
                   "type_name": lambda: bounded_text(adapter.GetElementAdapterType().GetTypeName()),
                   "type_uuid": lambda: guid(adapter.GetElementAdapterType().GetGuid()),
                   "layer_id": lambda: integer(adapter.GetCommonProperties().Layer),
                   "drawing_file": lambda: number, "file_state": lambda: state}
        for field in sorted(needed):
            if attribute_id(field) is None:
                result[field] = observation(readers[field])
        requested = [field for field in sorted(needed) if attribute_id(field) is not None]
        if requested:
            try:
                raw = adapter.GetAttributes(base.eAttibuteReadState.ReadAll)
                attributes = {}
                for ident, value in raw:
                    ident = integer(ident)
                    if f"attribute:{ident}" in requested:
                        if ident in attributes or not scalar(value):
                            raise ValueError("Ambiguous or unsupported attribute value")
                        attributes[ident] = value
                for field in requested:
                    ident = attribute_id(field)
                    result[field] = {"status": "observed", "value": attributes[ident]} if ident in attributes else {"status": "missing", "value": None}
            except Exception as exc:
                for field in requested:
                    result[field] = {"status": "not_checked", "value": None, "reason": type(exc).__name__}
        return result
