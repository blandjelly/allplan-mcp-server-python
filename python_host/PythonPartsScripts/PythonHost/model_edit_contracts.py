"""Dependency-free m4-model-edit-1 request validation."""
from __future__ import annotations

import math
import re

from .query_contracts import attribute_id, bounded_int, invalid, keys, predicate_fields, scalar
from .repair_contracts import validate_repair_request

SCHEMA = "m4-model-edit-1"
DEFAULT_NATIVE_TYPES = ["Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID",
                       "Wall_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID", "WindowDoor_TypeUUID"]
EDIT_TYPES = {"auto", "text", "integer", "real", "boolean", "enum"}
MODES = {"replace", "upsert", "add"}
# Exact values emitted by Allplan for an explicitly undefined stored attribute.
# Never normalize arbitrary strings or parse them as numbers.
UNDEFINED_ATTRIBUTE_VALUES = frozenset({"<niezdefiniowany>", "<undefined>"})


def is_undefined_attribute_value(value):
    return isinstance(value, str) and value in UNDEFINED_ATTRIBUTE_VALUES


UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")


def _query_scope(scope):
    from .query_contracts import validate_request as validate_query
    validate_query({"schema_version": "m1-query-1", "action": "query", "scope": scope,
                    "fields": [], "attribute_ids": []})


