"""MCP/HTTP and public Pydantic contract for drawing identity scans."""
import unittest

from fastmcp import Client
from pydantic import ValidationError

import test_component_identity as identity_fixtures
import test_mcp_smoke as smoke


class DrawingIdentityHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def attach(self, native):
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path == "/model-property-probe":
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle

    async def test_drawing_identity_scan_round_trips_through_http(self):
        native = identity_fixtures.ComponentIdentityTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        slab = native.element(1)
        slab.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        multislab = native.element(2)
        multislab.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        native.fixture([slab, multislab])
        native.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 3)]
        native.base.GetElement.side_effect = lambda _adapter: type("NativeSlab", (), {})()
        native.adapter_module.BaseElementAdapterParentElementService.GetParentElement.side_effect = (
            lambda _adapter: native.null_adapter())
        self.attach(native)

        async with Client(self.url, timeout=10) as client:
            response = await client.call_tool("model_property_probe", {"request": {
                "phase": "drawing_identity", "drawing_file": 101, "offset": 1, "limit": 1}})
        result = response.data
        self.assertEqual(result["state"], "observed")
        self.assertEqual(result["counts"]["model_identities"], 2)
        self.assertEqual(result["entries"][0]["ref"]["drawing_file"], 101)
        self.assertEqual(result["entries"][0]["ownership"]["status"], "observed")
        self.assertEqual(result["entries"][0]["native_representation"]["status"], "observed")
        self.assertEqual(result["entries"][0]["native_representation"]["value"]["property_owner"], "not_established")
        self.assertIsNone(result["pagination"]["next_offset"])
        self.assertFalse(result["pagination"]["has_more"])
        slab.GetAttributes.assert_not_called()
        slab.GetModelGeometry.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_http_schema_rejects_invalid_bounds_before_bridge(self):
        native = identity_fixtures.ComponentIdentityTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        self.attach(native)

        # The Pydantic discriminated input and JSON Schema exposed by the MCP
        # tool both constrain the phase-specific pagination contract.
        from allplan_mcp.property_models import DrawingIdentityProbeInput
        DrawingIdentityProbeInput(phase="drawing_identity", drawing_file=101)
        with self.assertRaises(ValidationError):
            DrawingIdentityProbeInput(phase="drawing_identity", drawing_file=101, limit=33)

        async with Client(self.url, timeout=10) as client:
            invalid = await client.call_tool("model_property_probe", {"request": {
                "phase": "drawing_identity", "drawing_file": 101, "offset": 10000}},
                raise_on_error=False)
        self.assertTrue(invalid.is_error)
        self.assertFalse(self.bridge_handler.calls)
        native.coord.GetInputViewDocument.assert_not_called()


if __name__ == "__main__":
    unittest.main()
