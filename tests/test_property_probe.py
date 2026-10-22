"""Isolated read/trace ordering and quarantine; no native Allplan acceptance."""
import json
import tempfile
import unittest
import weakref
from pathlib import Path

import test_model_properties as fixtures


class PropertyProbeTests(unittest.TestCase):
    setUp = fixtures.PropertyTests.setUp
    prepare_context = fixtures.PropertyTests.prepare_context
    prepare = fixtures.PropertyTests.prepare
    adapter = fixtures.PropertyTests.adapter
    native = fixtures.PropertyTests.native
    element = fixtures.PropertyTests.element
    assert_code = fixtures.PropertyTests.assert_code

    def fixture(self):
        fixtures.PropertyTests.fixture(self)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "native.jsonl"
        self.handler.property_probes.trace_path = self.path

    def probe(self, **request):
        result = self.handler.handle("/model-property-probe", {"schema_version": "m4-property-probe-1", **request})
        json.dumps(result, allow_nan=False)
        self.base.CreateElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.AttributeService.GetEnumValues.assert_not_called()
        return result

    def records(self):
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()]

    def test_sample_reads_one_foreground_column_without_metadata_enum_or_UI(self):
        self.fixture()
        elements = self.base.ElementsSelectService.SelectAllElements.return_value
        def raw(_state):
            records = self.records()
            self.assertEqual(records[-1]["api"], "BaseElementAdapter.GetAttributes(ReadAll)")
            self.assertEqual(records[-1]["state"], "started")
            return [(83, "R60")]
        elements[0].GetAttributes.side_effect = raw
        result = self.probe(phase="column_sample", drawing_file=101)
        self.assertEqual(result["sample"]["attributes"]["value"], [{"attribute_id": 83, "value": "R60"}])
        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        elements[1].GetAttributes.assert_not_called()  # wall excluded
        self.base.AttributeService.GetAttributeName.assert_not_called()
        self.assertEqual(self.records()[-1]["state"], "completed")
        self.assertFalse(self.handler.model_queries.selections)

    def test_unwritable_trace_rejects_before_document_or_property_call(self):
        self.fixture()
        self.handler.property_probes.trace_path = Path(self.directory.name)
        self.assert_code("probe_trace_unavailable", lambda: self.probe(phase="attribute_definition", attribute_id=83))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.AttributeService.GetAttributeName.assert_not_called()

    def test_native_enumeration_owner_lives_through_reader_and_not_in_JSON_cache(self):
        self.fixture()
        root = self.base.ElementsSelectService.SelectAllElements.return_value[0]
        owners = []
        class NativeOwnerList(list):
            pass
        def enumerate_roots(_doc):
            owner = NativeOwnerList([root])
            owners.append(weakref.ref(owner))
            return owner
        self.base.ElementsSelectService.SelectAllElements.side_effect = enumerate_roots
        def attributes(_state):
            self.assertIsNotNone(owners[-1](), "Native container died before the captured adapter reader")
            return [(83, "R60")]
        root.GetAttributes.side_effect = attributes
        self.probe(phase="column_sample", drawing_file=101)
        self.assertIsNone(owners[-1]())
        self.assertFalse(self.handler.model_queries.selections)

    def test_definition_stops_at_failed_method_and_preserves_native_boundary(self):
        self.fixture()
        self.base.AttributeService.GetAttributeType.side_effect = RuntimeError("fake native failure")
        result = self.probe(phase="attribute_definition", attribute_id=83)
        self.assertEqual(result["metadata"]["GetAttributeType"]["status"], "not_checked")
        self.assertEqual(set(result["metadata"]), {"GetAttributeName", "GetAttributeType"})
        self.base.AttributeService.GetAttributeUnit.assert_not_called()
        self.base.AttributeService.GetAttributeControlType.assert_not_called()
        records = self.records()
        failed = [item for item in records if item["state"] == "failed"]
        self.assertEqual(failed[0]["api"], "AttributeService.GetAttributeType")
        self.assertEqual(failed[0]["attribute_id"], 83)
        self.assertNotIn("fake native failure", self.path.read_text())

    def test_name_round_trip_mismatch_cannot_bind_semantic_alias(self):
        self.fixture()
        self.base.AttributeService.GetAttributeID.side_effect = None
        self.base.AttributeService.GetAttributeID.return_value = 83
        result = self.probe(phase="attribute_name", attribute_name="Fire resistance")
        self.assertFalse(result["exact_name_round_trip"])
        self.assertFalse(result["semantic_alias_verified"])
        self.base.AttributeService.GetAttributeType.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_native_base_exception_leaves_failed_call_trace_and_never_continues(self):
        self.fixture()
        self.base.AttributeService.GetAttributeName.side_effect = SystemExit("fake callback escape")
        with self.assertRaises(SystemExit):
            self.probe(phase="attribute_definition", attribute_id=83)
        self.assertEqual(self.records()[-1]["state"], "failed")
        self.assertEqual(self.records()[-1]["exception_type"], "SystemExit")
        self.base.AttributeService.GetAttributeType.assert_not_called()

    def test_polish_initial_case_miss_resolves_without_alias_or_catalog(self):
        self.fixture()
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: 981 if name == "Wartość U" else -1
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: "Wartość U"
        result = self.probe(phase="attribute_name", attribute_name="wartość U")
        self.assertEqual(result["attribute_id"], {"status": "observed", "value": 981})
        self.assertFalse(result["exact_name_round_trip"])
        self.assertTrue(result["case_insensitive_name_round_trip"])
        self.assertFalse(result["semantic_alias_verified"])
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_uppercase_project_attribute_resolves_from_lowercase_request_after_minus_one(self):
        self.fixture()
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: (
            20001 if name == "MCP_QA_MARK" else -1)
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: "MCP_QA_MARK"

        result = self.probe(phase="attribute_name", attribute_name="mcp_qa_mark")

        self.assertEqual(result["attribute_id"], {"status": "observed", "value": 20001})
        self.assertEqual(result["name"], {"status": "observed", "value": "MCP_QA_MARK"})
        self.assertTrue(result["case_insensitive_name_round_trip"])
        self.assertFalse(result["semantic_alias_verified"])
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.AttributeService.GetAttributeType.assert_not_called()
        self.base.AttributeService.GetEnumValues.assert_not_called()

    def test_conflicting_case_variants_are_not_checked_and_runtime_error_stops_search(self):
        self.fixture()
        calls = [0]
        def conflicting_lookup(doc, name):
            calls[0] += 1
            if calls[0] == 1:  # Initial exact lookup misses; fallback checks every spelling.
                return -1
            return {"mcp_qa_mark": 20001, "MCP_QA_MARK": 20002}.get(name, -1)
        self.base.AttributeService.GetAttributeID.side_effect = conflicting_lookup
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: {
            20001: "mcp_qa_mark", 20002: "MCP_QA_MARK"}[ident]
        ambiguous = self.probe(phase="attribute_name", attribute_name="mcp_qa_mark")
        self.assertEqual(ambiguous["attribute_id"]["status"], "not_checked")
        self.base.AttributeService.GetAttributeType.assert_not_called()
        self.base.AttributeService.GetEnumValues.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

        self.base.AttributeService.GetAttributeID.reset_mock()
        self.base.AttributeService.GetAttributeID.side_effect = RuntimeError("unexpected native failure")
        self.base.AttributeService.GetAttributeName.reset_mock()
        failed = self.probe(phase="attribute_name", attribute_name="mcp_qa_mark")
        self.assertEqual(failed["attribute_id"], {"status": "not_checked", "value": None,
                                                    "reason": "RuntimeError"})
        self.assertEqual(self.base.AttributeService.GetAttributeID.call_count, 1)
        self.base.AttributeService.GetAttributeName.assert_not_called()
        self.base.AttributeService.GetAttributeType.assert_not_called()

    def test_invalid_phase_fields_and_passive_scope_reject_without_attribute_reads(self):
        self.fixture()
        for request in ({"phase": "attribute_definition", "attribute_id": True},
                        {"phase": "column_sample", "drawing_file": 101, "attribute_id": 83},
                        {"phase": "attribute_name", "attribute_name": ""}, {"phase": "enum"}):
            self.assert_code("invalid_payload", lambda: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.assertFalse(self.path.exists())
        self.assert_code("probe_scope_unavailable", lambda: self.probe(phase="column_sample", drawing_file=102))
        self.base.ElementsSelectService.SelectAllElements.return_value[0].GetAttributes.assert_not_called()

    def test_trace_capacity_blocks_following_calls_without_pruning_old_evidence(self):
        self.fixture()
        data = b'x' * (1024 * 1024)
        self.path.write_bytes(data)
        self.assert_code("probe_trace_unavailable", lambda: self.probe(phase="layer_name", layer_short_name="W1"))
        self.assertEqual(self.path.read_bytes(), data)
        self.base.LayerService.GetIDByShortName.assert_not_called()

    def test_layer_name_probe_preserves_legacy_short_lookup_and_full_name_guidance(self):
        self.fixture()
        result = self.probe(phase="layer_name", layer_short_name="W1")
        self.assertEqual(result["resolution"]["status"], "resolved")
        self.assertEqual(result["resolution"]["candidates"][0]["short_name"], "W1")
        result = self.probe(phase="layer_name", layer_name="Ogólne03")
        self.assertEqual(result["resolution"]["status"], "catalog_scan_required")
        self.assertEqual(result["next_action"]["request"]["phase"], "layer_catalog")
        self.assertEqual(result["next_action"]["request"]["layer_name"], "Ogólne03")

    def test_layer_catalog_page_emits_all_exact_candidates_and_confirmation(self):
        self.fixture()
        result = self.probe(phase="layer_catalog", layer_name="Columns", offset=7, limit=2)
        catalog = result["catalog"]
        self.assertEqual(catalog["status"], "confirmation_required")
        self.assertEqual(catalog["candidate_ids"], [7])
        self.assertEqual(catalog["candidates"][0]["short_name"], "COL")
        self.assertEqual(result["next_action"]["action"], "ask_user_confirmation")
        self.assertTrue(result["next_action"]["search_incomplete"])
        continuation = result["next_action"]["continue_search"]
        self.assertEqual(continuation["request"]["offset"], 9)
        self.assertEqual(continuation["request"]["candidate_ids"], [7])
        self.assertNotIn("schema_version", continuation["request"])
        self.assertFalse(catalog["scan"]["complete"])

    def test_layer_name_contract_rejects_multiple_spellings_and_oversized_catalog_page(self):
        self.fixture()
        for request in (
            {"phase": "layer_name", "layer_name": "W1", "layer_short_name": "W1"},
            {"phase": "layer_name"},
            {"phase": "layer_catalog", "layer_name": "W1", "limit": 8193},
        ):
            self.assert_code("invalid_payload", lambda request=request: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()
