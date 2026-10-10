"""Real Streamable HTTP transport with a fake bridge; no Allplan claims."""
import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fastmcp import Client
from allplan_mcp.diagnostics import collect_diagnostics, collect_m2_stability, collect_m3_preview
from test_transport import stop_test_server, transport


class FakeBridge:
    def __init__(self):
        self.calls = []
    def handle(self, path, payload):
        self.calls.append((path, payload))
        if path == "/get-allplan-version":
            from allplan_mcp import __version__
            return {"version": "2026.fake", "embedded_python": {"version": "fake"},
                    "bridge_package": {"version": __version__}, "installed_bridge_integrity": {"status": "verified"},
                    "compatibility": {"major_matches": True, "runtime_verified": False}}
        if path == "/get-all-object-names":
            return {"names": ["Fake column"]}
        if path == "/get-model-context":
            return {"schema_version": "m1-context-probe-1", "read_only": True,
                    "identity_sample": {"requested": payload["identity_sample_size"], "items": []}}
        if path == "/create-box":
            return {"ok": True}
        if path == "/model-query":
            return {"schema_version": "m1-query-1", "read_only": True, "request": payload,
                    "selection_id": "a" * 32, "source_fingerprint": "fake-only"}
        if path == "/model-audit":
            return {"schema_version": "m2-audit-1", "read_only": True, "request": payload,
                    "report_text": "Fake audit transport only.", "findings": []}
        raise transport.BridgeError("unknown_route", "Unknown route", 404)


class MCPSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_conflict_gate_over_real_http_checks_excluded_peer_without_second_write(self):
        from allplan_mcp.conflict_diagnostics import collect_conflict
        from allplan_mcp.workflow_diagnostics import recover_workflow
        native, elements = self.numbering_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_conflict(self.url, root / 'conflict.json', confirm=lambda _: 'SPRAWDZ KONFLIKT')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            self.assertEqual(len(report['steps']), 12)
            self.assertTrue(all(s['ok'] for s in report['steps']))
            pointer = json.loads((root / 'm3-last-conflict-execution.json').read_text())
            saved = json.loads((root / ('m3-conflict-execution-' + report['execution_id'] + '.json')).read_text())
            self.assertEqual(pointer, saved)
            self.assertEqual(pointer['state'], 'completed')
            self.assertNotEqual(report['execution_id'], report['stale_apply_request']['execution_id'])
            recovered = await recover_workflow(self.url, root / 'recover.json', pointer)
            self.assertEqual(recovered['state'], 'ready_for_ui_observation')
            self.assertEqual(recovered['steps'][0]['response']['recovery']['observations'][0]['state'], 'new_value_observed')
        self.assertEqual(dict(elements[2].GetAttributes.return_value)[20001], 'S03')
        self.assertEqual(dict(elements[3].GetAttributes.return_value)[20001], 'S02')
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_conflict_gate_lost_reply_preserves_identity_and_recovers_without_new_apply(self):
        from allplan_mcp.conflict_diagnostics import collect_conflict
        from allplan_mcp.workflow_diagnostics import recover_workflow
        native, _ = self.numbering_native_bridge(lose_reply=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_conflict(self.url, root / 'conflict.json', confirm=lambda _: 'SPRAWDZ KONFLIKT')
            self.assertEqual(report['state'], 'unknown', report.get('message'))
            pointer = json.loads((root / 'm3-last-conflict-execution.json').read_text())
            self.assertEqual(pointer['state'], 'unknown')
            blocked = await collect_conflict(self.url, root / 'blocked.json', confirm=lambda _: self.fail('Unresolved write'))
            self.assertEqual(blocked['state'], 'blocked')
            self.assertEqual(json.loads((root / 'm3-last-conflict-execution.json').read_text()), pointer)
            previous = len(self.bridge_handler.calls)
            recovered = await recover_workflow(self.url, root / 'recover.json', pointer)
            self.assertEqual(recovered['state'], 'ready_for_ui_observation')
            self.assertEqual([p.get('action') for _, p in self.bridge_handler.calls[previous:]], ['recover'])
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    async def test_conflict_gate_cancel_or_changed_source_during_review_never_writes(self):
        from allplan_mcp.conflict_diagnostics import collect_conflict
        native, elements = self.numbering_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_conflict(self.url, root / 'cancel.json', confirm=lambda _: 'STOP')
            self.assertEqual(report['state'], 'cancelled')
            self.assertFalse((root / 'm3-last-conflict-execution.json').exists())
            def confirm(_):
                elements[2].GetAttributes.return_value = [(20001, 'MANUAL'), (20002, 'NEW')]
                return 'SPRAWDZ KONFLIKT'
            report = await collect_conflict(self.url, root / 'changed.json', confirm=confirm)
            self.assertEqual(report['state'], 'blocked')
            self.assertFalse((root / 'm3-last-conflict-execution.json').exists())
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_conflict_stale_rejection_lost_reply_retains_both_identities_and_blocks_rerun(self):
        from allplan_mcp.conflict_diagnostics import collect_conflict
        native, _ = self.numbering_native_bridge()
        original = self.bridge_handler.handle
        apply_calls = [0]
        def lose_stale(path, payload):
            if payload.get('action') == 'apply':
                apply_calls[0] += 1
                if apply_calls[0] == 2:
                    try:
                        original(path, payload)
                    except transport.BridgeError as exc:
                        self.assertEqual(exc.code, 'plan_expired')
                    raise transport.BridgeError('execution_unknown', 'Lost stale rejection reply', 503)
            return original(path, payload)
        self.bridge_handler.handle = lose_stale
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_conflict(self.url, root / 'conflict.json', confirm=lambda _: 'SPRAWDZ KONFLIKT')
            self.assertEqual(report['state'], 'unknown')
            pointer = json.loads((root / 'm3-last-conflict-execution.json').read_text())
            self.assertEqual(pointer['state'], 'completed')
            self.assertEqual(pointer['execution_id'], report['execution_id'])
            self.assertEqual(pointer['uncertain_stale_execution_id'], report['stale_apply_request']['execution_id'])
            blocked = await collect_conflict(self.url, root / 'blocked.json', confirm=lambda _: self.fail('Unresolved stale probe'))
            self.assertEqual(blocked['state'], 'blocked')
        self.assertEqual(apply_calls[0], 2)
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def numbering_native_bridge(self, **options):
        native, elements = self.workflow_native_bridge(**options)
        def attribute(data, targets, undefined, deleted):
            self.assertFalse(undefined)
            self.assertFalse(deleted)
            values = dict(targets[0].GetAttributes.return_value)
            self.assertIn(data[0][0], values)
            values.update(data)
            targets[0].GetAttributes.return_value = list(values.items())
        native.base.ElementsAttributeService.ChangeAttributes.side_effect = attribute
        return native, elements

    async def test_numbering_gate_over_real_http_applies_exact_marks_and_then_noops(self):
        from allplan_mcp.numbering_diagnostics import collect_numbering_apply
        native, elements = self.numbering_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_numbering_apply(self.url, root / 'numbering.json', confirm=lambda _: 'NUMERUJ KOPIE')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            self.assertEqual(len(report['steps']), 10)
            self.assertTrue(all(s['ok'] for s in report['steps']))
            pointer = json.loads((root / 'm3-last-numbering-execution.json').read_text())
            self.assertEqual(pointer['state'], 'completed')
            self.assertEqual(pointer['execution_id'], report['execution_id'])
            self.assertTrue((root / ('m3-numbering-execution-' + report['execution_id'] + '.json')).is_file())
        self.assertEqual(dict(elements[2].GetAttributes.return_value)[20001], 'S03')
        self.assertEqual(dict(elements[3].GetAttributes.return_value)[20001], 'S04')
        self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_count, 2)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_numbering_lost_reply_recovers_without_replaying_apply(self):
        from allplan_mcp.numbering_diagnostics import collect_numbering_apply
        from allplan_mcp.workflow_diagnostics import recover_workflow
        native, _ = self.numbering_native_bridge(lose_reply=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_numbering_apply(self.url, root / 'numbering.json', confirm=lambda _: 'NUMERUJ KOPIE')
            self.assertEqual(report['state'], 'unknown', report.get('message'))
            pointer = json.loads((root / 'm3-last-numbering-execution.json').read_text())
            previous = len(self.bridge_handler.calls)
            recovered = await recover_workflow(self.url, root / 'recover.json', pointer)
            self.assertEqual(recovered['state'], 'ready_for_ui_observation')
            self.assertEqual([p.get('action') for _, p in self.bridge_handler.calls[previous:]], ['recover'])
        self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_count, 2)

    async def test_numbering_cancellation_and_changed_marks_do_not_send_apply(self):
        from allplan_mcp.numbering_diagnostics import collect_numbering_apply
        native, elements = self.numbering_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_numbering_apply(self.url, root / 'cancel.json', confirm=lambda _: 'STOP')
            self.assertEqual(report['state'], 'cancelled')
            self.assertFalse((root / 'm3-last-numbering-execution.json').exists())
            elements[2].GetAttributes.return_value = [(20001, 'MANUAL'), (20002, 'NEW')]
            report = await collect_numbering_apply(self.url, root / 'wrong.json', confirm=lambda _: self.fail('Wrong fixture'))
            self.assertEqual(report['state'], 'blocked')
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def workflow_native_bridge(self, lose_reply=False, reject=False):
        from test_repair_execution import ExecutionTests
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        original = self.bridge_handler.handle
        lost = [False]
        def handle(path, payload):
            if path in {'/fix-model-issues', '/model-audit'}:
                self.bridge_handler.calls.append((path, payload))
                if reject and payload.get('action') == 'apply':
                    elements[4].IsInActiveLayer.return_value = False
                try:
                    result = native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code, str(exc), exc.status) from exc
                if lose_reply and payload.get('action') == 'apply' and not lost[0]:
                    lost[0] = True
                    raise transport.BridgeError('execution_unknown', 'Lost first completed workflow reply', 503)
                return result
            if path == '/get-allplan-version':
                result = original(path, payload)
                result['host_session_id'] = 'workflow-fake-session'
                return result
            return original(path, payload)
        self.bridge_handler.handle = handle
        return native, elements

    async def test_workflow_owner_gate_writes_two_separate_single_targets_and_deduplicates(self):
        from allplan_mcp.workflow_diagnostics import collect_workflow_apply
        native, elements = self.workflow_native_bridge()
        approvals = iter(['NAPRAW STANDARD', 'NAPRAW REGULE'])
        with tempfile.TemporaryDirectory() as directory:
            report = await collect_workflow_apply(self.url, Path(directory) / 'workflows.json',
                                                  confirm=lambda prompt: next(approvals))
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            self.assertEqual(len(report['steps']), 10)
            self.assertTrue(all(s['ok'] for s in report['steps']))
            self.assertEqual(len(report['executions']), 2)
            self.assertNotEqual(*[e['execution_id'] for e in report['executions']])
            for execution in report['executions']:
                saved = json.loads((Path(directory) / ('m3-workflow-execution-' + execution['execution_id'] + '.json')).read_text())
                self.assertEqual(saved['apply_request'], execution['apply_request'])
                self.assertEqual(saved['state'], 'completed')
            calls = [p for route, p in self.bridge_handler.calls if p.get('action') == 'apply']
            self.assertEqual([p['workflow_kind'] for p in calls],
                             ['office_standard_preview'] * 2 + ['rule_based_edit_preview'] * 2)
        native.base.ElementsLayerService.ChangeLayer.assert_called_once()
        native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
        self.assertEqual(elements[4].GetCommonProperties.return_value.Layer, 7)
        self.assertEqual(elements[5].GetAttributes.return_value[-1], (20002, 'NEW'))

    async def test_lost_workflow_reply_preserves_identity_and_recovery_does_not_apply(self):
        from allplan_mcp.workflow_diagnostics import collect_workflow_apply, recover_workflow
        native, elements = self.workflow_native_bridge(lose_reply=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_workflow_apply(self.url, root / 'lost.json', confirm=lambda prompt: 'NAPRAW STANDARD')
            self.assertEqual(report['state'], 'unknown')
            pointer = json.loads((root / 'm3-last-workflow-execution.json').read_text())
            self.assertEqual(pointer['execution_id'], report['executions'][0]['execution_id'])
            before = len(self.bridge_handler.calls)
            recovered = await recover_workflow(self.url, root / 'recover.json', pointer)
            self.assertEqual(recovered['state'], 'ready_for_ui_observation', recovered.get('message'))
            self.assertEqual([p.get('action') for route, p in self.bridge_handler.calls[before:]], ['recover'])
        self.assertEqual(elements[5].GetAttributes.return_value[-1], (20002, 'NWE'))
        native.base.ElementsLayerService.ChangeLayer.assert_called_once()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_workflow_rejection_is_explicit_and_sends_no_recovery(self):
        from allplan_mcp.workflow_diagnostics import collect_workflow_apply, recover_workflow
        native, elements = self.workflow_native_bridge(reject=True)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = await collect_workflow_apply(self.url, root / 'rejected.json', confirm=lambda prompt: 'NAPRAW STANDARD')
            self.assertEqual(report['state'], 'rejected')
            pointer = json.loads((root / 'm3-last-workflow-execution.json').read_text())
            self.assertFalse(pointer['native_setters_started'])
            before = len(self.bridge_handler.calls)
            recovered = await recover_workflow(self.url, root / 'recover.json', pointer)
            self.assertEqual(recovered['state'], 'rejected')
            self.assertEqual(len(self.bridge_handler.calls), before)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_workflow_gate_stops_on_wrong_fixture_and_second_write_needs_separate_confirmation(self):
        from allplan_mcp.workflow_diagnostics import collect_workflow_apply
        native, elements = self.workflow_native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            elements[5].GetAttributes.return_value = [(20001, 'S06'), (20002, 'NEW')]
            blocked = await collect_workflow_apply(self.url, root / 'wrong.json', confirm=lambda prompt: self.fail('No confirmation on wrong fixture'))
            self.assertEqual(blocked['state'], 'blocked')
            native.base.ElementsLayerService.ChangeLayer.assert_not_called()
            elements[5].GetAttributes.return_value = [(20001, 'S06'), (20002, 'NWE')]
            approvals = iter(['NAPRAW STANDARD', 'STOP'])
            stopped = await collect_workflow_apply(self.url, root / 'stop.json', confirm=lambda prompt: next(approvals))
            self.assertEqual(stopped['state'], 'stopped')
            self.assertEqual(len(stopped['executions']), 1)
        native.base.ElementsLayerService.ChangeLayer.assert_called_once()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_mark_owner_gate_reports_expected_collision_without_any_write_over_real_transport(self):
        from test_repair_execution import ExecutionTests
        from allplan_mcp.mark_diagnostics import collect_mark_preview
        from allplan_mcp import __version__
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        elements[4].GetCommonProperties.return_value.Layer = 7
        elements[5].GetAttributes.return_value = [(20001, 'S06'), (20002, 'NEW')]
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in {'/fix-model-issues', '/model-audit'}:
                self.bridge_handler.calls.append((path, payload))
                return native.handler.handle(path, payload)
            if path == '/get-allplan-version':
                result = original(path, payload)
                result['host_session_id'] = 'native-fake-session'
                result['bridge_package']['version'] = __version__
                return result
            return original(path, payload)
        self.bridge_handler.handle = handle
        with tempfile.TemporaryDirectory() as directory:
            report = await collect_mark_preview(self.url, Path(directory) / 'marks.json')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            self.assertTrue(all(s['ok'] for s in report['steps']))
            self.assertEqual(len(report['steps']), 10)
            calls = [p.get('action') for route, p in self.bridge_handler.calls if route == '/fix-model-issues']
            self.assertEqual(calls, ['preview', 'revalidate'] * 3)
            self.assertTrue((Path(directory) / 'marks.txt').exists())
            self.assertTrue(all(s['mcp_content'] for s in report['steps']))
            collision = next(s['response'] for s in report['steps'] if s['name'] == 'excluded_peer_collision')
            self.assertEqual(collision['state'], 'conflict')
            # A restored fixture differs: stop before issuing any mark proposal.
            elements[4].GetCommonProperties.return_value.Layer = 8
            self.bridge_handler.calls.clear()
            blocked = await collect_mark_preview(self.url, Path(directory) / 'wrong-fixture.json')
            self.assertEqual(blocked['state'], 'blocked')
            self.assertFalse(any(route == '/fix-model-issues' for route, _ in self.bridge_handler.calls))
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_mark_public_rule_preview_uses_exact_targets_and_cannot_bypass_apply(self):
        from test_repair_execution import ExecutionTests
        from uuid import uuid4
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path == '/fix-model-issues':
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)
        self.bridge_handler.handle = handle
        request = {'action': 'preview', 'audit': {'profile_id': 'native-model-qa-demo',
            'scope': {'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}},
            'repairs': [{'rule_id': 'QA-001', 'model_uuid': str(elements[2].GetModelElementUUID()), 'value': 'S03'},
                        {'rule_id': 'QA-002', 'model_uuid': str(elements[3].GetModelElementUUID()), 'value': 'S04'}],
            'selection': {'where': {'field': 'layer_id', 'op': 'exists'}}}
        async with Client(self.url) as client:
            plan = (await client.call_tool('rule_based_edit', {'request': request})).data
            self.assertEqual(plan['mark_validation']['state'], 'validated')
            self.assertEqual({c['new_value'] for c in plan['changes']}, {'S03', 'S04'})
            rejected = (await client.call_tool('fix_model_issues', {'request': {
                'action': 'apply', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash'],
                'execution_id': uuid4().hex, 'acknowledgement': 'disposable_copy_reviewed_two_repairs'}})).data
            self.assertEqual(rejected['error']['code'], 'repair_scope_unavailable')
            self.assertFalse(rejected['native_setters_started'])
            request['repairs'][0]['value'] = ' '
            native.coord.GetInputViewDocument.reset_mock()
            invalid = await client.call_tool('rule_based_edit', {'request': request}, raise_on_error=False)
            self.assertTrue(invalid.is_error)
            native.coord.GetInputViewDocument.assert_not_called()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_standard_owner_gate_is_read_only_over_real_transport_and_keeps_full_audit(self):
        from test_repair_execution import ExecutionTests
        from allplan_mcp.standard_diagnostics import collect_standard_preview
        from allplan_mcp import __version__
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        elements[4].GetCommonProperties.return_value.Layer = 7
        elements[5].GetAttributes.return_value = [(20001, 'S06'), (20002, 'NEW')]
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in {'/fix-model-issues', '/model-audit'}:
                self.bridge_handler.calls.append((path, payload))
                return native.handler.handle(path, payload)
            if path == '/get-allplan-version':
                result = original(path, payload)
                result['host_session_id'] = 'native-fake-session'
                result['bridge_package']['version'] = __version__
                return result
            return original(path, payload)
        self.bridge_handler.handle = handle
        with tempfile.TemporaryDirectory() as directory:
            report = await collect_standard_preview(self.url, Path(directory) / 'standards.json')
            self.assertEqual(report['state'], 'ready_for_ui_observation', report.get('message'))
            self.assertTrue(all(s['ok'] for s in report['steps']))
            self.assertEqual(len(report['steps']), 10)
            calls = [p.get('action') for route, p in self.bridge_handler.calls if route == '/fix-model-issues']
            self.assertEqual(calls, ['preview', 'revalidate'] * 3)
            self.assertTrue((Path(directory) / 'standards.txt').exists())
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_standard_and_rule_previews_share_native_plans_and_reject_legacy_apply(self):
        from test_repair_execution import ExecutionTests
        from uuid import uuid4
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path == '/fix-model-issues':
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)
        self.bridge_handler.handle = handle
        scope = {'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}
        async with Client(self.url) as client:
            standard = (await client.call_tool('apply_office_standard', {'request': {
                'action': 'preview', 'standard_id': 'native-model-qa-demo-layer-status',
                'standard_version': '1.0.0', 'scope': scope}})).data
            self.assertEqual(standard['workflow']['standard_version'], '1.0.0')
            self.assertTrue(standard['evaluation_apply_available'])
            self.assertEqual(len(standard['changes']), 2)
            request = {'action': 'preview', 'audit': {'profile_id': 'native-model-qa-demo', 'scope': scope},
                       'repairs': [{'rule_id': 'QA-003', 'value': 'structure'}, {'rule_id': 'QA-004', 'value': 'NEW'}],
                       'selection': {'where': {'not': {'field': 'status', 'op': 'eq', 'value': 'NEW'}},
                                     'exclude_model_uuids': [str(elements[4].GetModelElementUUID())]}}
            selected = (await client.call_tool('rule_based_edit', {'request': request})).data
            self.assertEqual([c['locator']['mark']['value'] for c in selected['changes']], ['S06'])
            check = (await client.call_tool('fix_model_issues', {'request': {
                'action': 'revalidate', 'plan_id': selected['plan_id'], 'plan_hash': selected['plan_hash']}})).data
            self.assertEqual(check['state'], 'unchanged')
            rejected = (await client.call_tool('fix_model_issues', {'request': {
                'action': 'apply', 'plan_id': selected['plan_id'], 'plan_hash': selected['plan_hash'],
                'execution_id': uuid4().hex, 'acknowledgement': 'disposable_copy_reviewed_two_repairs'}})).data
            self.assertEqual(rejected['error']['code'], 'repair_scope_unavailable')
            self.assertFalse(rejected['native_setters_started'])
            invalid = await client.call_tool('apply_office_standard', {'request': {
                'action': 'apply', 'standard_id': 'native-model-qa-demo-layer-status',
                'standard_version': '1.0.0', 'scope': scope}}, raise_on_error=False)
            self.assertTrue(invalid.is_error)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_explicit_apply_rejection_is_not_unknown_and_recovery_never_replays_it(self):
        from test_repair_execution import ExecutionTests
        from allplan_mcp.repair_diagnostics import apply_gate, recovery_gate
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in {"/fix-model-issues", "/model-audit"}:
                self.bridge_handler.calls.append((path, payload))
                if payload.get("action") == "apply":
                    elements[5].IsInActiveLayer.return_value = False
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)
        self.bridge_handler.handle = handle
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reject.json"
            rejected = await apply_gate(self.host_url, self.url, path, confirm=lambda prompt: "NAPRAW KOPIE")
            self.assertEqual(rejected["state"], "rejected", rejected)
            self.assertFalse(rejected["native_setters_started"])
            self.assertEqual(rejected["steps"][-1]["response"]["error"]["code"], "target_not_writable")
            previous = json.loads((Path(directory) / "m3-last-execution.json").read_text(encoding="utf-8"))
            self.assertEqual(previous["state"], "rejected")
            before = len(self.bridge_handler.calls)
            recovered = await recovery_gate(self.host_url, self.url, Path(directory) / "recover.json", previous)
            self.assertEqual(recovered["state"], "rejected")
            self.assertEqual(len(self.bridge_handler.calls), before)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_m3_lost_apply_response_saves_identity_and_recovery_does_not_retry(self):
        from test_repair_execution import ExecutionTests
        from allplan_mcp.repair_diagnostics import apply_gate, recovery_gate
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.writable_fixture()
        original = self.bridge_handler.handle
        lost = [False]
        def handle(path, payload):
            if path in {"/fix-model-issues", "/model-audit"}:
                self.bridge_handler.calls.append((path, payload))
                result = native.handler.handle(path, payload)
                if payload.get("action") == "apply" and not lost[0]:
                    lost[0] = True
                    raise transport.BridgeError("execution_unknown", "Simulated lost completed reply", 503)
                return result
            return original(path, payload)
        self.bridge_handler.handle = handle
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lost.json"
            result = await apply_gate(self.host_url, self.url, path, confirm=lambda prompt: "NAPRAW KOPIE")
            self.assertEqual(result["state"], "unknown")
            self.assertEqual(sum(p.get("action") == "apply" for _, p in self.bridge_handler.calls), 1)
            previous = json.loads((Path(directory) / "m3-last-execution.json").read_text(encoding="utf-8"))
            recovered = await recovery_gate(self.host_url, self.url, Path(directory) / "recover.json", previous)
            self.assertEqual(recovered["state"], "ready_for_ui_observation", recovered)
            native.base.ElementsLayerService.ChangeLayer.assert_called_once()
            native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    async def test_m3_apply_cli_and_recovery_use_real_transport_with_persisted_execution(self):
        from test_repair_execution import ExecutionTests
        from allplan_mcp.repair_diagnostics import apply_gate, recovery_gate
        native = ExecutionTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.writable_fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in {"/fix-model-issues", "/model-audit"}:
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)
        self.bridge_handler.handle = handle
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "apply.json"
            cancelled = await apply_gate(self.host_url, self.url, path, confirm=lambda prompt: "")
            self.assertEqual(cancelled["state"], "cancelled")
            native.base.ElementsLayerService.ChangeLayer.assert_not_called()
            applied = await apply_gate(self.host_url, self.url, path, confirm=lambda prompt: "NAPRAW KOPIE")
            self.assertEqual(applied["state"], "ready_for_ui_observation", applied)
            self.assertTrue(path.with_suffix(".txt").exists())
            previous = json.loads((Path(directory) / "m3-last-execution.json").read_text(encoding="utf-8"))
            self.assertEqual(previous["state"], "apply_pending")
            self.assertEqual(previous["execution_id"], applied["execution_id"])
            recovered = await recovery_gate(self.host_url, self.url, Path(directory) / "recover.json", previous)
            self.assertEqual(recovered["state"], "ready_for_ui_observation", recovered)
            elements[4].GetCommonProperties.return_value.Layer = 8
            elements[5].GetAttributes.return_value = [(20001, "S06"), (20002, "NWE")]
            undone = await recovery_gate(self.host_url, self.url, Path(directory) / "undo.json", previous, True)
            self.assertEqual(undone["state"], "ready_for_ui_observation", undone)
            native.base.ElementsLayerService.ChangeLayer.assert_called_once()
            native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    async def test_m3_preview_gate_real_transport_and_cli_preserve_two_changes_and_five_findings(self):
        from test_model_repair import RepairTests
        native = RepairTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in {'/fix-model-issues', '/model-audit'}:
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)
        self.bridge_handler.handle = handle
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'preview.json'
            env = os.environ.copy()
            env.update({'ALLPLAN_HOST_URL': self.host_url, 'MCP_URL': self.url, 'NO_PROXY': '127.0.0.1,localhost'})
            result = await asyncio.to_thread(subprocess.run, [sys.executable, '-m', 'allplan_mcp.diagnostics',
                '--m3-preview', '--output', str(output)], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(output.read_text(encoding='utf-8'))
            self.assertTrue(report['m3_preview']['checks_complete'])
            self.assertEqual(report['mcp']['fix_model_issues']['counts']['changes'], 2)
            self.assertEqual(report['mcp']['model_audit']['counts']['findings'], 5)
            self.assertEqual(report['m3_preview']['steps'][2]['response']['state'], 'unchanged')
            self.assertIn('M3 preview checks complete: True', output.with_suffix('.txt').read_text(encoding='utf-8'))
            self.assertIn('NWE', output.with_suffix('.txt').read_text(encoding='utf-8'))
        async with Client(self.url, timeout=5) as client:
            before = len(self.bridge_handler.calls)
            for request in ({'action': 'apply'}, {'action': 'revalidate', 'plan_id': 'bad', 'plan_hash': '0' * 64},
                            {**report['m3_preview']['request'], 'repairs': [{'rule_id':'QA-004','value':'NWE'}]}):
                response = await client.call_tool('fix_model_issues', {'request': request}, raise_on_error=False)
                self.assertTrue(response.is_error)
            self.assertEqual(len(self.bridge_handler.calls), before)
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.assertFalse(any(path == '/create-box' for path, _ in self.bridge_handler.calls))

    async def test_m3_preview_gate_stops_after_lost_response_without_retry_or_audit(self):
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path == '/fix-model-issues':
                self.bridge_handler.calls.append((path, payload))
                raise transport.BridgeError('query_read_failed', 'Fake unavailable preview', 503)
            return original(path, payload)
        self.bridge_handler.handle = handle
        report = await collect_m3_preview(self.host_url, self.url)
        self.assertFalse(report['m3_preview']['checks_complete'])
        self.assertEqual([s['name'] for s in report['m3_preview']['steps']], ['host_boundary_preflight', 'preview'])
        self.assertEqual(sum(path == '/fix-model-issues' for path, _ in self.bridge_handler.calls), 1)
        self.assertFalse(any(path == '/model-audit' for path, _ in self.bridge_handler.calls))

    async def test_model_audit_full_host_contract_transport_and_cli_reports(self):
        from test_model_audit import AuditTests
        from allplan_mcp.demo_profile import load_audit_profile
        native = AuditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path == "/model-audit":
                self.bridge_handler.calls.append((path, payload))
                return native.handler.handle(path, payload)
            return original(path, payload)
        self.bridge_handler.handle = handle
        request = {"scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
                   "profile_id": "native-model-qa-demo"}
        report = await collect_diagnostics(self.host_url, self.url, audit_request=request)
        audit = report["mcp"]["model_audit"]
        self.assertEqual(audit["counts"]["findings"], 5)
        self.assertEqual(audit["counts"]["affected_elements"], 5)
        self.assertTrue(audit["coverage"]["audit_complete"])
        self.assertTrue(audit["read_only"])
        self.assertEqual(report["allplan_acceptance"], "not_run")
        self.assertFalse(any(path == "/create-box" for path, _ in self.bridge_handler.calls))
        async with Client(self.url, timeout=5) as client:
            profile_resource = await client.read_resource("allplan://profiles/native-model-qa-demo/audit")
            self.assertEqual(json.loads(profile_resource[0].text), load_audit_profile())
            before = len(self.bridge_handler.calls)
            for bad in ({"scope": request["scope"]}, {**request, "profile": load_audit_profile()},
                        {**request, "max_adapters": True}, {**request, "rule_ids": []},
                        {**request, "scope": {**request["scope"], "drawing_files": [101,102], "include_passive": True}}):
                result = await client.call_tool("model_audit", {"request": bad}, raise_on_error=False)
                self.assertTrue(result.is_error)
            self.assertEqual(len(self.bridge_handler.calls), before)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "audit.json"
            request_path = Path(directory) / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            env = os.environ.copy()
            env.update({"ALLPLAN_HOST_URL": self.host_url, "MCP_URL": self.url, "NO_PROXY": "127.0.0.1,localhost"})
            result = await asyncio.to_thread(subprocess.run, [sys.executable, "-m", "allplan_mcp.diagnostics",
                "--audit-request", str(request_path), "--output", str(output)], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["mcp"]["model_audit"]["counts"]["findings"], 5)
            self.assertIn("5 findings on 5 elements", output.with_suffix(".txt").read_text(encoding="utf-8"))

    async def test_stability_cli_runs_two_reads_and_protected_host_rejection_then_health(self):
        from test_model_audit import AuditTests
        native = AuditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.fixture()
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path == '/model-audit':
                self.bridge_handler.calls.append((path,payload))
                try:
                    return native.handler.handle(path,payload)
                except native.module.BridgeError as exc:
                    raise transport.BridgeError(exc.code,str(exc),exc.status) from exc
            return original(path,payload)
        self.bridge_handler.handle=handle
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'stability.json'
            env=os.environ.copy()
            env.update({'ALLPLAN_HOST_URL':self.host_url,'MCP_URL':self.url,'NO_PROXY':'127.0.0.1,localhost'})
            result=await asyncio.to_thread(subprocess.run,[sys.executable,'-m','allplan_mcp.diagnostics',
                '--m2-stability','--output',str(output)],env=env,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(output.read_text(encoding='utf-8'))
            steps=report['m2_stability']['steps']
            self.assertTrue(report['m2_stability']['checks_complete'])
            self.assertTrue(all(step['ok'] for step in steps))
            self.assertEqual(steps[2]['response']['counts']['findings'],5)
            self.assertEqual(steps[4]['code'],'invalid_payload')
            self.assertIn('Stability checks complete: True',output.with_suffix('.txt').read_text(encoding='utf-8'))
        audits=[payload for path,payload in self.bridge_handler.calls if path=='/model-audit']
        self.assertEqual(len(audits),3)  # two valid reads and one direct host rejection
        self.assertEqual([p['scope']['drawing_files'] for p in audits],[[101],[101],[101,102]])
        self.assertFalse(any(path=='/create-box' for path,_ in self.bridge_handler.calls))

    async def test_stability_stops_after_second_read_failure_and_never_retries(self):
        original=self.bridge_handler.handle
        calls=[]
        def handle(path,payload):
            if path=='/model-audit':
                calls.append(payload)
                if len(calls)==2:
                    raise transport.BridgeError('query_read_failed','Fake read failed.',503)
            return original(path,payload)
        self.bridge_handler.handle=handle
        report=await collect_m2_stability(self.host_url,self.url)
        self.assertFalse(report['m2_stability']['checks_complete'])
        self.assertEqual(len(calls),2)
        self.assertEqual([s['name'] for s in report['m2_stability']['steps']],['host_boundary_preflight','audit_1','audit_2'])
        self.assertIn('no automatic retry',report['m2_stability']['stopped_reason'])

    async def test_stability_requires_loaded_boundary_and_matching_install_before_model_reads(self):
        original=self.bridge_handler.handle
        for defect in ('version','integrity','boundary'):
            def handle(path,payload):
                response=original(path,payload)
                if path=='/get-allplan-version':
                    if defect=='version':response['bridge_package']['version']='0.6.0'
                    if defect=='integrity':response['installed_bridge_integrity']['status']='mismatch'
                return response
            self.bridge_handler.handle=handle
            # The boundary marker is injected by the loaded WebRequestHandler;
            # removing it on the HTTP client models an older loaded transport.
            if defect=='boundary':
                from unittest.mock import patch
                from allplan_mcp.allplan_client import AllplanHostClient
                original_post=AllplanHostClient.post
                def post(client,path,*args,**kwargs):
                    response=original_post(client,path,*args,**kwargs)
                    response.pop('ui_dispatch_exception_boundary',None)
                    return response
                with patch.object(AllplanHostClient,'post',post):
                    report=await collect_m2_stability(self.host_url,self.url)
            else:
                report=await collect_m2_stability(self.host_url,self.url)
            self.assertFalse(report['m2_stability']['checks_complete'])
            self.assertEqual(len(report['m2_stability']['steps']),1)
        self.assertFalse(any(path in ('/model-audit','/get-model-context') for path,_ in self.bridge_handler.calls))

    async def test_model_audit_errors_are_captured_and_invalid_inputs_do_not_connect(self):
        request = {"scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
                   "profile_id": "native-model-qa-demo"}
        before = len(self.bridge_handler.calls)
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, audit_request={**request, "max_adapters": True})
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, query_request={"action": "profile", "profile_id": "native-model-qa-demo"}, audit_request=request)
        self.assertEqual(len(self.bridge_handler.calls), before)
        original = self.bridge_handler.handle
        def fail(path, payload):
            if path == "/model-audit":
                raise transport.BridgeError("profile_unbound", "Fake missing resources.", 409)
            return original(path, payload)
        self.bridge_handler.handle = fail
        report = await collect_diagnostics(self.host_url, self.url, audit_request=request)
        self.assertFalse(report["mcp"]["model_audit"]["ok"])
        self.assertIn("profile_unbound", report["mcp"]["model_audit"]["message"])

    async def test_final_batch_transports_geometry_profile_and_saves_summaries(self):
        from allplan_mcp.demo_profile import load_demo_profile
        request = {"action": "query", "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
                   "component_kind": "top_level_component", "coordinate_frame": "model_local", "profile_id": "native-model-qa-demo",
                   "fields": ["mark", "bounding_box_mm", "size_z_mm"],
                   "spatial_box": {"min": [-201,-201,-1], "max": [201,201,3001], "relation": "contained", "boundary": "exclusive", "frame": "model_local"}}
        requests = [{"action": "profile", "profile_id": "native-model-qa-demo"}, request]
        report = await collect_diagnostics(self.host_url, self.url, query_batch=requests)
        records = report["mcp"]["model_query_batch"]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["response"]["request"]["profile"], load_demo_profile())
        self.assertNotIn("profile_id", records[1]["response"]["request"])
        self.assertEqual(records[1]["summary"]["request"]["action"], "summary")
        self.assertEqual(len(records[1]["pages"]),1)
        self.assertNotIn("error", records[1])
        json.dumps(report, allow_nan=False)
        before = len(self.bridge_handler.calls)
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, query_batch=[request, {"action": "create_box"}])
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, query_batch=[{**request, "spatial_box": {
                **request["spatial_box"], "max": [float("inf"),1,1]}}])
        self.assertEqual(len(self.bridge_handler.calls), before)
        async with Client(self.url, timeout=5) as client:
            resource = await client.read_resource("allplan://profiles/native-model-qa-demo")
            self.assertEqual(json.loads(resource[0].text), load_demo_profile())
        self.assertFalse(any(route == "/create-box" for route, _ in self.bridge_handler.calls))

    async def test_diagnostic_repeated_cursor_is_bounded_and_preserves_partial_evidence(self):
        original = self.bridge_handler.handle
        def repeat_cursor(path, payload):
            response = original(path, payload)
            if path == "/model-query" and payload["action"] in {"query", "page"}:
                response["page"] = {"next_cursor": "b" * 32}
            return response
        self.bridge_handler.handle = repeat_cursor
        request = {"action": "query", "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"}}
        report = await collect_diagnostics(self.host_url, self.url, query_batch=[request])
        record = report["mcp"]["model_query_batch"][0]
        self.assertIn("cursor budget", record["error"]["message"])
        self.assertIn("response", record)
        self.assertEqual(len(record["pages"]), 2)
        pages = [payload for path, payload in self.bridge_handler.calls if path == "/model-query" and payload["action"] == "page"]
        self.assertEqual(len(pages),1)

    async def test_metadata_inspect_diagnostics_capture_and_invalid_request_no_native_call(self):
        request = {"action": "inspect", "scope": {"drawing_files": [1, 2], "include_passive": True, "visibility": "api_select_all"},
                   "attribute_ids": [498], "sample_limit": 10}
        report = await collect_diagnostics(self.host_url, self.url, request)
        self.assertEqual(report["model_query_request"], request)
        self.assertEqual(report["mcp"]["model_query"]["request"], {"schema_version": "m1-query-1", **request})
        self.assertTrue(report["mcp"]["model_query"]["request_id"])
        self.assertEqual(report["allplan_acceptance"], "not_run")
        before = len(self.bridge_handler.calls)
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, {**request, "sample_limit": 21})
        self.assertEqual(len(self.bridge_handler.calls), before)
        async with Client(self.url, timeout=5) as client:
            bad = await client.call_tool("model_query", {"request": {**request, "attribute_ids": [True]}}, raise_on_error=False)
            self.assertTrue(bad.is_error)
        self.assertFalse(any(route == "/create-box" for route, _ in self.bridge_handler.calls))

    async def asyncSetUp(self):
        self.bridge_handler = FakeBridge()
        self.bridge = transport.BridgeServer(("127.0.0.1", 0), self.bridge_handler, lambda callback: callback())
        self.bridge.start()
        self.addCleanup(stop_test_server, self, self.bridge)
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        self.url = f"http://127.0.0.1:{port}/mcp"
        self.host_url = f"http://127.0.0.1:{self.bridge.server_port}"
        environment = os.environ.copy()
        environment.update({"MCP_HOST": "127.0.0.1", "MCP_PORT": str(port),
                            "MCP_PATH": "/mcp", "ALLPLAN_HOST_URL": self.host_url,
                            "ALLPLAN_MCP_ENABLE_PYTHON_EXEC": "0", "NO_PROXY": "127.0.0.1,localhost"})
        self.output = tempfile.TemporaryFile(mode="w+")
        self.addCleanup(self.output.close)
        self.process = subprocess.Popen([sys.executable, "-m", "allplan_mcp.server"],
                                        env=environment, stdout=self.output, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop_process)
        deadline = asyncio.get_running_loop().time() + 15
        while asyncio.get_running_loop().time() < deadline:
            if self.process.poll() is not None:
                self.output.seek(0)
                self.fail(f"MCP server exited: {self.output.read()}")
            try:
                async with Client(self.url, timeout=1):
                    return
            except Exception:
                await asyncio.sleep(0.1)
        self.fail("MCP server startup timed out")

    def stop_process(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    async def test_discovery_health_version_names_box_and_diagnostic_bundle(self):
        async with Client(self.url, timeout=5) as client:
            names = {t.name for t in await client.list_tools()}
            self.assertEqual(names, {"allplan_health", "get_allplan_version", "get_all_object_names", "create_cube", "create_box", "get_model_context", "model_query", "model_audit", "fix_model_issues", "apply_office_standard", "rule_based_edit"})
            resources = await client.list_resources()
            self.assertIn("allplan://skills", {str(r.uri) for r in resources})
            health = (await client.call_tool("allplan_health")).data
            self.assertTrue(health["ok"])
            self.assertEqual(health["allplan_version"], "2026.fake")
            self.assertTrue(health["request_id"])
            self.assertEqual((await client.call_tool("get_allplan_version")).data, "2026.fake")
            self.assertEqual((await client.call_tool("get_all_object_names")).data, ["Fake column"])
            context = (await client.call_tool("get_model_context", {"identity_sample_size": 2})).data
            self.assertTrue(context["read_only"])
            self.assertEqual(context["identity_sample"]["requested"], 2)
            invalid = await client.call_tool("get_model_context", {"identity_sample_size": 21}, raise_on_error=False)
            self.assertTrue(invalid.is_error)
            box = (await client.call_tool("create_box", {"length": 1000, "width": 1000, "height": 1000})).data
            self.assertTrue(box["submitted"])
            self.assertFalse(box["readback_verified"])
        boxes = [p for route, p in self.bridge_handler.calls if route == "/create-box"]
        self.assertEqual(boxes, [{"length": 1000, "width": 1000, "height": 1000}])
        report = await collect_diagnostics(self.host_url, self.url)
        self.assertTrue(report["mcp"]["ok"])
        self.assertEqual(report["allplan_acceptance"], "not_run")
        self.assertEqual(report["mcp"]["get_allplan_version"], "2026.fake")
        self.assertEqual(report["mcp"]["get_model_context"]["identity_sample"]["requested"], 10)
        json.dumps(report)
        self.assertEqual(len([p for route, p in self.bridge_handler.calls if route == "/create-box"]), 1)
        self.bridge.stop()
        self.assertTrue(self.bridge.stopped.wait(2))
        async with Client(self.url, timeout=5) as client:
            result = await client.call_tool("allplan_health", raise_on_error=False)
            self.assertTrue(result.is_error)
            self.assertIn("host_absent", str(result.content))

    async def test_model_query_schema_transport_predicates_pages_and_summary(self):
        query = {"action": "query", "scope": {"drawing_files": [101, 102], "include_passive": True, "visibility": "api_select_all"},
                 "predicate": {"all": [{"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                                       {"not": {"field": "attribute:83", "op": "eq", "value": None}}]},
                 "attribute_ids": [83], "page_size": 1}
        async with Client(self.url, timeout=5) as client:
            tool = next(t for t in await client.list_tools() if t.name == "model_query")
            self.assertIn("request", tool.inputSchema["properties"])
            result = (await client.call_tool("model_query", {"request": query})).data
            self.assertTrue(result["read_only"])
            self.assertEqual(result["request"], {"schema_version": "m1-query-1", **query})
            for action in ("page", "summary"):
                follow = {"action": action, "selection_id": result["selection_id"]}
                response = (await client.call_tool("model_query", {"request": follow})).data
                self.assertEqual(response["request"], {"schema_version": "m1-query-1", **follow})
            null_cursor = {"action": "page", "selection_id": result["selection_id"], "cursor": None}
            response = (await client.call_tool("model_query", {"request": null_cursor})).data
            self.assertNotIn("cursor", response["request"])
            before = len(self.bridge_handler.calls)
            for bad in ({"action": "query", "scope": {"drawing_files": [-101], "include_passive": False, "visibility": "api_select_all"}},
                        {"action": "query", "scope": query["scope"], "page_size": True},
                        {"action": "summary", "selection_id": "a" * 32, "scope": query["scope"]}):
                result = await client.call_tool("model_query", {"request": bad}, raise_on_error=False)
                self.assertTrue(result.is_error)
            self.assertEqual(len(self.bridge_handler.calls), before)
        self.assertFalse(any(path == "/create-box" for path, _ in self.bridge_handler.calls))
