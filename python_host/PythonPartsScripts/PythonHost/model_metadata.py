"""Bounded read-only resource probe; no profile activation or native objects escape."""
from __future__ import annotations

import json

from .model_context import integer, observation, text
from .query_contracts import FIELDS, SCHEMA, fingerprint
from .transport import BridgeError


def bounded_text(value):
    value = text(value)
    if len(value) > 8192:
        raise ValueError("Metadata text exceeds 8192 characters")
    return value


def enum_code(value):
    # Native enum integer codes only; never serialize a native repr or guess labels.
    if isinstance(value, (bool, str, float)):
        raise ValueError("Expected a native enum or integer")
    return integer(int(value))


def inspect_metadata(service, doc, base, settings, request):
    started = service.clock()
    query = {"schema_version": SCHEMA, "action": "query", "scope": request["scope"],
             "fields": sorted(FIELDS), "attribute_ids": request["attribute_ids"],
             "max_adapters": request.get("max_adapters", 5000)}
    snapshot = service._scan(doc, base, settings, query)

    def check_budget():
        if service.clock() - started >= service.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Metadata inspection exceeded its time budget; no complete report was returned. Narrow the scope or attribute IDs.", 409)

    def read(reader):
        check_budget()
        result = observation(reader)
        check_budget()
        return result

    attributes = []
    for ident in sorted(request["attribute_ids"]):
        attributes.append({"attribute_id": ident,
                           "name": read(lambda: bounded_text(base.AttributeService.GetAttributeName(doc, ident))),
                           "type_code": read(lambda: enum_code(base.AttributeService.GetAttributeType(doc, ident))),
                           "unit_label": read(lambda: bounded_text(base.AttributeService.GetAttributeUnit(doc, ident))),
                           "control_type_code": read(lambda: enum_code(base.AttributeService.GetAttributeControlType(doc, ident)))})
    elements = snapshot["elements"][:request.get("sample_limit", 10)]
    doc_id = read(lambda: integer(doc.GetDocumentID()))
    layers = []
    layer_ids = sorted({element["fields"]["layer_id"]["value"] for element in elements
                        if element["fields"]["layer_id"]["status"] == "observed"})
    for ident in layer_ids:
        def layer_read(method_name):
            if doc_id["status"] != "observed":
                return {"status": "not_checked", "value": None, "reason": "document_id_unavailable"}
            return read(lambda: bounded_text(getattr(base.LayerService, method_name)(ident, doc_id["value"])))
        # AttributeService takes a DocumentAdapter; LayerService takes its integer ID.
        layers.append({"layer_id": ident,
                       "name": layer_read("GetNameByID"),
                       "short_name": layer_read("GetShortNameByID")})
    observations = [value for record in attributes + layers for value in record.values() if isinstance(value, dict)]
    observations += [value for element in elements for value in element["fields"].values()]
    observations.append(doc_id)
    failed = sum(value["status"] == "not_checked" for value in observations)
    result = {"schema_version": SCHEMA, "action": "inspect", "read_only": True,
              "runtime_verified": False, "usable_for_write": False, "profile_binding": "not_checked",
              "query_session_id": service.session_id, "document_id": doc_id,
              "source_fingerprint": snapshot["source_fingerprint"],
              "scope": snapshot["scope"], "counts": snapshot["counts"],
              "coverage": {**snapshot["coverage"], "metadata_reads_complete": failed == 0,
                           "metadata_reads_not_checked": failed, "layer_metadata_scope": "sampled_elements_only",
                           "attribute_native_presence": "not_checked", "attribute_unit_conversion": "not_checked"},
              "omissions": snapshot["omissions"], "not_checked_samples": snapshot["not_checked_samples"],
              "sample": {"limit": request.get("sample_limit", 10), "returned": len(elements),
                         "is_full_selection": len(elements) == len(snapshot["elements"]),
                         "order": "drawing_file_then_model_uuid", "elements": elements},
              "attribute_metadata": attributes, "layer_metadata": layers,
              "raw_attribute_semantics": "missing means absent from GetAttributes(ReadAll) response; passive native absence is not established"}
    result["probe_fingerprint"] = fingerprint(result)
    if len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode()) > service.MAX_SNAPSHOT_BYTES:
        raise BridgeError("scan_limit_exceeded", "Metadata report exceeded the 4 MiB budget; no complete report was returned.", 409)
    check_budget()
    return result
