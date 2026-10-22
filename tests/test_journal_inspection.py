"""Journal inspection reports blockers without model access or changing records."""
import copy
import unittest
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.repair_models import RepairRequest
import test_recovery_control as control


class JournalInspectionTests(unittest.TestCase):
    def setUp(self):
        self.native = control.RecoveryControlTests()
        self.native.setUp()
        self.addCleanup(self.native.doCleanups)
        self.elements = self.native.fixture_ready()
        self.executor = self.native.handler.repair_plans.executor

    def inspect(self):
        return self.native.call({'schema_version': 'm3-repair-1', 'action': 'inspect_journal'})

    def completed(self):
        plan = self.native.call(self.native.numbering_request())
        request = self.native.apply(plan)
        self.native.call(request)
        return request, self.executor.load(request['execution_id'])

    def test_empty_inspection_does_not_access_native_context(self):
        self.native.coord.GetInputViewDocument.side_effect = AssertionError('No document needed')
        self.native.settings.AllplanVersion.MainReleaseName.side_effect = AssertionError('No native API needed')
        result = self.inspect()
        self.assertEqual(result['state'], 'available')
        self.assertEqual(result['remaining_slots'], self.executor.MAX_RECORDS)
        self.assertEqual(result['records'], [])
        self.assertTrue(result['read_only'])
        self.assertFalse(result['native_model_access'])
        self.native.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_completed_and_undone_history_is_inspected_without_reconciliation(self):
        request, record = self.completed()
        saved = {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')}
        self.elements[2].GetAttributes.return_value = [(20001, '<niezdefiniowany>'), (20002, 'NEW')]
        self.native.base.ElementsSelectService.SelectAllElements.reset_mock()
        result = self.inspect()
        item = result['records'][0]
        self.assertEqual(item['execution_id'], request['execution_id'])
        self.assertEqual(item['plan_hash'], record['plan_hash'])
        self.assertEqual(item['outcome_counts'], {'applied': 2})
        self.assertFalse(item['requires_recovery'])
        self.assertEqual(result['current_model_values'], 'not_checked')
        self.assertEqual(saved, {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')})
        self.native.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_actual_unknown_marker_reports_original_id_without_recovering_it(self):
        plan = self.native.call(self.native.numbering_request())
        request = self.native.control(plan)
        self.native.call(request)
        before = self.executor.load(request['execution_id'])
        result = self.inspect()
        self.assertEqual(result['state'], 'blocked')
        self.assertEqual(result['new_execution_blockers'], ['recovery_required'])
        self.assertEqual(result['records'][0]['outcome_counts'], {'skipped': 1, 'unknown': 1})
        self.assertTrue(result['records'][0]['requires_recovery'])
        self.assertEqual(self.executor.load(request['execution_id']), before)
        self.native.recover(request)
        self.assertEqual(self.inspect()['state'], 'available')
        self.native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_capacity_preserves_exact_replay_and_reports_incomplete_over_capacity(self):
        request, record = self.completed()
        for _ in range(self.executor.MAX_RECORDS - 1):
            self.executor.save({**record, 'execution_id': uuid4().hex})
        full = self.inspect()
        self.assertEqual(full['record_count'], self.executor.MAX_RECORDS)
        self.assertEqual(full['remaining_slots'], 0)
        self.assertTrue(full['complete'])
        self.assertEqual(full['new_execution_blockers'], ['journal_full'])
        self.assertTrue(self.native.call(request)['replayed'])
        self.executor.save({**record, 'execution_id': uuid4().hex})
        oversized = self.inspect()
        self.assertFalse(oversized['complete'])
        self.assertIsNone(oversized['record_count'])
        self.assertEqual(oversized['new_execution_blockers'], ['capacity_exceeded'])
        self.assertEqual(len(oversized['records']), self.executor.MAX_RECORDS)
        self.assertEqual(len(list(self.executor.path.glob('*.json'))), self.executor.MAX_RECORDS + 1)

    def test_invalid_and_hashed_structurally_invalid_records_fail_closed(self):
        request, record = self.completed()
        malformed = copy.deepcopy(record)
        malformed['execution_id'] = uuid4().hex
        malformed['outcomes'] = []
        self.executor.save(malformed)  # A valid hash must not hide unusable structure.
        bad = self.executor.path / (uuid4().hex + '.json')
        bad.write_text('[]')
        before = {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')}
        result = self.inspect()
        self.assertEqual(result['new_execution_blockers'], ['invalid_record'])
        self.assertEqual(sum(r['integrity'] == 'unverifiable' for r in result['records']), 2)
        self.native.assert_code('repair_journal_unavailable', lambda: self.native.call({**request, 'execution_id': uuid4().hex}))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')})
        self.assertEqual(self.native.base.ElementsAttributeService.ChangeAttributes.call_count, 2)

    def test_schema_extra_fields_and_competing_lock_fail_before_model_access(self):
        adapter = TypeAdapter(RepairRequest)
        self.assertEqual(adapter.validate_python({'action': 'inspect_journal'}).action, 'inspect_journal')
        for key, value in [('execution_id', '0' * 32), ('acknowledgement', True), ('scope', {})]:
            with self.assertRaises(ValidationError):
                adapter.validate_python({'action': 'inspect_journal', key: value})
            self.native.assert_code('invalid_payload', lambda: self.native.call(
                {'schema_version': 'm3-repair-1', 'action': 'inspect_journal', key: value}))
        with self.executor.locked():
            self.native.assert_code('repair_journal_unavailable', self.inspect)
        self.native.coord.GetInputViewDocument.assert_not_called()
