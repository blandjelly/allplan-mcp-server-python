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

    def test_slab_tier_attribute_owner_without_exact_target_is_blocked(self):
        # 0.46.0 trial: Allplan shows the MultiSlab's attribute 508 as the slab
        # material; the tier keeps its own value that the UI does not display.
        slab, aggregate = self.material_slabs()
        plan = self.explicit_material_plan("Slab_TypeUUID")
        self.assertFalse(plan["apply_available"], plan)
        self.assertEqual(plan["changes"], [])
        row, = plan["blocked"]
        self.assertEqual(row["reason"], "slab_tier_not_shown_in_ui_use_multislab")
        self.assertEqual(row["ref"]["model_uuid"], slab.GetModelElementUUID())
        self.assertEqual(row["ui_owner"]["model_uuid"], aggregate.GetModelElementUUID())
        self.assertEqual(row["ui_owner"]["view_uuid"], aggregate.GetElementUUID())
        self.assertEqual(row["ui_owner"]["next_preview"]["native_types"], ["MultiSlab_TypeUUID"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_slab_tier_ui_owner_hint_leads_to_a_multislab_write_only(self):
        # The hint is never a redirection: the tier stays unchanged and only a
        # separate MultiSlab preview writes the value the UI shows.
        slab, aggregate = self.material_slabs()
        tier_before = copy.deepcopy(slab.GetAttributes.return_value)
        hint = self.explicit_material_plan("Slab_TypeUUID")["blocked"][0]["ui_owner"]
        plan = self.explicit_material_plan(hint["next_preview"]["native_types"][0])
        self.assertTrue(plan["apply_available"], plan)
        change, = plan["changes"]
        self.assertEqual(change["ref"]["model_uuid"], hint["model_uuid"])
        self.assertEqual(change["target_view_uuid"], hint["view_uuid"])
        self.highlight(plan)
        result = self.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(dict(aggregate.GetAttributes.return_value)[508], "Beton1")
        self.assertEqual(slab.GetAttributes.return_value, tier_before)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_unowned_slab_tier_attribute_also_names_the_ui_owner(self):
        _, aggregate = self.slab_fixture()
        row, = self.attribute_plan(native_types=["Slab_TypeUUID"])["blocked"]
        self.assertEqual(row["reason"], "slab_has_parent_requires_explicit_property_owner")
        self.assertEqual(row["ui_owner"]["model_uuid"], aggregate.GetModelElementUUID())

    def test_aggregate_without_owner_has_no_ui_owner_hint(self):
        self.slab_fixture()
        plan = self.attribute_plan(native_types=["MultiSlab_TypeUUID"])
        row, = plan["blocked"]
        self.assertEqual(row["reason"], "aggregate_slab_requires_explicit_property_owner")
        self.assertNotIn("ui_owner", row)

    def test_explicit_slab_material_owner_apply_readback_replay_no_op_without_redirect(self):
        slab, aggregate = self.material_slabs()
        for kind, target, other in (("MultiSlab_TypeUUID", aggregate, slab),):
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

    def test_attribute_owner_still_requires_exact_ownership_consensus_across_views(self):
        slab, aggregate = self.material_slabs()
        alias = copy.deepcopy(slab)
        alias.GetElementUUID.return_value = str(uuid4())
        self.parents[id(alias)] = aggregate
        self.children[id(alias)] = []
        self.base.ElementsSelectService.SelectAllElements.return_value = [slab, aggregate, alias]
        plan = self.explicit_material_plan("Slab_TypeUUID")
        self.assertFalse(plan["apply_available"], plan)
        self.assertEqual(plan["criteria"]["native_material_ownership"], [])
        entry, = plan["criteria"]["component_ownership"]
        self.assertEqual(entry["observation"]["reason"], "slab_ownership_representation_conflict")
        self.assertEqual(plan["blocked"][0]["reason"], "slab_ownership_unavailable")
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_explicit_parent_child_material_overlap_blocks_before_setters(self):
        slab, _ = self.material_slabs()
        request = self.request(predicate=None, native_types=["Slab_TypeUUID", "MultiSlab_TypeUUID"], changes=[{
            "target": {"kind": "attribute", "attribute_id": 508, "property_owner": "selected_element"},
            "value": "Beton1"}])
        plan = self.call(request)
        self.assertFalse(plan["apply_available"])
        # The tier is blocked before the overlap guard can see two changes.
        self.assertEqual({row["reason"] for row in plan["blocked"]},
                         {"slab_tier_not_shown_in_ui_use_multislab"})
        execution = importlib.import_module(self.module.__package__ + ".repair_execution")
        forged = copy.deepcopy(plan)
        forged["state"], forged["blocked"] = "preview_ready", []
        aggregate_change, = forged["changes"]
        tier = copy.deepcopy(aggregate_change)
        lineage = aggregate_change["resource"]["component_ownership"]["value"]["lineage"]
        tier["ref"]["model_uuid"] = slab.GetModelElementUUID()
        tier["resource"]["component_ownership"]["value"]["lineage"] = [
            {**lineage[0], "model_uuid": tier["ref"]["model_uuid"], "type_name": "Slab_TypeUUID"}, lineage[0]]
        forged["changes"].append(tier)
        ownership = importlib.import_module(self.module.__package__ + ".component_ownership")
        self.assertTrue(ownership.overlapping_slab_owners(forged["changes"]))
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


class ExactTierAttributeTests(unittest.TestCase):
    """0.46.0: a MultiSlab tier attribute is written on its parent-edge view."""
    locals().update({name: value for name, value in vars(EditOwnershipTests).items()
                     if not name.startswith("test_") and not name.startswith("__")})

    def exact_tier(self, shared=True, container=False):
        slab, aggregate = self.material_slabs()
        edge = copy.deepcopy(slab)
        edge.GetElementUUID.return_value = str(uuid4())
        if shared:
            edge.GetAttributes = slab.GetAttributes  # one native attribute store
        self.parents[id(edge)] = aggregate
        self.children[id(edge)] = []
        self.children[id(aggregate)] = [edge]
        if container:
            box = self.element(97, name="AttributeContainer_TypeUUID")
            self.parents[id(box)] = aggregate
            self.children[id(box)] = []
            self.children[id(aggregate)].append(box)
        self.base.ElementsSelectService.SelectAllElements.return_value = [slab, aggregate]
        self.exact = {"drawing_file": 101, "model_uuid": edge.GetModelElementUUID(),
                      "view_uuid": edge.GetElementUUID(), "parent_ref": {
                          "model_uuid": aggregate.GetModelElementUUID(),
                          "view_uuid": aggregate.GetElementUUID()}}
        return slab, aggregate, edge

    def exact_plan(self, **change):
        return self.preview(native_types=["Slab_TypeUUID"], predicate=None, exact_target=self.exact,
                            changes=[{"target": {"kind": "attribute", "attribute_id": 508,
                                                 "property_owner": "selected_element"},
                                      "value": "Beton1", **change}])

    def test_exact_tier_attribute_writes_parent_edge_view_and_reads_every_view(self):
        slab, _, edge = self.exact_tier()
        plan = self.exact_plan()
        self.assertTrue(plan["apply_available"], plan)
        change, = plan["changes"]
        self.assertEqual(change["target_view_uuid"], self.exact["view_uuid"])
        self.assertEqual(change["resource"]["component_ownership"]["value"]["target"]["view_uuid"],
                         self.exact["view_uuid"])
        self.assertEqual(change["resource"]["exact_target_binding"]["target"], self.exact)
        self.highlight(plan)
        execution = uuid4().hex
        result = self.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        setter = self.base.ElementsAttributeService.ChangeAttributes
        setter.assert_called_once()
        self.assertIs(setter.call_args.args[1][0], edge)
        outcome, = result["outcomes"]
        self.assertEqual(outcome["readback"]["value"], "Beton1")
        consensus = outcome["representation_consensus"]
        self.assertEqual({row["view_uuid"] for row in consensus["representations"]},
                         {slab.GetElementUUID(), edge.GetElementUUID()})
        self.assertTrue(consensus["reviewed_view_present"])
        self.assertEqual(consensus["exact_inventory"]["status"], "unchanged")
        self.assertTrue(self.apply(plan, execution)["replayed"])
        setter.assert_called_once()
        self.assertEqual(self.exact_plan()["state"], "no_op")

    def test_tier_write_that_other_view_does_not_show_stays_unknown(self):
        # The 0.45.0 symptom inverted: the reviewed view changes, another
        # wrapper of the same tier keeps the old value. Never applied.
        slab, _, edge = self.exact_tier(shared=False)
        edge.GetAttributes.return_value = list(slab.GetAttributes.return_value)
        plan = self.exact_plan()
        self.assertTrue(plan["apply_available"], plan)
        self.highlight(plan)
        execution = uuid4().hex
        result = self.apply(plan, execution)
        outcome, = result["outcomes"]
        self.assertEqual(outcome["state"], "unknown", outcome)
        self.assertFalse(outcome["representation_consensus"]["agreed"])
        self.assertEqual(dict(slab.GetAttributes.return_value)[508], "old")
        recovered = self.recover(execution)
        self.assertEqual(recovered["outcomes"][0]["state"], "unknown")
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_regenerated_attribute_container_is_accepted_after_setter(self):
        self.post_setter_drift("container")

    def test_other_post_setter_inventory_drift_stays_unknown(self):
        self.post_setter_drift("extra_child")

    def post_setter_drift(self, drift):
        _, aggregate, edge = self.exact_tier(container=True)
        setter = self.base.ElementsAttributeService.ChangeAttributes
        write = setter.side_effect

        def regenerate(*args):
            write(*args)
            if drift == "container":
                fresh = self.element(96, name="AttributeContainer_TypeUUID")
                self.parents[id(fresh)] = aggregate
                self.children[id(fresh)] = []
                self.children[id(aggregate)] = [edge, fresh]
            else:
                extra = self.element(95, name="Slab_TypeUUID")
                self.parents[id(extra)] = aggregate
                self.children[id(extra)] = []
                self.children[id(aggregate)].append(extra)

        setter.side_effect = regenerate
        plan = self.exact_plan()
        self.assertTrue(plan["apply_available"], plan)
        self.highlight(plan)
        result = self.apply(plan)
        outcome, = result["outcomes"]
        inventory = outcome["representation_consensus"]["exact_inventory"]
        self.assertEqual(inventory["status"], "changed")
        if drift == "container":
            self.assertEqual(outcome["state"], "applied", outcome)
            self.assertEqual(inventory["accepted"], "attribute_containers_regenerated")
        else:
            self.assertEqual(outcome["state"], "unknown", outcome)
            self.assertEqual(outcome["reason"], "exact_inventory_changed_after_setter")
            self.assertNotIn("accepted", inventory)
        setter.assert_called_once()

    def test_exact_tier_attribute_contract_is_narrow(self):
        from allplan_mcp.model_edit_models import ModelEditPreview
        self.exact_tier()
        owner = {"kind": "attribute", "attribute_id": 508, "property_owner": "selected_element"}
        valid = self.request(native_types=["Slab_TypeUUID"], predicate=None, exact_target=self.exact,
                             changes=[{"target": owner, "value": "Beton1"}])
        ModelEditPreview.model_validate(valid)
        for change in ({"target": owner, "value": "Beton1", "mode": "upsert"},
                       {"target": owner, "value": "Beton1", "mode": "add"},
                       {"target": {"kind": "attribute", "attribute_id": 508}, "value": "Beton1"},
                       {"target": {"kind": "attribute", "name": "Materiał", "property_owner": "selected_element"},
                        "value": "Beton1"},
                       {"target": {"kind": "layer", "short_name": "W1"}}):
            request = {**valid, "changes": [change]}
            with self.subTest(change=change):
                self.assert_code("invalid_payload", lambda: self.call(request))
                with self.assertRaises(ValueError):
                    ModelEditPreview.model_validate(request)
        with self.assertRaises(ValueError):
            ModelEditPreview.model_validate({**valid, "attribute_ids": [508]})
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_container_regeneration_classifier_is_one_for_one(self):
        target = importlib.import_module(self.module.__package__ + ".exact_material_target")
        tier, box, other = "Slab_TypeUUID|t|v", "AttributeContainer_TypeUUID|a|a", "AttributeContainer_TypeUUID|b|b"
        parent = "MultiSlab_TypeUUID|m|v"

        def summary(children, edges=(tier + ">" + parent,), **scalars):
            return {"schema_version": target.INVENTORY_SUMMARY_SCHEMA, "parent_representation_count": 1,
                    "child_visits": len(children), "target_in_direct_scan": True, **scalars,
                    "edges": list(edges), "parents": [{"parent": parent, "children": list(children)}]}

        before = summary([tier, box])
        self.assertTrue(target.attribute_containers_regenerated(before, summary([tier, other])))
        self.assertFalse(target.attribute_containers_regenerated(before, before))
        self.assertFalse(target.attribute_containers_regenerated(before, summary([tier, box, other])))
        self.assertFalse(target.attribute_containers_regenerated(before, summary([tier])))
        self.assertFalse(target.attribute_containers_regenerated(
            before, summary(["Slab_TypeUUID|t|w", other])))
        self.assertFalse(target.attribute_containers_regenerated(
            before, summary([tier, other], edges=())))
        self.assertFalse(target.attribute_containers_regenerated(
            before, summary([tier, other], target_in_direct_scan=False)))
        self.assertFalse(target.attribute_containers_regenerated({"schema_version": "x"}, before))
