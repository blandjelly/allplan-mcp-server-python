"""M3 planning/staleness checks over fake adapters, separate from native gates."""
import copy
import importlib
import json
import types
import unittest

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.repair_models import RepairRequest
import test_model_audit as fixtures


class RepairTests(unittest.TestCase):
    setUp = fixtures.AuditTests.setUp
    prepare_context = fixtures.AuditTests.prepare_context
    prepare = fixtures.AuditTests.prepare
    adapter = fixtures.AuditTests.adapter
    native = fixtures.AuditTests.native
    element = fixtures.AuditTests.element
    resources = fixtures.AuditTests.resources
    fixture = fixtures.AuditTests.fixture
    assert_code = fixtures.AuditTests.assert_code

    def request(self, **changes):
        return {"schema_version": "m3-repair-1", "action": "preview",
                "audit": fixtures.AuditTests.request(self),
                "repairs": [{"rule_id": "QA-003", "value": "structure"}, {"rule_id": "QA-004", "value": "NEW"}],
                **changes}

    def preview(self, **changes):
        result = self.handler.handle("/fix-model-issues", self.request(**changes))
        json.dumps(result, allow_nan=False)
        self.base.CreateElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        return result

    def revalidate(self, plan, **changes):
        return self.handler.handle("/fix-model-issues", {"schema_version": "m3-repair-1", "action": "revalidate",
            "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"], **changes})

    def test_exact_two_change_preview_revalidates_without_writes_or_selection_cache(self):
        self.fixture()
        plan = self.preview()
        self.assertEqual(plan["counts"], {"changes": 2, "excluded_findings": 3, "audit_findings": 5})
        self.assertEqual([(c["operation"], c["old_value"]["value"], c["new_value"]) for c in plan["changes"]],
                         [("set_layer", 8, 7), ("set_attribute", "NWE", "NEW")])
        self.assertEqual([c["locator"]["mark"]["value"] for c in plan["changes"]], ["S05", "S06"])
        self.assertTrue(plan["read_only"])
        self.assertFalse(plan["apply_available"])
        self.assertFalse(plan["usable_for_write"])
        self.assertEqual(plan["capabilities"]["native_write_readback"], "not_checked")
        self.assertEqual(self.revalidate(plan)["state"], "unchanged")
        # Caller mutation cannot alter the stored reviewed plan.
        plan["changes"][0]["new_value"] = 999
        self.assertEqual(self.handler.repair_plans.plans[plan["plan_id"]]["plan"]["changes"][0]["new_value"], 7)
        self.assertEqual(len(self.handler.model_queries.selections), 0)

    def test_manual_edits_additions_resource_context_and_layer_changes_conflict(self):
        for defect in ("status", "mark", "layer", "addition", "resource", "project", "document", "file_state"):
            with self.subTest(defect=defect):
                elements = self.fixture()
                plan = self.preview()
                if defect in {"status", "mark"}:
                    elements[5].GetAttributes.return_value = [(20001, "X" if defect == "mark" else "S06"), (20002, "NEW")]
                elif defect == "layer": elements[4].GetCommonProperties.return_value.Layer = 7
                elif defect == "addition": self.base.ElementsSelectService.SelectAllElements.return_value = elements + [self.element(20, attrs=[(20001,"S20"),(20002,"NEW")])]
                elif defect == "resource":
                    self.base.LayerService.GetNameByID.side_effect = lambda ident, doc: "Renamed"
                elif defect == "project": self.base.ProjectService.GetCurrentProjectNameAndHost.return_value = ("Other", "local")
                elif defect == "document": self.coord.GetInputViewDocument.return_value.GetDocumentID.return_value = 99
                elif defect == "file_state": self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 2)]
                self.assertEqual(self.revalidate(plan)["state"], "conflict")
                self.assert_code("plan_expired", lambda: self.revalidate(plan))

    def test_plan_hash_expiry_eviction_and_restart_require_new_preview(self):
        self.fixture()
        now = [0]
        self.handler.model_queries.clock = lambda: now[0]
        plan = self.preview()
        self.assert_code("plan_hash_mismatch", lambda: self.revalidate(plan, plan_hash="0" * 64))
        now[0] = 300
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        self.assert_code("plan_expired", lambda: self.revalidate(plan))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        now[0] = 0
        plan = self.preview()
        for _ in range(8): self.preview()
        self.assert_code("plan_expired", lambda: self.revalidate(plan))
        plan = self.preview()
        service = importlib.import_module("test_allplan_host.model_repair").RepairPlanService
        self.handler.repair_plans = service(self.handler.model_queries)
        self.assert_code("plan_expired", lambda: self.revalidate(plan))

    def test_plan_cannot_expire_during_slow_revalidation_and_report_unchanged(self):
        elements = self.fixture()
        now = [0]
        self.handler.model_queries.clock = lambda: now[0]
        plan = self.preview()
        now[0] = 299
        elements[0].GetAttributes.side_effect = lambda mode: (now.__setitem__(0, 300) or [(20001,"S01"),(20002,"NEW")])
        self.assert_code("plan_expired", lambda: self.revalidate(plan))

    def test_selected_finding_is_exact_and_stale_ids_reject(self):
        self.fixture()
        audit = self.handler.handle("/model-audit", fixtures.AuditTests.request(self))
        ident = next(f["finding_id"] for f in audit["findings"] if f["rule_id"] == "QA-004")
        plan = self.preview(finding_ids=[ident])
        self.assertEqual(plan["counts"]["changes"], 1)
        self.assertEqual(plan["changes"][0]["rule_id"], "QA-004")
        self.assert_code("finding_stale", lambda: self.preview(finding_ids=["0" * 64]))
        self.assertEqual(len(self.handler.repair_plans.plans), 1)

    def test_incomplete_or_inactive_scope_never_claims_ready_changes(self):
        self.fixture()
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 104
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(102, 1), (104, 3)]
        plan = self.preview()
        self.assertEqual(plan["state"], "not_checked")
        self.assertEqual(plan["changes"], [])
        self.assertFalse(plan["coverage"]["audit_complete"])
        self.fixture()
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 104
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 1), (104, 3)]
        plan = self.preview()
        self.assertEqual(plan["changes"], [])
        self.assertEqual(plan["state"], "not_checked")

    def test_noop_when_selected_rules_already_pass(self):
        elements = self.fixture()
        elements[4].GetCommonProperties.return_value.Layer = 7
        elements[5].GetAttributes.return_value = [(20001,"S06"),(20002,"NEW")]
        plan = self.preview()
        self.assertEqual(plan["changes"], [])
        self.assertEqual(plan["counts"]["audit_findings"], 3)
        self.assertEqual(self.revalidate(plan)["state"], "unchanged")

    def test_apply_and_invalid_host_inputs_reject_before_native_reads(self):
        self.fixture()
        self.coord.GetInputViewDocument.reset_mock()
        bad_requests = [self.request(action="apply"), self.request(action="delete"),
                        self.request(repairs=[{"rule_id":"QA-001","value":"S03"}]),
                        self.request(repairs=[{"rule_id":"QA-004","value":"NWE"}]),
                        self.request(repairs=[{"rule_id":"QA-003","value":"review"}]),
                        self.request(repairs=self.request()["repairs"] * 2),
                        self.request(audit={**fixtures.AuditTests.request(self), "scope":{"drawing_files":[101],"include_passive":True,"visibility":"api_select_all"}}),
                        self.request(finding_ids=["0" * 64] * 2), self.request(unknown=True)]
        for request in bad_requests:
            self.assert_code("invalid_payload",
                             lambda: self.handler.handle("/fix-model-issues", request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_public_choice_validation_rejects_apply_coercion_and_unsupported_rules(self):
        self.fixture()
        request = self.request()
        request.pop("schema_version")
        request["audit"].pop("schema_version")
        adapter = TypeAdapter(RepairRequest)
        self.assertEqual(adapter.validate_python(request).action, "preview")
        for bad in ({**request,"action":"apply"}, {**request,"repairs":[{"rule_id":"QA-001","value":"S03"}]},
                    {**request,"repairs":[{"rule_id":"QA-004","value":True}]},
                    {**request,"repairs":[{"rule_id":"QA-004","value":"NWE"}]},
                    {**request,"repairs":request["repairs"] * 2}):
            with self.assertRaises(ValidationError): adapter.validate_python(bad)
        missing_policy = copy.deepcopy(request)
        del missing_policy["audit"]["profile"]["string_policies"]["status"]
        with self.assertRaises(ValidationError): adapter.validate_python(missing_policy)

    def test_unknown_symbols_never_imply_writability_and_oversize_plan_not_cached(self):
        self.fixture()
        module = importlib.import_module("test_allplan_host.repair_contracts")
        probe = module.capability_probe(types.SimpleNamespace())
        self.assertTrue(all(s["status"] == "not_checked" for s in probe["symbols"].values()))
        self.assertFalse(probe["apply_available"])
        self.handler.repair_plans.MAX_PLAN_BYTES = 1
        self.assert_code("scan_limit_exceeded", lambda: self.preview())
        self.assertEqual(len(self.handler.repair_plans.plans), 0)

    def test_overlapping_rules_never_plan_two_values_for_one_property(self):
        self.fixture()
        request = self.request()
        extra = copy.deepcopy(request["audit"]["profile"]["rules"][-1])
        extra["rule_id"] = "QA-005"
        request["audit"]["profile"]["rules"].append(extra)
        request["repairs"].append({"rule_id":"QA-005","value":"EXISTING"})
        self.assert_code("repair_conflict", lambda: self.handler.handle("/fix-model-issues",request))
        self.assertEqual(len(self.handler.repair_plans.plans), 0)
