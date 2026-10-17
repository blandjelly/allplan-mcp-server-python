"""Full semantic Wall filter via real MCP HTTP with native fakes."""
import json
import tempfile
import unittest
from pathlib import Path

from fastmcp import Client

from allplan_mcp.wall_filter_diagnostics import run
import test_mcp_smoke as smoke
import test_wall_probe as fixtures


class WallFilterHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def native_bridge(self, pending_path=None, lost_reply=False):
        native = fixtures.WallProbeTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.wall_fixture()
        native.handler.wall_filters.trace_path = native.path
        original = self.bridge_handler.handle

        def handle(route, payload):
            if route not in ('/model-wall-filter', '/model-selection'):
                return original(route, payload)
            self.bridge_handler.calls.append((route, payload))
            if pending_path is not None and route == '/model-wall-filter':
                step = json.loads(pending_path.read_text(encoding='utf-8'))['steps'][-1]
                self.assertEqual(step['state'], 'request_pending')
                self.assertEqual(step['tool'], 'model_wall_filter')
            try:
                result = native.handler.handle(route, payload)
            except native.module.BridgeError as exc:
                raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            if lost_reply:
                raise smoke.transport.BridgeError('execution_unknown', 'lost native reply', 503)
            return result

        self.bridge_handler.handle = handle
        return native

    async def test_highlight_full_filter_persisted_request_and_same_session_health(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'filter.json'
            native = self.native_bridge(path)
            thick = native.element(3, name='Wall_TypeUUID')
            native.elements.append(thick)
            import types
            other = fixtures.WallElement(types.SimpleNamespace(TierCount=1, GetWallTierProperties=lambda _: types.SimpleNamespace(Thickness=240)))
            native.base.GetElement.side_effect = lambda adapter: other if adapter is thick else native.wall
            report = await run(self.url, path)
            self.assertEqual(report['state'], 'awaiting_owner_observation', report.get('message'))
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), report)
            self.assertEqual([step['name'] for step in report['steps']], ['health_before', 'wall_thickness_filter', 'health_after'])
            result = report['steps'][1]['response']
            self.assertTrue(result['criterion_complete'])
            self.assertEqual(result['counts']['matched'], 1)
            self.assertEqual(result['counts']['submitted_model_identities'], 1)
            self.assertEqual(native.base.GetElement.call_count, 2)
            native.tier.read_material.assert_not_called()
            self.assertFalse(report['model_setters_requested'])
            native.module.AllplanIFW.HighlightService.HighlightElements.assert_called_once()
            # Explicit clear uses the existing presentation route and does not
            # repeat thickness/native reads.
            async with Client(self.url) as client:
                clear = (await client.call_tool('model_selection', {'request': {'action': 'clear_highlight'}})).data
            self.assertEqual(clear['state'], 'submitted')
            self.assertEqual(native.base.GetElement.call_count, 2)

    async def test_query_never_highlights_and_unknown_wall_blocks_with_health_after(self):
        native = self.native_bridge()
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'query.json', query_only=True)
            self.assertEqual(report['state'], 'awaiting_owner_observation', report.get('message'))
            native.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
            native.props.TierCount = 2
            report = await run(self.url, Path(directory) / 'blocked.json')
        self.assertEqual(report['state'], 'blocked')
        self.assertEqual(report['steps'][-1]['name'], 'health_after')
        native.module.AllplanIFW.HighlightService.CancelAllHighlightedElements.assert_not_called()

    async def test_lost_reply_stops_without_health_after_or_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'lost.json'
            native = self.native_bridge(path, lost_reply=True)
            report = await run(self.url, path)
            self.assertEqual(report['state'], 'blocked')
            self.assertEqual(len(report['steps']), 2)
            self.assertEqual(report['steps'][-1]['state'], 'request_pending')
            self.assertFalse(report['automatic_retry'])
            native.base.GetElement.assert_called_once()
            self.assertEqual(sum(r == '/model-wall-filter' for r, _ in self.bridge_handler.calls), 1)

    async def test_invalid_mcp_inputs_are_rejected_before_host_and_old_package_blocks(self):
        native = self.native_bridge()
        async with Client(self.url) as client:
            before = len(self.bridge_handler.calls)
            for fields in ({'drawing_file': True}, {'threshold': {'value': True, 'unit': 'cm'}},
                           {'threshold': {'value': 24, 'unit': 'inch'}}, {'action': 'apply'},
                           {'max_walls': 101}, {'exclude_model_uuids': None}, {'scope': 'project'}):
                result = await client.call_tool('model_wall_filter', {'request': {'action': 'query', 'drawing_file': 101, **fields}}, raise_on_error=False)
                self.assertTrue(result.is_error, fields)
            self.assertEqual(len(self.bridge_handler.calls), before)
        original = self.bridge_handler.handle

        def old(route, payload):
            result = original(route, payload)
            if route == '/get-allplan-version':
                result['bridge_package']['version'] = '0.18.2'
            return result

        self.bridge_handler.handle = old
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'old.json')
        self.assertEqual(report['state'], 'blocked')
        self.assertEqual(len(report['steps']), 1)
        native.base.GetElement.assert_not_called()

    async def test_new_highlight_invalidates_old_repair_presentation(self):
        native = self.native_bridge()
        native.handler.repair_plans.plans['old'] = {'presentation': {'verified': True}}
        with tempfile.TemporaryDirectory() as directory:
            report = await run(self.url, Path(directory) / 'filter.json')
        self.assertEqual(report['state'], 'awaiting_owner_observation', report.get('message'))
        self.assertNotIn('presentation', native.handler.repair_plans.plans['old'])
