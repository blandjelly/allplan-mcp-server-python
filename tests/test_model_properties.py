"""M4 boundary/regression checks with native fakes, not UI acceptance."""
import json
import unittest

import test_m1_completion as fixtures


class PropertyTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    adapter = fixtures.M1CompletionTests.adapter
    native = fixtures.M1CompletionTests.native
    element = fixtures.M1CompletionTests.element
    assert_code = fixtures.M1CompletionTests.assert_code

    def fixture(self, elements=None):
        self.native(elements or [self.element(attrs=[(83, "R60"), (20001, "S01")]),
                                 self.element(2, name="Wall_TypeUUID", attrs=[(83, "")])])
        names = {83: "Odporność ogniowa", 20001: "MCP_QA_MARK"}
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: next((ident for ident, actual in names.items() if actual == name), -1)
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: names[ident]
        self.base.AttributeService.GetAttributeType.return_value = 67
        self.base.AttributeService.GetAttributeUnit.return_value = ""
        self.base.AttributeService.GetAttributeControlType.return_value = 1
        self.base.AttributeService.GetEnumValues.side_effect = lambda doc, ident: ["R30", "R60"] if ident == 83 else []
        self.base.LayerService.GetIDByShortName.side_effect = lambda name, doc: {"COL": 7, "W1": 8}.get(name, -1)
        self.base.LayerService.GetShortNameByID.side_effect = lambda ident, doc: {7: "COL", 8: "W1"}[ident]
        self.base.LayerService.GetNameByID.side_effect = lambda ident, doc: {7: "Columns", 8: "W1"}[ident]
        self.adapter_module.BaseElementAdapterList = list

    def discover(self, **changes):
        # Test dormant discovery semantics with fakes. The public bridge route
        # is quarantined independently and must never execute this function.
        from test_allplan_host.model_properties import discover_properties
        result = discover_properties(self.handler.model_queries, self.coord.GetInputViewDocument(), self.base,
                                     self.settings, {"schema_version": "m4-properties-1", **changes})
        json.dumps(result, allow_nan=False)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.CreateElements.assert_not_called()
        self.assertFalse(self.handler.model_queries.selections)
        return result

    def query(self, **changes):
        return self.handler.handle("/model-query", {"schema_version": "m1-query-1", "action": "query", **changes})

    def present(self, **changes):
        return self.handler.handle("/model-selection", {"schema_version": "m4-selection-1", "action": "highlight", **changes})

    def test_discovery_exact_native_names_types_units_enums_and_separate_properties(self):
        self.fixture()
        result = self.discover(attribute_names=["Odporność ogniowa", "Fire resistance"], layer_short_names=["W1"])
        self.assertEqual(result["status"], "ready_for_owner_test")
        self.assertFalse(result["usable_for_write"])
        self.assertEqual(result["scope"]["requested"]["drawing_files"], [101, 102, 104])
        resolutions = result["attribute_name_resolution"]
        self.assertEqual(resolutions[0]["resolution"]["value"]["attribute_id"], 83)
        self.assertFalse(resolutions[0]["semantic_alias_verified"])
        self.assertEqual(resolutions[1]["resolution"]["status"], "not_checked")
        self.assertEqual(result["attribute_metadata"][0]["enum_values"]["reason"], "native_enum_probe_not_accepted")
        self.base.AttributeService.GetEnumValues.assert_not_called()
        self.assertEqual(result["attribute_metadata"][0]["type_code"]["value"], 67)
        self.assertEqual(result["layer_name_resolution"][0]["resolution"]["value"], {"layer_id": 8, "short_name": "W1"})
        keys = {item["property_key"] for item in result["support_registry"]}
        self.assertTrue({"native.material", "visual.surface", "organizational.layer", "wall.total_thickness", "attribute:83"} <= keys)
        self.assertTrue(all(item["accepted_on_build"] is None and item["replace"] == "unsupported_by_this_tool" for item in result["support_registry"]))

    def test_metadata_budget_reports_unsampled_definitions_and_failure_does_not_erase_value(self):
        self.fixture()
        result = self.discover(metadata_limit=1, sample_limit=1)
        self.assertEqual(result["coverage"]["attribute_ids_without_metadata"], [20001])
        self.assertFalse(result["coverage"]["metadata_complete_for_discovered_ids"])
        self.assertFalse(result["sample"]["is_full_selection"])
        self.base.AttributeService.GetAttributeType.side_effect = RuntimeError("blocked")
        self.base.AttributeService.GetEnumValues.return_value = []
        self.base.AttributeService.GetEnumValues.side_effect = RuntimeError("blocked")
        result = self.discover()
        self.assertEqual(result["attribute_metadata"][0]["type_code"]["status"], "not_checked")
        self.assertEqual(result["sample"]["elements"][0]["attributes"]["value"][0], {"attribute_id": 83, "value": "R60"})

    def test_mismatched_name_and_layer_round_trips_never_bind(self):
        self.fixture()
        self.base.AttributeService.GetAttributeID.return_value = 83
        self.base.AttributeService.GetAttributeID.side_effect = None
        self.base.LayerService.GetIDByShortName.side_effect = None
        self.base.LayerService.GetIDByShortName.return_value = 7
        result = self.discover(attribute_names=["Fire resistance"], layer_short_names=["W1"])
        self.assertEqual(result["attribute_name_resolution"][0]["resolution"]["status"], "not_checked")
        self.assertEqual(result["layer_name_resolution"][0]["resolution"]["status"], "not_checked")

    def test_attribute_spelling_variants_bind_casefolded_actual_name_without_definition_scan(self):
        self.fixture()
        from test_allplan_host.model_properties import resolve_attribute_name

        variants = {"MCP_QA_MARK": 20001, "mcp_qa_mark": 20001,
                    "Mcp_qa_mark": 20001, "mCP_QA_MARK": 20001}
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: variants.get(name, -1)
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: "MCP_QA_MARK"

        for requested in ("mcp_qa_mark", "MCP_QA_MARK"):
            with self.subTest(requested=requested):
                self.base.AttributeService.GetAttributeID.reset_mock()
                self.base.AttributeService.GetAttributeName.reset_mock()
                ident, actual = resolve_attribute_name(
                    self.coord.GetInputViewDocument(), self.base, requested,
                    lambda _api, callback: callback())
                self.assertEqual((ident, actual), (20001, "MCP_QA_MARK"))
                self.assertIn("MCP_QA_MARK", [call.args[1] for call in self.base.AttributeService.GetAttributeID.call_args_list])
                self.base.AttributeService.GetAttributeType.assert_not_called()
                self.base.AttributeService.GetEnumValues.assert_not_called()

    def test_attribute_case_variant_conflict_is_ambiguous_and_runtime_failure_stops_lookup(self):
        self.fixture()
        from test_allplan_host.model_properties import resolve_attribute_name

        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: {
            "mcp_qa_mark": 20001, "MCP_QA_MARK": 20002}.get(name, -1)
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: {
            20001: "mcp_qa_mark", 20002: "MCP_QA_MARK"}[ident]
        with self.assertRaises(ValueError):
            resolve_attribute_name(self.coord.GetInputViewDocument(), self.base, "mcp_qa_mark",
                                   lambda _api, callback: callback())
        self.assertEqual(self.base.AttributeService.GetAttributeID.call_count, 5)
        self.base.AttributeService.GetAttributeType.assert_not_called()
        self.base.AttributeService.GetEnumValues.assert_not_called()

        self.base.AttributeService.GetAttributeID.reset_mock()
        self.base.AttributeService.GetAttributeID.side_effect = RuntimeError("unexpected native failure")
        with self.assertRaises(RuntimeError):
            resolve_attribute_name(self.coord.GetInputViewDocument(), self.base, "mcp_qa_mark",
                                   lambda _api, callback: callback())
        self.assertEqual(self.base.AttributeService.GetAttributeID.call_count, 1)

    def test_full_layer_name_without_sdk_lookup_reports_catalog_followup(self):
        self.fixture()
        result = self.discover(layer_names=["Ogólne03"])
        resolved = result["layer_full_name_resolution"][0]
        self.assertEqual(resolved["requested_name"], "Ogólne03")
        self.assertTrue(resolved["catalog_scan_required"])
        self.assertEqual(resolved["resolution"]["value"]["status"], "catalog_scan_required")

    def test_absent_null_empty_undefined_failed_and_passive_values_remain_distinct(self):
        elements = [self.element(i, attrs=attrs) for i, attrs in enumerate(([], [(83, None)], [(83, "")], [(83, "<niezdefiniowany>")]), 1)]
        elements += [self.element(5), self.element(6, number=-102)]
        elements[4].GetAttributes.side_effect = RuntimeError("unreadable")
        self.fixture(elements)
        result = self.discover()
        samples = result["sample"]["elements"]
        self.assertEqual([s["attributes"]["value"] for s in samples[:4]], [[], [{"attribute_id": 83, "value": None}], [{"attribute_id": 83, "value": ""}], [{"attribute_id": 83, "value": "<niezdefiniowany>"}]])
        self.assertEqual(samples[4]["attributes"]["status"], "not_checked")
        self.assertIn("not_proven_native_absence", samples[5]["presence_semantics"])

    def test_differing_attribute_representations_are_not_first_view_success(self):
        self.fixture([self.element(attrs=[(83, "R60")]), self.element(attrs=[(83, "R30")])])
        result = self.discover()
        self.assertEqual(result["sample"]["elements"][0]["attributes"]["status"], "not_checked")
        self.assertFalse(result["attribute_metadata"])

    def test_invalid_contracts_reject_before_native_document_and_enumeration(self):
        for route, request in (("/model-properties", {"schema_version": "m4-properties-1", "metadata_limit": True}),
                               ("/model-properties", {"schema_version": "m4-properties-1", "attribute_names": ["x", "x"]}),
                               ("/model-properties", {"schema_version": "m4-properties-1", "scope": "project"}),
                               ("/model-properties", {"schema_version": "m4-properties-1", "native_types": ["Door_TypeUUID"]}),
                               ("/model-selection", {"schema_version": "m4-selection-1", "action": "clear_highlight", "selection_id": "a" * 32})):
            self.assert_code("invalid_payload", lambda: self.handler.handle(route, request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_crashing_discovery_route_is_quarantined_before_all_native_access(self):
        self.assert_code("native_probe_blocked", lambda: self.handler.handle("/model-properties", {"schema_version": "m4-properties-1"}))
        self.coord.GetInputViewDocument.assert_not_called()
        self.settings.AllplanVersion.MainReleaseName.assert_not_called()
        self.assertFalse(self.base.mock_calls)

    def test_open_default_passive_known_unknown_and_inventory_change_invalidate(self):
        self.fixture([self.element(), self.element(2, number=-102)])
        result = self.query()
        self.assertEqual(result["counts"]["matched_model_identities"], 2)
        self.assertTrue(result["scope"]["requested"]["include_passive"])
        self.base.DrawingFileService.return_value.GetFileState.return_value += [(105, 3)]
        self.assert_code("selection_stale", lambda: self.present(selection_id=result["selection_id"]))
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 99)]
        result = self.query()
        self.assertFalse(result["coverage"]["requested_scope_complete"])
        self.assertEqual(result["omissions"], [{"drawing_file": 101, "reason": "unknown_file_state"}])

    def test_highlight_uses_full_selection_all_pages_and_excludes_only_explicit_member(self):
        elements = [self.element(i) for i in range(1, 206)] + [self.element(206, number=-102)]
        self.fixture(elements)
        query = self.query(page_size=1)
        exclude = elements[0].GetModelElementUUID()
        result = self.present(selection_id=query["selection_id"], exclude_model_uuids=[exclude])
        self.assertEqual(result["state"], "submitted")
        self.assertEqual(result["counts"]["matched"], 206)
        self.assertEqual(result["counts"]["submitted_model_identities"], 205)
        self.assertEqual(result["counts"]["not_editable"], 1)
        self.assertIsNone(result["counts"]["selected"])
        self.assertIsNone(result["counts"]["highlighted"])
        submitted = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual(len(submitted), 205)
        self.assertNotIn(id(elements[0]), [id(e) for e in submitted])
        self.module.AllplanIFW.HighlightService.CancelAllHighlightedElements.assert_called_once_with(42)
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.assertEqual(self.handler.model_queries.selections[query["selection_id"]]["request"]["page_size"], 1)

    def test_stale_expired_during_scan_and_absent_exception_never_touch_ui(self):
        self.fixture()
        query = self.query()
        self.assert_code("invalid_payload", lambda: self.present(selection_id=query["selection_id"], exclude_model_uuids=["a0000000-0000-4000-8000-000000000001"]))
        self.base.ElementsSelectService.SelectAllElements.return_value[0].GetCommonProperties.return_value.Layer = 9
        self.assert_code("selection_stale", lambda: self.present(selection_id=query["selection_id"]))
        query = self.query()
        service = self.handler.model_queries
        entry = service.selections[query["selection_id"]]
        now = [entry["created"] + 299]
        service.clock = lambda: now[0]
        original = service._scan
        def expire(*args, **kwargs):
            result = original(*args, **kwargs)
            now[0] += 2
            return result
        service._scan = expire
        self.assert_code("selection_unavailable", lambda: self.present(selection_id=query["selection_id"]))
        self.module.AllplanIFW.HighlightService.CancelAllHighlightedElements.assert_not_called()

    def test_native_select_is_unsupported_and_does_not_substitute_highlight(self):
        self.fixture()
        result = self.present(action="select", selection_id="a" * 32)
        self.assertEqual(result["state"], "unsupported")
        self.assertFalse(result["ui_calls_started"])
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()

    def test_ui_exception_is_unknown_without_retry_and_clear_is_document_wide(self):
        self.fixture()
        query = self.query()
        api = self.module.AllplanIFW.HighlightService
        api.HighlightElements.side_effect = RuntimeError("UI unavailable")
        result = self.present(selection_id=query["selection_id"])
        self.assertEqual(result["state"], "unknown")
        self.assertIsNone(result["counts"]["submitted_model_identities"])
        api.HighlightElements.assert_called_once()
        result = self.present(action="clear_highlight")
        self.assertEqual(result["state"], "submitted")
        self.assertIn("other_sources", result["clear_scope"])
        self.assertEqual(api.CancelAllHighlightedElements.call_count, 2)

    def test_discovery_over_budget_and_duplicate_inventory_have_no_partial_success(self):
        self.fixture()
        element = self.base.ElementsSelectService.SelectAllElements.return_value[0]
        element.GetAttributes.return_value = [(i, "x") for i in range(1, 258)]
        result = self.discover()
        self.assertEqual(result["sample"]["elements"][0]["attributes"]["status"], "not_checked")
        self.handler.model_queries.MAX_SNAPSHOT_BYTES = 512
        self.assert_code("scan_limit_exceeded", self.discover)
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 3), (101, 3)]
        self.assert_code("context_unavailable", self.query)
