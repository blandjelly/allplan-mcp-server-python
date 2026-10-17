"""Wall-tier layer ownership rules using fake Allplan adapters."""
import importlib
import types
import unittest
import weakref

import test_m1_completion as fixtures


class WallLayerTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    adapter = fixtures.M1CompletionTests.adapter
    native = fixtures.M1CompletionTests.native
    element = fixtures.M1CompletionTests.element

    def setup_wall(self, layers=(3735,), extra=()):
        root = self.element(1, name="Wall_TypeUUID")
        root.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3735)
        root.GetElementAdapterType.return_value.GetGuid.return_value = "20000000-0000-4000-8000-000000000001"
        tiers = []
        for i, layer in enumerate(layers, 2):
            tier = self.element(i, name="WallTier_TypeUUID", number=101)
            tier.GetCommonProperties.return_value = types.SimpleNamespace(Layer=layer)
            tier.IsNull.return_value = False
            tier.IsDeleted.return_value = False
            tier.IsValid.return_value = True
            tier.IsInActiveDocument.return_value = True
            tier.IsInActiveLayer.return_value = True
            tier.IsLabelElement.return_value = False
            tiers.append(tier)
        children = [*tiers, *extra]
        self.native([root, *children])
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 101
        self.children[id(root)] = children
        for tier in tiers:
            self.parents[id(tier)] = root
        module = importlib.import_module("test_allplan_host.wall_layer")
        return module, root, tiers

    def change_for(self, evidence):
        return {"operation": "set_wall_layer", "adapter_version": "m4-model-edit-1",
                "property_role": "layer", "field": "layer_id", "native_type": "Wall_TypeUUID",
                "ref": {"drawing_file": evidence["root"]["drawing_file"],
                        "model_uuid": evidence["root"]["model_uuid"],
                        "type_uuid": evidence["root"]["type_uuid"], "type_name": "Wall_TypeUUID"},
                "old_value": {"status": "observed", "value": evidence["tiers"][0]["layer"]},
                "new_value": 3701,
                "resource": {"short_name": "SZ_OGÓ02", "layer_id": 3701,
                             "wall_layer_ownership": evidence}}

    def test_observation_uses_direct_tiers_and_effective_layer_requires_agreement(self):
        axis = self.element(20, name="WallAxis_TypeUUID")
        opening = self.element(21, name="WindowDoor_TypeUUID")
        module, root, tiers = self.setup_wall((3735, 3735), (axis, opening))
        evidence = module.observe(root, self.adapter_module)
        self.assertEqual(module.layer_value(evidence), {"status": "observed", "value": 3735})
        self.assertEqual(len(evidence["tiers"]), 2)
        self.assertEqual({tier["type_name"] for tier in evidence["tiers"]}, {"WallTier_TypeUUID"})
        self.assertTrue(module.same_owners(evidence, evidence))
        self.assertEqual(self.children[id(root)], [*tiers, axis, opening])

    def test_mixed_tier_layers_are_not_one_effective_wall_layer(self):
        module, root, _tiers = self.setup_wall((3735, 3701))
        evidence = module.observe(root, self.adapter_module)
        self.assertEqual(module.layer_value(evidence), {
            "status": "not_checked", "value": None, "reason": "mixed_wall_tier_layers"})

    def test_exact_duplicate_tier_wrapper_is_collapsed_but_conflict_is_rejected(self):
        module, root, tiers = self.setup_wall((3735,))
        duplicate = self.element(2, name="WallTier_TypeUUID")
        duplicate.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3735)
        self.parents[id(duplicate)] = root
        self.children[id(root)].append(duplicate)
        evidence = module.observe(root, self.adapter_module)
        self.assertEqual(len(evidence["tiers"]), 1)

        duplicate.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3701)
        with self.assertRaises(self.module.BridgeError):
            module.observe(root, self.adapter_module)
        self.parents[id(tiers[0])] = root
        tiers[0].GetDrawingfileNumber.return_value = 102
        with self.assertRaises(self.module.BridgeError):
            module.observe(root, self.adapter_module)

    def test_write_targets_only_fresh_tiers_and_keeps_root_unchanged(self):
        module, root, tiers = self.setup_wall((3735, 3735))
        self.adapter_module.BaseElementAdapterList = list
        evidence = module.observe(root, self.adapter_module)

        import NemAll_Python_IFW_ElementAdapter as live_adapters
        original_get_children = live_adapters.BaseElementAdapterChildElementsService.GetChildModelElements
        class ChildOwner:
            def __init__(self, values):
                self.values = values
            def __iter__(self):
                return iter(self.values)
        owner_refs = []
        def get_children(element, include_children):
            owner = ChildOwner(original_get_children(element, include_children))
            owner_refs.append(weakref.ref(owner))
            return owner
        live_adapters.BaseElementAdapterChildElementsService.GetChildModelElements = get_children

        def native_change(targets, short_name):
            self.assertEqual(short_name, "SZ_OGÓ02")
            self.assertEqual(targets, tiers)
            self.assertIsNotNone(owner_refs[-1]())
            for target in targets:
                target.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3701)
            return targets

        self.base.ElementsLayerService.ChangeLayer.side_effect = native_change
        change = self.change_for(evidence)
        self.assertTrue(module.preflight(self.base, root, change, self.adapter_module))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        returned = module.write(self.base, root, change, self.adapter_module)
        self.assertEqual(root.GetCommonProperties().Layer, 3735)
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        targets = self.base.ElementsLayerService.ChangeLayer.call_args.args[0]
        self.assertIs(returned, targets)
        self.assertEqual(targets, tiers)
        self.assertNotIn(root, targets)

    def test_membership_or_layer_change_after_preview_blocks_before_setter(self):
        module, root, _tiers = self.setup_wall((3735,))
        self.adapter_module.BaseElementAdapterList = list
        reviewed = module.observe(root, self.adapter_module)
        extra = self.element(30, name="WallTier_TypeUUID")
        extra.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3735)
        self.parents[id(extra)] = root
        self.children[id(root)].append(extra)
        change = self.change_for(reviewed)
        with self.assertRaises(self.module.BridgeError) as error:
            module.write(self.base, root, change, self.adapter_module)
        self.assertEqual(error.exception.code, "selection_stale")
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_wrong_parent_or_cross_file_tier_is_rejected(self):
        module, root, tiers = self.setup_wall((3735,))
        other = self.element(40, name="Wall_TypeUUID")
        self.parents[id(tiers[0])] = other
        with self.assertRaises(self.module.BridgeError):
            module.observe(root, self.adapter_module)

    def test_passive_wall_can_be_read_but_never_preflighted_for_write(self):
        module, root, tiers = self.setup_wall((3735,))
        root.GetDrawingfileNumber.return_value = -101
        tiers[0].GetDrawingfileNumber.return_value = -101
        evidence = module.observe(root, self.adapter_module)
        self.assertEqual(evidence["root"]["drawing_file"], 101)
        self.assertEqual(evidence["root"]["signed_drawing_file"], -101)
        self.assertEqual(module.layer_value(evidence), {"status": "observed", "value": 3735})
        change = self.change_for(evidence)
        with self.assertRaises(self.module.BridgeError):
            module.preflight(self.base, root, change, self.adapter_module)
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_valid_change_is_pure_and_rejects_incomplete_or_mismatched_manifest(self):
        module, root, _tiers = self.setup_wall((3735, 3735))
        evidence = module.observe(root, self.adapter_module)
        change = self.change_for(evidence)
        self.assertTrue(module.valid_change(change))
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements = (
            lambda *_args: self.fail("valid_change must not call Allplan"))
        self.assertTrue(module.valid_change(change))
        malformed = {**change, "resource": {**change["resource"],
                                             "wall_layer_ownership": {"schema_version": module.SCHEMA,
                                                                      "complete": True, "root": {}, "tiers": []}}}
        self.assertFalse(module.valid_change(malformed))
        mismatched = {**change, "ref": {**change["ref"], "model_uuid": "00000000-0000-4000-8000-000000000999"}}
        self.assertFalse(module.valid_change(mismatched))

    def test_multiple_views_and_tier_limit_fail_closed(self):
        module, root, tiers = self.setup_wall((3735,))
        second = self.element(50, name="WallTier_TypeUUID")
        second.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3735)
        self.parents[id(second)] = root
        # Same model, different view is not an interchangeable write owner.
        second.GetModelElementUUID.return_value = tiers[0].GetModelElementUUID()
        self.children[id(root)].append(second)
        with self.assertRaises(self.module.BridgeError):
            module.observe(root, self.adapter_module)

        many = [self.element(i + 100, name="WallTier_TypeUUID") for i in range(module.MAX_TIERS + 1)]
        for tier in many:
            tier.GetCommonProperties.return_value = types.SimpleNamespace(Layer=3735)
            self.parents[id(tier)] = root
        self.children[id(root)] = many
        with self.assertRaises(self.module.BridgeError):
            module.observe(root, self.adapter_module)


if __name__ == "__main__":
    unittest.main()
