"""Portable fake resources only; metadata/passive semantics need Allplan evidence."""
import types
import unittest

import test_model_query as query_fixtures


class MetadataTests(unittest.TestCase):
    setUp = query_fixtures.QueryTests.setUp
    prepare_context = query_fixtures.QueryTests.prepare_context
    prepare = query_fixtures.QueryTests.prepare
    adapter = query_fixtures.QueryTests.adapter
    assert_code = query_fixtures.QueryTests.assert_code

    def setup_metadata(self, adapters=None):
        self.prepare(adapters)
        self.base.AttributeService.GetAttributeName.return_value = "Description"
        self.base.AttributeService.GetAttributeType.return_value = 4
        self.base.AttributeService.GetAttributeUnit.return_value = ""
        self.base.AttributeService.GetAttributeControlType.return_value = 1
        self.base.LayerService.GetNameByID.return_value = "Columns"
        self.base.LayerService.GetShortNameByID.return_value = "COL"

    def request(self, **changes):
        return {"schema_version": "m1-query-1", "action": "inspect",
                "scope": {"drawing_files": [101, 102], "include_passive": True, "visibility": "api_select_all"},
                "attribute_ids": [498], **changes}

    def inspect(self, **changes):
        result = self.handler.handle("/model-query", self.request(**changes))
        self.base.CreateElements.assert_not_called()
        self.assertEqual(len(self.handler.model_queries.selections), 0)
        return result

    def test_native_api_arguments_and_raw_passive_omission_are_distinct(self):
        first, passive = self.adapter(attrs=[(498, "Słup")]), self.adapter(number=-102, ident=2)
        self.setup_metadata([passive, first])
        result = self.inspect()
        doc = self.coord.GetInputViewDocument.return_value
        self.base.AttributeService.GetAttributeName.assert_called_once_with(doc, 498)
        self.base.AttributeService.GetAttributeType.assert_called_once_with(doc, 498)
        self.base.AttributeService.GetAttributeControlType.assert_called_once_with(doc, 498)
        self.base.LayerService.GetNameByID.assert_called_once_with(7, 42)
        self.base.LayerService.GetShortNameByID.assert_called_once_with(7, 42)
        self.assertEqual(result["attribute_metadata"][0]["unit_label"], {"status": "observed", "value": ""})
        values = [e["fields"]["attribute:498"] for e in result["sample"]["elements"]]
        self.assertEqual(values, [{"status": "observed", "value": "Słup"}, {"status": "missing", "value": None}])
        self.assertEqual(result["coverage"]["attribute_native_presence"], "not_checked")
        self.assertFalse(result["runtime_verified"])
        self.assertEqual(result["profile_binding"], "not_checked")
        self.assertNotIn("selection_id", result)

    def test_failed_resource_fields_do_not_erase_observed_values_or_bind(self):
        self.setup_metadata([self.adapter(attrs=[(498, None)])])
        self.base.AttributeService.GetAttributeName.side_effect = RuntimeError("unavailable")
        self.base.AttributeService.GetAttributeType.return_value = True
        self.base.AttributeService.GetAttributeUnit.return_value = "x" * 8193
        self.base.LayerService = types.SimpleNamespace()
        result = self.inspect()
        self.assertEqual(result["attribute_metadata"][0]["name"]["status"], "not_checked")
        self.assertEqual(result["attribute_metadata"][0]["type_code"]["status"], "not_checked")
        self.assertEqual(result["coverage"]["metadata_reads_not_checked"], 5)
        self.assertFalse(result["coverage"]["metadata_reads_complete"])
        self.assertEqual(result["sample"]["elements"][0]["fields"]["attribute:498"], {"status": "observed", "value": None})

    def test_sample_is_bounded_sorted_and_layers_cover_only_sample(self):
        self.setup_metadata([self.adapter(ident=i, layer=i) for i in range(4, 0, -1)])
        result = self.inspect(sample_limit=2)
        self.assertEqual(result["counts"]["matched_model_identities"], 4)
        self.assertEqual([r["layer_id"] for r in result["layer_metadata"]], [1, 2])
        self.assertFalse(result["sample"]["is_full_selection"])
        self.assertEqual(result["sample"]["returned"], 2)

    def test_invalid_inspect_contract_never_reads_native_resources(self):
        self.setup_metadata()
        requests = [self.request(sample_limit=x) for x in (0, 21, True)]
        requests += [self.request(attribute_ids=[498, 498]), self.request(predicate={}), self.request(page_size=1),
                     self.request(scope={"drawing_files": [101, 101], "include_passive": True, "visibility": "api_select_all"})]
        missing = self.request()
        del missing["attribute_ids"]
        requests.append(missing)
        for request in requests:
            self.assert_code("invalid_payload", lambda: self.handler.handle("/model-query", request))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.AttributeService.GetAttributeName.assert_not_called()

    def test_resource_change_affects_probe_fingerprint_not_element_source(self):
        self.setup_metadata([self.adapter()])
        first = self.inspect()
        self.base.LayerService.GetNameByID.return_value = "Renamed"
        second = self.inspect()
        self.assertEqual(first["source_fingerprint"], second["source_fingerprint"])
        self.assertNotEqual(first["probe_fingerprint"], second["probe_fingerprint"])

    def test_budget_failure_returns_no_selection_or_partial_success(self):
        self.setup_metadata([self.adapter()])
        now = [0]
        self.handler.model_queries.clock = lambda: now[0]
        def delayed(*args):
            now[0] = 6
            return "Description"
        self.base.AttributeService.GetAttributeName.side_effect = delayed
        self.assert_code("scan_limit_exceeded", self.inspect)
        self.assertEqual(len(self.handler.model_queries.selections), 0)

    def test_unloaded_requested_scope_is_omitted_and_empty_layers_are_not_invented(self):
        self.setup_metadata()
        result = self.inspect(scope={"drawing_files": [999], "include_passive": True, "visibility": "api_select_all"})
        self.assertEqual(result["omissions"], [{"drawing_file": 999, "reason": "unloaded_or_unavailable"}])
        self.assertFalse(result["coverage"]["requested_scope_complete"])
        self.assertEqual(result["layer_metadata"], [])
        self.assertEqual(result["attribute_metadata"][0]["name"]["value"], "Description")
