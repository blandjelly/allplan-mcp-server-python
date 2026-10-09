"""Dependency-free, versioned M2 validation; run before native reads."""
from __future__ import annotations

import json
import math
import re

from .profile_contracts import validate_profile
from .query_contracts import bounded_int, invalid, keys, validate_request

SCHEMA = "m2-audit-1"
DIMENSIONS = {"size_x_mm", "size_y_mm", "size_z_mm"}


def normalized(value, policy):
    if not isinstance(value, str):
        return value
    value = value.strip() if policy["trim"] else value
    return value if policy["case_sensitive"] else value.casefold()


def bounded_string(value, limit, label):
    if not isinstance(value, str) or not 1 <= len(value) <= limit:
        invalid(f"{label} must be a nonempty string of at most {limit} characters.")


def validate_audit_profile(profile):
    required = {"schema_version", "profile_id", "profile_version", "read_profile", "string_policies", "rules"}
    keys(profile, required, required)
    if profile["schema_version"] != "m2-profile-1" or profile["profile_id"] != "native-model-qa-demo":
        invalid("Unsupported audit profile/schema.")
    if not isinstance(profile["profile_version"], str) or not re.fullmatch(r"[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}", profile["profile_version"]):
        invalid("Audit profile_version must be a bounded semantic version.")
    try:
        size = len(json.dumps(profile, ensure_ascii=False, allow_nan=False).encode())
    except (TypeError, ValueError, OverflowError):
        invalid("Audit profile must be finite JSON.")
    if size > 64 * 1024:
        invalid("Audit profile exceeds 64 KiB.")
    validate_profile(profile["read_profile"])
    policies = profile["string_policies"]
    keys(policies, {"mark", "status"}, {"mark", "status"})
    for policy in policies.values():
        keys(policy, {"trim", "case_sensitive", "missing"}, {"trim", "case_sensitive", "missing"})
        if type(policy["trim"]) is not bool or type(policy["case_sensitive"]) is not bool:
            invalid("String normalization flags must be boolean.")
        missing = policy["missing"]
        keys(missing, {"absent", "null", "empty", "literals"}, {"absent", "null", "empty", "literals"})
        if any(type(missing[k]) is not bool for k in ("absent", "null", "empty")):
            invalid("Missing-value flags must be boolean.")
        literals = missing["literals"]
        if not isinstance(literals, list) or len(literals) > 20:
            invalid("Missing literals must contain at most 20 strings.")
        for value in literals:
            bounded_string(value, 128, "Missing literal")
        if len({normalized(v, policy) for v in literals}) != len(literals):
            invalid("Duplicate normalized missing literals.")
    rules = profile["rules"]
    if not isinstance(rules, list) or not 1 <= len(rules) <= 32:
        invalid("Audit profile must contain 1..32 rules.")
    ids = set()
    common = {"rule_id", "kind", "severity", "remedy"}
    for rule in rules:
        if not isinstance(rule, dict):
            invalid("Audit rules must be objects.")
        kind = rule.get("kind")
        extra = {"required_attribute": {"attribute"},
                 "unique_attribute": {"attribute", "ignore_missing", "uniqueness_scope"},
                 "required_layer": {"expected_layer"},
                 "allowed_attribute_values": {"attribute", "allowed_values"},
                 "dimension_range": {"field", "min_mm", "max_mm", "tolerance_mm"}}.get(kind) if isinstance(kind, str) else None
        if extra is None:
            invalid("Unsupported audit rule kind.")
        keys(rule, common | extra, common | extra)
        ident = rule["rule_id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Z][A-Z0-9-]{0,31}", ident) or ident in ids:
            invalid("Rule IDs must be distinct bounded uppercase identifiers.")
        ids.add(ident)
        if rule["severity"] not in ("info", "warning", "error"):
            invalid("Unsupported severity.")
        bounded_string(rule["remedy"], 512, "Remedy")
        if "attribute" in rule and rule["attribute"] not in ("mark", "status"):
            invalid("Audit attribute must reference a typed profile binding.")
        if kind == "unique_attribute":
            if type(rule["ignore_missing"]) is not bool or rule["uniqueness_scope"] != ["drawing_file", "element_family"]:
                invalid("Uniqueness requires explicit drawing_file/element_family scope and boolean ignore_missing.")
        if kind == "required_layer" and rule["expected_layer"] not in ("structure", "review"):
            invalid("Unknown layer binding.")
        if kind == "allowed_attribute_values":
            values = rule["allowed_values"]
            if not isinstance(values, list) or not 1 <= len(values) <= 100:
                invalid("Allowed values must contain 1..100 strings.")
            policy = policies[rule["attribute"]]
            for value in values:
                bounded_string(value, 128, "Allowed value")
                if is_missing_string(value, policy):
                    invalid("Allowed values cannot also mean missing.")
            if len({normalized(v, policy) for v in values}) != len(values):
                invalid("Duplicate normalized allowed values.")
        if kind == "dimension_range":
            if not isinstance(rule["field"], str) or rule["field"] not in DIMENSIONS:
                invalid("Dimension rule requires an axis-aligned size_*_mm field.")
            for key in ("min_mm", "max_mm", "tolerance_mm"):
                value = rule[key]
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    invalid("Dimensions/tolerance must be finite nonnegative mm numbers.")
            if rule["min_mm"] > rule["max_mm"]:
                invalid("Dimension range is reversed.")
    return profile


def is_missing_string(value, policy):
    value = normalized(value, policy)
    return ((policy["missing"]["empty"] and value == "")
            or value in {normalized(v, policy) for v in policy["missing"]["literals"]})


def query_request(request):
    profile = request["profile"]
    fields = {"mark", "status", "layer_id", "file_state", "bounding_box_mm"}
    fields.update(rule["field"] for rule in selected_rules(request) if rule["kind"] == "dimension_range")
    return {"schema_version": "m1-query-1", "action": "query", "scope": request["scope"],
            "profile": profile["read_profile"], "component_kind": "top_level_component",
            "coordinate_frame": "model_local", "fields": sorted(fields),
            "max_adapters": request.get("max_adapters", 5000)}


def selected_rules(request):
    ids = request.get("rule_ids")
    return [r for r in request["profile"]["rules"] if ids is None or r["rule_id"] in ids]


def validate_audit_request(request):
    keys(request, {"schema_version", "scope", "profile", "rule_ids", "max_adapters"}, {"schema_version", "scope", "profile"})
    if request["schema_version"] != SCHEMA:
        invalid(f"schema_version must be {SCHEMA}.")
    validate_audit_profile(request["profile"])
    if "rule_ids" in request:
        ids = request["rule_ids"]
        if not isinstance(ids, list) or not 1 <= len(ids) <= 32 or any(not isinstance(v, str) for v in ids):
            invalid("rule_ids must contain 1..32 distinct configured rule IDs.")
        if len(set(ids)) != len(ids) or not set(ids) <= {r["rule_id"] for r in request["profile"]["rules"]}:
            invalid("Duplicate or unknown rule IDs.")
    bounded_int(request.get("max_adapters", 5000), 1, 10000, "max_adapters")
    validate_request(query_request(request))
    if not set(request["scope"]["drawing_files"]) <= set(request["profile"]["read_profile"]["scope"]["drawing_files"]):
        invalid("Requested audit files exceed the explicit profile scope.")
