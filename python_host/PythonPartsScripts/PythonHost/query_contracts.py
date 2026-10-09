"""Dependency-free JSON contracts and three-valued predicates for M1 queries."""
from __future__ import annotations

import hashlib
import json
import math
import re

from .transport import BridgeError

SCHEMA = "m1-query-1"
BASIC_FIELDS = {"display_name", "type_name", "type_uuid", "layer_id", "drawing_file", "file_state"}
GEOMETRY_FIELDS = {"bounding_box_mm", "size_x_mm", "size_y_mm", "size_z_mm",
                   "center_x_mm", "center_y_mm", "center_z_mm", "min_z_mm", "max_z_mm"}
FIELDS = BASIC_FIELDS | GEOMETRY_FIELDS | {"hierarchy", "mark", "status"}
OPS = {"eq", "ne", "lt", "lte", "gt", "gte", "in", "contains", "exists", "is_null"}


def invalid(message):
    raise BridgeError("invalid_payload", message)


def keys(value, allowed, required=()):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        invalid(f"Expected object with required keys {sorted(required)} and allowed keys {sorted(allowed)}.")


def bounded_int(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        invalid(f"{label} must be an integer from {low} to {high}.")
    return value


def scalar(value):
    if value is None or isinstance(value, (bool, str)):
        return not isinstance(value, str) or len(value) <= 8192
    return isinstance(value, (int, float)) and math.isfinite(value)


def attribute_id(field):
    match = re.fullmatch(r"attribute:([1-9][0-9]{0,9})", field) if isinstance(field, str) else None
    return int(match[1]) if match else None


def predicate_fields(node, depth=0, budget=None):
    """Validate the entire tree before any API access; never ignore a bad branch."""
    if node is None and depth == 0:
        return set()
    budget = [0] if budget is None else budget
    budget[0] += 1
    if depth > 8 or budget[0] > 64:
        invalid("Predicate must have at most 64 nodes and depth 8.")
    if not isinstance(node, dict):
        invalid("Predicate must be an object.")
    for group in ("all", "any", "not"):
        if group in node:
            keys(node, {group}, {group})
            children = [node[group]] if group == "not" else node[group]
            if not isinstance(children, list) or not 1 <= len(children) <= 64:
                invalid("Predicate groups must contain 1 to 64 predicates.")
            result = set()
            for child in children:
                result.update(predicate_fields(child, depth + 1, budget))
            return result
    keys(node, {"field", "op", "value", "tolerance", "case_sensitive", "trim"}, {"field", "op"})
    field, op = node["field"], node["op"]
    if not isinstance(field, str) or (field not in FIELDS - {"bounding_box_mm", "hierarchy"} and attribute_id(field) is None):
        invalid("Unknown predicate field; use a supported field or attribute:<positive ID>.")
    if attribute_id(field) is not None:
        bounded_int(attribute_id(field), 1, 2147483647, "attribute ID")
    if not isinstance(op, str) or op not in OPS:
        invalid("Unknown predicate operator.")
    if op in {"exists", "is_null"}:
        if set(node) != {"field", "op"}:
            invalid("exists/is_null accept only field and op.")
    else:
        if "value" not in node:
            invalid("This predicate requires a value.")
        values = node["value"] if op == "in" else [node["value"]]
        if not isinstance(values, list) or not 1 <= len(values) <= 100 or not all(scalar(v) for v in values):
            invalid("Predicate values must be bounded finite JSON scalars; in requires a nonempty list.")
        for flag in ("case_sensitive", "trim"):
            if flag in node and not isinstance(node[flag], bool):
                invalid(f"{flag} must be boolean.")
        tolerance = node.get("tolerance", 0)
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or tolerance < 0:
            invalid("tolerance must be a finite nonnegative absolute number.")
        if "tolerance" in node and (op not in {"eq", "ne", "lt", "lte", "gt", "gte"} or not numeric(node["value"])):
            invalid("tolerance is supported only for numeric comparisons.")
        if op in {"lt", "lte", "gt", "gte"} and not numeric(node["value"]):
            invalid("Ordered comparisons require a numeric value.")
        if op == "contains" and not isinstance(node["value"], str):
            invalid("contains requires a string value.")
    return {field}


def validate_request(request):
    if isinstance(request, dict) and request.get("action") == "profile":
        keys(request, {"schema_version", "action", "profile"}, {"schema_version", "action", "profile"})
        if request["schema_version"] != SCHEMA:
            invalid(f"schema_version must be {SCHEMA}.")
        from .profile_contracts import validate_profile
        validate_profile(request["profile"])
        return
    if isinstance(request, dict) and request.get("action") == "inspect":
        keys(request, {"schema_version", "action", "scope", "attribute_ids", "sample_limit", "max_adapters"},
             {"schema_version", "action", "scope", "attribute_ids"})
        bounded_int(request.get("sample_limit", 10), 1, 20, "sample_limit")
        validate_request({**{k: v for k, v in request.items() if k != "sample_limit"}, "action": "query"})
        return
    extensions = {"component_kind", "coordinate_frame", "spatial_box", "profile"}
    keys(request, {"schema_version", "action", "scope", "predicate", "fields", "attribute_ids", "page_size", "max_adapters", "selection_id", "cursor"} | extensions, {"schema_version", "action"})
    if request["schema_version"] != SCHEMA:
        invalid(f"schema_version must be {SCHEMA}.")
    action = request["action"]
    if action == "query":
        keys(request, {"schema_version", "action", "scope", "predicate", "fields", "attribute_ids", "page_size", "max_adapters"} | extensions, {"schema_version", "action", "scope"})
        if request.get("component_kind", "model_identity") not in ("model_identity", "top_level_component"):
            invalid("component_kind must be model_identity or top_level_component.")
        if request.get("coordinate_frame", "model_local") not in ("model_local", "project_global"):
            invalid("coordinate_frame must be model_local or project_global.")
        if "spatial_box" in request:
            from .spatial_contracts import validate_spatial
            validate_spatial(request["spatial_box"])
            if request["spatial_box"]["frame"] != request.get("coordinate_frame", "model_local"):
                invalid("Spatial box frame must equal coordinate_frame.")
        if "profile" in request:
            from .profile_contracts import validate_profile
            validate_profile(request["profile"])
        scope = request["scope"]
        keys(scope, {"drawing_files", "include_passive", "visibility"}, {"drawing_files", "include_passive", "visibility"})
        files = scope["drawing_files"]
        if not isinstance(files, list) or not 1 <= len(files) <= 100:
            invalid("scope.drawing_files must contain 1 to 100 explicit positive IDs.")
        for number in files:
            bounded_int(number, 1, 2147483647, "drawing-file ID")
        if len(set(files)) != len(files):
            invalid("Duplicate drawing-file IDs are not allowed.")
        if not isinstance(scope["include_passive"], bool) or scope["visibility"] != "api_select_all":
            invalid("Explicit include_passive boolean and visibility=api_select_all are required.")
        fields = request.get("fields", ["display_name", "layer_id"])
        if not isinstance(fields, list) or len(fields) > len(FIELDS) or any(not isinstance(f, str) or f not in FIELDS for f in fields) or len(set(fields)) != len(fields):
            invalid("fields must be distinct supported field names.")
        ids = request.get("attribute_ids", [])
        if not isinstance(ids, list) or len(ids) > 32:
            invalid("attribute_ids must be a list of at most 32 IDs.")
        for ident in ids:
            bounded_int(ident, 1, 2147483647, "attribute ID")
        if len(set(ids)) != len(ids):
            invalid("Duplicate attribute IDs are not allowed.")
        needed = predicate_fields(request.get("predicate"))
        needed.update(fields)
        if needed & {"mark", "status"} and "profile" not in request:
            invalid("mark/status fields require an explicit validated profile.")
        needed.update(f"attribute:{ident}" for ident in ids)
        if len({f for f in needed if attribute_id(f) is not None}) > 32:
            invalid("At most 32 distinct attributes may be read.")
        bounded_int(request.get("max_adapters", 5000), 1, 10000, "max_adapters")
    elif action in {"page", "summary"}:
        allowed = {"schema_version", "action", "selection_id"}
        if action == "page":
            allowed.update({"cursor", "page_size"})
        keys(request, allowed, {"schema_version", "action", "selection_id"})
        ident = request["selection_id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[0-9a-f]{32}", ident):
            invalid("selection_id must be the ID returned by model_query.")
        if "cursor" in request and (not isinstance(request["cursor"], str) or not re.fullmatch(r"[0-9a-f]{32}", request["cursor"])):
            invalid("cursor must be a returned opaque cursor; omit it for the first page.")
    else:
        invalid("action must be query, page, summary, inspect or profile.")
    if action != "summary":
        bounded_int(request.get("page_size", 100), 1, 200, "page_size")


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def evaluate(node, fields):
    """True/False/None, where None means not_checked and survives negation."""
    if node is None:
        return True
    if "not" in node:
        value = evaluate(node["not"], fields)
        return None if value is None else not value
    for group in ("all", "any"):
        if group in node:
            values = [evaluate(child, fields) for child in node[group]]
            decisive = False if group == "all" else True
            if decisive in values:
                return decisive
            return None if None in values else not decisive
    observed = fields[node["field"]]
    status, actual, op = observed["status"], observed.get("value"), node["op"]
    if status == "not_checked":
        return None
    if op == "exists":
        return status == "observed"
    if status != "observed":
        return None
    if op == "is_null":
        return actual is None
    def normalized(value):
        if isinstance(value, str):
            value = value.strip() if node.get("trim", False) else value
            value = value if node.get("case_sensitive", True) else value.casefold()
        return value
    actual = normalized(actual)
    expected = node["value"]
    def equals(left, right):
        right = normalized(right)
        if numeric(left) and numeric(right):
            return abs(left - right) <= node.get("tolerance", 0)
        return type(left) is type(right) and left == right
    if op == "in":
        return any(equals(actual, value) for value in expected)
    if op in {"eq", "ne"}:
        equal = equals(actual, expected)
        return equal if op == "eq" else not equal
    if op == "contains":
        return normalized(expected) in actual if isinstance(actual, str) else None
    if not numeric(actual):
        return None
    tolerance = node.get("tolerance", 0)
    if op == "lt":
        return actual < expected - tolerance
    if op == "lte":
        return actual <= expected + tolerance
    if op == "gt":
        return actual > expected + tolerance
    return actual >= expected - tolerance


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()).hexdigest()