def _preview(request):
    keys(request, {"schema_version", "action", "scope", "native_types", "predicate", "attribute_ids",
                   "attribute_read_mode", "changes", "exclude_model_uuids", "max_adapters", "exact_target"}, {"schema_version", "action"})
    scope = request.get("scope", "open_drawings")
    _query_scope(scope)
    native_types = request.get("native_types", DEFAULT_NATIVE_TYPES)
    from .native_readers import COMPONENT_TYPES
    if (not isinstance(native_types, list) or len(native_types) > 16
            or any(not isinstance(item, str) or not item.strip() or len(item) > 128 for item in native_types)
            or len(set(native_types)) != len(native_types)):
        invalid("native_types must be a distinct list of at most 16 bounded names.")
    if any(item not in COMPONENT_TYPES for item in native_types):
        invalid("native_types must name documented supported native variants; use semantic family predicates to narrow them.")
    predicate = request.get("predicate")
    criterion_fields = predicate_fields(predicate)
    if criterion_fields & {"mark", "status"}:
        invalid("Use explicit attribute IDs instead of profile-only mark/status aliases.")
    referenced_criteria = {attribute_id(f) for f in criterion_fields if attribute_id(f) is not None}
    ids = request.get("attribute_ids", [])
    if not isinstance(ids, list) or len(ids) > 32:
        invalid("attribute_ids must contain at most 32 IDs.")
    for ident in ids:
        bounded_int(ident, 1, 2147483647, "attribute ID")
    if len(set(ids)) != len(ids):
        invalid("Duplicate attribute IDs are not allowed.")
    read_mode = request.get("attribute_read_mode", "stored")
    if not isinstance(read_mode, str) or read_mode not in {"stored", "all_and_computable"}:
        invalid("attribute_read_mode must be stored or all_and_computable.")
    bounded_int(request.get("max_adapters", 5000), 1, 10000, "max_adapters")
    changes = request.get("changes")
    if not isinstance(changes, list) or not 1 <= len(changes) <= 16:
        invalid("changes must contain 1 to 16 edits.")
    referenced_ids = set(ids) | referenced_criteria
    for change in changes:
        if not isinstance(change, dict):
            invalid("Each change must be an object.")
        target = change.get("target")
        if not isinstance(target, dict):
            invalid("Each change requires a target object.")
        if target.get("kind") == "delete":
            keys(change, {"target"}, {"target"})
            keys(target, {"kind"}, {"kind"})
            if len(changes) != 1:
                invalid("Deletion must be the only change in a plan.")
        elif target.get("kind") == "native_material":
            keys(change, {"target", "value"}, {"target", "value"})
            keys(target, {"kind", "tier_index"}, {"kind", "tier_index"})
            if type(target["tier_index"]) is not int or target["tier_index"] != 1:
                invalid("Native material requires explicit tier_index=1 (single-tier Wall or exact native element properties).")
            value = change["value"]
            if not isinstance(value, str) or not value.strip() or len(value) > 255 or any(ord(c) < 32 for c in value):
                invalid("Native material must be an exact nonempty string of at most 255 characters.")
            if len(changes) != 1:
                invalid("Native material must be the only change in a plan.")
        elif target.get("kind") == "attribute":
            keys(change, {"target", "value_type", "value", "mode"}, {"target", "value"})
            keys(target, {"kind", "attribute_id", "name", "property_owner"}, {"kind"})
            if "property_owner" in target and target["property_owner"] != "selected_element":
                invalid("property_owner must be selected_element; no automatic owner redirection is supported.")
            if "attribute_id" not in target and "name" not in target:
                invalid("Attribute target requires an attribute_id or exact name.")
            if "attribute_id" in target:
                ident = bounded_int(target["attribute_id"], 1, 2147483647, "attribute_id")
                referenced_ids.add(ident)
            if "name" in target and (not isinstance(target["name"], str) or not target["name"].strip() or len(target["name"]) > 128):
                invalid("Attribute name must be a bounded nonempty exact name.")
            value_type = change.get("value_type", "auto")
            value = change["value"]
            if not isinstance(value_type, str) or value_type not in EDIT_TYPES or not scalar(value):
                invalid("Attribute value must be a bounded JSON scalar with a supported value_type.")
            valid = ((value_type == "auto" and value is not None)
                     or (value_type == "text" and isinstance(value, str))
                     or (value_type == "enum" and isinstance(value, str) and bool(value))
                     or (value_type == "integer" and isinstance(value, int) and not isinstance(value, bool))
                     or (value_type == "real" and isinstance(value, (int, float)) and not isinstance(value, bool))
                     or (value_type == "boolean" and isinstance(value, bool)))
            if not valid or (isinstance(value, float) and not math.isfinite(value)):
                invalid("Attribute value must match value_type and be finite.")
            mode = change.get("mode", "replace")
            if not isinstance(mode, str) or mode not in MODES:
                invalid("mode must be replace, upsert or add.")
        elif target.get("kind") == "layer":
            keys(change, {"target"}, {"target"})
            keys(target, {"kind", "short_name", "name", "expected_layer_id", "expected_name"}, {"kind"})
            if ("expected_layer_id" in target) != ("expected_name" in target):
                invalid("A confirmed layer requires both expected_layer_id and expected_name.")
            if "expected_layer_id" in target:
                bounded_int(target["expected_layer_id"], 0, 65535, "expected_layer_id")
                expected = target["expected_name"]
                if not isinstance(expected, str) or not expected.strip() or len(expected) > 512:
                    invalid("expected_name must be the bounded exact API layer name.")
            if ("short_name" in target) == ("name" in target):
                invalid("Layer target requires exactly one short_name or exact name.")
            field = "short_name" if "short_name" in target else "name"
            limit = 16 if field == "short_name" else 128
            name = target[field]
            if not isinstance(name, str) or not name.strip() or len(name) > limit:
                invalid(f"Layer {field} must be a bounded nonempty string.")
        else:
            invalid("target.kind must be attribute, layer, native_material or delete.")
    if "exact_target" in request:
        t = request["exact_target"]
        keys(t, {"drawing_file", "model_uuid", "view_uuid", "parent_ref"},
             {"drawing_file", "model_uuid", "view_uuid", "parent_ref"})
        bounded_int(t["drawing_file"], 1, 2147483647, "drawing_file")
        p = t["parent_ref"]
        keys(p, {"model_uuid", "view_uuid"}, {"model_uuid", "view_uuid"})
        for ref in (t, p):
            for k in ("model_uuid", "view_uuid"):
                if (not isinstance(ref[k], str) or not UUID.fullmatch(ref[k])
                        or ref[k] == "00000000-0000-0000-0000-000000000000"):
                    invalid("Exact target references require canonical nonzero UUIDs.")
        if (t["model_uuid"] == p["model_uuid"] or native_types != ["Slab_TypeUUID"]
                or predicate is not None or request.get("exclude_model_uuids") or ids
                or len(changes) != 1 or changes[0]["target"]["kind"] != "native_material"
                or not isinstance(scope, dict) or scope["drawing_files"] != [t["drawing_file"]]
                or scope["include_passive"]):
            invalid("exact_target requires one foreground Slab native-material edit without criteria or exclusions.")
    if len(referenced_ids) > 32:
        invalid("At most 32 distinct attribute IDs may be read or edited.")
    exceptions = request.get("exclude_model_uuids", [])
    if (not isinstance(exceptions, list) or len(exceptions) > 100
            or any(not isinstance(item, str) or not UUID.fullmatch(item) for item in exceptions)
            or len(set(exceptions)) != len(exceptions)):
        invalid("exclude_model_uuids must contain at most 100 distinct UUIDs.")
    if "00000000-0000-0000-0000-000000000000" in exceptions:
        invalid("Exceptions must name nonzero model UUIDs.")


def validate_request(request):
    if not isinstance(request, dict) or request.get("schema_version") != SCHEMA:
        invalid("Expected m4-model-edit-1 request.")
    action = request.get("action")
    if action == "preview":
        _preview(request)
        return
    if isinstance(action, str) and action in {"highlight", "revalidate", "apply", "recover"}:
        converted = {**request, "schema_version": "m3-repair-1"}
        if action == "highlight":
            converted["action"] = "revalidate"
        if action == "recover":
            digest = converted.pop("reconciliation_hash", None)
            ack = converted.pop("acknowledgement", None)
            if digest is not None or ack is not None:
                if (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
                        or ack != "reviewed_material_reconciliation"):
                    invalid("Reconciliation needs its reviewed hash and acknowledgement together.")
        validate_repair_request(converted)
        if "workflow_kind" in request or "evaluation_stop" in request:
            invalid("No alternate workflow or diagnostic interruption on this route.")
        if action == "apply" and request["acknowledgement"] != "disposable_copy_reviewed_plan":
            invalid("Use disposable_copy_reviewed_plan for model edits.")
        return
    invalid("Action must be preview, highlight, revalidate, apply or recover.")
