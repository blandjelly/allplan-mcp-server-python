"""One Wall request through real MCP HTTP; no native Allplan claims."""
import json
import tempfile
import unittest
from pathlib import Path

from fastmcp import Client
from allplan_mcp.wall_diagnostics import run
import test_wall_probe as native_tests
import test_mcp_smoke as smoke


class WallProbeHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def native_bridge(self, pending_path=None, lost_reply=False):
        native = native_tests.WallProbeTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.wall_fixture()
        original = self.bridge_handler.handle
        def handle(route, payload):
            if route != '/model-property-probe':
                return original(route, payload)
            self.bridge_handler.calls.append((route, payload))
            if pending_path is not None:
                saved = json.loads(pending_path.read_text(encoding='utf-8'))
                self.assertEqual(saved['steps'][-1]['state'], 'request_pending')
                self.assertEqual(saved['steps'][-1]['request']['phase'], 'wall_sample')
            try:
                result = native.handler.handle(route, payload)
            except native.module.BridgeError as exc:
                raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            if lost_reply:
                raise smoke.transport.BridgeError('execution_unknown', 'lost native reply', 503)
            return result
        self.bridge_handler.handle = handle
        return native

    async def test_one_native_sample_with_pending_report_and_same_session_health(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'wall.json'
            native = self.native_bridge(path)
            report = await run(self.url, path)
            self.assertEqual(report['state'], 'awaiting_owner_observation', report.get('message'))
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), report)
            self.assertFalse(report['model_setters_requested'])
            self.assertEqual([step['name'] for step in report['steps']], ['health_before', 'one_wall_sample', 'health_after'])
            sample = report['steps'][1]['response']['sample']
            self.assertEqual(sample['total_thickness_mm']['value'], 200)
            self.assertEqual(sample['native_material']['value'], 'C25/30')
            self.assertEqual([r for r, p in self.bridge_handler.calls], ['/get-allplan-version', '/model-property-probe', '/get-allplan-version'])
            native.base.GetElement.assert_called_once()

    async def test_lost_reply_is_saved_not_retried_or_followed_by_native_health(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'wall.json'
            native = self.native_bridge(path, lost_reply=True)
            report = await run(self.url, path)
            self.assertEqual(report['state'], 'blocked')
            self.assertEqual(report['steps'][-1]['state'], 'request_pending')
            self.assertEqual(len(report['steps']), 2)
            native.base.GetElement.assert_called_once()
            self.assertFalse(report['automatic_retry'])

    async def test_multitier_is_blocked_with_health_after_and_no_material_read(self):
        native = self.native_bridge()
        native.props.TierCount = 2
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'wall.json')
        self.assertEqual(report['state'], 'blocked')
        self.assertEqual(report['steps'][-1]['name'], 'health_after')
        native.props.GetWallTierProperties.assert_not_called()
        native.tier.read_material.assert_not_called()

    async def test_old_bridge_and_invalid_requests_never_start_wall_read(self):
        native = self.native_bridge()
        original = self.bridge_handler.handle
        def old_bridge(route, payload):
            result = original(route, payload)
            if route == '/get-allplan-version':
                result['bridge_package']['version'] = '0.17.2'
            return result
        self.bridge_handler.handle = old_bridge
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'wall.json')
        self.assertEqual(report['state'], 'blocked')
        self.assertEqual(len(report['steps']), 1)
        async with Client(self.url) as client:
            before = len(self.bridge_handler.calls)
            for request in ({'phase': 'wall_sample', 'drawing_file': True},
                            {'phase': 'wall_sample', 'drawing_file': 101, 'model_uuid': None},
                            {'phase': 'wall_sample', 'drawing_file': 101, 'attribute_id': 935}):
                result = await client.call_tool('model_property_probe', {'request': request}, raise_on_error=False)
                self.assertTrue(result.is_error)
            self.assertEqual(len(self.bridge_handler.calls), before)
        native.base.GetElement.assert_not_called()
