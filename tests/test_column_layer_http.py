"""Real MCP HTTP path, launcher identity persistence, no broad metadata requests."""
import json
import tempfile
import unittest
from pathlib import Path
from fastmcp import Client
import test_column_layer as native_tests
import test_mcp_smoke as smoke
from allplan_mcp.column_layer_diagnostics import run


class ColumnLayerHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def native_bridge(self, lost_reply_path=None):
        native = native_tests.ColumnLayerTests()
        native.setUp()
        native.fixture()
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
        native = self.native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            report = await run(self.url, path, confirm=lambda plan: True)
            self.assertEqual(report['state'], 'completed', report.get('message'))
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), report)
            self.assertTrue(report['model_setters_requested'])
            self.assertEqual(native.base.ElementsLayerService.ChangeLayer.call_count, 2)
            self.assertFalse(any(p in {'/model-properties', '/model-property-probe'} for p, _ in self.bridge_handler.calls))
            no_op = await run(self.url, Path(directory) / 'noop.json', confirm=lambda plan: self.fail('No-op must not ask Apply'))
            self.assertEqual(no_op['state'], 'no_op')

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
