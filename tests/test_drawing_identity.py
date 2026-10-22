"""Bounded drawing-wide adapter identity reads (fake SDK only)."""
import json
import unittest

import test_component_identity as fixtures


class DrawingIdentityTests(unittest.TestCase):
    setUp = fixtures.ComponentIdentityTests.setUp
    prepare_context = fixtures.ComponentIdentityTests.prepare_context
    prepare = fixtures.ComponentIdentityTests.prepare
    adapter = fixtures.ComponentIdentityTests.adapter
    native = fixtures.ComponentIdentityTests.native
    probe = fixtures.ComponentIdentityTests.probe
    element = fixtures.ComponentIdentityTests.element
    assert_code = fixtures.ComponentIdentityTests.assert_code

    def fixture(self, elements=None):
        fixtures.ComponentIdentityTests.fixture(self, elements)
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 3)]
        self.base.GetElement.side_effect = lambda adapter: type("NativeSlab", (), {})()
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda _adapter: self.null_adapter())
        return self.native_elements

    @staticmethod
    def null_adapter():
        from unittest.mock import MagicMock
        parent = MagicMock()
        parent.IsNull.return_value = True
        return parent

    def drawing_probe(self, **changes):
        return self.probe(phase="drawing_identity", drawing_file=101, **changes)

    def test_complete_scan_is_paginated_and_reports_only_direct_identity_evidence(self):
        slab = self.element(1)
        slab.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        aggregate = self.element(2)
        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        self.fixture([slab, aggregate])

        result = self.drawing_probe(limit=1)
        json.dumps(result, allow_nan=False)
        self.assertEqual(result["state"], "observed", result)
        self.assertEqual(result["scope"]["included_files"][0]["drawing_file"], 101)
        self.assertTrue(result["coverage"]["requested_scope_complete"])
        self.assertEqual(result["counts"], {"model_identities": 2, "view_identities": 2,
                                            "returned": 1, "observed": 1, "not_checked": 0})
        self.assertEqual(result["pagination"], {"offset": 0, "limit": 1, "total": 2,
                                               "next_offset": 1, "has_more": True})
        entry = result["entries"][0]
        self.assertEqual(entry["ref"]["drawing_file"], 101)
        self.assertEqual(entry["ref"]["model_uuid"], slab.GetModelElementUUID.return_value)
        self.assertEqual(entry["view_uuid"], slab.GetElementUUID.return_value)
        self.assertEqual(entry["ownership"]["status"], "observed")
        self.assertEqual(entry["native_representation"]["status"], "observed")
        self.assertEqual(entry["native_representation"]["value"]["python_type"], "NativeSlab")
        self.assertEqual(entry["native_representation"]["value"]["property_owner"], "not_established")
        slab.GetAttributes.assert_not_called()
        aggregate.GetAttributes.assert_not_called()
        slab.GetModelGeometry.assert_not_called()
        aggregate.GetModelGeometry.assert_not_called()
        slab.GetCommonProperties.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.CreateElements.assert_not_called()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()

    def test_passive_or_incomplete_scope_fails_closed(self):
        self.fixture([self.element()])
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 4), (102, 5)]
        self.assert_code("probe_scope_unavailable", self.drawing_probe)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_conflicting_wrappers_for_same_model_and_view_stay_not_checked(self):
        first, second = self.element(7), self.element(7)
        first.GetElementUUID.return_value = second.GetElementUUID.return_value = (
            "10000000-0000-4000-8000-000000000007")
        self.fixture([first, second])
        parent_a, parent_b = self.element(8), self.element(9)
        self.parents[id(first)] = parent_a
        self.parents[id(second)] = parent_b
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda adapter: self.parents.get(id(adapter), self.null_adapter()))
        self.base.GetElement.side_effect = lambda adapter: type(
            "NativeA" if adapter is first else "NativeB", (), {})()

        result = self.drawing_probe()
        self.assertEqual(result["counts"]["model_identities"], 1)
        self.assertEqual(result["counts"]["view_identities"], 1)
        entry = result["entries"][0]
        self.assertEqual(entry["representation_count"], 2)
        self.assertEqual(entry["native_representation"]["status"], "not_checked")
        self.assertEqual(entry["native_representation"]["reason"], "identity_representation_conflict")
        self.assertEqual(entry["ownership"]["status"], "not_checked")
        self.assertEqual(entry["ownership"]["reason"], "identity_representation_conflict")

    def test_slab_child_keeps_multislab_parent_lineage_in_drawing_inventory(self):
        child = self.element(11)
        child.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        aggregate = self.element(10)
        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        self.fixture([child])
        self.parents[id(child)] = aggregate
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda adapter: aggregate if adapter is child else self.null_adapter())

        result = self.drawing_probe()
        entry = result["entries"][0]
        self.assertEqual(entry["ownership"]["status"], "observed")
        ownership = entry["ownership"]["value"]
        self.assertEqual(ownership["target"]["model_uuid"], child.GetModelElementUUID.return_value)
        self.assertEqual(ownership["lineage"][1]["model_uuid"], aggregate.GetModelElementUUID.return_value)
        self.assertEqual(ownership["lineage"][1]["type_name"], "MultiSlab_TypeUUID")

    def test_multiple_views_and_empty_offset_page_have_explicit_pagination(self):
        first = self.adapter(ident=15, view=15)
        second = self.adapter(ident=15, view=16)
        first.IsNull.return_value = second.IsNull.return_value = False
        self.fixture([first, second])
        self.base.GetElement.side_effect = lambda _adapter: type("NativeSlab", (), {})()

        page = self.drawing_probe(limit=1)
        self.assertEqual(page["counts"]["model_identities"], 1)
        self.assertEqual(page["counts"]["view_identities"], 2)
        self.assertTrue(page["pagination"]["has_more"])
        empty = self.drawing_probe(offset=9999, limit=1)
        self.assertEqual(empty["state"], "observed")
        self.assertEqual(empty["entries"], [])
        self.assertEqual(empty["counts"]["returned"], 0)
        self.assertEqual(empty["counts"]["observed"], 0)
        self.assertIsNone(empty["pagination"]["next_offset"])

    def test_native_representation_failure_is_entry_local_and_redacts_exception_text(self):
        target = self.element(12)
        self.fixture([target])
        self.base.GetElement.side_effect = RuntimeError("secret SDK detail")

        result = self.drawing_probe()
        observation = result["entries"][0]["native_representation"]
        self.assertEqual(observation["status"], "not_checked")
        self.assertEqual(observation["diagnostic"], {"stage": "native_representation", "error_type": "RuntimeError"})
        self.assertNotIn("secret SDK detail", json.dumps(result))

    def test_scan_budget_error_propagates_without_partial_page(self):
        self.fixture([self.element(18)])
        ticks = [0]

        def advance_clock():
            ticks[0] += 11
            return ticks[0]

        self.handler.model_queries.clock = advance_clock
        self.assert_code("scan_limit_exceeded", self.drawing_probe)

    def test_bad_pagination_is_rejected_before_document_or_enumeration(self):
        self.fixture([self.element()])
        valid = {"phase": "drawing_identity", "drawing_file": 101}
        for request in ({**valid, "offset": True}, {**valid, "offset": 10000},
                        {**valid, "limit": 0}, {**valid, "limit": 33},
                        {"phase": "drawing_identity", "offset": 0}):
            self.assert_code("invalid_payload", lambda request=request: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()


if __name__ == "__main__":
    unittest.main()
