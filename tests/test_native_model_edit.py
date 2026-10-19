"""Generic native attribute/layer adapter boundaries with fake Allplan APIs."""
import importlib
import types
import unittest

import test_m1_completion as fixtures


class NativeModelEditTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    adapter = fixtures.M1CompletionTests.adapter
    native = fixtures.M1CompletionTests.native
    element = fixtures.M1CompletionTests.element

    def edit_adapter(self):
        return importlib.import_module("test_allplan_host.native_model_edit")

    def test_numeric_undefined_replacement_requires_the_exact_reviewed_marker(self):
        element = self.element()
        self.native([element])
        self.adapter_module.BaseElementAdapterList = list
        change = {"adapter_version": "m4-model-edit-1", "operation": "set_attribute",
                  "resource": {"attribute_id": 83, "data_type": "real"},
                  "new_value": 0.2, "old_value": {"status": "observed", "value": "<niezdefiniowany>"}}
        adapter = self.edit_adapter()
        with self.assertRaises(self.module.BridgeError):
            adapter.write(self.base, element, change)
        change["old_value_state"] = "undefined"
        adapter.write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once_with([(83, 0.2)], [element], False, False)
        self.base.ElementsAttributeService.ChangeAttributes.reset_mock()
        for raw in ("abc", "0,2", 0.1):
            change["old_value"]["value"] = raw
            with self.assertRaises(self.module.BridgeError):
                adapter.write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_attribute_fields_distinguishes_stored_missing_from_computed_complete_absence(self):
        element = self.element(attrs=[])
        self.native([element])
        self.base.eAttibuteReadState.ReadAllAndComputable = 3
        adapter = self.edit_adapter()

        stored = adapter.attribute_fields(element, self.base, [83], "stored")["attribute:83"]
        complete = adapter.attribute_fields(element, self.base, [83], "all_and_computable")["attribute:83"]

        self.assertEqual(stored["status"], "missing")
        self.assertFalse(stored["presence_proven"])
        self.assertEqual(complete["status"], "absent")
        self.assertTrue(complete["presence_proven"])
        self.assertEqual([call.args[0] for call in element.GetAttributes.call_args_list], [1, 1, 3])

    def test_computed_only_value_is_visible_but_marked_not_editable(self):
        element = self.element(attrs=[])
        self.native([element])
        self.base.eAttibuteReadState.ReadAllAndComputable = 3
        element.GetAttributes.side_effect = lambda mode: [] if mode == 1 else [(83, "derived")]
        result = self.edit_adapter().attribute_fields(element, self.base, [83], "all_and_computable")["attribute:83"]
        self.assertEqual(result, {"status": "observed", "value": "derived",
                                  "computed_only": True, "presence_proven": False})

    def test_computed_inclusive_absence_requires_both_successful_read_modes(self):
        element = self.element(attrs=[])
        self.native([element])
        self.base.eAttibuteReadState.ReadAllAndComputable = 3
        element.GetAttributes.side_effect = [RuntimeError("stored read failed"), []]
        result = self.edit_adapter().attribute_fields(element, self.base, [83], "all_and_computable")["attribute:83"]
        self.assertEqual(result["status"], "not_checked")
        element.GetAttributes.assert_called_once_with(1)

    def test_attribute_fields_keeps_explicit_null_and_rejects_ambiguous_values(self):
        element = self.element(attrs=[(83, None)])
        self.native([element])
        self.base.eAttibuteReadState.ReadAllAndComputable = 3
        adapter = self.edit_adapter()
        self.assertEqual(adapter.attribute_fields(element, self.base, [83])["attribute:83"],
                         {"status": "observed", "value": None})
        element.GetAttributes.return_value = [(83, "A"), (83, "B")]
        self.assertEqual(adapter.attribute_fields(element, self.base, [83])["attribute:83"]["status"],
                         "not_checked")

    def test_write_requires_adapter_version_typed_scalar_and_proven_add_absence(self):
        element = self.element()
        self.native([element])
        self.adapter_module.BaseElementAdapterList = list
        change = {"adapter_version": "other", "operation": "set_attribute",
                  "resource": {"attribute_id": 83, "data_type": "string"},
                  "new_value": "R30", "old_value": {"status": "observed", "value": "R60"}}
        with self.assertRaises(self.module.BridgeError):
            self.edit_adapter().write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

        change["adapter_version"] = "m4-model-edit-1"
        change["new_value"] = False
        with self.assertRaises(self.module.BridgeError):
            self.edit_adapter().write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

        change.update(operation="add_attribute", new_value="R30",
                      resource={"attribute_id": 83, "data_type": "string", "read_mode": "all_and_computable"},
                      old_value={"status": "absent", "presence_proven": True,
                                 "evidence": "absent_from_ReadAllAndComputable"})
        self.edit_adapter().write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once_with([(83, "R30")], [element], False, False)

    def test_integer_checkbox_binding_is_exact_and_optional(self):
        element = self.element(attrs=[(83, 0)])
        self.native([element])
        self.adapter_module.BaseElementAdapterList = list
        adapter = self.edit_adapter()
        change = {"adapter_version": "m4-model-edit-1", "operation": "set_attribute",
                  "resource": {"attribute_id": 83, "data_type": "integer",
                               "native_type_member": "Integer", "value_codec": "integer_checkbox_boolean",
                               "boolean_binding": {"control_type_member": "CheckBox", "false_value": 0,
                                                   "true_value": 1, "value": True, "encoded_value": 1}},
                  "old_value": {"status": "observed", "value": 0}, "new_value": 1}
        adapter.write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once_with([(83, 1)], [element], False, False)

        self.base.ElementsAttributeService.ChangeAttributes.reset_mock()
        change["resource"]["boolean_binding"]["encoded_value"] = 0
        with self.assertRaises(self.module.BridgeError):
            adapter.write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

        change["resource"].pop("boolean_binding")
        change["resource"].pop("value_codec")
        change["new_value"] = 7
        adapter.write(self.base, element, change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once_with([(83, 7)], [element], False, False)

    def test_add_rejects_stored_read_omission_and_replace_rejects_unknown_old_value(self):
        element = self.element()
        self.native([element])
        self.adapter_module.BaseElementAdapterList = list
        adapter = self.edit_adapter()
        base_change = {"adapter_version": "m4-model-edit-1", "operation": "add_attribute",
                       "resource": {"attribute_id": 83, "data_type": "integer", "read_mode": "stored"},
                       "new_value": 7, "old_value": {"status": "missing", "presence_proven": False}}
        with self.assertRaises(self.module.BridgeError):
            adapter.write(self.base, element, base_change)
        base_change.update(operation="set_attribute", resource={"attribute_id": 83, "data_type": "integer"},
                           old_value={"status": "not_checked", "value": None})
        with self.assertRaises(self.module.BridgeError):
            adapter.write(self.base, element, base_change)
        base_change.update(old_value={"status": "observed", "value": 7, "computed_only": True})
        with self.assertRaises(self.module.BridgeError):
            adapter.write(self.base, element, base_change)
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_layer_write_uses_exact_short_name_and_attribute_type_checks_are_strict(self):
        element = self.element()
        self.native([element])
        self.adapter_module.BaseElementAdapterList = list
        adapter = self.edit_adapter()
        adapter.write(self.base, element, {"adapter_version": "m4-model-edit-1", "operation": "set_layer",
                                           "resource": {"short_name": "STR"}})
        self.base.ElementsLayerService.ChangeLayer.assert_called_once_with([element], "STR")
        self.assertTrue(adapter.value_matches("a", "text"))
        self.assertTrue(adapter.value_matches(3, "integer"))
        self.assertFalse(adapter.value_matches(True, "integer"))
        self.assertTrue(adapter.value_matches(3.5, "real"))
        self.assertTrue(adapter.value_matches(False, "boolean"))

    def test_resolve_gates_six_exact_roots_and_rejects_family_mismatch(self):
        self.native()
        query = self.handler.model_queries
        adapter = self.edit_adapter()
        families = ("Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID",
                    "Wall_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID")
        for index, family in enumerate(families, start=1):
            element = self.element(index, name=family)
            self.base.ElementsSelectService.SelectAllElements.return_value = [element]
            type_uuid = element.GetElementAdapterType.return_value.GetGuid.return_value
            change = {"native_type": family,
                      "ref": {"drawing_file": 101,
                              "model_uuid": element.GetModelElementUUID.return_value,
                              "type_uuid": type_uuid}}
            self.assertIs(adapter.resolve(self.coord.GetInputViewDocument(), self.base, query, change), element)
        change["native_type"] = "Wall_TypeUUID"
        self.assert_code("repair_conflict", lambda: adapter.resolve(
            self.coord.GetInputViewDocument(), self.base, query, change))

    def test_unrelated_broken_hierarchy_cannot_poison_exact_target_resolution(self):
        target = self.element(1, name="Beam_TypeUUID")
        unrelated = self.element(2, name="Wall_TypeUUID")
        self.native([target, unrelated])
        # A stale/unrelated adapter can fail while walking its parent chain.
        # Direct model identity lets resolution safely exclude it first.
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = (
            lambda element: (_ for _ in ()).throw(RuntimeError("unrelated parent unavailable"))
            if element is unrelated else types.SimpleNamespace(IsNull=lambda: True))
        change = {"native_type": "Beam_TypeUUID", "ref": {
            "drawing_file": 101, "model_uuid": target.GetModelElementUUID.return_value,
            "type_uuid": target.GetElementAdapterType.return_value.GetGuid.return_value}}
        resolved = self.edit_adapter().resolve(self.coord.GetInputViewDocument(), self.base,
                                               self.handler.model_queries, change)
        self.assertIs(resolved, target)
        self.assertEqual(unrelated.GetElementUUID.call_count, 0)

    def test_child_only_enumeration_resolves_its_component_root(self):
        target = self.element(1, name="Beam_TypeUUID")
        child = self.element(2, name="BeamAxis_TypeUUID")
        self.native([child])
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = (
            lambda element: target if element is child else types.SimpleNamespace(IsNull=lambda: True))
        change = {"native_type": "Beam_TypeUUID", "ref": {
            "drawing_file": 101, "model_uuid": target.GetModelElementUUID.return_value,
            "type_uuid": target.GetElementAdapterType.return_value.GetGuid.return_value}}
        resolved = self.edit_adapter().resolve(self.coord.GetInputViewDocument(), self.base,
                                               self.handler.model_queries, change)
        self.assertIs(resolved, target)

    def test_deleted_same_identity_wrapper_is_skipped_only_when_lifecycle_is_known(self):
        target = self.element(1, name="Beam_TypeUUID")
        deleted = self.element(1, name="Beam_TypeUUID")
        deleted.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000002"
        deleted.IsDeleted.return_value = True
        self.native([deleted, target])
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = (
            lambda element: (_ for _ in ()).throw(RuntimeError("deleted wrapper has no parent"))
            if element is deleted else types.SimpleNamespace(IsNull=lambda: True))
        change = {"native_type": "Beam_TypeUUID", "ref": {
            "drawing_file": 101, "model_uuid": target.GetModelElementUUID.return_value,
            "type_uuid": target.GetElementAdapterType.return_value.GetGuid.return_value}}
        resolved = self.edit_adapter().resolve(self.coord.GetInputViewDocument(), self.base,
                                               self.handler.model_queries, change)
        self.assertIs(resolved, target)
        self.assertEqual(deleted.GetElementUUID.call_count, 0)

    def assert_code(self, code, callback):
        with self.assertRaises(self.module.BridgeError) as error:
            callback()
        self.assertEqual(error.exception.code, code)
