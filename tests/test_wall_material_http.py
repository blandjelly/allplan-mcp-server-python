"""Public MCP HTTP contract for native Wall material editing."""
import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastmcp import Client

import test_mcp_smoke as smoke
import test_wall_material_edit as fixture_module
import test_native_material_columns as column_fixtures


class WallMaterialHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    async def test_material_edit_with_axis_preview_highlight_apply_and_replay_over_http(self):
        native = fixture_module.WallMaterialEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        axis = native.native.element(21, name="WallAxis_TypeUUID")
        axis.GetModelGeometry.return_value = SimpleNamespace()
        native.native.children[id(native.tier)] = [axis]
        native.native.parents[id(axis)] = native.tier
        native.tier.GetModelGeometry.side_effect = ValueError("reported tier geometry failure")
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path == "/model-edit":
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.native.handler.handle(path, payload)
                except native.native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle
        request = native.request()
        async with Client(self.url, timeout=10) as client:
            preview = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(preview["counts"]["changes"], 1)
            self.assertEqual(preview["changes"][0]["resource"]["tier_index"], 1)
            axis_state = preview["changes"][0]["resource"]["native_material_state"]["auxiliary_components"]["tier"][0]
            self.assertEqual(axis_state["ownership"]["target"]["type_name"], "WallAxis_TypeUUID")
            self.assertEqual(axis_state["geometry"]["status"], "not_checked")
            self.assertEqual(preview["changes"][0]["resource"]["native_material_state"]["tier_geometry"]["status"],
                             "not_checked")
            highlighted = (await client.call_tool("model_edit", {
                "request": preview["next_action"]["request"]})).data
            execution_id = uuid4().hex
            apply_request = {**highlighted["next_action"]["request"], "execution_id": execution_id}
            applied = (await client.call_tool("model_edit", {"request": apply_request})).data
            self.assertEqual(applied["state"], "completed", applied)
            self.assertEqual(native.material, "C35/45")
            replay = (await client.call_tool("model_edit", {"request": apply_request})).data
            self.assertTrue(replay["replayed"])
            self.assertEqual(native.native.base.ModifyElements.call_count, 1)

    async def test_missing_tier_index_fails_at_public_contract_before_bridge(self):
        async with Client(self.url, timeout=10) as client:
            valid = {"schema_version": "m4-model-edit-1", "action": "preview",
                     "scope": {"drawing_files": [101], "include_passive": False,
                               "visibility": "api_select_all"},
                     "predicate": None, "changes": [
                         {"target": {"kind": "native_material", "tier_index": 1},
                          "value": "C35/45"}]}
            invalid = []
            missing = {**valid, "changes": [{"target": {"kind": "native_material"},
                                               "value": "C35/45"}]}
            invalid.append(missing)
            for tier_index in (True, 1.0, 2):
                invalid.append({**valid, "changes": [{"target": {
                    "kind": "native_material", "tier_index": tier_index}, "value": "C35/45"}]})
            for value in ("   ", "C35\n/45"):
                invalid.append({**valid, "changes": [{"target": {
                    "kind": "native_material", "tier_index": 1}, "value": value}]})
            for request in invalid:
                with self.subTest(request=request):
                    result = await client.call_tool("model_edit", {"request": request}, raise_on_error=False)
                    self.assertTrue(result.is_error)
            self.assertFalse(any(path == "/model-edit" for path, _ in self.bridge_handler.calls))

    async def test_preservation_failure_keeps_material_read_and_reports_http_diagnostic(self):
        native = fixture_module.WallMaterialEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        del native.properties.GetWallTierProperties(1).CommonProperties.Pen
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path == "/model-edit":
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.native.handler.handle(path, payload)
                except native.native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle
        async with Client(self.url, timeout=10) as client:
            result = (await client.call_tool("model_edit", {
                "request": native.request()})).data

        self.assertTrue(result["apply_available"], result)
        self.assertEqual(len(result["changes"]), 1)
        self.assertEqual(result["criteria"]["required_field_failures"], [])
        self.assertEqual(result["criteria"]["operation_eligibility_failures"], [])
        self.assertEqual(result["criteria"]["checks"][0]["decision"], "matched")
        diagnostic = result["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.assertEqual(diagnostic["reason"], "wall_material_read_unavailable")
        self.assertEqual(diagnostic["diagnostic"], {
            "stage": "material_common_Pen", "error_type": "AttributeError"})
        self.assertEqual(native.native.base.ModifyElements.call_count, 0)

    async def test_column_native_material_apply_readback_and_replay_over_http(self):
        native = column_fixtures.ColumnMaterialTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path == "/model-edit":
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.native.handler.handle(path, payload)
                except native.native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle
        async with Client(self.url, timeout=10) as client:
            preview = (await client.call_tool("model_edit", {"request": native.fixture.request(
                native_types=["Column_TypeUUID"])})).data
            self.assertTrue(preview["apply_available"], preview)
            highlighted = (await client.call_tool("model_edit", {
                "request": preview["next_action"]["request"]})).data
            request = {**highlighted["next_action"]["request"], "execution_id": uuid4().hex}
            applied = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(applied["state"], "completed", applied)
            self.assertEqual(native.properties.Material, "C35/45")
            self.assertTrue((await client.call_tool("model_edit", {"request": request})).data["replayed"])
            native.native.base.ModifyElements.assert_called_once()
