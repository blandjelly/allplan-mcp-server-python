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


def load_office_standard():
    result = copy.deepcopy(STANDARD)
    result["standard_fingerprint"] = hashlib.sha256(json.dumps(STANDARD, sort_keys=True, ensure_ascii=False,
                                                            allow_nan=False, separators=(",", ":")).encode()).hexdigest()
    return result
