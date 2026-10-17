"""Client/host parity for the strict, dependency-free M4 edit request contract."""
import importlib
import math
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import TypeAdapter, ValidationError

from allplan_mcp.model_edit_models import ModelEditRequest
HOST = Path(__file__).resolve().parents[1] / "python_host/PythonPartsScripts/PythonHost"


class ModelEditContractTests(unittest.TestCase):
    def setUp(self):
        package = types.ModuleType("test_allplan_host")
        package.__path__ = [str(HOST)]
        modules = {name: None for name in list(sys.modules) if name.startswith("test_allplan_host.")}
        modules["test_allplan_host"] = package
        self.patch = patch.dict(sys.modules, modules)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.contracts = importlib.import_module("test_allplan_host.model_edit_contracts")
        self.errors = importlib.import_module("test_allplan_host.transport")

    def request(self, **updates):
        value = {"schema_version": "m4-model-edit-1", "action": "preview",
                 "predicate": {"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                 "changes": [{"target": {"kind": "attribute", "attribute_id": 20001},
                              "value_type": "text", "value": "Ready", "mode": "upsert"}]}
        value.update(updates)
        return value

    def assert_both_reject(self, request):
        with self.assertRaises(ValidationError):
            TypeAdapter(ModelEditRequest).validate_python(request)
        with self.assertRaises(self.errors.BridgeError):
            self.contracts.validate_request(request)

    def test_default_scope_and_documented_native_types_are_typed(self):
        request = self.request(predicate=None)
        parsed = TypeAdapter(ModelEditRequest).validate_python(request)
        self.contracts.validate_request(request)
        self.assertEqual(parsed.scope, "open_drawings")
        self.assertEqual(parsed.native_types, ["Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID",
                                               "Wall_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID", "WindowDoor_TypeUUID"])

    def test_typed_layer_and_attribute_edits_validate(self):
        request = self.request(changes=[
            {"target": {"kind": "attribute", "name": "MCP_QA_STATUS"}, "value_type": "integer", "value": 3},
            {"target": {"kind": "layer", "short_name": "W1"}},
        ])
        TypeAdapter(ModelEditRequest).validate_python(request)
        self.contracts.validate_request(request)

    def test_invalid_type_values_unknown_keys_predicates_and_missing_bindings_fail_parity(self):
        cases = [
            self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 1}, "value_type": "integer", "value": True}]),
            self.request(changes=[{"target": {"kind": "attribute"}, "value_type": "text", "value": "x"}]),
            self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 1}, "value_type": "real", "value": math.inf}]),
            self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 1}, "value_type": [], "value": "x"}]),
            self.request(unexpected=True),
            self.request(predicate={"not": {"field": "unknown", "op": "eq", "value": "x"}}),
            self.request(changes=[{"target": {"kind": "layer", "short_name": "W1"}, "value": "illegal"}]),
        ]
        for request in cases:
            with self.subTest(request=request):
                self.assert_both_reject(request)

    def test_invalid_scope_and_oversized_changes_reject_before_host_api_access(self):
        self.assert_both_reject(self.request(scope={"drawing_files": [True], "include_passive": False,
                                                    "visibility": "api_select_all"}))
        self.assert_both_reject(self.request(changes=[{"target": {"kind": "attribute", "attribute_id": i + 1},
                                                       "value_type": "text", "value": "x"} for i in range(17)]))
