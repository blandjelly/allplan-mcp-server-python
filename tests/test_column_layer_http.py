"""Real MCP HTTP path, launcher identity persistence, no broad metadata requests."""
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from fastmcp import Client
import test_column_layer as native_tests
import test_mcp_smoke as smoke
from allplan_mcp.column_layer_diagnostics import run
from allplan_mcp.column_layer_models import ColumnLayerPreview


class ColumnLayerHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def native_bridge(self, lost_reply_path=None, values=None):
        native = native_tests.ColumnLayerTests()
        native.setUp()
        native.fixture(**({'values': values} if values is not None else {}))
        self.addCleanup(native.doCleanups)
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in {'/column-layer', '/fix-model-issues'}:
                self.bridge_handler.calls.append((path, payload))
                if lost_reply_path and path == '/column-layer' and payload['action'] == 'apply':
                    report = json.loads(lost_reply_path.read_text(encoding='utf-8'))
                    self.assertEqual(report['steps'][-1]['state'], 'request_pending')
                    self.assertEqual(report['apply_request']['execution_id'], payload['execution_id'])
                    self.assertEqual(report['state'], 'apply_pending')
                try:
                    result = native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
                if lost_reply_path and path == '/column-layer' and payload['action'] == 'apply':
                    raise smoke.transport.BridgeError('execution_unknown', 'Simulated lost reply after write', 503)
                return result
            return original(path, payload)
        self.bridge_handler.handle = handle
        return native

    async def test_launcher_completes_exact_changes_and_health_without_broad_discovery(self):
        native = self.native_bridge(values=('<niezdefiniowany>', 'F120', 'F120', 'F120', '', '  '))
        elements = native.base.ElementsSelectService.SelectAllElements.return_value
        elements[0].GetCommonProperties.return_value.Layer = 8
        typed = ColumnLayerPreview(action='preview', drawing_file=101)
        expected_names = ['Klasa odporności ogniowej', 'Fire resistance classification']
        self.assertEqual(typed.attribute_names, expected_names)
        self.assertEqual(importlib.import_module('test_allplan_host.column_layer').DEFAULT_NAMES, expected_names)
        direct = native.preview()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            report = await run(self.url, path, confirm=lambda plan: True)
            self.assertEqual(report['state'], 'completed', report.get('message'))
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), report)
            self.assertTrue(report['model_setters_requested'])
            plan = next(step['response'] for step in report['steps'] if step['name'] == 'preview')
            self.assertEqual(plan['criteria']['binding'], direct['criteria']['binding'])
            self.assertEqual(plan['criteria']['checks'], direct['criteria']['checks'])
            self.assertEqual(plan['changes'], direct['changes'])
            self.assertEqual(plan['counts']['highlight_targets'], 3)
            shown = next(step['response'] for step in report['steps'] if step['name'] == 'highlight_exact_targets')
            self.assertEqual(shown['counts']['submitted_model_identities'], 3)
            request = next(payload for route, payload in self.bridge_handler.calls
                           if route == '/column-layer' and payload['action'] == 'preview')
            self.assertNotIn('attribute_names', request)
            self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 2)
            self.assertFalse(any(p in {'/model-properties', '/model-property-probe'} for p, _ in self.bridge_handler.calls))
            native.module.AllplanIFW.HighlightService.HighlightElements.reset_mock()
            no_op = await run(self.url, Path(directory) / 'noop.json', confirm=lambda plan: self.fail('No-op must not ask Apply'))
            self.assertEqual(no_op['state'], 'no_op')
            self.assertFalse(no_op['model_setters_requested'])
            self.assertNotIn('apply_request', no_op)
            shown = next(step['response'] for step in no_op['steps'] if step['name'] == 'highlight_exact_targets')
            self.assertEqual(shown['counts']['submitted_model_identities'], 3)
            self.assertEqual(no_op['steps'][-1]['name'], 'health_after')
            sent = native.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
            self.assertEqual([id(e) for e in sent], [id(elements[i]) for i in (0, 4, 5)])
            self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 2)

    async def test_highlight_count_mismatch_blocks_apply(self):
        native = self.native_bridge()
        original = self.bridge_handler.handle
        def mismatch(route, payload):
            result = original(route, payload)
            if route == '/column-layer' and payload['action'] == 'highlight':
                result['counts']['submitted_model_identities'] = 1
            return result
        self.bridge_handler.handle = mismatch
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'report.json',
                               confirm=lambda plan: self.fail('Uncertain highlight must not ask Apply'))
        self.assertEqual(report['state'], 'blocked')
        self.assertFalse(report['model_setters_requested'])
        self.assertNotIn('apply_request', report)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_no_matches_clear_highlights_without_asking_apply(self):
        native = self.native_bridge(values=('F120',))
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'report.json',
                               confirm=lambda plan: self.fail('No matches must not ask Apply'))
        self.assertEqual(report['state'], 'no_op')
        self.assertFalse(report['model_setters_requested'])
        native.module.AllplanIFW.HighlightService.CancelAllHighlightedElements.assert_called_once()
        native.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_legacy_catalog_blocks_launcher_before_scan_highlight_or_apply(self):
        native = self.native_bridge()
        native.attribute_catalog({1398: 'Odporność ogniowa'})
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'report.json',
                               confirm=lambda plan: self.fail('Unavailable binding must not ask Apply'))
        self.assertEqual(report['state'], 'blocked')
        self.assertIn('property_binding_unavailable', report['message'])
        self.assertFalse(report['model_setters_requested'])
        self.assertNotIn('apply_request', report)
        self.assertEqual([payload['action'] for route, payload in self.bridge_handler.calls
                          if route == '/column-layer'], ['preview'])
        native.base.ElementsSelectService.SelectAllElements.assert_not_called()
        native.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_missing_classification_blocks_launcher_without_treating_legacy_blank_as_missing(self):
        native = self.native_bridge(values=('F30',))
        native.base.ElementsSelectService.SelectAllElements.return_value[0].GetAttributes.return_value = [(1398, '')]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            report = await run(self.url, path,
                               confirm=lambda plan: self.fail('Unknown value must not ask Apply'))
            text_report = path.with_suffix('.txt').read_text(encoding='utf-8')
        self.assertEqual(report['state'], 'blocked')
        for detail in ('Klasa odporności ogniowej', '935', 'absent_from_readall_unknown'):
            self.assertIn(detail, report['message'])
            self.assertIn(detail, text_report)
        plan = next(step['response'] for step in report['steps'] if step['name'] == 'preview')
        self.assertEqual(plan['criteria']['checks'][0]['value_state'], 'absent_from_readall_unknown')
        self.assertEqual(plan['changes'], [])
        self.assertFalse(report['model_setters_requested'])
        self.assertNotIn('apply_request', report)
        self.assertEqual([payload['action'] for route, payload in self.bridge_handler.calls
                          if route == '/column-layer'], ['preview'])
        native.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_preview_only_and_typed_validation_never_send_apply(self):
        native = self.native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'report.json', confirm=lambda plan: False)
            self.assertEqual(report['state'], 'preview_only')
            self.assertNotIn('apply_request', report)
        async with Client(self.url) as client:
            before = len(self.bridge_handler.calls)
            result = await client.call_tool('column_layer', {'request': {'action': 'preview', 'drawing_file': True}}, raise_on_error=False)
            self.assertTrue(result.is_error)
            self.assertEqual(len(self.bridge_handler.calls), before)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()

    async def test_lost_response_preserves_exact_execution_and_recover_never_reapplies(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            native = self.native_bridge(lost_reply_path=path)
            report = await run(self.url, path, confirm=lambda plan: True)
            self.assertEqual(report['state'], 'unknown')
            self.assertEqual(report['steps'][-1]['state'], 'request_pending')
            self.assertEqual(sum(r == '/column-layer' and p['action'] == 'apply' for r, p in self.bridge_handler.calls), 1)
            recovered = await run(self.url, Path(directory) / 'recover.json', recover_from=path)
            self.assertEqual(recovered['state'], 'recovered', recovered.get('message'))
            self.assertEqual(recovered['apply_request'], report['apply_request'])
            self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 2)

    async def test_mismatched_bridge_stops_before_any_plan(self):
        native = self.native_bridge()
        original = self.bridge_handler.handle
        def mismatch(route, payload):
            result = original(route, payload)
            if route == '/get-allplan-version':
                result['bridge_package']['version'] = '0.16.1'
            return result
        self.bridge_handler.handle = mismatch
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'report.json', confirm=lambda plan: True)
        self.assertEqual(report['state'], 'blocked')
        self.assertEqual(len(self.bridge_handler.calls), 1)
        native.base.ElementsLayerService.ChangeLayer.assert_not_called()
