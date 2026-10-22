"""Wall layer root no-op regression through the typed planner and real journal."""
import copy
import sys
import unittest
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import patch

import test_model_edit as fixtures


class WallLayerEditTests(unittest.TestCase):
    def fixture(self, layers=(3735,), root_layer=3735):
        native = self.native = fixtures.ModelEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        root = native.fixture(("",))[0]
        root.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        root.GetElementAdapterType.return_value.GetGuid.return_value = "20000000-0000-4000-8000-000000000001"
        root.GetCommonProperties.return_value.Layer = root_layer
        tiers = [native.element(i + 10, name="WallTier_TypeUUID") for i in range(len(layers))]
        axis = native.element(50, name="WallAxis_TypeUUID")
        opening = native.element(51, name="WindowDoor_TypeUUID")
        for tier, layer in zip(tiers, layers):
            tier.GetCommonProperties.return_value = SimpleNamespace(Layer=layer)
            for name, value in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                                ("IsInActiveDocument", True), ("IsInActiveLayer", True), ("IsLabelElement", False)):
                getattr(tier, name).return_value = value
        native.children[id(root)] = [*tiers, axis, opening]
        for child in (*tiers, axis, opening):
            native.parents[id(child)] = root
        native.base.ElementsSelectService.SelectAllElements.return_value = [root, *tiers, axis, opening]
        native.base.DrawingFileService.GetActiveFileNumber.return_value = 101

        def change_layer(targets, name):
            # Reproduce the incident: a root-only request does nothing. Native
            # layers live on the directly owned tiers in this fake model.
            for target in targets:
                if any(target is tier for tier in tiers):
                    target.GetCommonProperties.return_value.Layer = 8
        native.base.ElementsLayerService.ChangeLayer.side_effect = change_layer
        return root, tiers, axis, opening

    def thickness(self, values):
        class Wall:
            def __init__(self, root):
                self.Properties = SimpleNamespace(TierCount=1,
                    GetWallTierProperties=lambda index: SimpleNamespace(Thickness=values[id(root)]))
        sdk = patch.dict(sys.modules, {"NemAll_Python_ArchElements": SimpleNamespace(WallElement=Wall)})
        sdk.start()
        self.addCleanup(sdk.stop)
        self.native.base.GetElement.side_effect = lambda root: Wall(root)

    def preview(self, predicate=None):
        return self.native.preview(native_types=["Wall_TypeUUID"],
            predicate=predicate or {"field": "family", "op": "eq", "value": "wall"},
            changes=[{"target": {"kind": "layer", "short_name": "W1"}}])

    def query(self, component=False):
        request = {"schema_version": "m1-query-1", "action": "query",
                   "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
                   "component_kind": "semantic_component", "fields": ["layer_id"],
                   "predicate": {"field": "type_name", "op": "eq", "value": "Wall_TypeUUID"}}
        if component:
            request["layer_resolution"] = "component"
        return self.native.handler.handle("/model-query", request)

    def test_root_no_op_is_fixed_by_tier_setter_fresh_readback_and_replay(self):
        root, tiers, axis, opening = self.fixture((3735, 3735))
        native = self.native
        before_extras = [e.GetCommonProperties.return_value.Layer for e in (axis, opening)]
        plan = self.preview()
        self.assertTrue(plan["evaluation_apply_available"], plan)
        self.assertEqual(len(plan["changes"]), 1)
        self.assertEqual(plan["changes"][0]["operation"], "set_wall_layer")
        self.assertEqual(len(plan["changes"][0]["resource"]["wall_layer_ownership"]["tiers"]), 2)
        native.highlight(plan)
        execution = uuid4().hex
        result = native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        self.assertTrue(result["audited_fields_match_plan"])
        sent = native.base.ElementsLayerService.ChangeLayer.call_args.args[0]
        self.assertEqual({id(e) for e in sent}, {id(e) for e in tiers})
        self.assertEqual(root.GetCommonProperties.return_value.Layer, 3735)
        self.assertEqual([tier.GetCommonProperties.return_value.Layer for tier in tiers], [8, 8])
        self.assertEqual([e.GetCommonProperties.return_value.Layer for e in (axis, opening)], before_extras)
        self.assertEqual(self.query()["elements"][0]["fields"]["layer_id"]["value"], 3735)
        self.assertEqual(self.query(True)["elements"][0]["fields"]["layer_id"]["value"], 8)
        self.assertTrue(native.apply(plan, execution)["replayed"])
        self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 1)
        self.assertEqual(self.preview()["state"], "no_op")
        native.base.ModifyElements.assert_not_called()
        native.base.CreateElements.assert_not_called()
        native.base.DeleteElements.assert_not_called()

    def test_default_layer_zero_root_and_tiers_apply_readback_replay_and_no_op(self):
        root, tiers, *_ = self.fixture((0, 0), root_layer=0)
        native = self.native
        plan = self.preview()
        self.assertTrue(plan["evaluation_apply_available"], plan)
        change = plan["changes"][0]
        self.assertEqual(change["old_value"], {"status": "observed", "value": 0})
        self.assertEqual(change["resource"]["wall_layer_ownership"]["root"]["layer"], 0)
        self.assertEqual([item["layer"] for item in change["resource"]["wall_layer_ownership"]["tiers"]], [0, 0])
        native.highlight(plan)
        execution = uuid4().hex
        result = native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(root.GetCommonProperties.return_value.Layer, 0)
        self.assertEqual([tier.GetCommonProperties.return_value.Layer for tier in tiers], [8, 8])
        self.assertEqual(self.query()["elements"][0]["fields"]["layer_id"]["value"], 0)
        self.assertEqual(self.query(True)["elements"][0]["fields"]["layer_id"]["value"], 8)
        self.assertTrue(native.apply(plan, execution)["replayed"])
        self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 1)
        self.assertEqual(self.preview()["state"], "no_op")

    def test_default_layer_zero_root_with_positive_tier_layer_is_preserved(self):
        root, tiers, *_ = self.fixture((3735,), root_layer=0)
        native = self.native
        plan = self.preview()
        self.assertTrue(plan["evaluation_apply_available"], plan)
        self.assertEqual(plan["changes"][0]["old_value"], {"status": "observed", "value": 3735})
        self.assertEqual(plan["changes"][0]["resource"]["wall_layer_ownership"]["root"]["layer"], 0)
        native.highlight(plan)
        execution = uuid4().hex
        self.assertEqual(native.apply(plan, execution)["state"], "completed")
        self.assertEqual(root.GetCommonProperties.return_value.Layer, 0)
        self.assertEqual(tiers[0].GetCommonProperties.return_value.Layer, 8)
        self.assertTrue(native.apply(plan, execution)["replayed"])
        self.assertEqual(self.preview()["state"], "no_op")
        self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 1)

    def test_default_layer_zero_old_value_drift_conflicts_before_apply(self):
        _root, tiers, *_ = self.fixture((0,), root_layer=0)
        native = self.native
        plan = self.preview()
        self.assertTrue(plan["evaluation_apply_available"], plan)
        native.highlight(plan)
        tiers[0].GetCommonProperties.return_value.Layer = 3735
        native.assert_code("repair_conflict", lambda: native.apply(plan))
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.assertEqual(list(native.plans.executor.path.glob("*.json")), [])

    def test_mixed_tiers_and_unknown_ownership_block_before_any_setter(self):
        _root, tiers, *_ = self.fixture((3735, 8))
        plan = self.preview()
        self.assertFalse(plan["evaluation_apply_available"])
        self.assertEqual(plan["state"], "not_checked")
        tiers[1].GetCommonProperties.return_value.Layer = 3735
        self.native.parents.pop(id(tiers[1]))
        unknown = self.preview()
        self.assertFalse(unknown["evaluation_apply_available"])
        self.native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_changed_tier_membership_and_locked_tier_reject_apply_before_journal(self):
        _root, tiers, *_ = self.fixture()
        native = self.native
        plan = self.preview()
        native.highlight(plan)
        tiers[0].IsInActiveLayer.return_value = False
        native.assert_code("target_not_writable", lambda: native.apply(plan))
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.assertEqual(list(native.plans.executor.path.glob("*.json")), [])
        tiers[0].IsInActiveLayer.return_value = True
        tiers[0].GetModelElementUUID.return_value = "10000000-0000-4000-8000-000000000999"
        native.assert_code("repair_conflict", lambda: native.apply(plan))
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_reviewed_manifest_is_required_for_direct_scope_guard(self):
        self.fixture()
        plan = self.preview()
        forged = copy.deepcopy(plan)
        forged["changes"][0]["resource"]["wall_layer_ownership"]["tiers"] = []
        self.assertFalse(self.native.plans.executor.evaluation_scope(forged))

    def test_native_thickness_criterion_is_bound_for_all_wall_peers_before_write(self):
        root, tiers, *_ = self.fixture()
        native = self.native
        other = native.element(70, name="Wall_TypeUUID")
        other_tier = native.element(71, name="WallTier_TypeUUID")
        other.GetCommonProperties.return_value.Layer = 3735
        other_tier.GetCommonProperties.return_value.Layer = 3735
        native.children[id(other)] = [other_tier]
        native.parents[id(other_tier)] = other
        native.base.ElementsSelectService.SelectAllElements.return_value.extend([other, other_tier])
        thickness = {id(root): 200, id(other): 240}
        self.thickness(thickness)
        criterion = {"field": "wall.total_thickness_mm", "op": "lt", "value": 240}
        plan = self.preview(criterion)
        self.assertEqual(plan["counts"]["matched"], 1)
        self.assertEqual(plan["counts"]["nonmatching"], 1)
        self.assertEqual(plan["changes"][0]["ref"]["model_uuid"], root.GetModelElementUUID())
        native.highlight(plan)
        # A previously nonmatching peer now qualifies: it must force a fresh
        # plan rather than silently widening or preserving a stale target set.
        thickness[id(other)] = 200
        native.assert_code("repair_conflict", lambda: native.apply(plan))
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        thickness[id(other)] = 240
        fresh = self.preview(criterion)
        native.highlight(fresh)
        result = native.apply(fresh)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(tiers[0].GetCommonProperties.return_value.Layer, 8)
        self.assertEqual(other_tier.GetCommonProperties.return_value.Layer, 3735)
        self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 1)

    def test_lost_setter_reply_recovers_tier_state_without_writing_again(self):
        _root, tiers, *_ = self.fixture()
        native = self.native
        original = native.base.ElementsLayerService.ChangeLayer.side_effect
        def lost_reply(targets, name):
            original(targets, name)
            raise RuntimeError("reply lost after tier write")
        native.base.ElementsLayerService.ChangeLayer.side_effect = lost_reply
        plan = self.preview()
        native.highlight(plan)
        execution = uuid4().hex
        result = native.apply(plan, execution)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        recovered = native.recover(execution)
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.assertEqual(recovered["outcomes"][0]["reason"], "new_value_observed")
        self.assertTrue(native.apply(plan, execution)["replayed"])
        self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 1)
        self.assertEqual(tiers[0].GetCommonProperties.return_value.Layer, 8)

    def test_nonwall_unknown_thickness_does_not_block_decisive_wall_criterion(self):
        root, tiers, *_ = self.fixture()
        native = self.native
        column = native.element(80, name="Column_TypeUUID")
        native.base.ElementsSelectService.SelectAllElements.return_value.append(column)
        self.thickness({id(root): 200})
        plan = native.preview(predicate={"all": [
            {"field": "family", "op": "eq", "value": "wall"},
            {"field": "wall.total_thickness_mm", "op": "lt", "value": 240}]},
            changes=[{"target": {"kind": "layer", "short_name": "W1"}}])
        self.assertTrue(plan["evaluation_apply_available"], plan)
        self.assertFalse(plan["coverage"]["returned_fields_complete"])
        self.assertTrue(plan["coverage"]["required_destination_fields_complete"])
        native.highlight(plan)
        self.assertEqual(native.apply(plan)["state"], "completed")
        self.assertEqual(tiers[0].GetCommonProperties.return_value.Layer, 8)

    def test_matched_wall_unknown_layer_has_actionable_diagnostic_and_no_apply(self):
        root, *_ = self.fixture()
        self.native.children[id(root)] = []
        plan = self.preview()
        self.assertFalse(plan["evaluation_apply_available"])
        failure = plan["criteria"]["required_field_failures"][0]
        self.assertEqual(failure["field"], "layer_id")
        self.assertEqual(failure["observation"]["status"], "not_checked")
        self.native.base.ElementsLayerService.ChangeLayer.assert_not_called()
