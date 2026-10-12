"""Selected mark gate over real MCP/bridge HTTP, using stateful native fakes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from allplan_mcp.selected_mark_diagnostics import collect_selected_mark, inspect_selected_mark
import test_mcp_smoke as smoke


class SelectedMarkHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process
    workflow_native_bridge = smoke.MCPSmokeTests.workflow_native_bridge
    numbering_native_bridge = smoke.MCPSmokeTests.numbering_native_bridge
    recovery_native_bridge = smoke.MCPSmokeTests.recovery_native_bridge

    async def test_selected_write_keeps_excluded_peer_journal_and_undo_snapshot(self):
        native, elements, restart = self.recovery_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_selected_mark(self.url, root / 'check.json', confirm=lambda _: 'ZMIEN C04')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            self.assertEqual(len(report['steps']), 13)
            self.assertTrue(all(s['ok'] for s in report['steps']))
            self.assertEqual(dict(elements[1].GetAttributes.return_value)[20001], 'S02')
            self.assertEqual(dict(elements[2].GetAttributes.return_value)[20001], '<niezdefiniowany>')
            self.assertEqual(dict(elements[3].GetAttributes.return_value)[20001], 'S04')
            pointer_path = root / 'm3-last-selected-mark-execution.json'
            pointer = json.loads(pointer_path.read_text())
            self.assertTrue((root / ('m3-selected-mark-execution-' + report['execution_id'] + '.json')).exists())
            self.assertEqual(pointer['apply_request'], report['apply_request'])
            restart()
            elements[3].GetAttributes.return_value = [(20001, 'S02'), (20002, 'NEW')]
            calls = len(self.bridge_handler.calls)
            checked = await inspect_selected_mark(self.url, root / 'undo.json', pointer_path, after_undo=True)
            self.assertEqual(checked['state'], 'ready_for_ui_observation', checked.get('message'))
            self.assertEqual(len(checked['steps']), 6)
            self.assertFalse(any(p.get('action') == 'apply' for _, p in self.bridge_handler.calls[calls:]))
            self.assertEqual(json.loads(pointer_path.read_text())['state'], 'undo_checked')
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_lost_write_reply_keeps_id_and_recover_never_replays_apply(self):
        native, elements, _ = self.recovery_native_bridge(lose_reply=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_selected_mark(self.url, root / 'lost.json', confirm=lambda _: 'ZMIEN C04')
            self.assertEqual(report['state'], 'unknown', report.get('message'))
            pointer = root / 'm3-last-selected-mark-execution.json'
            self.assertEqual(json.loads(pointer.read_text())['execution_id'], report['execution_id'])
            before = len(self.bridge_handler.calls)
            inspected = await inspect_selected_mark(self.url, root / 'recover.json', pointer)
            self.assertEqual(inspected['state'], 'ready_for_ui_observation', inspected.get('message'))
            self.assertFalse(any(p.get('action') == 'apply' for _, p in self.bridge_handler.calls[before:]))
            blocked = await collect_selected_mark(self.url, root / 'blocked.json', confirm=lambda _: self.fail('No second Apply'))
            self.assertEqual(blocked['state'], 'blocked')
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    async def test_cancel_changed_excluded_peer_and_invalid_journal_never_write(self):
        native, elements, _ = self.recovery_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cancelled = await collect_selected_mark(self.url, root / 'cancel.json', confirm=lambda _: 'STOP')
            self.assertEqual(cancelled['state'], 'cancelled')
            def changed(_):
                elements[1].GetAttributes.return_value = [(20001, 'S07'), (20002, 'NEW')]
                return 'ZMIEN C04'
            conflict = await collect_selected_mark(self.url, root / 'conflict.json', confirm=changed)
            self.assertEqual(conflict['state'], 'blocked')
            self.assertFalse((root / 'm3-last-selected-mark-execution.json').exists())
            (native.handler.repair_plans.executor.path / ('0' * 32 + '.json')).write_text('{}')
            blocked = await collect_selected_mark(self.url, root / 'journal.json', confirm=lambda _: self.fail('Bad journal'))
            self.assertEqual(blocked['state'], 'blocked')
            self.assertEqual(blocked['steps'][-1]['name'], 'journal_before')
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_collateral_change_stops_inspection_and_keeps_original_identity(self):
        native, elements, _ = self.recovery_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_selected_mark(self.url, root / 'check.json', confirm=lambda _: 'ZMIEN C04')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            elements[0].GetAttributes.return_value = [(20001, 'S07'), (20002, 'NEW')]
            pointer = root / 'm3-last-selected-mark-execution.json'
            inspected = await inspect_selected_mark(self.url, root / 'inspect.json', pointer)
            self.assertEqual(inspected['state'], 'blocked')
            self.assertEqual(inspected['steps'][-1]['name'], 'snapshot_inspection')
            self.assertEqual(json.loads(pointer.read_text())['state'], 'completed')
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    async def test_pre_setter_rejection_retains_identity_and_persistence_failure_sends_no_apply(self):
        native, elements, _ = self.recovery_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch('allplan_mcp.selected_mark_diagnostics.persist', side_effect=OSError('Unwritable pointer')):
                failed = await collect_selected_mark(self.url, root / 'save.json', confirm=lambda _: 'ZMIEN C04')
            self.assertEqual(failed['state'], 'blocked')
            self.assertFalse(any(p.get('action') == 'apply' for _, p in self.bridge_handler.calls))
            def disallow(_):
                elements[3].IsInActiveLayer.return_value = False
                return 'ZMIEN C04'
            rejected = await collect_selected_mark(self.url, root / 'rejected.json', confirm=disallow)
            self.assertEqual(rejected['state'], 'rejected', rejected.get('message'))
            self.assertFalse(rejected['native_setters_started'])
            pointer = root / 'm3-last-selected-mark-execution.json'
            self.assertEqual(json.loads(pointer.read_text())['state'], 'rejected')
            calls = len(self.bridge_handler.calls)
            result = await inspect_selected_mark(self.url, root / 'inspect.json', pointer)
            self.assertEqual(result['state'], 'rejected')
            self.assertEqual(len(self.bridge_handler.calls), calls)
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_successful_final_slot_reports_full_journal_without_invalidating_gate(self):
        native, elements, _ = self.recovery_native_bridge()
        c03 = str(elements[2].GetModelElementUUID())
        plan = native.preview(repairs=[{'rule_id': 'QA-001', 'model_uuid': c03, 'value': 'S03'}])
        request = native.apply_request(plan, acknowledgement='disposable_copy_reviewed_plan')
        native.call(request)
        executor = native.handler.repair_plans.executor
        record = executor.load(request['execution_id'])
        for _ in range(126):
            executor.save({**record, 'execution_id': uuid4().hex})
        elements[2].GetAttributes.return_value = [(20001, '<niezdefiniowany>'), (20002, 'NEW')]
        with tempfile.TemporaryDirectory() as directory:
            report = await collect_selected_mark(self.url, Path(directory) / 'check.json', confirm=lambda _: 'ZMIEN C04')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            journal = next(s['response'] for s in report['steps'] if s['name'] == 'journal_after')
            self.assertEqual(journal['new_execution_blockers'], ['journal_full'])
            self.assertEqual(journal['record_count'], 128)
        self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_count, 2)
