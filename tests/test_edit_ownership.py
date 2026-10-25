"""Family/owner regressions through the shared executor; no native acceptance."""
import copy
import importlib
import unittest
from uuid import uuid4

import test_model_edit as fixtures


class EditOwnershipTests(unittest.TestCase):
    setUp = fixtures.ModelEditTests.setUp
    prepare_context = fixtures.ModelEditTests.prepare_context
    prepare = fixtures.ModelEditTests.prepare
    adapter = fixtures.ModelEditTests.adapter
    native = fixtures.ModelEditTests.native
    element = fixtures.ModelEditTests.element
    assert_code = fixtures.ModelEditTests.assert_code
    fixture = fixtures.ModelEditTests.fixture
    attribute_catalog = fixtures.ModelEditTests.attribute_catalog
    setter_fakes = fixtures.ModelEditTests.setter_fakes
    request = fixtures.ModelEditTests.request
    call = fixtures.ModelEditTests.call
    preview = fixtures.ModelEditTests.preview
    plan_request = fixtures.ModelEditTests.plan_request
    highlight = fixtures.ModelEditTests.highlight
    apply = fixtures.ModelEditTests.apply
    recover = fixtures.ModelEditTests.recover

    def slab_fixture(self):
        elements = self.fixture(("old", "old"))
        slab, aggregate = elements
        slab.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        self.parents[id(slab)] = aggregate
        self.children[id(aggregate)] = [slab]
        self.setter_fakes(elements)
        return slab, aggregate

    def attribute_plan(self, **updates):
        return self.preview(predicate=None, changes=[
            {"target": {"kind": "attribute", "attribute_id": 935}, "value": "new"}], **updates)

    def test_parent_and_child_slab_never_become_two_writes_or_redirect_to_parent(self):
        slab, aggregate = self.slab_fixture()
        plan = self.attribute_plan(native_types=["Slab_TypeUUID", "MultiSlab_TypeUUID"])
        self.assertEqual(plan["counts"]["matched"], 2)
        self.assertEqual(plan["changes"], [])
        self.assertFalse(plan["apply_available"])
        self.assertEqual({item["reason"] for item in plan["blocked"]}, {
            "slab_has_parent_requires_explicit_property_owner", "aggregate_slab_requires_explicit_property_owner"})
        evidence = plan["criteria"]["component_ownership"]
        child = next(item for item in evidence if item["ref"]["model_uuid"] == slab.GetModelElementUUID())
        self.assertEqual(child["observation"]["value"]["lineage"][1]["model_uuid"], aggregate.GetModelElementUUID())
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_slab_child_alone_in_type_filter_still_requires_owner(self):
        self.slab_fixture()
        plan = self.attribute_plan(native_types=["Slab_TypeUUID"])
        self.assertEqual(plan["counts"]["matched"], 1)
        self.assertFalse(plan["apply_available"])
        self.assertEqual(plan["blocked"][0]["reason"], "slab_has_parent_requires_explicit_property_owner")

    def explicit_material_plan(self, kind, **updates):
        return self.preview(native_types=[kind], predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 508, "property_owner": "selected_element"},
            "value": "Beton1", "mode": "upsert"}], **updates)

    def material_slabs(self):
        slab, aggregate = self.slab_fixture()
        for element in (slab, aggregate):
            element.GetAttributes.return_value = [(508, "old")]
        self.attribute_catalog({508: "Materiał"})
        return slab, aggregate

    def test_explicit_slab_material_owner_apply_readback_replay_no_op_without_redirect(self):
        slab, aggregate = self.material_slabs()
        for kind, target, other in (("MultiSlab_TypeUUID", aggregate, slab), ("Slab_TypeUUID", slab, aggregate)):
            with self.subTest(kind=kind):
                target.GetAttributes.return_value = [(508, "old")]
                self.base.ElementsAttributeService.ChangeAttributes.reset_mock()
                before = copy.deepcopy(other.GetAttributes.return_value)
                plan = self.explicit_material_plan(kind)
                self.assertTrue(plan["apply_available"], plan)
                self.assertEqual(plan["changes"][0]["ref"]["model_uuid"], target.GetModelElementUUID())
                self.highlight(plan)
                execution = uuid4().hex
                result = self.apply(plan, execution)
                self.assertEqual(result["state"], "completed", result)
                self.assertEqual(result["outcomes"][0]["readback"]["value"], "Beton1")
                self.assertEqual(other.GetAttributes.return_value, before)
                self.assertTrue(self.apply(plan, execution)["replayed"])
                self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
                self.assertEqual(self.explicit_material_plan(kind)["state"], "no_op")
                self.base.GetElement.assert_not_called()

    def test_explicit_material_owner_can_upsert_after_complete_absence_read(self):
        _, aggregate = self.material_slabs()
        aggregate.GetAttributes.return_value = []
        plan = self.explicit_material_plan("MultiSlab_TypeUUID", attribute_read_mode="all_and_computable")
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["changes"][0]["operation"], "add_attribute")
        self.highlight(plan)
        self.assertEqual(self.apply(plan)["state"], "completed")
        self.assertEqual(dict(aggregate.GetAttributes.return_value)[508], "Beton1")

    def test_explicit_parent_child_material_overlap_blocks_before_setters(self):
        self.material_slabs()
        request = self.request(predicate=None, native_types=["Slab_TypeUUID", "MultiSlab_TypeUUID"], changes=[{
            "target": {"kind": "attribute", "attribute_id": 508, "property_owner": "selected_element"},
            "value": "Beton1"}])
        plan = self.call(request)
        self.assertFalse(plan["apply_available"])
        self.assertIn("overlapping_slab_property_owners", {row["reason"] for row in plan["blocked"]})
        execution = importlib.import_module(self.module.__package__ + ".repair_execution")
        forged = copy.deepcopy(plan)
        forged["state"], forged["blocked"] = "preview_ready", []
        self.assertFalse(execution.RepairExecutor.model_edit_scope(forged))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_explicit_owner_forgery_and_fresh_lineage_drift_block_final_setter(self):
        slab, aggregate = self.material_slabs()
        plan = self.explicit_material_plan("MultiSlab_TypeUUID")
        native = importlib.import_module(self.module.__package__ + ".native_model_edit")
        damaged = copy.deepcopy(plan["changes"][0])
        damaged["resource"]["component_ownership"]["value"]["target"]["model_uuid"] = slab.GetModelElementUUID()
        self.assert_code("target_not_writable", lambda: native.write(self.base, aggregate, damaged))
        self.highlight(plan)
        self.children[id(aggregate)] = []
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_explicit_owner_readback_drift_remains_unknown_and_is_never_retried(self):
        _, aggregate = self.material_slabs()
        setter = self.base.ElementsAttributeService.ChangeAttributes.side_effect

        def mutate_then_reparent(*args):
            setter(*args)
            self.parents[id(aggregate)] = self.element(99, name="Macro_TypeUUID")

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = mutate_then_reparent
        plan = self.explicit_material_plan("MultiSlab_TypeUUID")
        self.highlight(plan)
        execution = uuid4().hex
        result = self.apply(plan, execution)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.apply(plan, execution)["replayed"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_unavailable_slab_parent_blocks_preview(self):
        slab, _ = self.slab_fixture()
        def unavailable(_):
            raise RuntimeError("native parent unavailable")
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = unavailable
        plan = self.attribute_plan(native_types=["Slab_TypeUUID"])
        self.assertFalse(plan["apply_available"])
        self.assertEqual(plan["blocked"][0]["reason"], "slab_ownership_unavailable")
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_slab_reparenting_after_highlight_conflicts_before_setter(self):
        slab, aggregate = self.slab_fixture()
        self.parents.clear()
        self.children.clear()
        plan = self.attribute_plan(native_types=["Slab_TypeUUID"])
        self.assertTrue(plan["apply_available"])
        self.highlight(plan)
        self.parents[id(slab)] = aggregate
        self.children[id(aggregate)] = [slab]
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_standalone_slabs_with_equal_geometry_remain_distinct_exact_targets(self):
        slab, other = self.slab_fixture()
        self.parents.clear()
        self.children.clear()
        other.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        plan = self.attribute_plan(native_types=["Slab_TypeUUID"])
        self.assertEqual(plan["counts"]["changes"], 2)
        self.assertEqual({item["ref"]["model_uuid"] for item in plan["changes"]},
                         {slab.GetModelElementUUID(), other.GetModelElementUUID()})
        self.highlight(plan)
        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed", result)
        self.assertTrue(result["audited_fields_match_plan"])
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 2)
        self.assertEqual(self.attribute_plan(native_types=["Slab_TypeUUID"])["state"], "no_op")

    def test_legacy_or_forged_slab_change_cannot_bypass_executor_or_final_setter(self):
        slab, _ = self.slab_fixture()
        self.parents.clear()
        self.children.clear()
        plan = self.attribute_plan(native_types=["Slab_TypeUUID"])
        execution = importlib.import_module(self.module.__package__ + ".repair_execution")
        native = importlib.import_module(self.module.__package__ + ".native_model_edit")
        for damaged_value in (None, {}, {"status": "observed", "value": []}):
            damaged = copy.deepcopy(plan)
            damaged["changes"][0]["resource"]["component_ownership"] = damaged_value
            self.assertFalse(execution.RepairExecutor.model_edit_scope(damaged))
            self.assert_code("target_not_writable", lambda: native.write(self.base, slab, damaged["changes"][0]))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_changed_slab_owner_at_readback_is_unknown_and_replay_never_repeats_setter(self):
        slab, aggregate = self.slab_fixture()
        self.parents.clear()
        self.children.clear()
        setter = self.base.ElementsAttributeService.ChangeAttributes.side_effect
        def reparent_after_write(*args):
            setter(*args)
            self.parents[id(slab)] = aggregate
            self.children[id(aggregate)] = [slab]
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = reparent_after_write
        plan = self.attribute_plan(native_types=["Slab_TypeUUID"])
        self.highlight(plan)
        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_w1_exact_targets_exclusions_fresh_readback_replay_and_no_op_by_adapter(self):
        # Wall tier ownership is exercised independently in test_wall_layer_edit.
        for family in ("Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID", "Slab_TypeUUID", "WindowDoor_TypeUUID"):
            with self.subTest(family=family):
                elements = self.fixture(("", ""))
                self.setter_fakes(elements)
                self.base.ElementsLayerService.ChangeLayer.reset_mock()
                for element in elements:
                    element.GetElementAdapterType.return_value.GetTypeName.return_value = family
                excluded = elements[1].GetModelElementUUID()
                request = {"native_types": [family], "predicate": None,
                           "exclude_model_uuids": [excluded], "changes": [{"target": {
                               "kind": "layer", "short_name": "W1", "expected_layer_id": 8, "expected_name": "W1"}}]}
                plan = self.preview(**request)
                self.assertEqual(plan["counts"]["excluded"], 1)
                self.assertEqual(plan["counts"]["changes"], 1)
                self.assertEqual(plan["changes"][0]["target_view_uuid"], elements[0].GetElementUUID())
                self.highlight(plan)
                execution_id = uuid4().hex
                result = self.apply(plan, execution_id)
                self.assertEqual(result["state"], "completed", result)
                self.assertEqual(result["outcomes"][0]["readback"]["value"], 8)
                self.assertTrue(result["audited_fields_match_plan"])
                self.assertEqual(elements[1].GetCommonProperties.return_value.Layer, 7)
                self.assertTrue(self.apply(plan, execution_id)["replayed"])
                self.assertEqual(self.base.ElementsLayerService.ChangeLayer.call_count, 1)
                self.assertEqual(self.preview(**request)["state"], "no_op")

    def test_unsupported_sdk_date_and_vector_types_fail_before_enumeration(self):
        for member in ("Date", "Vector", "Byte", "Object"):
            with self.subTest(member=member):
                self.fixture(("",))
                setattr(self.attribute_type_enum, member, 300)
                self.attribute_type_names[935] = member
                self.assert_code("attribute_type_unsupported", self.attribute_plan)
                self.base.ElementsSelectService.SelectAllElements.assert_not_called()
                self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_native_material_never_becomes_an_attribute_change_or_layer(self):
        self.fixture(("",))
        self.assert_code("invalid_payload", lambda: self.preview(changes=[{
            "target": {"kind": "native_material"}, "value": "C35/45"}]))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ModifyElements.assert_not_called()

    def test_native_selection_returns_unsupported_without_highlight_or_input_calls(self):
        self.fixture(("",))
        result = self.handler.handle("/model-selection", {
            "schema_version": "m4-selection-1", "action": "select", "selection_id": uuid4().hex})
        self.assertEqual(result["status"], "unsupported")
        self.assertFalse(result["ui_calls_started"])
        self.assertFalse(result["next_action"]["automatic_highlight_fallback"])
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
