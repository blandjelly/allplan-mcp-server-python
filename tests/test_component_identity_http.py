"""Real MCP HTTP contracts for identity reads and slab write blocking."""
import unittest

from fastmcp import Client

import test_component_identity as identity_fixtures
import test_edit_ownership as edit_fixtures
import test_mcp_smoke as smoke


class ComponentIdentityHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def attach(self, native, routes):
        original = self.bridge_handler.handle
        def handle(path, payload):
            if path in routes:
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)
        self.bridge_handler.handle = handle

    async def test_exact_identity_probe_and_opt_in_query_serialize_through_http(self):
        native = identity_fixtures.ComponentIdentityTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        target = native.fixture()[0]
        native.base.GetElement.return_value = object()
        self.attach(native, {"/model-property-probe", "/model-query"})
        async with Client(self.url, timeout=10) as client:
            result = (await client.call_tool("model_property_probe", {"request": {
                "phase": "component_identity", "drawing_file": 101,
                "model_uuid": target.GetModelElementUUID(), "view_uuid": target.GetElementUUID()}})).data
            self.assertEqual(result["state"], "observed")
            self.assertFalse(result["property_write_available"])
            self.assertEqual(result["ownership"]["target"]["model_uuid"], target.GetModelElementUUID())
            query = (await client.call_tool("model_query", {"request": {
                "action": "query", "scope": {"drawing_files": [101], "include_passive": False,
                                               "visibility": "api_select_all"},
                "fields": ["component_ownership"]}})).data
            self.assertEqual(query["elements"][0]["fields"]["component_ownership"]["status"], "observed")
        target.GetAttributes.assert_not_called()
        target.GetModelGeometry.assert_not_called()
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_invalid_identity_rejects_before_bridge_and_native_failure_is_structured(self):
        native = identity_fixtures.ComponentIdentityTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        target = native.fixture()[0]
        native.base.GetElement.side_effect = RuntimeError("unavailable")
        self.attach(native, {"/model-property-probe"})
        request = {"phase": "component_identity", "drawing_file": 101,
                   "model_uuid": target.GetModelElementUUID(), "view_uuid": target.GetElementUUID()}
        async with Client(self.url, timeout=10) as client:
            invalid = await client.call_tool("model_property_probe", {"request": {
                **request, "view_uuid": "00000000-0000-0000-0000-000000000000"}}, raise_on_error=False)
            self.assertTrue(invalid.is_error)
            self.assertFalse(self.bridge_handler.calls)
            failed = await client.call_tool("model_property_probe", {"request": request}, raise_on_error=False)
            self.assertTrue(failed.is_error)
            self.assertIn("probe_scope_unavailable", str(failed.content))
        native.base.GetElement.assert_called_once_with(target)
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_parent_and_child_slabs_have_visible_blockers_without_setters(self):
        native = edit_fixtures.EditOwnershipTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.slab_fixture()
        self.attach(native, {"/model-edit"})
        request = native.request(native_types=["Slab_TypeUUID", "MultiSlab_TypeUUID"], predicate=None,
            changes=[{"target": {"kind": "attribute", "attribute_id": 935}, "value": "new"}])
        async with Client(self.url, timeout=10) as client:
            plan = (await client.call_tool("model_edit", {"request": request})).data
        self.assertFalse(plan["apply_available"])
        self.assertEqual(plan["counts"]["matched"], 2)
        self.assertEqual(len(plan["criteria"]["component_ownership"]), 2)
        self.assertEqual({item["reason"] for item in plan["blocked"]}, {
            "slab_has_parent_requires_explicit_property_owner", "aggregate_slab_requires_explicit_property_owner"})
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
