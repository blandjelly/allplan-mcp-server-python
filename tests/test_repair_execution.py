"""Mutation failure, replay and restart recovery checks with stateful native fakes."""
import copy
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import test_model_repair as fixtures
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
                              ("IsInMacro", True), ("IsLabelElement", True)):
            with self.subTest(method=method):
                elements = self.writable_fixture()
                request = self.apply_request(self.preview())
                getattr(elements[5], method).return_value = value
                self.assert_code("target_not_writable", lambda: self.call(request))
                self.base.ElementsLayerService.ChangeLayer.assert_not_called()
                self.assertFalse(list(Path(self.directory.name).glob("*.json")))
        elements = self.writable_fixture()
        request = self.apply_request(self.preview())
        elements[5].GetAttributes.return_value = [(20001, "S06"), (20002, "EXISTING")]
        self.assert_code("repair_conflict", lambda: self.call(request))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

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
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
