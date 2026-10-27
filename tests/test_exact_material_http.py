"""Public MCP validation and exact-child execution through HTTP."""
import unittest
from uuid import uuid4
from fastmcp import Client
import test_exact_material_target as fixtures
import test_wall_material_http as http
import test_mcp_smoke as smoke


class ExactMaterialHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process
    route_model_edit = http.WallMaterialHTTPTests.route_model_edit

    async def test_exact_child_apply_and_replay_over_public_schema(self):
        fixture = fixtures.ExactMaterialTargetTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.route_model_edit(fixture.f.native)
        async with Client(self.url, timeout=30) as client:
            for updates in ({"exact_target": None}, {"native_types": ["MultiSlab_TypeUUID"]}):
                rejected = await client.call_tool("model_edit", {"request": {**fixture.request, **updates}}, raise_on_error=False)
                self.assertTrue(rejected.is_error)
            self.assertFalse(self.bridge_handler.calls)
            plan = (await client.call_tool("model_edit", {"request": fixture.request})).data
            self.assertTrue(plan["apply_available"], plan)
            highlighted = (await client.call_tool("model_edit", {"request": plan["next_action"]["request"]})).data
            request = {**highlighted["next_action"]["request"], "execution_id": uuid4().hex}
            result = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(result["state"], "completed", result)
            self.assertTrue((await client.call_tool("model_edit", {"request": request})).data["replayed"])
        fixture.f.native.base.ModifyElements.assert_called_once()
