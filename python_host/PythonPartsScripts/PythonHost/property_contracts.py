"""Dependency-free M4 metadata/presentation contracts, validated before API access."""
import re

from .native_readers import COMPONENT_TYPES
from .query_contracts import SCHEMA, bounded_int, invalid, keys, validate_request

PROPERTIES_SCHEMA = "m4-properties-1"
SELECTION_SCHEMA = "m4-selection-1"
PROBE_SCHEMA = "m4-property-probe-1"


def validate_probe(request):
    keys(request, {"schema_version", "phase", "drawing_file", "attribute_name", "attribute_id", "layer_short_name",
                   "layer_name", "offset", "limit", "candidate_ids",
                   "model_uuid", "view_uuid", "name_contains", "offset", "limit"},
         {"schema_version", "phase"})
    if request["schema_version"] != PROBE_SCHEMA:
        invalid(f"schema_version must be {PROBE_SCHEMA}.")
    if request["phase"] == "wall_sample":
        keys(request, {"schema_version", "phase", "drawing_file", "model_uuid"}, {"schema_version", "phase", "drawing_file"})
        bounded_int(request["drawing_file"], 1, 2147483647, "drawing_file")
        if "model_uuid" in request and (not isinstance(request["model_uuid"], str)
                or not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", request["model_uuid"])
                or request["model_uuid"] == "00000000-0000-0000-0000-000000000000"):
            invalid("model_uuid must name one canonical nonzero model UUID.")
        return
    if request["phase"] == "element_attributes":
        keys(request, {"schema_version", "phase", "drawing_file", "model_uuid", "view_uuid",
                       "name_contains", "offset", "limit"},
             {"schema_version", "phase", "drawing_file", "model_uuid", "view_uuid"})
        bounded_int(request["drawing_file"], 1, 2147483647, "drawing_file")
        for field in ("model_uuid", "view_uuid"):
            value = request[field]
            if (not isinstance(value, str)
                    or not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", value)
                    or value == "00000000-0000-0000-0000-000000000000"):
                invalid(f"{field} must be one canonical nonzero UUID.")
        contains = request.get("name_contains", "")
        if (not isinstance(contains, str) or len(contains) > 64
                or any(ord(char) < 32 for char in contains)):
            invalid("name_contains must be bounded text without control characters.")
        bounded_int(request.get("offset", 0), 0, 255, "offset")
        bounded_int(request.get("limit", 32), 1, 32, "limit")
        return
    if request["phase"] == "layer_catalog":
        keys(request, {"schema_version", "phase", "layer_name", "offset", "limit", "candidate_ids"},
             {"schema_version", "phase", "layer_name"})
        names([request["layer_name"]], 1, 128, "layer_name")
        bounded_int(request.get("offset", 0), 0, 65536, "offset")
        bounded_int(request.get("limit", 8192), 1, 8192, "limit")
        ids = request.get("candidate_ids", [])
        if (not isinstance(ids, list) or len(ids) > 8192
                or any(isinstance(item, bool) or not isinstance(item, int) or not 0 <= item <= 65535 for item in ids)
                or len(set(ids)) != len(ids)):
            invalid("candidate_ids must contain at most 8192 distinct documented layer IDs.")
        return
    required = {"column_sample": "drawing_file", "attribute_name": "attribute_name",
                "attribute_definition": "attribute_id"}.get(request["phase"] if isinstance(request["phase"], str) else "")
    if request["phase"] == "layer_name":
        keys(request, {"schema_version", "phase", "layer_short_name", "layer_name"},
             {"schema_version", "phase"})
        has_short, has_name = "layer_short_name" in request, "layer_name" in request
        if has_short == has_name:
            invalid("Provide exactly one of layer_short_name or layer_name.")
        field = "layer_short_name" if has_short else "layer_name"
        names([request[field]], 1, 16 if has_short else 128, field)
        return
    if required is None:
        invalid("Unknown isolated property probe phase.")
    keys(request, {"schema_version", "phase", required}, {"schema_version", "phase", required})
    if required in ("drawing_file", "attribute_id"):
        bounded_int(request[required], 1, 2147483647, required)
    else:
        names([request[required]], 1, 16 if required == "layer_short_name" else 128, required)


def names(value, limit, length, label):
    if (not isinstance(value, list) or len(value) > limit
            or any(not isinstance(item, str) or not item.strip() or len(item) > length
                   or any(ord(c) < 32 for c in item) for item in value)
            or len(set(value)) != len(value)):
        invalid(f"{label} must contain distinct, bounded nonempty names.")


def validate_properties(request):
    keys(request, {"schema_version", "scope", "native_types", "attribute_names", "layer_short_names", "layer_names",
                   "sample_limit", "metadata_limit", "max_adapters"}, {"schema_version"})
    if request["schema_version"] != PROPERTIES_SCHEMA:
        invalid(f"schema_version must be {PROPERTIES_SCHEMA}.")
    validate_request({"schema_version": SCHEMA, "action": "query", "scope": request.get("scope", "open_drawings"),
                      "max_adapters": request.get("max_adapters", 5000)})
    types = request.get("native_types", ["Column_TypeUUID", "Wall_TypeUUID"])
    if (not isinstance(types, list) or not 1 <= len(types) <= 6
            or any(not isinstance(item, str) or item not in COMPONENT_TYPES for item in types)
            or len(set(types)) != len(types)):
        invalid("native_types must name distinct supported native variants.")
    names(request.get("attribute_names", []), 16, 128, "attribute_names")
    names(request.get("layer_short_names", []), 16, 16, "layer_short_names")
    names(request.get("layer_names", []), 16, 128, "layer_names")
    bounded_int(request.get("sample_limit", 10), 1, 20, "sample_limit")
    bounded_int(request.get("metadata_limit", 64), 1, 128, "metadata_limit")


def validate_selection(request):
    keys(request, {"schema_version", "action", "selection_id", "exclude_model_uuids"}, {"schema_version", "action"})
    if request["schema_version"] != SELECTION_SCHEMA:
        invalid(f"schema_version must be {SELECTION_SCHEMA}.")
    if request["action"] == "clear_highlight":
        keys(request, {"schema_version", "action"}, {"schema_version", "action"})
        return
    if request["action"] not in ("highlight", "select"):
        invalid("action must be highlight, select or clear_highlight.")
    keys(request, {"schema_version", "action", "selection_id", "exclude_model_uuids"}, {"schema_version", "action", "selection_id"})
    if not isinstance(request["selection_id"], str) or not re.fullmatch(r"[0-9a-f]{32}", request["selection_id"]):
        invalid("selection_id must be returned by model_query.")
    ids = request.get("exclude_model_uuids", [])
    if (not isinstance(ids, list) or len(ids) > 100
            or any(not isinstance(item, str) or not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", item) for item in ids)
            or len(set(ids)) != len(ids) or "00000000-0000-0000-0000-000000000000" in ids):
        invalid("Exceptions must be distinct nonzero canonical model UUIDs (at most 100).")
