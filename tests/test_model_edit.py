"""Typed model-edit workflow over fake native adapters and the shared M3 executor."""
import json
import importlib
import unittest
from types import SimpleNamespace
from uuid import uuid4

import test_column_layer as fixtures


class ModelEditTests(unittest.TestCase):
    setUp = fixtures.ColumnLayerTests.setUp
    prepare = fixtures.ColumnLayerTests.prepare
    prepare_context = fixtures.ColumnLayerTests.prepare_context
    adapter = fixtures.ColumnLayerTests.adapter
    element = fixtures.ColumnLayerTests.element
    native = fixtures.ColumnLayerTests.native
    assert_code = fixtures.ColumnLayerTests.assert_code

    def fixture(self, values=("", "F60", "<niezdefiniowany>")):
        self.attribute_type_enum = SimpleNamespace(String=101, Integer=102, Double=103, Boolean=104)
        self.attribute_type_names = {935: "String", 20001: "Integer", 20002: "Boolean", 20017: "String"}
        self.base.AttributeService.AttributeType = self.attribute_type_enum
        self.base.AttributeService.GetAttributeType.side_effect = lambda doc, ident: getattr(
            self.attribute_type_enum, self.attribute_type_names.get(ident, "Unsupported"), 999)
        elements = fixtures.ColumnLayerTests.fixture(self, values)
        return elements

    def attribute_catalog(self, names):
        fixtures.ColumnLayerTests.attribute_catalog(self, names)
        for ident in names:
            self.attribute_type_names.setdefault(ident, "String")

    def request(self, **updates):
        request = {
            "schema_version": "m4-model-edit-1", "action": "preview",
            "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
            "predicate": {"field": "attribute:935", "op": "eq", "value": ""},
            "changes": [
                {"target": {"kind": "attribute", "attribute_id": 935},
                 "value_type": "text", "value": "F120", "mode": "replace"},
                {"target": {"kind": "layer", "short_name": "W1"}},
            ],
        }
        request.update(updates)
        return request

    def call(self, request):
        result = self.handler.handle("/model-edit", request)
        json.dumps(result, allow_nan=False)
        return result

    def preview(self, **updates):
        return self.call(self.request(**updates))

    def plan_request(self, plan):
        return {"schema_version": "m4-model-edit-1", "action": "highlight",
                "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]}

    def highlight(self, plan):
        return self.call(self.plan_request(plan))

    def apply(self, plan, execution_id=None):
        return self.call({"schema_version": "m4-model-edit-1", "action": "apply",
                          "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
                          "execution_id": execution_id or uuid4().hex,
                          "acknowledgement": "disposable_copy_reviewed_plan"})

    def recover(self, execution_id):
        return self.call({"schema_version": "m4-model-edit-1", "action": "recover",
                          "execution_id": execution_id})

    def setter_fakes(self, elements):
        def change_attributes(attributes, targets, *flags):
            self.assertEqual(len(targets), 1)
            element = targets[0]
            current = list(element.GetAttributes.return_value)
            for ident, value in attributes:
                for index, pair in enumerate(current):
                    if pair[0] == ident:
                        current[index] = (ident, value)
                        break
                else:
                    current.append((ident, value))
            element.GetAttributes.return_value = current

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = change_attributes
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 101
        return elements

    def test_attribute_and_layer_apply_replay_then_criterion_no_op(self):
        elements = self.fixture(("", "F60", "<niezdefiniowany>"))
        self.setter_fakes(elements)
        plan = self.preview()
        self.assertTrue(plan["apply_available"])
        self.assertTrue(plan["usable_for_write"])
        self.assertTrue(plan["capabilities"]["apply_available"])
        self.assertFalse(plan["production_apply_available"])
        self.assertEqual(plan["allplan_acceptance"], "not_run")
        self.assertFalse(plan["native_acceptance_blocks_evaluation"])
        self.assertEqual(plan["next_action"]["request"], self.plan_request(plan))
        self.assertEqual(plan["write_blockers"], [])
        self.assertEqual(plan["counts"]["matched"], 1)
        self.assertEqual(plan["counts"]["changes"], 2)
        self.assertEqual(plan["changes"][0]["ref"]["model_uuid"], elements[0].GetModelElementUUID())
        self.assertEqual(self.highlight(plan)["state"], "submitted")
        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.assertEqual(elements[0].GetAttributes.return_value, [(935, "F120")])
        self.assertEqual(elements[0].GetCommonProperties.return_value.Layer, 8)
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)
        self.assertEqual(self.base.ElementsLayerService.ChangeLayer.call_count, 1)
        next_plan = self.preview()
        self.assertEqual(next_plan["state"], "no_op")
        self.assertNotIn("matched", [check["decision"] for check in next_plan["criteria"]["checks"]])

    def test_layer_exact_name_resolves_only_verified_unique_short_name(self):
        elements = self.fixture(("",))
        self.setter_fakes(elements)
        plan = self.preview(predicate=None, changes=[{"target": {"kind": "layer", "name": "W1"}}])
        self.assertEqual(plan["changes"][0]["resource"]["short_name"], "W1")
        self.assertEqual(plan["changes"][0]["resource"]["requested_name"], "W1")
        self.highlight(plan)
        self.assertEqual(self.apply(plan)["state"], "completed")

    def test_layer_full_name_without_unique_sdk_lookup_requires_catalog_probe(self):
        self.fixture(("",))
        self.assert_code("layer_name_catalog_required", lambda: self.preview(predicate=None, changes=[
            {"target": {"kind": "layer", "name": "Structural layer"}},
        ]))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_excluded_target_stays_out_of_changes_and_highlight(self):
        elements = self.fixture(("", "", "F60"))
        self.setter_fakes(elements)
        excluded = elements[0].GetModelElementUUID()
        plan = self.preview(exclude_model_uuids=[excluded])
        self.assertEqual(plan["counts"]["excluded"], 1)
        self.assertEqual(plan["counts"]["matched"], 1)
        self.assertEqual({change["ref"]["model_uuid"] for change in plan["changes"]},
                         {elements[1].GetModelElementUUID()})
        self.highlight(plan)
        shown = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(item) for item in shown], [id(elements[1])])

    def test_newly_matching_peer_conflicts_before_any_setter(self):
        elements = self.fixture(("", "F60"))
        self.setter_fakes(elements)
        plan = self.preview()
        self.assertEqual(plan["counts"]["matched"], 1)
        self.highlight(plan)
        elements[1].GetAttributes.return_value = [(935, "")]
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_matching_target_already_at_values_is_a_no_op_and_empty_match_is_clear(self):
        elements = self.fixture(("F120", "F60"))
        elements[0].GetCommonProperties.return_value.Layer = 8
        self.setter_fakes(elements)
        matching = self.preview(predicate={"field": "attribute:935", "op": "eq", "value": "F120"})
        self.assertEqual(matching["state"], "no_op")
        self.assertEqual(matching["counts"]["matched"], 1)
        self.assertEqual(matching["counts"]["changes"], 0)
        self.assertEqual(len(matching["highlight_targets"]), 1)
        empty = self.preview(predicate={"field": "attribute:935", "op": "eq", "value": "absent-value"})
        self.assertEqual(empty["state"], "no_op")
        self.assertEqual(empty["counts"]["changes"], 0)
        self.assertFalse(empty["highlight_targets"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_declared_value_type_mismatch_fails_before_scan(self):
        self.fixture(("",))
        plan = self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 935},
                                      "value_type": "integer", "value": 120}])
        self.assert_code("attribute_type_unsupported", lambda: self.call(plan))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_lowercase_polish_attribute_name_binds_actual_project_spelling(self):
        self.fixture(("",))
        self.attribute_catalog({935: "Materiał"})
        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "name": "materiał"},
            "value": "bloczki gazobetonowe"}])
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["changes"][0]["resource"]["name"], "Materiał")
        self.assertEqual(plan["changes"][0]["resource"]["attribute_id"], 935)
        self.assert_code("attribute_name_unresolved", lambda: self.preview(
            predicate=None, changes=[{"target": {"kind": "attribute", "name": "Material"},
                                      "value": "concrete"}]))

    def test_name_lookup_runtime_failure_is_not_retried_with_other_spellings(self):
        self.fixture(("",))
        self.base.AttributeService.GetAttributeID.side_effect = RuntimeError("native failure")
        self.assert_code("attribute_name_unresolved", lambda: self.preview(
            changes=[{"target": {"kind": "attribute", "name": "materiał"}, "value": "x"}]))
        self.assertEqual(self.base.AttributeService.GetAttributeID.call_count, 1)

    def test_unsupported_native_attribute_type_fails_before_scan(self):
        self.fixture(("",))
        self.attribute_type_names[935] = "Unsupported"
        plan = self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 935},
                                      "value_type": "text", "value": "F120"}])
        self.assert_code("attribute_type_unsupported", lambda: self.call(plan))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_nonexistent_attribute_binding_fails_before_scan(self):
        self.fixture(("",))
        plan = self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 30000},
                                      "value_type": "text", "value": "F120"}])
        self.assert_code("property_binding_unavailable", lambda: self.call(plan))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_explicit_integer_boolean_values_apply_with_their_native_types(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, 1), (20002, False)])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_COUNT", 20002: "QA_FLAG"})
        self.setter_fakes(elements)
        plan = self.preview(changes=[
            {"target": {"kind": "attribute", "attribute_id": 20001}, "value_type": "integer", "value": 7},
            {"target": {"kind": "attribute", "attribute_id": 20002}, "value_type": "boolean", "value": True},
        ])
        self.assertEqual(plan["counts"]["changes"], 2)
        self.highlight(plan)
        self.assertEqual(self.apply(plan)["state"], "completed")
        self.assertEqual(elements[0].GetAttributes.return_value,
                         [(935, ""), (20001, 7), (20002, True)])

    def test_integer_checkbox_boolean_uses_sdk_bound_zero_one_encoding(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, 0)])
        self.attribute_catalog({935: "Fire", 20001: "Element nośny"})
        self.attribute_type_names[20001] = "Integer"
        controls = SimpleNamespace(CheckBox=41, Edit=42)
        self.base.AttributeService.AttributeControlType = controls
        self.base.AttributeService.GetAttributeControlType.return_value = controls.CheckBox
        self.setter_fakes(elements)

        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 20001}, "value": True,
        }])
        change = plan["changes"][0]
        self.assertEqual(change["new_value"], 1)
        self.assertEqual(change["resource"]["native_type_member"], "Integer")
        self.assertEqual(change["resource"]["boolean_binding"], {
            "control_type_member": "CheckBox", "false_value": 0, "true_value": 1,
            "value": True, "encoded_value": 1,
        })
        self.assertEqual(change["resource"]["value_codec"], "integer_checkbox_boolean")
        self.highlight(plan)
        self.assertEqual(self.apply(plan)["state"], "completed")
        self.assertEqual(elements[0].GetAttributes.return_value, [(935, ""), (20001, 1)])

    def test_integer_boolean_requires_runtime_checkbox_control_member(self):
        self.fixture(("",))
        self.attribute_catalog({935: "Fire", 20001: "Element nośny"})
        self.attribute_type_names[20001] = "Integer"
        controls = SimpleNamespace(Edit=42)
        self.base.AttributeService.AttributeControlType = controls
        self.base.AttributeService.GetAttributeControlType.return_value = controls.Edit

        self.assert_code("attribute_type_unsupported", lambda: self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 20001}, "value": True,
        }]))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_exact_undefined_numeric_old_value_is_preserved_through_apply_recovery_and_noop(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, "<niezdefiniowany>")])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_REAL"})
        self.attribute_type_names[20001] = "Double"
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 101

        def write_then_lose_reply(attributes, targets, *flags):
            targets[0].GetAttributes.return_value = [(935, ""), (20001, 0.2)]
            raise RuntimeError("simulated lost native setter reply")

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = write_then_lose_reply
        plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                            changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                      "value_type": "real", "value": 0.2, "mode": "upsert"}])
        self.assertEqual(plan["counts"]["changes"], 1)
        change = plan["changes"][0]
        self.assertEqual(change["old_value"], {"status": "observed", "value": "<niezdefiniowany>"})
        self.assertEqual(change["old_value_state"], "undefined")
        self.assertTrue(plan["undefined_policy"]["raw_old_value_preserved"])
        self.highlight(plan)
        execution_id = uuid4().hex
        applied = self.apply(plan, execution_id)
        self.assertEqual(applied["outcomes"][0]["state"], "unknown")
        recovery = self.recover(execution_id)
        self.assertEqual(recovery["recovery"]["observations"][0]["state"], "new_value_observed")
        self.assertEqual(recovery["outcomes"][0]["state"], "reconciled")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = None
        next_plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                                 changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                           "value_type": "real", "value": 0.2, "mode": "upsert"}])
        self.assertEqual(next_plan["state"], "no_op")

    def test_arbitrary_numeric_strings_remain_type_mismatches(self):
        elements = self.fixture(("",))
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_REAL"})
        self.attribute_type_names[20001] = "Double"
        for raw in ("0,2", "abc"):
            elements[0].GetAttributes.return_value = [(935, ""), (20001, raw)]
            plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                                changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                          "value_type": "real", "value": 0.2, "mode": "replace"}])
            self.assertEqual(plan["state"], "not_checked", raw)
            self.assertEqual(plan["blocked"][0]["reason"], "old_value_type_differs", raw)
            self.assertFalse(plan["changes"], raw)
            self.assertNotIn("old_value_state", plan["changes"][0] if plan["changes"] else {})

    def test_undefined_old_value_change_conflicts_if_raw_value_changes_before_apply(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, "<niezdefiniowany>")])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_REAL"})
        self.attribute_type_names[20001] = "Double"
        self.setter_fakes(elements)
        plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                            changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                      "value_type": "real", "value": 0.2, "mode": "replace"}])
        self.assertEqual(plan["changes"][0]["old_value"],
                         {"status": "observed", "value": "<niezdefiniowany>"})
        self.highlight(plan)
        elements[0].GetAttributes.return_value = [(935, ""), (20001, "<undefined>")]
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_executor_scope_requires_exact_undefined_annotation(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, "<niezdefiniowany>")])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_REAL"})
        self.attribute_type_names[20001] = "Double"
        plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                            changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                      "value_type": "real", "value": 0.2, "mode": "replace"}])
        RepairExecutor = importlib.import_module("test_allplan_host.repair_execution").RepairExecutor
        self.assertTrue(RepairExecutor.model_edit_scope(plan))

        missing_marker = json.loads(json.dumps(plan))
        missing_marker["changes"][0].pop("old_value_state")
        self.assertFalse(RepairExecutor.model_edit_scope(missing_marker))

        fake_marker = json.loads(json.dumps(plan))
        fake_marker["changes"][0]["old_value"]["value"] = "0,2"
        self.assertFalse(RepairExecutor.model_edit_scope(fake_marker))

        unexpected_marker = json.loads(json.dumps(plan))
        unexpected_marker["changes"][0]["old_value"]["value"] = 1.0
        self.assertFalse(RepairExecutor.model_edit_scope(unexpected_marker))

    def test_more_than_32_native_changes_are_never_applicable(self):
        elements = self.fixture(tuple("" for _ in range(17)))
        for element in elements:
            element.GetAttributes.return_value.extend([(20001, 1), (20002, False)])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_COUNT", 20002: "QA_FLAG"})
        self.setter_fakes(elements)
        plan = self.preview(changes=[
            {"target": {"kind": "attribute", "attribute_id": 20001}, "value_type": "integer", "value": 7},
            {"target": {"kind": "attribute", "attribute_id": 20002}, "value_type": "boolean", "value": True},
        ])
        self.assertEqual(plan["counts"]["changes"], 34)
        self.assertEqual(plan["state"], "not_checked")
        self.assertFalse(plan["evaluation_apply_available"])
        self.assertFalse(plan["apply_available"])
        self.assertIn("change_limit_exceeded", plan["write_blockers"])
        self.assertIsNone(plan["next_action"])
        self.assert_code("repair_scope_unavailable", lambda: self.highlight(plan))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_readall_omission_is_unknown_but_computable_absence_allows_add(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value = [(935, "")]
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20017: "QA_COMPUTED"})
        self.setter_fakes(elements)
        request = self.request(
            predicate={"field": "attribute:20017", "op": "is_unset"},
            changes=[{"target": {"kind": "attribute", "attribute_id": 20017},
                      "value_type": "text", "value": "created", "mode": "upsert"}],
        )
        stored = self.call(request)
        self.assertEqual(stored["state"], "not_checked")
        self.assertFalse(stored["evaluation_apply_available"])
        computable = self.call({**request, "attribute_read_mode": "all_and_computable"})
        self.assertEqual(computable["criteria"]["checks"][0]["decision"], "matched")
        self.assertEqual(computable["changes"][0]["operation"], "add_attribute")
        self.highlight(computable)
        self.assertEqual(self.apply(computable)["state"], "completed")
        self.assertEqual(elements[0].GetAttributes.return_value, [(935, ""), (20017, "created")])

    def test_integer_readback_boolean_true_is_unknown_recovered_without_retry(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, 1)])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_COUNT"})
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 101

        def wrong_native_scalar(attributes, targets, *flags):
            targets[0].GetAttributes.return_value = [(935, ""), (20001, True)]

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = wrong_native_scalar
        plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                            changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                      "value_type": "integer", "value": 2}])
        self.assertEqual(plan["counts"]["changes"], 1)
        self.highlight(plan)
        execution_id = uuid4().hex
        applied = self.apply(plan, execution_id)
        self.assertEqual(applied["state"], "stopped")
        self.assertEqual(applied["outcomes"][0]["state"], "unknown")
        self.assertEqual(applied["outcomes"][0]["readback"], {"status": "observed", "value": True})
        recovered = self.recover(execution_id)
        self.assertEqual(recovered["recovery"]["observations"][0]["state"], "conflict")
        replay = self.apply(plan, execution_id)
        self.assertTrue(replay["replayed"])
        self.assertFalse(replay["automatic_retry"])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_setter_reply_loss_recovers_from_journal_without_a_duplicate_write(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, 1)])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20001: "QA_COUNT"})
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 101

        def write_then_lose_reply(attributes, targets, *flags):
            targets[0].GetAttributes.return_value = [(935, ""), (20001, 2)]
            raise RuntimeError("simulated lost native setter reply")

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = write_then_lose_reply
        plan = self.preview(predicate={"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                            changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                      "value_type": "integer", "value": 2}])
        self.highlight(plan)
        execution_id = uuid4().hex
        applied = self.apply(plan, execution_id)
        self.assertEqual(applied["outcomes"][0]["state"], "unknown")
        recovery = self.recover(execution_id)
        self.assertEqual(recovery["recovery"]["observations"][0]["state"], "new_value_observed")
        self.assertEqual(recovery["outcomes"][0]["state"], "reconciled")
        replay = self.apply(plan, execution_id)
        self.assertTrue(replay["replayed"])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_add_existing_equal_value_is_blocked_and_computed_only_target_is_read_only(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20017, "present")])
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20017: "QA_COMPUTED"})
        existing = self.preview(changes=[{"target": {"kind": "attribute", "attribute_id": 20017},
                                          "value_type": "text", "value": "present", "mode": "add"}])
        self.assertEqual(existing["state"], "not_checked")
        self.assertEqual(existing["blocked"][0]["reason"], "add_requires_proven_absence")
        self.assertFalse(existing["changes"])

        self.base.eAttibuteReadState.ReadAll = "ReadAll"
        self.base.eAttibuteReadState.ReadAllAndComputable = "ReadAllAndComputable"
        elements[0].GetAttributes.side_effect = lambda state: (
            [(935, "")] if state == "ReadAll" else [(935, ""), (20017, "computed-value")])
        computed = self.preview(attribute_read_mode="all_and_computable",
                                changes=[{"target": {"kind": "attribute", "attribute_id": 20017},
                                          "value_type": "text", "value": "replace", "mode": "upsert"}])
        self.assertEqual(computed["state"], "not_checked")
        self.assertEqual(computed["blocked"][0]["reason"], "computed_attribute_is_read_only")
        self.assertFalse(computed["changes"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_wall_material_attribute_target_is_independent_of_geometry_readers(self):
        elements = self.fixture(("",))
        wall = elements[0]
        wall.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        wall.GetElementAdapterType.return_value.GetGuid.return_value = "20000000-0000-4000-8000-000000000935"
        wall.GetAttributes.return_value = [(20017, "Concrete")]
        self.attribute_catalog({935: "Klasa odporności ogniowej", 20017: "Wall material"})
        self.setter_fakes(elements)
        plan = self.preview(native_types=["Wall_TypeUUID"],
                            predicate={"field": "attribute:20017", "op": "eq", "value": "Concrete"},
                            changes=[{"target": {"kind": "attribute", "attribute_id": 20017},
                                      "value_type": "text", "value": "Stone", "mode": "replace"}])
        self.assertEqual(plan["counts"]["matched"], 1)
        self.assertEqual(plan["changes"][0]["native_type"], "Wall_TypeUUID")
        self.highlight(plan)
        self.assertEqual(self.apply(plan)["state"], "completed")
        self.assertEqual(wall.GetAttributes.return_value, [(20017, "Stone")])
        wall.GetModelGeometry.assert_not_called()

    def test_auto_type_uses_metadata_for_arbitrary_attributes_across_component_families(self):
        for native_type in ("Column_TypeUUID", "Wall_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID",
                            "Beam_TypeUUID", "SkeletonBeam_TypeUUID", "WindowDoor_TypeUUID"):
            with self.subTest(native_type=native_type):
                elements = self.fixture(("",))
                element = elements[0]
                element.GetElementAdapterType.return_value.GetTypeName.return_value = native_type
                element.GetAttributes.return_value = [(20001, 1), (20002, False), (20017, "old")]
                self.attribute_catalog({20001: "Custom integer", 20002: "Custom boolean", 20017: "Custom text"})
                self.setter_fakes(elements)
                plan = self.preview(native_types=[native_type], predicate=None, changes=[
                    {"target": {"kind": "attribute", "attribute_id": 20001}, "value": 7},
                    {"target": {"kind": "attribute", "attribute_id": 20002}, "value_type": "auto", "value": True},
                    {"target": {"kind": "attribute", "name": "Custom text"}, "value": "new"}])
                self.assertTrue(plan["apply_available"], plan)
                shown = self.highlight(plan)
                self.assertEqual(shown["next_action"]["request"]["action"], "apply")
                self.assertIn("execution_id", shown["next_action"]["required_request_fields"])
                self.assertTrue(self.call({**self.plan_request(plan), "action": "revalidate"})["apply_available"])
                self.assertEqual(self.apply(plan)["state"], "completed")
                self.assertEqual(dict(element.GetAttributes.return_value), {20001: 7, 20002: True, 20017: "new"})

    def test_unresolved_exact_attribute_name_gives_a_discovery_path_before_scan(self):
        self.fixture(("",))
        self.base.AttributeService.GetAttributeID.side_effect = ValueError("unknown project name")
        request = self.request(changes=[{"target": {"kind": "attribute", "name": "Przenikalność cieplna U"},
                                         "value": 0.2}])
        with self.assertRaises(self.module.BridgeError) as caught:
            self.call(request)
        self.assertEqual(caught.exception.code, "attribute_name_unresolved")
        self.assertIn("element_attributes", str(caught.exception))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_auto_type_never_converts_text_numbers_or_boolean_to_integer(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, 1)])
        self.attribute_catalog({935: "Fire", 20001: "Integer"})
        for value in (True, "0,2", "7"):
            with self.subTest(value=value):
                self.assert_code("attribute_type_unsupported", lambda: self.preview(
                    predicate=None, changes=[{"target": {"kind": "attribute", "attribute_id": 20001}, "value": value}]))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_integer_element_nośny_does_not_guess_boolean_encoding(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value.extend([(20001, 0)])
        self.attribute_catalog({935: "Fire", 20001: "Element nośny"})

        for value_type, value in (("auto", True), ("boolean", True)):
            with self.subTest(value_type=value_type):
                self.assert_code("attribute_type_unsupported", lambda: self.preview(
                    predicate=None, changes=[{"target": {"kind": "attribute", "attribute_id": 20001},
                                             "value_type": value_type, "value": value}]))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_explicit_enum_label_roundtrip_apply_replay_and_noop(self):
        elements = self.fixture(("",))
        elements[0].GetAttributes.return_value = [(20001, "Existing building")]
        self.attribute_catalog({20001: "Construction category"})
        self.attribute_type_names[20001] = "Integer"
        enum_values = {"New building": 0, "Existing building": 1}
        self.base.AttributeService.GetEnumIDFromValueString.side_effect = lambda ident, label: enum_values[label]
        self.base.AttributeService.GetEnumValueStringFromID.side_effect = lambda ident, key: next(
            label for label, value in enum_values.items() if value == key)
        self.setter_fakes(elements)
        request = self.request(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 20001}, "value_type": "enum", "value": "New building"}])
        plan = self.call(request)
        self.assertTrue(plan["apply_available"])
        self.assertEqual(plan["changes"][0]["resource"]["enum_binding"], {"enum_id": 0, "value": "New building"})
        self.highlight(plan)
        execution = uuid4().hex
        self.assertEqual(self.apply(plan, execution)["state"], "completed")
        self.assertTrue(self.apply(plan, execution)["replayed"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_args.args[0], [(20001, "New building")])
        self.assertEqual(self.call(request)["state"], "no_op")
        self.base.AttributeService.GetEnumValues.assert_not_called()

    def test_enum_mapping_change_or_invalid_label_stops_before_any_setter(self):
        self.fixture(("old",))
        self.base.AttributeService.GetEnumIDFromValueString.return_value = 0
        self.base.AttributeService.GetEnumValueStringFromID.return_value = "new"
        request = self.request(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 935}, "value_type": "enum", "value": "new"}])
        plan = self.call(request)
        self.highlight(plan)
        self.base.AttributeService.GetEnumIDFromValueString.return_value = 1
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.AttributeService.GetEnumValueStringFromID.return_value = "different"
        self.assert_code("attribute_enum_unresolved", lambda: self.call(request))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.AttributeService.GetEnumValues.assert_not_called()

    def test_auto_sdk_enum_type_binds_exact_label_without_enumerating_catalog(self):
        elements = self.fixture(("old",))
        elements[0].GetAttributes.return_value.extend([(20001, "Existing")])
        self.attribute_catalog({935: "Fire", 20001: "Construction category"})
        self.attribute_type_enum.Enum = 105
        self.attribute_type_names[20001] = "Enum"
        enum_values = {"New": 0, "Existing": 1}
        self.base.AttributeService.GetEnumIDFromValueString.side_effect = lambda ident, label: enum_values[label]
        self.base.AttributeService.GetEnumValueStringFromID.side_effect = lambda ident, key: next(
            label for label, value in enum_values.items() if value == key)
        self.setter_fakes(elements)

        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 20001}, "value": "New",
        }])
        self.assertEqual(plan["changes"][0]["resource"]["data_type"], "enum")
        self.assertEqual(plan["changes"][0]["resource"]["enum_binding"], {"enum_id": 0, "value": "New"})
        self.highlight(plan)
        self.assertEqual(self.apply(plan)["state"], "completed")
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_args.args[0], [(20001, "New")])
        self.base.AttributeService.GetEnumValues.assert_not_called()

    def test_enum_binding_marker_is_required_by_executor_and_native_adapter(self):
        import copy
        from unittest.mock import patch
        from types import SimpleNamespace
        self.fixture(("old",))
        self.base.AttributeService.GetEnumIDFromValueString.return_value = 0
        self.base.AttributeService.GetEnumValueStringFromID.return_value = "new"
        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 935}, "value_type": "enum", "value": "new"}])
        damaged = copy.deepcopy(plan)
        damaged["changes"][0]["resource"].pop("enum_binding")
        execution = importlib.import_module(self.module.__package__ + ".repair_execution")
        native = importlib.import_module(self.module.__package__ + ".native_model_edit")
        self.assertFalse(execution.RepairExecutor.model_edit_scope(damaged))
        with patch.dict("sys.modules", {"NemAll_Python_IFW_ElementAdapter": SimpleNamespace(BaseElementAdapterList=list)}):
            self.assert_code("target_not_writable", lambda: native.write(self.base, object(), damaged["changes"][0]))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
