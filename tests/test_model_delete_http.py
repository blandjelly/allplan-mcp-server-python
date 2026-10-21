"""Public MCP HTTP contract for the guarded model-object delete workflow."""
import unittest
from uuid import uuid4

from fastmcp import Client

import test_mcp_smoke as smoke
import test_model_edit as fixtures


class ModelDeleteHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    async def test_model_delete_preview_highlight_apply_replay_over_http(self):
        native = fixtures.ModelEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        targets = native.fixture(("",))
        target = targets[0]
        native.base.DrawingFileService.GetActiveFileNumber.return_value = 101

        def delete_elements(doc, adapters):
            self.assertEqual([item.GetModelElementUUID() for item in adapters],
                             [target.GetModelElementUUID()])
            target.IsDeleted.return_value = True
            native.base.ElementsSelectService.SelectAllElements.side_effect = lambda current_doc: [
                item for item in targets if not item.IsDeleted()
            ]

        native.base.DeleteElements.side_effect = delete_elements
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path == "/model-edit":
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle
        request = native.request(predicate=None, native_types=["Column_TypeUUID"],
                                 changes=[{"target": {"kind": "delete"}}])
        async with Client(self.url, timeout=10) as client:
            preview = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(preview["counts"]["changes"], 1)
            highlighted = (await client.call_tool("model_edit", {
                "request": preview["next_action"]["request"]})).data
            execution_id = uuid4().hex
            apply_request = {**highlighted["next_action"]["request"], "execution_id": execution_id}
            applied = (await client.call_tool("model_edit", {"request": {
                **apply_request}})).data
            self.assertEqual(applied["state"], "completed", applied)
            self.assertTrue(applied["audited_fields_match_plan"])
            self.assertEqual(target.IsDeleted.return_value, True)
            replay = (await client.call_tool("model_edit", {"request": apply_request})).data
            self.assertTrue(replay["replayed"])
            self.assertEqual(native.base.DeleteElements.call_count, 1)
