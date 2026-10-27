"""Exact child opt-in through the normal planner, journal and native guards."""
import copy
import importlib
import unittest
from uuid import uuid4

import test_native_material_families as families


class ExactMaterialTargetTests(unittest.TestCase):
    def setUp(self):
        helper = families.NativeMaterialFamiliesTests()
        self.f = helper.fixture("Slab_TypeUUID", families.SlabElement)
        self.addCleanup(helper.doCleanups)
        f = self.f
        self.parent = f.native.element(98, name="MultiSlab_TypeUUID")
        f.native.parents[id(f.root)] = self.parent
        f.native.children[id(self.parent)] = [f.root]
        f.native.base.ElementsSelectService.SelectAllElements.return_value = [self.parent]
        for adapter in (f.root, self.parent):
            adapter.IsNull.return_value = False
            adapter.IsDeleted.return_value = False
            adapter.IsValid.return_value = True
        self.target = {"drawing_file": 101, "model_uuid": f.root.GetModelElementUUID(),
                       "view_uuid": f.root.GetElementUUID(), "parent_ref": {
                           "model_uuid": self.parent.GetModelElementUUID(),
                           "view_uuid": self.parent.GetElementUUID()}}
        self.request = f.fixture.request(native_types=["Slab_TypeUUID"], exact_target=self.target)

    def preview(self):
        return self.f.native.call(self.request)

    def test_missing_direct_child_preview_highlight_apply_replay_and_noop(self):
        f = self.f
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(len(plan["changes"]), 1)
        self.assertEqual(plan["changes"][0]["target_view_uuid"], self.target["view_uuid"])
        self.assertEqual(plan["changes"][0]["ref"]["model_uuid"], self.target["model_uuid"])
        f.native.highlight(plan)
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        self.assertEqual(self.preview()["state"], "no_op")
        f.native.base.ModifyElements.assert_called_once()
        f.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertTrue(all(call.args[0] is f.root for call in f.native.base.GetElement.call_args_list))

    def test_parent_child_view_or_inventory_drift_prevents_setters(self):
        f = self.f
        for drift in ("parent_view", "child_view", "inventory", "value"):
            with self.subTest(drift=drift):
                plan = self.preview()
                f.native.highlight(plan)
                old_parent = self.parent.GetElementUUID.return_value
                old_child = f.root.GetElementUUID.return_value
                old_material = f.properties.Material
                if drift == "parent_view": self.parent.GetElementUUID.return_value = str(uuid4())
                elif drift == "child_view": f.root.GetElementUUID.return_value = str(uuid4())
                elif drift == "inventory": f.native.children[id(self.parent)] = []
                else: f.properties.Material = "drift"
                with self.assertRaises(f.native.module.BridgeError): f.native.apply(plan)
                f.native.base.ModifyElements.assert_not_called()
                self.parent.GetElementUUID.return_value = old_parent
                f.root.GetElementUUID.return_value = old_child
                f.properties.Material = old_material
                f.native.children[id(self.parent)] = [f.root]

    def test_host_and_public_contract_reject_ambiguous_scope_before_native_read(self):
        from allplan_mcp.model_edit_models import ModelEditPreview
        for updates in ({"native_types": ["MultiSlab_TypeUUID"]}, {"exact_target": None},
                        {"predicate": {"field": "type_name", "op": "eq", "value": "Slab_TypeUUID"}},
                        {"scope": "open_drawings"}, {"exclude_model_uuids": [str(uuid4())]},
                        {"exact_target": {**self.target, "view_uuid": "00000000-0000-0000-0000-000000000000"}}):
            request = {**self.request, **updates}
            with self.subTest(updates=updates):
                with self.assertRaises(self.f.native.module.BridgeError): self.f.native.call(request)
                with self.assertRaises(ValueError): ModelEditPreview.model_validate(request)
        self.f.native.base.ModifyElements.assert_not_called()

    def test_wrong_parent_hint_stale_child_and_same_model_other_view_do_not_redirect(self):
        f = self.f
        wrong = copy.deepcopy(self.request)
        wrong["exact_target"]["parent_ref"]["view_uuid"] = str(uuid4())
        with self.assertRaises(f.native.module.BridgeError): f.native.call(wrong)
        f.root.IsDeleted.return_value = True
        with self.assertRaises(f.native.module.BridgeError): self.preview()
        f.root.IsDeleted.return_value = False
        alias = copy.deepcopy(f.root)
        alias.GetElementUUID.return_value = str(uuid4())
        alias.GetModelElementUUID.return_value = self.target["model_uuid"]
        alias.GetElementAdapterType.return_value.GetGuid.return_value = f.root.GetElementAdapterType.return_value.GetGuid.return_value
        alias.IsNull.return_value = False
        alias.IsDeleted.return_value = False
        alias.IsValid.return_value = True
        f.native.parents[id(alias)] = self.parent
        f.native.children[id(alias)] = []
        f.native.base.ElementsSelectService.SelectAllElements.return_value = [self.parent, alias]
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["changes"][0]["target_view_uuid"], self.target["view_uuid"])
        f.native.base.ModifyElements.assert_not_called()

    def test_final_mutation_boundary_rechecks_parent_inventory(self):
        f = self.f
        plan = self.preview()
        sibling = f.native.element(91, name="Slab_TypeUUID")
        f.native.children[id(self.parent)] = [f.root, sibling]
        module = importlib.import_module(f.native.module.__package__ + ".wall_material")
        with self.assertRaises(f.native.module.BridgeError):
            module.write(f.native.base, f.root, plan["changes"][0], f.native.handler.current_document())
        f.native.base.ModifyElements.assert_not_called()

    def test_tampered_owner_binding_and_resolution_budget_stop_before_setters(self):
        f = self.f
        plan = self.preview()
        change = copy.deepcopy(plan["changes"][0])
        change["resource"]["exact_target_binding"]["target"]["parent_ref"]["view_uuid"] = str(uuid4())
        module = importlib.import_module(f.native.module.__package__ + ".wall_material")
        self.assertFalse(module.valid_change(change))
        with self.assertRaises(f.native.module.BridgeError):
            module.write(f.native.base, f.root, change, f.native.handler.current_document())
        now = [0.0]
        f.native.handler.model_queries.clock = lambda: now[0]
        def expire(doc):
            now[0] = 11.0
            return [self.parent]
        f.native.base.ElementsSelectService.SelectAllElements.side_effect = expire
        f.native.assert_code("scan_limit_exceeded", self.preview)
        f.native.base.ModifyElements.assert_not_called()

    def test_regenerated_view_stays_unknown_and_recovery_never_retries(self):
        f = self.f
        setter = f.native.base.ModifyElements.side_effect
        def regenerate(*args):
            result = setter(*args)
            f.root.GetElementUUID.return_value = str(uuid4())
            return result
        f.native.base.ModifyElements.side_effect = regenerate
        plan = self.preview()
        f.native.highlight(plan)
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["outcomes"][0]["state"], "unknown", result)
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        self.assertEqual(f.native.recover(execution)["outcomes"][0]["state"], "unknown")
        f.native.base.ModifyElements.assert_called_once()

    def test_lost_response_recovery_never_repeats_setter(self):
        f = self.f
        setter = f.native.base.ModifyElements.side_effect
        def lost(*args):
            setter(*args)
            raise RuntimeError("lost response")
        f.native.base.ModifyElements.side_effect = lost
        plan = self.preview()
        f.native.highlight(plan)
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["outcomes"][0]["state"], "unknown", result)
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        self.assertEqual(f.native.recover(execution)["outcomes"][0]["state"], "reconciled")
        f.native.base.ModifyElements.assert_called_once()


if __name__ == "__main__": unittest.main()
