"""Controlled interruption uses the actual durable marker and normal recovery."""
from uuid import uuid4
from unittest.mock import patch
import unittest

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.repair_models import RepairRequest
import test_mark_execution as marks


class RecoveryControlTests(unittest.TestCase):
    setUp = marks.MarkExecutionTests.setUp
    prepare_context = marks.MarkExecutionTests.prepare_context
    prepare = marks.MarkExecutionTests.prepare
    adapter = marks.MarkExecutionTests.adapter
    native = marks.MarkExecutionTests.native
    element = marks.MarkExecutionTests.element
    resources = marks.MarkExecutionTests.resources
    fixture = marks.MarkExecutionTests.fixture
    assert_code = marks.MarkExecutionTests.assert_code
    request = marks.MarkExecutionTests.request
    preview = marks.MarkExecutionTests.preview
    writable_fixture = marks.MarkExecutionTests.writable_fixture
    apply_request = marks.MarkExecutionTests.apply_request
    apply = marks.MarkExecutionTests.apply
    call = marks.MarkExecutionTests.call
    recover = marks.MarkExecutionTests.recover
    marks_fixture = marks.MarkExecutionTests.marks_fixture
    numbering_request = marks.MarkExecutionTests.numbering_request

    def fixture_ready(self):
        elements = self.marks_fixture()
        elements[4].GetCommonProperties.return_value.Layer = 7
        elements[5].GetAttributes.return_value = [(20001, 'S06'), (20002, 'NEW')]
        return elements

    def control(self, plan):
        return self.apply_request(plan, acknowledgement='disposable_copy_reviewed_recovery_test',
                          evaluation_stop='after_first_setter_before_readback')

    def test_unknown_marker_survives_restart_and_reconciles_without_second_setter(self):
        elements = self.fixture_ready()
        plan = self.call(self.numbering_request())
        request = self.control(plan)
        executor = self.handler.repair_plans.executor
        with patch.object(executor, 'save', wraps=executor.save) as saves:
            result = self.call(request)
        self.assertEqual(saves.call_count, 2)  # Initial record and actual write-ahead marker.
        self.assertEqual(result['state'], 'running')
        self.assertEqual([o['state'] for o in result['outcomes']], ['unknown', 'skipped'])
        self.assertNotIn('readback', result['outcomes'][0])
        self.assertNotIn('audit_after', result)
        persisted = executor.load(request['execution_id'])
        self.assertEqual(persisted['outcomes'], result['outcomes'])
        self.assertEqual(dict(elements[2].GetAttributes.return_value)[20001], 'S03')
        self.assertEqual(dict(elements[3].GetAttributes.return_value)[20001], 'S02')
        self.assertTrue(self.call(request)['replayed'])
        self.assert_code('repair_recovery_required', lambda: self.call({**request, 'execution_id': uuid4().hex}))
        service = type(self.handler.repair_plans)
        self.handler.model_queries.session_id = uuid4().hex
        self.handler.repair_plans = service(self.handler.model_queries, self.directory.name)
        recovered = self.recover(request)
        self.assertEqual(recovered['state'], 'stopped')
        self.assertEqual([o['state'] for o in recovered['outcomes']], ['reconciled', 'skipped'])
        self.assertEqual([o['state'] for o in recovered['recovery']['observations']], ['new_value_observed', 'old_value_observed'])
        self.assertTrue(self.call(request)['replayed'])
        elements[2].GetAttributes.return_value = [(20001, '<niezdefiniowany>'), (20002, 'NEW')]
        undone = self.recover(request)
        self.assertEqual([o['state'] for o in undone['recovery']['observations']], ['old_value_observed'] * 2)
        self.assertEqual(undone['outcomes'], recovered['outcomes'])
        self.assertTrue(self.call(request)['replayed'])
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_control_contract_pairing_rejected_before_document_access(self):
        elements = self.fixture_ready()
        request = self.control(self.call(self.numbering_request()))
        public = {k: v for k, v in request.items() if k != 'schema_version'}
        adapter = TypeAdapter(RepairRequest)
        self.assertEqual(adapter.validate_python(public).evaluation_stop, 'after_first_setter_before_readback')
        invalid = [{k: v for k, v in request.items() if k != 'evaluation_stop'},
                   {**request, 'acknowledgement': 'disposable_copy_reviewed_plan'},
                   {**request, 'evaluation_stop': None}, {**request, 'evaluation_stop': True},
                   {**request, 'evaluation_stop': 'after_second_setter'}]
        for bad in invalid:
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    adapter.validate_python({k: v for k, v in bad.items() if k != 'schema_version'})
                self.coord.GetInputViewDocument.reset_mock()
                self.assert_code('invalid_payload', lambda: self.call(bad))
                self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_stop_scope_and_request_hash_cannot_change_reviewed_authority(self):
        elements = self.fixture_ready()
        c03 = str(elements[2].GetModelElementUUID())
        single = self.preview(repairs=[{'rule_id': 'QA-001', 'model_uuid': c03, 'value': 'S03'}])
        self.assert_code('repair_scope_unavailable', lambda: self.call(self.control(single)))
        plan = self.call(self.numbering_request())
        request = self.control(plan)
        self.call(request)
        altered = {k: v for k, v in request.items() if k != 'evaluation_stop'}
        altered['acknowledgement'] = 'disposable_copy_reviewed_plan'
        self.assert_code('execution_id_conflict', lambda: self.call(altered))
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_actual_native_exception_uses_normal_stopped_unknown_path(self):
        self.fixture_ready()
        request = self.control(self.call(self.numbering_request()))
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = RuntimeError('native failure')
        result = self.call(request)
        self.assertEqual(result['state'], 'stopped')
        self.assertEqual([o['state'] for o in result['outcomes']], ['unknown', 'skipped'])
        self.assertEqual([o['state'] for o in self.recover(request)['recovery']['observations']], ['old_value_observed'] * 2)
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
