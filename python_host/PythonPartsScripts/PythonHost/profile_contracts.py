"""Validated read-only demo profile and project-local resource binding."""
from __future__ import annotations

import copy
import json
from uuid import UUID

from .model_context import integer, observation, text
from .model_metadata import bounded_text, enum_code
from .query_contracts import bounded_int, fingerprint, invalid, keys
from .transport import BridgeError


def validate_profile(profile):
    keys(profile, {"schema_version", "profile_id", "profile_version", "target", "units", "scope", "bindings", "rules", "numeric_tolerances"},
         {"schema_version", "profile_id", "profile_version", "target", "units", "scope", "bindings", "rules", "numeric_tolerances"})
    if profile["schema_version"] != "m1-profile-1" or profile["profile_id"] != "native-model-qa-demo" or profile["profile_version"] not in {"1.0.0", "1.0.1", "1.0.2"}:
        invalid("Unsupported demo profile/schema version.")
    try:
        serialized = json.dumps(profile, allow_nan=False)
    except (ValueError, TypeError):
        invalid("Profile must be finite JSON.")
    if len(serialized) > 16384:
        invalid("Profile exceeds 16 KiB.")
    keys(profile["target"], {"allplan_major_version", "native_type_name", "native_type_id"}, {"allplan_major_version", "native_type_name", "native_type_id"})
    target = profile["target"]
    if type(target["allplan_major_version"]) is not int or target["allplan_major_version"] != 2026 or target["native_type_name"] != "Column_TypeUUID":
        invalid("The demo targets ordinary Allplan 2026 columns.")
    try:
        if UUID(target["native_type_id"]).int == 0:
            raise ValueError()
    except (TypeError, ValueError, AttributeError):
        invalid("Profile must declare a nonzero native type GUID.")
    if profile["units"] != {"length": "mm", "angle": "deg", "frame": "model_local"}:
        invalid("Profile units/frame must be explicit mm/deg/model_local.")
    scope = profile["scope"]
    keys(scope, {"drawing_files", "uniqueness_scope", "floor_mapping"}, {"drawing_files", "uniqueness_scope", "floor_mapping"})
    files = scope["drawing_files"]
    if not isinstance(files, list) or not 1 <= len(files) <= 100:
        invalid("Profile must specify 1..100 drawing files.")
    for number in files:
        bounded_int(number, 1, 2147483647, "profile drawing file")
    if len(set(files)) != len(files) or scope["uniqueness_scope"] != ["drawing_file", "element_family"]:
        invalid("Duplicate files or unsupported uniqueness scope.")
    mapping = scope["floor_mapping"]
    if not isinstance(mapping, dict) or len(mapping) > 100 or any(not isinstance(k, str) or not k.isdecimal() or int(k) < 1 or not isinstance(v, str) or not 1 <= len(v) <= 128 for k, v in mapping.items()):
        invalid("Floor mapping must contain bounded explicit file IDs/names.")
    bindings = profile["bindings"]
    keys(bindings, {"attributes", "layers"}, {"attributes", "layers"})
    keys(bindings["attributes"], {"mark", "status"}, {"mark", "status"})
    keys(bindings["layers"], {"structure", "review"}, {"structure", "review"})
    names = []
    for role, resource in bindings["attributes"].items():
        keys(resource, {"name", "data_type", "expected_type_code"}, {"name", "data_type", "expected_type_code"})
        if not isinstance(resource["name"], str) or not 1 <= len(resource["name"]) <= 128 or resource["data_type"] != "string":
            invalid("Demo attributes must be named string resources.")
        bounded_int(resource["expected_type_code"], 1, 255, "attribute type code")
        names.append(resource["name"])
    if len(set(names)) != 2:
        invalid("Mark/status must use distinct attribute definitions.")
    layer_names = []
    for resource in bindings["layers"].values():
        keys(resource, {"short_name"}, {"short_name"})
        if not isinstance(resource["short_name"], str) or not 1 <= len(resource["short_name"]) <= 16:
            invalid("Layer short names must have 1..16 characters.")
        layer_names.append(resource["short_name"])
    if len(set(layer_names)) != 2:
        invalid("Structure/review must use distinct layers.")
    rules = profile["rules"]
    expected = [{"rule_id": "QA-001", "kind": "required_attribute", "attribute": "mark"},
                {"rule_id": "QA-002", "kind": "unique_attribute", "attribute": "mark", "ignore_missing": True},
                {"rule_id": "QA-003", "kind": "required_layer", "expected_layer": "structure"},
                {"rule_id": "QA-004", "kind": "allowed_attribute_values", "attribute": "status", "allowed_values": ["NEW", "EXISTING"], "repair_mapping": {"NWE": "NEW"}}]
    if (rules != expected or not isinstance(rules, list) or type(rules[1].get("ignore_missing")) is not bool
            or profile["numeric_tolerances"] != {"length_mm": 1.0}
            or type(profile["numeric_tolerances"]["length_mm"]) not in (int, float)):
        invalid("Demo rule references/values or tolerance differ from schema m1-profile-1.")
    return profile


