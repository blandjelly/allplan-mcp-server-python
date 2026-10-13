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
        if phase == "column_sample":
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
        elif phase == "attribute_name":
            name = request["attribute_name"]
            ident = read("AttributeService.GetAttributeID", lambda: positive_id(base.AttributeService.GetAttributeID(doc, name)))
            result["requested_name"] = name
            result["attribute_id"] = ident
            if ident["status"] == "observed":
                actual = read("AttributeService.GetAttributeName", lambda: bounded_text(base.AttributeService.GetAttributeName(doc, ident["value"])), attribute_id=ident["value"])
                result["name"] = actual
                result["exact_name_round_trip"] = actual["status"] == "observed" and actual["value"] == name
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
        else:
            name = request["layer_short_name"]
            result["requested_short_name"] = name
            ident = read("LayerService.GetIDByShortName", lambda: positive_id(base.LayerService.GetIDByShortName(name, doc)))
            result["layer_id"] = ident
            if ident["status"] == "observed":
                doc_id = read("DocumentAdapter.GetDocumentID", lambda: integer(doc.GetDocumentID()))
                if doc_id["status"] == "observed":
                    actual = read("LayerService.GetShortNameByID", lambda: bounded_text(base.LayerService.GetShortNameByID(ident["value"], doc_id["value"])), layer_id=ident["value"])
                    result["short_name"] = actual
                    result["exact_name_round_trip"] = actual["status"] == "observed" and actual["value"] == name
        result["probe_fingerprint"] = fingerprint(result)
        trace.record("probe", "completed")
        budget()
        return result
