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
        self.assert_code("property_binding_unavailable", lambda: self.call(plan))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_unsupported_native_attribute_type_fails_before_scan(self):
        self.fixture(("",))
        self.attribute_type_names[935] = "Unsupported"
        plan = self.request(changes=[{"target": {"kind": "attribute", "attribute_id": 935},
                                      "value_type": "text", "value": "F120"}])
        self.assert_code("property_binding_unavailable", lambda: self.call(plan))
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
