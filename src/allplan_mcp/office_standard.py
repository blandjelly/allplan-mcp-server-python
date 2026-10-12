"""One versioned evaluation preset; project resource IDs are resolved freshly."""
import copy
import hashlib
import json

STANDARD = {
    "schema_version": "m3-standard-1",
    "standard_id": "native-model-qa-demo-layer-status",
    "standard_version": "1.0.0",
    "audit_profile_id": "native-model-qa-demo",
    "repairs": [{"rule_id": "QA-003", "value": "structure"}, {"rule_id": "QA-004", "value": "NEW"}],
    "supported_properties": ["layer", "existing_string_status"],
    "deferred_properties": ["mark_assignment", "numbering", "graphical_labels", "file_moves"],
    "read_only": True,
}


MARK_STANDARD = {
    "schema_version": "m3-standard-1",
    "standard_id": "native-model-qa-demo-mark-numbering",
    "standard_version": "1.0.0",
    "audit_profile_id": "native-model-qa-demo",
    "repairs": [],
    "numbering": {"policy_id": "preserve-valid-fill-gaps", "policy_version": "1.0.0",
                  "prefix": "S", "start": 1, "width": 2,
                  "order": ["center_y_mm", "center_x_mm", "center_z_mm", "model_uuid"],
                  "required_rule_id": "QA-001", "unique_rule_id": "QA-002"},
    "supported_properties": ["existing_string_mark", "deterministic_numbering"],
    "deferred_properties": ["graphical_labels", "file_moves", "attribute_append"],
    "read_only": True,
}


def load_office_standard(standard_id=STANDARD["standard_id"]):
    definition = {s["standard_id"]: s for s in (STANDARD, MARK_STANDARD)}[standard_id]
    result = copy.deepcopy(definition)
    result["standard_fingerprint"] = hashlib.sha256(json.dumps(definition, sort_keys=True, ensure_ascii=False,
                                                            allow_nan=False, separators=(",", ":")).encode()).hexdigest()
    return result
