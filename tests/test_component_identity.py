"""Bounded component lineage and identity probe safety contracts (fake SDK only)."""
import json
import unittest
import weakref
from unittest.mock import MagicMock

import test_property_probe as fixtures


class ComponentIdentityTests(unittest.TestCase):
    setUp = fixtures.PropertyProbeTests.setUp
    prepare_context = fixtures.PropertyProbeTests.prepare_context
    prepare = fixtures.PropertyProbeTests.prepare
    native = fixtures.PropertyProbeTests.native
    probe = fixtures.PropertyProbeTests.probe
    adapter = fixtures.PropertyProbeTests.adapter
    element = fixtures.PropertyProbeTests.element
    assert_code = fixtures.PropertyProbeTests.assert_code

    def fixture(self, elements=None):
        fixtures.PropertyProbeTests.fixture(self)
        self.native_elements = elements or [self.element()]
        self.base.ElementsSelectService.SelectAllElements.return_value = self.native_elements
        self.parents, self.children = {}, {}
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = MagicMock(
            side_effect=lambda element: self.parents.get(id(element), self.null_adapter()))
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements = MagicMock(
            side_effect=lambda element, include_hidden: self.children.get(id(element), []))
        return self.native_elements

    @staticmethod
    def null_adapter():
        from unittest.mock import MagicMock
        parent = MagicMock()
        parent.IsNull.return_value = True
        return parent

    def identity_probe(self, adapter=None):
        adapter = adapter or self.native_elements[0]
        self.base.GetElement.return_value = type("NativeSlab", (), {})()
        request = {"phase": "component_identity", "drawing_file": 101,
                   "model_uuid": adapter.GetModelElementUUID.return_value,
                   "view_uuid": adapter.GetElementUUID.return_value}
        return self.probe(**request)

    def test_slab_child_identity_remains_distinct_from_multislab_parent(self):
        aggregate = self.element(10)
        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        aggregate.GetModelElementUUID.return_value = "00000000-0000-4000-8000-000000000010"
        aggregate.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000010"
        child = self.element(11)
        child.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        child.GetModelElementUUID.return_value = "00000000-0000-4000-8000-000000000011"
        child.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000011"
        self.fixture([child])
        self.parents[id(child)] = aggregate
        result = self.identity_probe(child)
        self.assertEqual(result["ownership"]["target"]["model_uuid"], child.GetModelElementUUID.return_value)
        self.assertEqual(result["ownership"]["target"]["type_name"], "Slab_TypeUUID")
        self.assertEqual(result["ownership"]["lineage"][1]["model_uuid"], aggregate.GetModelElementUUID.return_value)
        self.assertEqual(result["ownership"]["lineage"][1]["type_name"], "MultiSlab_TypeUUID")
        self.assertNotEqual(result["ownership"]["target"]["model_uuid"], result["ownership"]["terminal_root"]["model_uuid"])
        self.assertEqual(result["physical_target_equivalence"], "not_established")

    def test_identity_probe_reports_exact_target_lineage_and_direct_children_read_only(self):
        root = self.element(20)
        child = self.element(21)
        child.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        child.GetModelElementUUID.return_value = "00000000-0000-4000-8000-000000000021"
        child.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000021"
        self.fixture([root])
        self.children[id(root)] = [child]
        self.parents[id(child)] = root
        report = self.identity_probe(root)
        json.dumps(report, allow_nan=False)
        self.assertTrue(report["ownership"]["parent_chain_complete"])
        self.assertTrue(report["ownership"]["children_complete"])
        self.assertEqual(report["ownership"]["children"][0]["model_uuid"], child.GetModelElementUUID.return_value)
        self.assertEqual(report["native_representation"]["property_owner"], "not_established")
        self.assertFalse(report["property_write_available"])
        self.assertFalse(report["bounds_used_for_identity"])
        root.GetAttributes.assert_not_called()
        root.GetModelGeometry.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.CreateElements.assert_not_called()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()

    def test_differing_wrapper_parent_lineage_conflicts(self):
        first, second = self.element(30), self.element(30)
        parent_a, parent_b = self.element(31), self.element(32)
        first.GetElementUUID.return_value = second.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000030"
        self.fixture([first, second])
        self.parents[id(first)] = parent_a
        self.parents[id(second)] = parent_b
        self.base.GetElement.return_value = object()
        request = {"phase": "component_identity", "drawing_file": 101,
                   "model_uuid": first.GetModelElementUUID.return_value,
                   "view_uuid": first.GetElementUUID.return_value}
        with self.assertRaises(self.module.BridgeError) as error:
            self.probe(**request)
        self.assertEqual(error.exception.code, "probe_scope_unavailable")
        first.GetAttributes.assert_not_called()
        second.GetAttributes.assert_not_called()

    def test_query_component_ownership_is_opt_in_and_not_a_predicate_field(self):
        adapter = self.element()
        self.fixture([adapter])
        self.handler.handle("/model-query", {"schema_version": "m1-query-1", "action": "query",
            "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"}})
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements.assert_not_called()
        self.assertNotIn("component_ownership", self.handler.model_queries.selections[next(iter(self.handler.model_queries.selections))]["snapshot"]["elements"][0]["fields"])
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        result = self.handler.handle("/model-query", {"schema_version": "m1-query-1", "action": "query",
            "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
            "fields": ["component_ownership"]})
        self.assertEqual(result["elements"][0]["fields"]["component_ownership"]["status"], "observed")
        self.assertTrue(self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements.called)
        self.assert_code("invalid_payload", lambda: self.handler.handle("/model-query", {
            "schema_version": "m1-query-1", "action": "query",
            "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
            "predicate": {"field": "component_ownership", "op": "exists"}}))
        self.assertEqual(self.base.ElementsSelectService.SelectAllElements.call_count, 1)

    def test_lineage_cycles_cross_file_parents_and_invalid_children_fail_closed(self):
        from test_allplan_host.component_ownership import observation

        target = self.element(40)
        self.fixture([target])
        self.parents[id(target)] = target
        result = observation(target)
        self.assertEqual(result["status"], "not_checked")
        self.assertIsNone(result["value"])

        other_file = self.element(41, number=102)
        self.parents[id(target)] = other_file
        result = observation(target, include_children=False)
        self.assertEqual(result["status"], "not_checked")

        child = self.element(42)
        unrelated_parent = self.element(43)
        self.parents[id(target)] = self.null_adapter()
        self.children[id(target)] = [child]
        self.parents[id(child)] = unrelated_parent
        result = observation(target)
        self.assertEqual(result["status"], "not_checked")

    def test_child_budget_overflow_is_not_reported_as_complete(self):
        from test_allplan_host.component_ownership import observation

        target = self.element(50)
        self.fixture([target])
        children = [self.element(100 + index) for index in range(257)]
        self.children[id(target)] = children
        for child in children:
            self.parents[id(child)] = target
        result = observation(target)
        self.assertEqual(result["status"], "not_checked")
        self.assertIsNone(result["value"])

    def test_component_identity_contract_rejects_bad_ids_before_document_access(self):
        self.fixture([self.element()])
        valid = {"phase": "component_identity", "drawing_file": 101,
                 "model_uuid": "00000000-0000-4000-8000-000000000001",
                 "view_uuid": "10000000-0000-4000-8000-000000000001"}
        invalid = [
            {key: value for key, value in valid.items() if key != "model_uuid"},
            {**valid, "model_uuid": "not-a-uuid"},
            {**valid, "view_uuid": "00000000-0000-0000-0000-000000000000"},
        ]
        for request in invalid:
            self.assert_code("invalid_payload", lambda request=request: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_unavailable_native_element_or_hierarchy_never_returns_an_owner(self):
        from test_allplan_host.component_ownership import observation

        target = self.element(60)
        self.fixture([target])
        self.parents[id(target)] = RuntimeError("unavailable")
        # A thrown hierarchy read is represented as unavailable evidence.
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda element: (_ for _ in ()).throw(RuntimeError("unavailable"))
            if element is target else self.null_adapter())
        ownership = observation(target)
        self.assertEqual(ownership["status"], "not_checked")
        self.assertIsNone(ownership["value"])

        request = {"phase": "component_identity", "drawing_file": 101,
                   "model_uuid": target.GetModelElementUUID.return_value,
                   "view_uuid": target.GetElementUUID.return_value}
        self.assert_code("probe_scope_unavailable", lambda: self.probe(**request))
        self.base.GetElement.assert_not_called()
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = lambda _: self.null_adapter()
        self.base.GetElement.side_effect = RuntimeError("unavailable")
        self.assert_code("probe_scope_unavailable", lambda: self.probe(**request))
        self.base.GetElement.assert_called_once_with(target)

    def test_native_enumeration_container_lives_through_identity_probe(self):
        target = self.element(70)
        self.fixture([target])
        owners = []

        class NativeOwnerList(list):
            pass

        def enumerate_adapters(_doc):
            owner = NativeOwnerList([target])
            owners.append(weakref.ref(owner))
            return owner

        self.base.ElementsSelectService.SelectAllElements.side_effect = enumerate_adapters
        self.base.GetElement.side_effect = lambda adapter: self.assertIsNotNone(owners[-1]()) or object()
        result = self.identity_probe(target)
        self.assertEqual(result["state"], "observed")
        self.assertIsNone(owners[-1]())


if __name__ == "__main__":
    unittest.main()
