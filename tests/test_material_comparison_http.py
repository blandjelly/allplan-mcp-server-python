"""Material comparison through the public MCP HTTP schema and host route."""
import unittest

from fastmcp import Client

import test_component_identity_http as identity_http
import test_material_comparison as fixtures
import test_mcp_smoke as smoke


class MaterialComparisonHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process
    attach = identity_http.ComponentIdentityHTTPTests.attach

    def native_bridge(self):
        native = fixtures.MaterialComparisonTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.material_fixture()
        self.attach(native, {"/model-property-probe"})
        return native

    async def test_native_and_attribute_values_roundtrip_without_selection_or_setters(self):
        native = self.native_bridge()
        async with Client(self.url, timeout=10) as client:
            result = (await client.call_tool("model_property_probe", {"request": native.request()})).data
        self.assertEqual(result["phase"], "material_comparison")
        self.assertEqual(result["state"], "observed", result)
        target = result["representations"][0]["target"]["value"]
        self.assertEqual(target["native_material"]["value"], "native")
        self.assertEqual(target["read_modes"]["ReadAllAndComputable"]["value"][0]["value"], "Żelbet")
        self.assertEqual(result["metadata"][0]["name"]["value"], "Materiał")
        self.assertEqual(result["setter_calls_started"], 0)
        self.assertEqual(len(self.bridge_handler.calls), 1)
        native.base.GetElement.assert_called_once_with(native.target)
        native.base.ModifyElements.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertFalse(native.handler.model_queries.selections)

    async def test_invalid_contract_stops_before_bridge_and_getter_error_is_local(self):
        native = self.native_bridge()
        native.base.GetElement.side_effect = RuntimeError("private native details")
        async with Client(self.url, timeout=10) as client:
            for changes in ({"attribute_ids": [True]}, {"attribute_ids": []},
                            {"view_uuid": "00000000-0000-0000-0000-000000000000"}):
                rejected = await client.call_tool("model_property_probe", {
                    "request": native.request(**changes)}, raise_on_error=False)
                self.assertTrue(rejected.is_error)
            self.assertFalse(self.bridge_handler.calls)
            result = (await client.call_tool("model_property_probe", {"request": native.request()})).data
        self.assertEqual(result["state"], "not_checked")
        value = result["representations"][0]["target"]["value"]
        self.assertEqual(value["native_material"]["status"], "not_checked")
        self.assertEqual(value["read_modes"]["ReadAll"]["value"][0]["value"], "Żelbet")
        self.assertNotIn("private native details", str(result))
        self.assertEqual(len(self.bridge_handler.calls), 1)
        native.base.GetElement.assert_called_once_with(native.target)
        native.base.ModifyElements.assert_not_called()

    async def test_unenumerated_slab_child_uses_only_explicit_parent_without_writes(self):
        native = self.native_bridge()
        child, parent = native.slab_child_fixture()
        async with Client(self.url, timeout=10) as client:
            blocked = await client.call_tool("model_property_probe", {"request": native.request()}, raise_on_error=False)
            self.assertTrue(blocked.is_error)
            self.assertIn("probe_scope_unavailable", str(blocked))
            result = (await client.call_tool("model_property_probe", {"request": native.request(
                parent_ref=native.parent_ref, include_parent=True)})).data
        self.assertEqual(result["ref"]["model_uuid"], child.GetModelElementUUID())
        self.assertFalse(result["identity_resolution"]["target_in_direct_scan"])
        row = result["representations"][0]
        self.assertEqual(row["target"]["value"]["native_material"]["value"], " ")
        self.assertEqual(row["parent"]["value"]["evidence"]["native_material"]["value"], "parent-native")
        native.base.ModifyElements.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        native.base.DeleteElements.assert_not_called()
        self.assertFalse(native.handler.model_queries.selections)

    async def test_parent_contract_rejects_invalid_hint_before_bridge_and_never_guesses_missing_view(self):
        native = self.native_bridge()
        child, parent = native.slab_child_fixture()
        async with Client(self.url, timeout=10) as client:
            for hint in (None, {}, {**native.parent_ref, "model_uuid": child.GetModelElementUUID()},
                         {**native.parent_ref, "view_uuid": "00000000-0000-0000-0000-000000000000"}):
                rejected = await client.call_tool("model_property_probe", {"request": native.request(parent_ref=hint)}, raise_on_error=False)
                self.assertTrue(rejected.is_error)
            self.assertFalse(self.bridge_handler.calls)
            wrong = {**native.parent_ref, "view_uuid": "10000000-0000-4000-8000-000000000099"}
            rejected = await client.call_tool("model_property_probe", {"request": native.request(parent_ref=wrong)}, raise_on_error=False)
            self.assertTrue(rejected.is_error)
            self.assertIn("probe_scope_unavailable", str(rejected))
        native.base.GetElement.assert_not_called()
        child.GetAttributes.assert_not_called()
        native.base.ModifyElements.assert_not_called()


if __name__ == "__main__":
    unittest.main()
