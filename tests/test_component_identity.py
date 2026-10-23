"""Bounded component lineage and identity probe safety contracts (fake SDK only)."""
import json
import unittest
import weakref
from unittest.mock import MagicMock

from pydantic import ValidationError

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

    def attribute_evidence_probe(self, adapter=None, *, ids=(83,), include_parent=False, **overrides):
        self.handler.model_queries.clock = lambda: 0.0
        adapter = adapter or self.native_elements[0]
        self.base.GetElement.return_value = type("NativeSlab", (), {})()
        self.base.eAttibuteReadState.ReadAll = "ReadAll"
        self.base.eAttibuteReadState.ReadAllAndComputable = "ReadAllAndComputable"
        self.base.AttributeService.AttributeType = type(
            "AttributeType", (), {"String": 11, "Integer": 12, "Date": 13, "Vector": 14})
        if self.base.AttributeService.GetAttributeType.side_effect is None:
            self.base.AttributeService.GetAttributeType.side_effect = lambda _doc, ident: {
                83: 11, 84: 13, 85: 999}[ident]
        request = {"phase": "attribute_evidence", "drawing_file": 101,
                   "model_uuid": adapter.GetModelElementUUID.return_value,
                   "view_uuid": adapter.GetElementUUID.return_value,
                   "attribute_ids": list(ids), "include_parent": include_parent}
        request.update(overrides)
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

    def test_identity_probe_does_not_require_layer_or_display_name_consensus(self):
        first, second = self.element(30), self.element(30)
        first.GetElementUUID.return_value = second.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000030"
        first.GetCommonProperties.return_value.Layer = 7
        second.GetCommonProperties.return_value.Layer = 8
        first.GetDisplayName.return_value = "Slab representation A"
        second.GetDisplayName.return_value = "Slab representation B"
        self.fixture([first, second])
        result = self.identity_probe(first)
        self.assertEqual(result["state"], "observed")
        self.assertEqual(result["representation_count"], 2)
        self.assertFalse(result["property_write_available"])
        first.GetCommonProperties.assert_not_called()
        second.GetCommonProperties.assert_not_called()
        first.GetDisplayName.assert_not_called()
        second.GetDisplayName.assert_not_called()

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

    def test_native_read_failures_report_bounded_stage_and_exception_type(self):
        from test_allplan_host.component_ownership import observation

        target = self.element(44)
        self.fixture([target])
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda _element: (_ for _ in ()).throw(RuntimeError("secret SDK detail")))
        result = observation(target)
        self.assertEqual(result, {"status": "not_checked", "value": None,
                                  "reason": "component_read_unavailable",
                                  "diagnostic": {"stage": "parent", "error_type": "RuntimeError"}})
        self.assertNotIn("secret SDK detail", json.dumps(result))
        json.dumps(result, allow_nan=False)

        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda _element: self.null_adapter())
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements.side_effect = (
            lambda *_: (_ for _ in ()).throw(LookupError("private detail")))
        result = observation(target)
        self.assertEqual(result, {"status": "not_checked", "value": None,
                                  "reason": "component_read_unavailable",
                                  "diagnostic": {"stage": "children", "error_type": "LookupError"}})
        self.assertNotIn("private detail", json.dumps(result))

    def test_structural_validation_failures_have_stable_reasons_and_stages(self):
        from test_allplan_host.component_ownership import observation

        target, child = self.element(45), self.element(46)
        self.fixture([target])
        self.children[id(target)] = [child]
        self.parents[id(target)] = self.null_adapter()
        self.parents[id(child)] = self.element(47)
        result = observation(target)
        self.assertEqual(result["reason"], "component_child_owner_mismatch")
        self.assertEqual(result["diagnostic"], {"stage": "child_parent_identity", "error_type": "ValueError"})

        self.parents[id(target)] = target
        self.children[id(target)] = []
        result = observation(target)
        self.assertEqual(result["reason"], "component_parent_cycle")
        self.assertEqual(result["diagnostic"], {"stage": "parent_identity", "error_type": "ValueError"})

    def test_child_parent_view_difference_is_recorded_but_logical_owner_must_match(self):
        from test_allplan_host.component_ownership import observation

        target = self.element(48)
        child = self.element(49, name="AttributeContainer_TypeUUID")
        parent_view = self.element(50)
        parent_view.GetModelElementUUID.return_value = target.GetModelElementUUID.return_value
        parent_view.GetElementAdapterType.return_value.GetTypeName.return_value = (
            target.GetElementAdapterType.return_value.GetTypeName.return_value)
        parent_view.GetElementAdapterType.return_value.GetGuid.return_value = (
            target.GetElementAdapterType.return_value.GetGuid.return_value)
        self.fixture([target])
        self.children[id(target)] = [child]
        self.parents[id(child)] = parent_view

        result = observation(target)
        self.assertEqual(result["status"], "observed")
        edge = result["value"]["child_parent_edges"][0]
        self.assertEqual(edge["child"]["model_uuid"], child.GetModelElementUUID.return_value)
        self.assertEqual(edge["parent"]["model_uuid"], target.GetModelElementUUID.return_value)
        self.assertNotEqual(edge["parent"]["view_uuid"], target.GetElementUUID.return_value)

        parent_view.GetModelElementUUID.return_value = self.element(51).GetModelElementUUID.return_value
        rejected = observation(target)
        self.assertEqual(rejected["status"], "not_checked")
        self.assertEqual(rejected["reason"], "component_child_owner_mismatch")

    def test_alternate_view_logical_self_child_and_ancestry_cycle_are_rejected(self):
        from test_allplan_host.component_ownership import observation

        target = self.element(52)
        alternate = self.element(53)
        alternate.GetModelElementUUID.return_value = target.GetModelElementUUID.return_value
        alternate.GetElementAdapterType.return_value.GetTypeName.return_value = (
            target.GetElementAdapterType.return_value.GetTypeName.return_value)
        alternate.GetElementAdapterType.return_value.GetGuid.return_value = (
            target.GetElementAdapterType.return_value.GetGuid.return_value)
        self.fixture([target])
        self.parents[id(target)] = alternate
        cycle = observation(target, include_children=False)
        self.assertEqual(cycle["status"], "not_checked")
        self.assertEqual(cycle["reason"], "component_parent_cycle")

        self.parents[id(target)] = self.null_adapter()
        self.children[id(target)] = [alternate]
        self.parents[id(alternate)] = target
        self_child = observation(target)
        self.assertEqual(self_child["status"], "not_checked")
        self.assertEqual(self_child["reason"], "component_child_owner_mismatch")

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

    def test_attribute_evidence_keeps_exact_identity_metadata_and_read_modes_separate(self):
        target = self.element(80, attrs=[(83, "stored"), (84, object())])
        self.fixture([target])
        target.GetAttributes.side_effect = lambda mode: (
            [(83, "stored"), (84, [1, 2])] if mode == "ReadAll"
            else [(83, "computed"), (84, [3, 4])])
        self.base.AttributeService.GetAttributeType.side_effect = lambda _doc, ident: {83: 11, 84: 13}[ident]
        result = self.attribute_evidence_probe(target, ids=(83, 84))
        representation = result["representations"][0]["target"]["value"]
        self.assertEqual(result["state"], "observed")
        self.assertEqual(result["ref"]["model_uuid"], target.GetModelElementUUID.return_value)
        self.assertEqual(result["view_uuid"], target.GetElementUUID.return_value)
        self.assertEqual(result["attribute_ids"], [83, 84])
        self.assertEqual(result["metadata"][0]["type_binding"]["value"]["matching_sdk_members"], ["String"])
        self.assertEqual(result["metadata"][1]["type_binding"]["value"]["matching_sdk_members"], ["Date"])
        self.assertEqual(representation["read_modes"]["ReadAll"]["value"][0]["value"], "stored")
        self.assertEqual(representation["read_modes"]["ReadAllAndComputable"]["value"][0]["value"], "computed")
        self.assertEqual([item["attribute_id"] for item in representation["read_modes"]["ReadAll"]["value"]], [83, 84])
        self.assertEqual(representation["read_modes"]["ReadAll"]["value"][1]["value"], [1, 2])
        self.assertEqual(representation["read_modes"]["ReadAll"]["value"][1]["encoding"], "json_sequence")
        self.assertEqual(representation["read_modes"]["ReadAll"]["value"][1]["member_types"],
                         [{"module": "builtins", "name": "int"}, {"module": "builtins", "name": "int"}])
        self.assertFalse(result["property_write_available"])
        self.assertEqual(result["setter_calls_started"], 0)

    def test_wrong_exact_reference_stops_before_any_attribute_read(self):
        target = self.element(81)
        self.fixture([target])
        self.base.GetElement.return_value = object()
        request = {"phase": "attribute_evidence", "drawing_file": 101,
                   "model_uuid": "00000000-0000-4000-8000-000000000099",
                   "view_uuid": target.GetElementUUID.return_value, "attribute_ids": [83]}
        self.assert_code("probe_scope_unavailable", lambda: self.probe(**request))
        target.GetAttributes.assert_not_called()

    def test_attribute_evidence_invalid_null_refs_duplicate_and_boolean_ids_precede_document(self):
        self.fixture([self.element(82)])
        valid = {"phase": "attribute_evidence", "drawing_file": 101,
                 "model_uuid": self.native_elements[0].GetModelElementUUID.return_value,
                 "view_uuid": self.native_elements[0].GetElementUUID.return_value, "attribute_ids": [83]}
        for request in ({**valid, "model_uuid": "00000000-0000-0000-0000-000000000000"},
                        {**valid, "view_uuid": "00000000-0000-0000-0000-000000000000"},
                        {**valid, "attribute_ids": [83, 83]}, {**valid, "attribute_ids": [True]}):
            with self.subTest(request=request):
                self.assert_code("invalid_payload", lambda request=request: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        from allplan_mcp.property_models import AttributeEvidenceProbeInput
        public_valid = {**valid, "model_uuid": "00000000-0000-4000-8000-000000000001",
                        "view_uuid": "10000000-0000-4000-8000-000000000001"}
        for request in ({**public_valid, "model_uuid": "00000000-0000-0000-0000-000000000000"},
                        {**public_valid, "view_uuid": "00000000-0000-0000-0000-000000000000"},
                        {**public_valid, "attribute_ids": [True]},
                        {**public_valid, "attribute_ids": [83, 83]}):
            with self.subTest(public_request=request), self.assertRaises(ValidationError):
                AttributeEvidenceProbeInput.model_validate(request)

    def test_child_inventory_mismatch_does_not_erase_ancestry_or_values(self):
        target, child, unrelated = self.element(83), self.element(84), self.element(85)
        self.fixture([target])
        target.GetAttributes.side_effect = lambda mode: [(83, mode)]
        self.children[id(target)] = [child]
        self.parents[id(child)] = unrelated
        result = self.attribute_evidence_probe(target)
        evidence = result["representations"][0]["target"]["value"]
        self.assertEqual(evidence["ancestry"]["status"], "observed")
        self.assertEqual(evidence["children"]["status"], "not_checked")
        self.assertEqual(evidence["children"]["reason"], "component_child_owner_mismatch")
        self.assertEqual(evidence["read_modes"]["ReadAll"]["value"][0]["value"], "ReadAll")
        self.assertFalse(result["evidence_complete"])
        self.assertEqual(result["state"], "not_checked")

    def test_optional_immediate_parent_has_independent_identity_and_values(self):
        target, parent = self.element(86), self.element(87)
        self.fixture([target])
        self.parents[id(target)] = parent
        target.GetAttributes.side_effect = lambda mode: [(83, "target-" + mode)]
        parent.GetAttributes.side_effect = lambda mode: [(83, "parent-" + mode)]
        result = self.attribute_evidence_probe(target, include_parent=True)
        row = result["representations"][0]
        self.assertEqual(row["parent"]["status"], "observed")
        parent_evidence = row["parent"]["value"]["evidence"]
        self.assertEqual(parent_evidence["ref"]["model_uuid"], parent.GetModelElementUUID.return_value)
        self.assertNotEqual(parent_evidence["ref"]["model_uuid"], row["target"]["value"]["ref"]["model_uuid"])
        self.assertEqual(parent_evidence["read_modes"]["ReadAll"]["value"][0]["value"], "parent-ReadAll")
        self.assertEqual(row["target"]["value"]["read_modes"]["ReadAll"]["value"][0]["value"], "target-ReadAll")

    def test_read_mode_failure_is_isolated_and_duplicate_attribute_rows_fail_that_read(self):
        target = self.element(88)
        self.fixture([target])
        target.GetAttributes.side_effect = lambda mode: (_ for _ in ()).throw(RuntimeError("private")) if mode == "ReadAll" else [(83, "ok")]
        result = self.attribute_evidence_probe(target)
        modes = result["representations"][0]["target"]["value"]["read_modes"]
        self.assertEqual(modes["ReadAll"]["status"], "not_checked")
        self.assertEqual(modes["ReadAll"]["reason"], "RuntimeError")
        self.assertEqual(modes["ReadAllAndComputable"]["value"][0]["value"], "ok")
        target.GetAttributes.side_effect = lambda _mode: [(83, "first"), (83, "duplicate")]
        result = self.attribute_evidence_probe(target)
        modes = result["representations"][0]["target"]["value"]["read_modes"]
        self.assertEqual(modes["ReadAll"]["status"], "not_checked")
        self.assertEqual(modes["ReadAll"]["reason"], "ValueError")
        self.assertEqual(result["representation_consensus"], True)
        self.assertFalse(result["evidence_complete"])
        self.assertEqual(result["state"], "not_checked")

    def test_wrapper_conflicts_remain_visible_instead_of_first_wrapper_winning(self):
        first, second = self.element(89), self.element(89)
        first.GetElementUUID.return_value = second.GetElementUUID.return_value
        self.fixture([first, second])
        first.GetAttributes.side_effect = lambda _mode: [(83, "A")]
        second.GetAttributes.side_effect = lambda _mode: [(83, "B")]
        result = self.attribute_evidence_probe(first)
        self.assertEqual(result["representation_count"], 2)
        self.assertFalse(result["representation_consensus"])
        self.assertEqual(result["state"], "not_checked")
        self.assertFalse(result["evidence_complete"])

    def test_metadata_failure_keeps_consensus_but_does_not_claim_complete_evidence(self):
        target = self.element(90)
        self.fixture([target])
        self.base.AttributeService.GetAttributeType.side_effect = RuntimeError("private metadata")
        result = self.attribute_evidence_probe(target)
        self.assertTrue(result["representation_consensus"])
        self.assertFalse(result["evidence_complete"])
        self.assertEqual(result["state"], "not_checked")
        self.assertEqual(result["metadata"][0]["type_binding"]["status"], "not_checked")

    def test_attribute_evidence_traces_both_modes_and_holds_native_enumerator_until_reads_finish(self):
        target = self.element(91)
        self.fixture([target])
        self.base.AttributeService.GetAttributeType.side_effect = lambda _doc, _ident: 11
        owners = []

        class NativeOwnerList(list):
            pass

        def enumerate_adapters(_doc):
            owner = NativeOwnerList([target])
            owners.append(weakref.ref(owner))
            return owner

        self.base.ElementsSelectService.SelectAllElements.side_effect = enumerate_adapters
        def read_attributes(mode):
            self.assertIsNotNone(owners[-1](), "Native adapter owner must live through requested value reads.")
            return [(83, mode)]
        target.GetAttributes.side_effect = read_attributes
        self.attribute_evidence_probe(target)
        calls = [json.loads(line)["api"] for line in self.path.read_text(encoding="utf-8").splitlines()]
        self.assertIn("BaseElementAdapter.GetAttributes.evidence.ReadAll", calls)
        self.assertIn("BaseElementAdapter.GetAttributes.evidence.ReadAllAndComputable", calls)
        self.assertIsNone(owners[-1]())

    def test_attribute_evidence_result_budget_blocks_oversized_wrapper_report(self):
        adapters = [self.element(92) for _ in range(16)]
        for adapter in adapters:
            adapter.GetElementUUID.return_value = adapters[0].GetElementUUID.return_value
            adapter.GetAttributes.side_effect = lambda _mode: [(ident, "x" * 8192) for ident in range(1, 17)]
        self.fixture(adapters)
        self.base.AttributeService.GetAttributeType.side_effect = lambda _doc, _ident: 11
        self.assert_code("scan_limit_exceeded", lambda: self.attribute_evidence_probe(
            adapters[0], ids=tuple(range(1, 17))))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_untrusted_values_are_bounded_and_never_stringified(self):
        from test_allplan_host.attribute_evidence import describe_value

        class Hostile:
            def __repr__(self):
                raise AssertionError("repr must not run")
            __str__ = __repr__

        for value in (Hostile(), float("nan"), "x" * 8193, [1] * 65, [[1]], {"nested": 1}):
            with self.subTest(kind=type(value).__name__):
                evidence = describe_value(value)
                json.dumps(evidence, allow_nan=False)
                self.assertEqual(evidence["status"], "not_checked")
                self.assertIsNone(evidence["value"])
        hostile = describe_value(Hostile())
        self.assertEqual(hostile["runtime_type"], {"module": __name__, "name": "Hostile"})
        self.assertNotIn("repr", json.dumps(hostile))

    def test_seventeenth_exact_wrapper_is_rejected_before_attribute_reads(self):
        adapters = [self.element(93) for _ in range(17)]
        for adapter in adapters:
            adapter.GetElementUUID.return_value = adapters[0].GetElementUUID.return_value
        self.fixture(adapters)
        self.assert_code("probe_scope_unavailable", lambda: self.attribute_evidence_probe(adapters[0]))
        for adapter in adapters:
            adapter.GetAttributes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
