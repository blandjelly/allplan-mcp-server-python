"""Mutation failure, replay and restart recovery checks with stateful native fakes."""
import copy
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import test_model_repair as fixtures
import test_model_edit as model_edit_fixtures
from allplan_mcp.repair_models import RepairRequest
from pydantic import TypeAdapter, ValidationError


class ExecutionTests(unittest.TestCase):
    prepare_context = fixtures.RepairTests.prepare_context
    prepare = fixtures.RepairTests.prepare
    adapter = fixtures.RepairTests.adapter
    native = fixtures.RepairTests.native
    element = fixtures.RepairTests.element
    resources = fixtures.RepairTests.resources
    fixture = fixtures.RepairTests.fixture
    assert_code = fixtures.RepairTests.assert_code
    request = fixtures.RepairTests.request
    preview = fixtures.RepairTests.preview

    def setUp(self):
        fixtures.RepairTests.setUp(self)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.handler.repair_plans.executor.path = Path(self.directory.name)

    def writable_fixture(self):
        elements = self.fixture()
        self.adapter_module.BaseElementAdapterList = list
        for e in elements:
            for method, value in (("IsDeleted", False), ("IsValid", True), ("IsInActiveDocument", True),
                                  ("IsInActiveLayer", True), ("IsInMacro", False), ("IsLabelElement", False)):
                getattr(e, method).return_value = value
        def layer(targets, short_name):
            self.assertEqual(short_name, "SZ_OGÓ01")
            targets[0].GetCommonProperties.return_value.Layer = 7
            return targets
        def attribute(data, targets, undefined, deleted):
            self.assertEqual(data, [(20002, "NEW")])
            self.assertFalse(undefined)
            self.assertFalse(deleted)
            targets[0].GetAttributes.return_value = [(20001, "S06"), (20002, "NEW")]
            return targets
        self.base.ElementsLayerService.ChangeLayer.side_effect = layer
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = attribute
        return elements

    def apply_request(self, plan, **overrides):
        return {"schema_version": "m3-repair-1", "action": "apply", "plan_id": plan["plan_id"],
                "plan_hash": plan["plan_hash"], "execution_id": uuid4().hex,
                "acknowledgement": "disposable_copy_reviewed_two_repairs", **overrides}

    def call(self, request):
        return self.handler.handle("/fix-model-issues", request)

    def recover(self, request):
        return self.call({"schema_version": "m3-repair-1", "action": "recover", "execution_id": request["execution_id"]})

    def test_apply_readback_three_findings_replay_restart_and_undo_never_repeat(self):
        elements = self.writable_fixture()
        request = self.apply_request(self.preview())
        result = self.call(request)
        self.assertEqual(result["state"], "completed")
        self.assertEqual([o["state"] for o in result["outcomes"]], ["applied", "applied"])
        self.assertEqual(result["audit_after"]["counts"]["findings"], 3)
        self.assertFalse(result["runtime_verified"])
        self.assertEqual(len(self.handler.repair_plans.plans), 0)
        for restart in (False, True):
            if restart:
                service = importlib.import_module("test_allplan_host.model_repair").RepairPlanService
                self.handler.repair_plans = service(self.handler.model_queries, self.directory.name)
            self.assertTrue(self.call(request)["replayed"])
        elements[4].GetCommonProperties.return_value.Layer = 8
        elements[5].GetAttributes.return_value = [(20001, "S06"), (20002, "NWE")]
        recovered = self.recover(request)
        self.assertTrue(recovered["read_only"])
        self.assertEqual([o["state"] for o in recovered["recovery"]["observations"]], ["old_value_observed"] * 2)
        self.assertTrue(self.call(request)["replayed"])
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        self.assert_code("execution_id_conflict", lambda: self.call({**request, "plan_hash": "0" * 64}))

    def test_all_targets_checked_before_first_write_and_manual_change_conflicts(self):
        for method, value in (("IsDeleted", True), ("IsValid", False), ("IsInActiveLayer", False),
                              ("IsLabelElement", True)):
            with self.subTest(method=method):
                elements = self.writable_fixture()
                request = self.apply_request(self.preview())
                getattr(elements[5], method).return_value = value
                # The query layer now excludes an explicitly deleted adapter
                # before execution and correctly invalidates this plan.
                expected_code = "repair_conflict" if method == "IsDeleted" else "target_not_writable"
                self.assert_code(expected_code, lambda: self.call(request))
                self.base.ElementsLayerService.ChangeLayer.assert_not_called()
                self.assertFalse(list(Path(self.directory.name).glob("*.json")))
        elements = self.writable_fixture()
        request = self.apply_request(self.preview())
        elements[5].GetAttributes.return_value = [(20001, "S06"), (20002, "EXISTING")]
        self.assert_code("repair_conflict", lambda: self.call(request))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_native_column_parent_flag_does_not_mean_macro_and_is_retained(self):
        elements = self.writable_fixture()
        # Reproduce the observed 0.8.0 rejection flag, while the required parent
        # service establishes both terminal roots as the reviewed Columns.
        for element in elements[:6]:
            element.IsInMacro.return_value = True
        result = self.call(self.apply_request(self.preview()))
        self.assertEqual(result["state"], "completed")
        self.assertEqual(result["audit_after"]["counts"]["findings"], 3)
        self.assertEqual([d["native_flags"]["IsInMacro"]["value"] for d in result["target_preflight"]], [True, True])
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_macro_or_unknown_ancestor_cannot_become_a_writable_column_root(self):
        for name in ("Macro_TypeUUID", "MacroPlacement_TypeUUID", "Unknown_TypeUUID"):
            with self.subTest(name=name):
                elements = self.writable_fixture()
                plan = self.preview()
                container = self.element(70, name=name)
                self.parents[id(elements[4])] = container
                adapter = importlib.import_module("test_allplan_host.native_repairs")
                self.assert_code("repair_conflict", lambda: adapter.resolve(
                    self.coord.GetInputViewDocument(), self.base, self.handler.model_queries,
                    plan["changes"][0], writable=True))
                self.base.ElementsLayerService.ChangeLayer.assert_not_called()
                self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_no_change_and_exception_stop_without_second_write_or_rollback(self):
        self.writable_fixture()
        request = self.apply_request(self.preview())
        self.base.ElementsLayerService.ChangeLayer.side_effect = lambda *a: []
        result = self.call(request)
        self.assertEqual([o["state"] for o in result["outcomes"]], ["failed", "skipped"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.reset_mock()
        self.writable_fixture()
        request = self.apply_request(self.preview())
        self.base.ElementsLayerService.ChangeLayer.side_effect = RuntimeError("native failure")
        result = self.call(request)
        self.assertEqual([o["state"] for o in result["outcomes"]], ["unknown", "skipped"])
        self.assertTrue(self.call(request)["replayed"])
        # Another execution cannot silently bypass an unresolved write.
        plan = self.handler.repair_plans.handle(self.coord.GetInputViewDocument(), self.base, self.settings, self.request())
        self.assert_code("repair_recovery_required", lambda: self.call(self.apply_request(plan)))
        recovery = self.recover(request)
        self.assertEqual(recovery["outcomes"][0]["state"], "reconciled")
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_crash_after_write_ahead_marker_recovery_never_resumes(self):
        self.writable_fixture()
        request = self.apply_request(self.preview())
        self.base.ElementsLayerService.ChangeLayer.side_effect = SystemExit("simulated process interruption")
        with self.assertRaises(SystemExit):
            self.call(request)
        self.assertEqual(self.call(request)["outcomes"][0]["state"], "unknown")
        service = importlib.import_module("test_allplan_host.model_repair").RepairPlanService
        self.handler.model_queries.session_id = uuid4().hex
        self.handler.repair_plans = service(self.handler.model_queries, self.directory.name)
        self.assertEqual(self.recover(request)["outcomes"][0]["state"], "reconciled")
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_corrupt_journal_and_persistence_failure_block_writes(self):
        self.writable_fixture()
        request = self.apply_request(self.preview())
        executor = self.handler.repair_plans.executor
        with patch.object(executor, "save", side_effect=self.module.BridgeError("repair_journal_unavailable", "disk full", 503)):
            self.assert_code("repair_journal_unavailable", lambda: self.call(request))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.call(request)
        record = Path(self.directory.name) / (request["execution_id"] + ".json")
        value = json.loads(record.read_text())
        value["state"] = "tampered"
        record.write_text(json.dumps(value))
        self.assert_code("repair_journal_unavailable", lambda: self.call(request))
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()

    def test_public_apply_requires_exact_acknowledgement_and_execution_identity(self):
        self.writable_fixture()
        request = self.apply_request(self.preview())
        public = {k: v for k, v in request.items() if k != "schema_version"}
        adapter = TypeAdapter(RepairRequest)
        self.assertEqual(adapter.validate_python(public).action, "apply")
        for bad in ({**public, "acknowledgement": True}, {**public, "execution_id": ""},
                    {**public, "acknowledgement": "yes"}):
            with self.assertRaises(ValidationError):
                adapter.validate_python(bad)
        self.coord.GetInputViewDocument.reset_mock()
        self.assert_code("invalid_payload", lambda: self.call({**request, "acknowledgement": False}))
        self.coord.GetInputViewDocument.assert_not_called()

    def test_unknown_recovery_and_wrong_project_are_read_only(self):
        self.writable_fixture()
        self.assert_code("execution_not_found", lambda: self.recover({"execution_id": uuid4().hex}))
        request = self.apply_request(self.preview())
        self.call(request)
        self.base.ProjectService.GetCurrentProjectNameAndHost.return_value = ("Other", "local")
        self.assert_code("repair_conflict", lambda: self.recover(request))
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()

    def test_serialized_writers_and_journal_capacity_do_not_evict_deduplication(self):
        self.writable_fixture()
        request = self.apply_request(self.preview())
        executor = self.handler.repair_plans.executor
        service = importlib.import_module("test_allplan_host.model_repair").RepairPlanService
        other = service(self.handler.model_queries, self.directory.name).executor
        with executor.locked():
            self.assert_code("repair_journal_unavailable", lambda: other.handle(
                self.coord.GetInputViewDocument(), self.base, self.settings, request))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        result = self.call(request)
        executor.MAX_RECORDS = 1
        another = {**request, "execution_id": uuid4().hex}
        self.assert_code("repair_journal_full", lambda: self.call(another))
        self.assertTrue(self.call(request)["replayed"])
        self.assertEqual(self.call(request)["outcomes"], result["outcomes"])

    def test_collateral_audited_change_is_reported_as_verification_failure(self):
        elements = self.writable_fixture()
        request = self.apply_request(self.preview())
        original = self.base.ElementsAttributeService.ChangeAttributes.side_effect
        def collateral(*args):
            original(*args)
            elements[0].GetCommonProperties.return_value.Layer = 8
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = collateral
        result = self.call(request)
        self.assertEqual(result["state"], "verification_failed")
        self.assertFalse(result["audited_fields_match_plan"])
        self.assertEqual(result["audit_after"]["counts"]["findings"], 4)

    def test_post_write_journal_failure_retains_unknown_marker_and_blocks_replay(self):
        self.writable_fixture()
        request = self.apply_request(self.preview())
        executor = self.handler.repair_plans.executor
        original = executor.save
        calls = [0]
        def fail_readback_save(record):
            calls[0] += 1
            if calls[0] == 3:
                raise self.module.BridgeError("repair_journal_unavailable", "disk full", 503)
            original(record)
        with patch.object(executor, "save", side_effect=fail_readback_save):
            self.assert_code("repair_journal_unavailable", lambda: self.call(request))
        self.assertEqual(self.call(request)["outcomes"][0]["state"], "unknown")
        recovery = self.recover(request)
        self.assertEqual(recovery["outcomes"][0]["reason"], "new_value_observed")
        self.assertFalse(recovery["write_blocked"])
        self.assertEqual(recovery["blockers"], [])
        self.assertEqual(recovery["next_action"]["action"], "preview")
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()


class ModelEditRecoveryTests(unittest.TestCase):
    """M4 recovery uses only current project/document identity and exact targets."""

    element = model_edit_fixtures.ModelEditTests.element
    adapter = model_edit_fixtures.ModelEditTests.adapter
    native = model_edit_fixtures.ModelEditTests.native
    prepare = model_edit_fixtures.ModelEditTests.prepare
    prepare_context = model_edit_fixtures.ModelEditTests.prepare_context
    request = model_edit_fixtures.ModelEditTests.request
    plan_request = model_edit_fixtures.ModelEditTests.plan_request
    preview = model_edit_fixtures.ModelEditTests.preview
    highlight = model_edit_fixtures.ModelEditTests.highlight
    attribute_catalog = model_edit_fixtures.ModelEditTests.attribute_catalog

    def setUp(self):
        model_edit_fixtures.ModelEditTests.setUp(self)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.handler.repair_plans.executor.path = Path(self.directory.name)

    def call(self, request):
        return self.handler.handle("/model-edit", request)

    def test_known_old_value_recovery_avoids_failed_global_criterion_scan(self):
        elements = model_edit_fixtures.ModelEditTests.fixture(self, ("old",))
        model_edit_fixtures.ModelEditTests.setter_fakes(self, elements)
        plan = model_edit_fixtures.ModelEditTests.preview(
            self, predicate=None,
            changes=[{"target": {"kind": "attribute", "attribute_id": 935},
                      "value_type": "text", "value": "new", "mode": "replace"}])
        model_edit_fixtures.ModelEditTests.highlight(self, plan)
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = RuntimeError("reply lost")
        execution_id = uuid4().hex
        result = self.call({"schema_version": "m4-model-edit-1", "action": "apply",
                            "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
                            "execution_id": execution_id,
                            "acknowledgement": "disposable_copy_reviewed_plan"})
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        executor = self.handler.repair_plans.executor
        second_id = uuid4().hex
        second_record = copy.deepcopy(executor.load(execution_id))
        second_record.update(execution_id=second_id, request_hash="f" * 64)
        executor.save(second_record)

        # A full predicate/model scan can fail on stale wrappers. Recovery
        # must still observe the exact journal target under matching project
        # and document identity, without ever retrying the setter.
        self.handler.repair_plans.source_observation = lambda *args: (_ for _ in ()).throw(
            AssertionError("global source scan must not run during M4 recover"))
        recovered = self.call({"schema_version": "m4-model-edit-1", "action": "recover",
                              "execution_id": execution_id})
        self.assertEqual(recovered["recovery"]["observations"][0]["state"], "old_value_observed")
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.assertTrue(recovered["write_blocked"])
        self.assertEqual(recovered["blockers"], ["recovery_required"])
        self.assertEqual(recovered["next_action"], {"action": "recover", "execution_id": second_id})
        self.assertEqual(recovered["recovery"]["identity"]["method"], "context_probe_no_model_scan")

        second_recovery = self.call({"schema_version": "m4-model-edit-1", "action": "recover",
                                     "execution_id": second_id})
        self.assertFalse(second_recovery["write_blocked"])
        self.assertEqual(second_recovery["blockers"], [])
        self.assertEqual(second_recovery["next_action"]["action"], "preview")
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_executor_scope_requires_integer_checkbox_binding_marker(self):
        elements = model_edit_fixtures.ModelEditTests.fixture(self, ("old",))
        elements[0].GetAttributes.return_value.extend([(20001, 0)])
        self.attribute_catalog({20001: "Element nośny"})
        self.attribute_type_names[20001] = "Integer"
        controls = SimpleNamespace(CheckBox=41, Edit=42)
        self.base.AttributeService.AttributeControlType = controls
        self.base.AttributeService.GetAttributeControlType.return_value = controls.CheckBox
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = lambda *args: args[1]
        plan = model_edit_fixtures.ModelEditTests.preview(self, predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 20001}, "value": True}])
        executor = self.handler.repair_plans.executor
        self.assertTrue(executor.model_edit_scope(plan))

        missing = copy.deepcopy(plan)
        missing["changes"][0]["resource"].pop("boolean_binding")
        self.assertFalse(executor.model_edit_scope(missing))
        tampered = copy.deepcopy(plan)
        tampered["changes"][0]["resource"]["boolean_binding"]["encoded_value"] = 0
        self.assertFalse(executor.model_edit_scope(tampered))

    def test_real_attribute_integer_native_readback_reconciles_without_retry(self):
        elements = model_edit_fixtures.ModelEditTests.fixture(self, (3,))
        self.attribute_type_names[935] = "Double"
        def writes_integer_payload(attributes, targets, *flags):
            self.assertEqual(attributes, [(935, 5.0)])
            targets[0].GetAttributes.return_value = [(935, 5)]
            return targets
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = writes_integer_payload
        plan = model_edit_fixtures.ModelEditTests.preview(self, predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 935},
            "value_type": "real", "value": 5.0, "mode": "replace"}])
        model_edit_fixtures.ModelEditTests.highlight(self, plan)

        native_repairs = importlib.import_module("test_allplan_host.native_repairs")
        original_resolve = native_repairs.resolve
        calls = [0]
        def fail_first_fresh_resolve(*args, **kwargs):
            if kwargs.get("writable") is not True:
                calls[0] += 1
                if calls[0] == 1:
                    raise self.module.BridgeError("repair_conflict", "synthetic fresh root conflict", 409)
            return original_resolve(*args, **kwargs)
        with patch.object(native_repairs, "resolve", side_effect=fail_first_fresh_resolve):
            result = model_edit_fixtures.ModelEditTests.apply(self, plan)
            self.assertEqual(result["outcomes"][0]["state"], "unknown")
            recovered = model_edit_fixtures.ModelEditTests.recover(self, result["execution_id"])

        self.assertEqual(recovered["recovery"]["observations"][0]["state"], "new_value_observed")
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.assertEqual(recovered["outcomes"][0]["readback"]["value"], 5)
        self.assertFalse(recovered["write_blocked"])
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()


if __name__ == "__main__":
    unittest.main()
