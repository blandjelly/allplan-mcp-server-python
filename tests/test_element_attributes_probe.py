"""One-identity attribute listing boundaries; no native Allplan acceptance."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.property_models import PropertyProbeRequest
import test_model_properties as fixtures


class ElementAttributesProbeTests(unittest.TestCase):
    setUp = fixtures.PropertyTests.setUp
    prepare_context = fixtures.PropertyTests.prepare_context
    prepare = fixtures.PropertyTests.prepare
    adapter = fixtures.PropertyTests.adapter
    native = fixtures.PropertyTests.native
    element = fixtures.PropertyTests.element
    assert_code = fixtures.PropertyTests.assert_code

    def setup_element(self, attrs=None):
        self.root = self.element(attrs=attrs or [(83, "R60"), (20001, 7), (20002, True)])
        self.native([self.root])
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.handler.property_probes.trace_path = Path(self.directory.name) / "native.jsonl"
        names = {83: "Klasa odporności ogniowej", 20001: "Opis", 20002: "Aktywny"}
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: names[ident]
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: next(
            (ident for ident, actual in names.items() if actual == name), -1)
        types = SimpleNamespace(String=101, Integer=102, Double=103, Boolean=104)
        self.base.AttributeService.AttributeType = types
        type_by_id = {83: types.String, 20001: types.Integer, 20002: types.Boolean}
        self.base.AttributeService.GetAttributeType.side_effect = lambda doc, ident: type_by_id[ident]
        self.adapter_module.BaseElementAdapterList = list

    def request(self, **updates):
        return {"schema_version": "m4-property-probe-1", "phase": "element_attributes",
                "drawing_file": 101, "model_uuid": "00000000-0000-4000-8000-000000000001",
                "view_uuid": "10000000-0000-4000-8000-000000000001", **updates}

    def probe(self, **updates):
        result = self.handler.handle("/model-property-probe", self.request(**updates))
        json.dumps(result, allow_nan=False)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.AttributeService.GetAttributeControlType.assert_not_called()
        self.base.AttributeService.GetAttributeUnit.assert_not_called()
        self.base.AttributeService.GetEnumValues.assert_not_called()
        return result

    def test_exact_identity_lists_readall_values_searches_and_pages_with_runtime_types(self):
        self.setup_element()
        result = self.probe(name_contains="odp", limit=1)
        self.assertEqual(result["total_matches"], 1)
        self.assertTrue(result["listing_complete"])
        self.assertEqual(result["attributes"][0]["name"]["value"], "Klasa odporności ogniowej")
        self.assertEqual(result["attributes"][0]["supported_scalar_value_types"], ["text"])
        self.assertEqual(result["writable"], "not_established")
        self.assertEqual(self.root.GetAttributes.call_count, 1)

        self.base.AttributeService.GetAttributeName.reset_mock()
        first = self.probe(limit=2)
        self.assertEqual(first["total_matches"], 3)
        self.assertEqual(first["next_offset"], 2)
        self.assertFalse(first["listing_complete"])
        second = self.probe(offset=2, limit=2)
        self.assertEqual([item["attribute_id"] for item in first["attributes"] + second["attributes"]],
                         [83, 20001, 20002])
        self.assertTrue(second["listing_complete"])
        self.assertEqual(second["attributes"][0]["supported_scalar_value_types"], ["boolean"])

    def test_wrong_model_or_view_stops_before_raw_attribute_read(self):
        self.setup_element()
        with self.assertRaises(self.module.BridgeError) as error:
            self.probe(view_uuid="10000000-0000-4000-8000-000000000099")
        self.assertEqual(error.exception.code, "probe_scope_unavailable")
        self.root.GetAttributes.assert_not_called()

    def test_equivalent_wrappers_for_one_root_view_are_accepted(self):
        self.setup_element()
        wrapper = self.element(ident=9, attrs=[(83, "R60"), (20001, 7), (20002, True)])
        wrapper.GetModelElementUUID.return_value = self.root.GetModelElementUUID.return_value
        wrapper.GetElementUUID.return_value = self.root.GetElementUUID.return_value
        wrapper.GetElementAdapterType.return_value.GetGuid.return_value = self.root.GetElementAdapterType.return_value.GetGuid.return_value
        wrapper.GetDisplayName.return_value = self.root.GetDisplayName.return_value
        self.base.ElementsSelectService.SelectAllElements.return_value.append(wrapper)
        result = self.probe()
        self.assertEqual(result["total_matches"], 3)
        self.assertEqual([row["attribute_id"] for row in result["attributes"]], [83, 20001, 20002])
        self.assertEqual(result["adapter_attribute_consistency"], "consistent")
        self.root.GetAttributes.assert_called_once()
        wrapper.GetAttributes.assert_called_once()

    def test_distinct_wrappers_with_different_attributes_are_not_used(self):
        self.setup_element()
        wrapper = self.element(ident=9, attrs=[(83, "R30"), (20001, 7), (20002, True)])
        wrapper.GetModelElementUUID.return_value = self.root.GetModelElementUUID.return_value
        wrapper.GetElementUUID.return_value = self.root.GetElementUUID.return_value
        wrapper.GetElementAdapterType.return_value.GetGuid.return_value = self.root.GetElementAdapterType.return_value.GetGuid.return_value
        wrapper.GetDisplayName.return_value = self.root.GetDisplayName.return_value
        self.base.ElementsSelectService.SelectAllElements.return_value.append(wrapper)
        result = self.probe()
        self.assertEqual(result["attributes"]["status"], "not_checked")
        self.assertEqual(result["attributes"]["reason"], "conflicting_adapter_attributes")
        self.assertEqual(result["adapter_attribute_consistency"], "conflicting")
        self.assertFalse(result["listing_complete"])
        self.root.GetAttributes.assert_called_once()
        wrapper.GetAttributes.assert_called_once()

    def test_repeated_same_adapter_instance_is_read_once(self):
        self.setup_element()
        self.base.ElementsSelectService.SelectAllElements.return_value.append(self.root)
        result = self.probe()
        self.assertEqual(result["adapter_attribute_representation_count"], 1)
        self.assertEqual(result["attributes"][0]["attribute_id"], 83)
        self.root.GetAttributes.assert_called_once()

    def test_multiple_views_or_conflicting_root_fields_still_block(self):
        for conflict in ("view", "display_name"):
            with self.subTest(conflict=conflict):
                self.setup_element()
                wrapper = self.element(ident=9, attrs=[(83, "R60"), (20001, 7), (20002, True)])
                wrapper.GetModelElementUUID.return_value = self.root.GetModelElementUUID.return_value
                wrapper.GetElementAdapterType.return_value.GetGuid.return_value = self.root.GetElementAdapterType.return_value.GetGuid.return_value
                if conflict == "view":
                    wrapper.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000099"
                else:
                    wrapper.GetElementUUID.return_value = self.root.GetElementUUID.return_value
                    wrapper.GetDisplayName.return_value = "Different component"
                self.base.ElementsSelectService.SelectAllElements.return_value.append(wrapper)
                with self.assertRaises(self.module.BridgeError) as error:
                    self.probe()
                self.assertEqual(error.exception.code, "probe_scope_unavailable")
                self.root.GetAttributes.assert_not_called()
                wrapper.GetAttributes.assert_not_called()

    def test_unfiltered_metadata_failures_keep_raw_rows_and_allow_pagination(self):
        self.setup_element()
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: (
            (_ for _ in ()).throw(RuntimeError("unavailable")) if ident == 20001
            else {83: "Klasa odporności ogniowej", 20002: "Aktywny"}[ident])
        first = self.probe(limit=2)
        self.assertEqual([row["attribute_id"] for row in first["attributes"]], [83, 20001])
        self.assertEqual(first["attributes"][1]["value"], 7)
        self.assertEqual(first["attributes"][1]["name"]["status"], "not_checked")
        self.assertEqual(first["total_matches_status"], "observed")
        self.assertEqual(first["next_offset"], 2)
        self.assertFalse(first["listing_complete"])
        second = self.probe(offset=2, limit=2)
        self.assertEqual([row["attribute_id"] for row in second["attributes"]], [20002])
        self.assertIsNone(second["next_offset"])
        self.assertTrue(second["listing_complete"])
        self.assertFalse(second["metadata_complete"])

    def test_filtered_listing_reports_unknown_name_coverage(self):
        self.setup_element()
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: (
            (_ for _ in ()).throw(RuntimeError("unavailable")) if ident == 20001
            else {83: "Klasa odporności ogniowej", 20002: "Aktywny"}[ident])
        result = self.probe(name_contains="not-present")
        self.assertEqual(result["attributes"], [])
        self.assertEqual(result["filter_unknown_name_count"], 1)
        self.assertEqual(result["total_matches_status"], "not_checked")
        self.assertFalse(result["listing_complete"])

    def test_invalid_identity_and_unbounded_page_reject_before_document_access(self):
        self.setup_element()
        self.coord.GetInputViewDocument.reset_mock()
        for request in (self.request(model_uuid="00000000-0000-0000-0000-000000000000"),
                        self.request(offset=256), self.request(limit=33),
                        self.request(name_contains="bad\nfilter")):
            self.assert_code("invalid_payload", lambda: self.handler.handle("/model-property-probe", request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.root.GetAttributes.assert_not_called()

    def test_mcp_request_model_accepts_phase_and_rejects_null_identity(self):
        adapter = TypeAdapter(PropertyProbeRequest)
        parsed = adapter.validate_python({key: value for key, value in self.request(name_contains="fire").items()
                                          if key != "schema_version"})
        self.assertEqual(parsed.phase, "element_attributes")
        with self.assertRaises(ValidationError):
            adapter.validate_python({key: value for key, value in self.request(
                view_uuid="00000000-0000-0000-0000-000000000000").items() if key != "schema_version"})