def bind_profile(doc, base, profile, context, check_budget):
    validate_profile(profile)
    attributes, layers = {}, {}
    def read(reader, diagnostic):
        check_budget()
        result = observation(reader)
        check_budget()
        if result["status"] == "not_checked":
            result["diagnostic"] = copy.deepcopy(diagnostic)
        return result
    for role, resource in profile["bindings"]["attributes"].items():
        diagnostic = {"requested_name": resource["name"], "stage": "GetAttributeID"}
        def attribute(resource=resource, diagnostic=diagnostic):
            raw_id = integer(base.AttributeService.GetAttributeID(doc, resource["name"]))
            diagnostic["returned_id"] = raw_id
            ident = bounded_int(raw_id, 1, 2147483647, "resolved attribute ID")
            diagnostic["stage"] = "GetAttributeName"
            name = bounded_text(base.AttributeService.GetAttributeName(doc, ident))
            diagnostic["returned_name"] = name
            diagnostic["stage"] = "GetAttributeType"
            code = enum_code(base.AttributeService.GetAttributeType(doc, ident))
            diagnostic["returned_type_code"] = code
            diagnostic["expected_type_code"] = resource["expected_type_code"]
            diagnostic["stage"] = "attribute_round_trip"
            if name != resource["name"] or code != resource["expected_type_code"]:
                raise ValueError("Attribute name/type round-trip mismatch")
            return {"attribute_id": ident, "name": name, "type_code": code, "data_type": "string",
                    "write_eligibility": "not_checked"}
        attributes[role] = read(attribute, diagnostic)
    for role, resource in profile["bindings"]["layers"].items():
        diagnostic = {"requested_short_name": resource["short_name"], "stage": "GetIDByShortName"}
        def layer(resource=resource, diagnostic=diagnostic):
            raw_id = integer(base.LayerService.GetIDByShortName(resource["short_name"], doc))
            diagnostic["returned_id"] = raw_id
            ident = bounded_int(raw_id, 1, 2147483647, "resolved layer ID")
            diagnostic["stage"] = "GetDocumentID"
            doc_id = integer(doc.GetDocumentID())
            diagnostic["stage"] = "GetShortNameByID"
            short_name = bounded_text(base.LayerService.GetShortNameByID(ident, doc_id))
            diagnostic["returned_short_name"] = short_name
            diagnostic["stage"] = "layer_round_trip"
            if short_name != resource["short_name"]:
                raise ValueError("Layer short-name round-trip mismatch")
            diagnostic["stage"] = "GetNameByID"
            name = bounded_text(base.LayerService.GetNameByID(ident, doc_id))
            return {"layer_id": ident, "short_name": short_name,
                    "name": name, "write_eligibility": "not_checked"}
        layers[role] = read(layer, diagnostic)
    complete = all(v["status"] == "observed" for v in list(attributes.values()) + list(layers.values()))
    if complete:
        complete = (len({v["value"]["attribute_id"] for v in attributes.values()}) == 2
                    and len({v["value"]["layer_id"] for v in layers.values()}) == 2)
    project = context["project"]
    verified_context = project["status"] == "observed" and project["value"]["key_status"] == "observed" and context["document_id"]["status"] == "observed"
    complete = complete and verified_context
    result = {"schema_version": "m1-profile-binding-1", "profile_id": profile["profile_id"],
              "profile_version": profile["profile_version"], "profile": copy.deepcopy(profile),
              "status": "bound_for_read" if complete else "not_checked", "read_only": True,
              "attributes": attributes, "layers": layers, "project": copy.deepcopy(project),
              "document_id": copy.deepcopy(context["document_id"]),
              "levels": {"status": "observed", "source": "profile_configuration_not_native_BWS",
                         "value": copy.deepcopy(profile["scope"]["floor_mapping"])},
              "runtime_verified": False, "active_for_write": False, "write_eligibility": "not_checked"}
    result["binding_fingerprint"] = fingerprint(result)
    return result


def require_bound(binding):
    if binding["status"] != "bound_for_read":
        raise BridgeError("profile_unbound", "Demo attribute/layer resources are absent, incompatible or ambiguous. Run action=profile and follow the packaged UI recipe; no query selection was created.", 409)
