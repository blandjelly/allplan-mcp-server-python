"""Variable-size Column repairs and workflow execution preserve the shared guards."""
import copy
import unittest
from pathlib import Path

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.standard_models import OfficeStandardRequest, RuleBasedRequest
import test_repair_execution as executions


class SupportedExecutionTests(unittest.TestCase):
    setUp = executions.ExecutionTests.setUp
    prepare_context = executions.ExecutionTests.prepare_context
    prepare = executions.ExecutionTests.prepare
    adapter = executions.ExecutionTests.adapter
    native = executions.ExecutionTests.native
    element = executions.ExecutionTests.element
    resources = executions.ExecutionTests.resources
    fixture = executions.ExecutionTests.fixture
    assert_code = executions.ExecutionTests.assert_code
    request = executions.ExecutionTests.request
    preview = executions.ExecutionTests.preview
    writable_fixture = executions.ExecutionTests.writable_fixture
    apply_request = executions.ExecutionTests.apply_request
    call = executions.ExecutionTests.call
    recover = executions.ExecutionTests.recover

    def apply(self, plan, **changes):
        return self.apply_request(plan, acknowledgement='disposable_copy_reviewed_plan', **changes)

    def test_one_status_repair_has_readback_four_findings_recovery_and_exact_replay(self):
        self.writable_fixture()
        plan = self.preview(repairs=[{'rule_id': 'QA-004', 'value': 'NEW'}])
        self.assertTrue(plan['evaluation_apply_available'])
        request = self.apply(plan)
        result = self.call(request)
        self.assertEqual(result['state'], 'completed')
        self.assertTrue(result['audited_fields_match_plan'])
        self.assertEqual(result['audit_after']['counts']['findings'], 4)
        self.assertEqual([o['state'] for o in result['outcomes']], ['applied'])
        self.assertTrue(self.call(request)['replayed'])
        recovered = self.recover(request)
        self.assertEqual([o['state'] for o in recovered['recovery']['observations']], ['new_value_observed'])
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_selected_single_layer_retains_exception_and_full_source_verification(self):
        elements = self.writable_fixture()
        plan = self.preview(selection={'where': {'field': 'layer_id', 'op': 'exists'},
                            'exclude_model_uuids': [str(elements[5].GetModelElementUUID())]},
                            workflow={'kind': 'rule_based_edit_preview'})
        self.assertEqual(len(plan['changes']), 1)
        self.assertEqual(plan['selection_result']['excluded_elements'], 1)
        result = self.call(self.apply(plan, workflow_kind='rule_based_edit_preview'))
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(result['audit_after']['counts']['findings'], 4)
        self.assertEqual(elements[5].GetAttributes.return_value[-1], (20002, 'NWE'))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_three_changes_verify_the_full_snapshot_and_replay_without_setters(self):
        elements = self.writable_fixture()
        elements[3].GetCommonProperties.return_value.Layer = 8
        plan = self.preview()
        self.assertEqual(len(plan['changes']), 3)
        self.assertTrue(plan['evaluation_apply_available'])
        request = self.apply(plan)
        result = self.call(request)
        self.assertEqual(result['state'], 'completed')
        self.assertTrue(result['audited_fields_match_plan'])
        self.assertEqual([o['state'] for o in result['outcomes']], ['applied'] * 3)
        self.assertEqual(result['audit_after']['counts']['findings'], 3)
        self.assertTrue(self.call(request)['replayed'])
        self.assertEqual(self.base.ElementsLayerService.ChangeLayer.call_count, 2)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_office_standard_uses_same_executor_and_workflow_mismatch_rejects(self):
        self.writable_fixture()
        plan = self.preview(workflow={'kind': 'office_standard_preview', 'standard_id': 'demo',
                                     'standard_version': '1.0.0', 'standard_fingerprint': 'a' * 64})
        self.assert_code('repair_scope_unavailable', lambda: self.call(self.apply(plan, workflow_kind='rule_based_edit_preview')))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertFalse(list(Path(self.directory.name).glob('*.json')))
        result = self.call(self.apply(plan, workflow_kind='office_standard_preview'))
        self.assertEqual(result['state'], 'completed')
        self.assertEqual(result['audit_after']['counts']['findings'], 3)

    def test_bound_foreground_file_and_explicit_status_value_are_not_hardcoded(self):
        elements = self.writable_fixture()
        for element in elements:
            if abs(element.GetDrawingfileNumber()) == 101:
                element.GetDrawingfileNumber.return_value = 201
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 201
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(201, 3)]
        request = self.request(repairs=[{'rule_id': 'QA-004', 'value': 'EXISTING'}])
        request['audit']['scope']['drawing_files'] = [201]
        request['audit']['profile']['read_profile']['scope']['drawing_files'] = [201]
        def attribute(data, targets, undefined, deleted):
            self.assertEqual(data, [(20002, 'EXISTING')])
            targets[0].GetAttributes.return_value = [(20001, 'S06'), (20002, 'EXISTING')]
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = attribute
        plan = self.handler.handle('/fix-model-issues', request)
        self.assertTrue(plan['evaluation_apply_available'])
        self.assertEqual(self.call(self.apply(plan))['state'], 'completed')

    def test_excluded_peer_change_invalidates_selected_plan_before_any_setter(self):
        elements = self.writable_fixture()
        plan = self.preview(selection={'where': {'field': 'layer_id', 'op': 'exists'},
                            'exclude_model_uuids': [str(elements[5].GetModelElementUUID())]})
        elements[5].GetAttributes.return_value = [(20001, 'OTHER'), (20002, 'NWE')]
        self.assert_code('repair_conflict', lambda: self.call(self.apply(plan)))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.assertFalse(list(Path(self.directory.name).glob('*.json')))

    def test_old_acknowledgement_does_not_expand_and_mark_metadata_stays_blocked(self):
        elements = self.writable_fixture()
        plan = self.preview(repairs=[{'rule_id': 'QA-004', 'value': 'NEW'}])
        self.assert_code('repair_scope_unavailable', lambda: self.call(self.apply_request(plan)))
        marks = [{'rule_id': 'QA-001', 'model_uuid': str(elements[2].GetModelElementUUID()), 'value': 'S03'}]
        plan = self.preview(repairs=marks)
        self.assert_code('repair_scope_unavailable', lambda: self.call(self.apply(plan)))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_public_workflow_actions_require_reviewed_identity_and_host_rejects_bad_ack_before_reads(self):
        self.writable_fixture()
        plan = self.preview()
        request = self.apply(plan)
        public = {k: v for k, v in request.items() if k != 'schema_version'}
        for model in [OfficeStandardRequest, RuleBasedRequest]:
            self.assertEqual(TypeAdapter(model).validate_python(public).action, 'apply')
            for bad in [{**public, 'acknowledgement': True}, {**public, 'scope': {}}, {**public, 'execution_id': ''}]:
                with self.assertRaises(ValidationError):
                    TypeAdapter(model).validate_python(bad)
        for bad in [{**request, 'acknowledgement': {}}, {**request, 'workflow_kind': []}]:
            self.coord.GetInputViewDocument.reset_mock()
            self.assert_code('invalid_payload', lambda: self.call(bad))
            self.coord.GetInputViewDocument.assert_not_called()

    def test_empty_oversize_unknown_and_non_column_plans_are_not_executable(self):
        self.writable_fixture()
        plan = self.preview()
        checker = self.handler.repair_plans.executor.evaluation_scope
        for mutate in [lambda p: p.update(changes=[]),
                       lambda p: p.update(changes=p['changes'] * 17),
                       lambda p: p['coverage'].update(audit_complete=False),
                       lambda p: p['scope']['included_files'][0].update(state='active_background'),
                       lambda p: p['changes'][0]['ref'].update(type_uuid='unsupported'),
                       lambda p: p['changes'][1].update(property_role='mark')]:
            candidate = copy.deepcopy(plan)
            mutate(candidate)
            self.assertFalse(checker(candidate))
