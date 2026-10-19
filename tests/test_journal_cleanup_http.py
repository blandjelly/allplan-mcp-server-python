"""User-confirmed maintenance through MCP/HTTP, then normal guarded model edits."""
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from fastmcp import Client
import test_mcp_smoke as smoke
import test_model_edit as fixtures


class JournalCleanupHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    def native_fixture(self):
        native = fixtures.ModelEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        native.fixture(("",))
        native.attribute_catalog({935: "Klasa odporności ogniowej"})
        native.setter_fakes(native.base.ElementsSelectService.SelectAllElements.return_value)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        plans = native.handler.repair_plans
        plans.executor.path = Path(temporary.name) / "repairs"
        plans.trace_path = Path(temporary.name) / "m4-native-probe.jsonl"
        # These are workflow tests; production clock expiry has dedicated tests.
        plans.queries.clock = lambda: 0.0
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path in {"/model-edit", "/fix-model-issues"}:
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle
        return native

    async def test_full_trace_prompts_then_confirmed_rotation_restores_preview(self):
        native = self.native_fixture()
        path = native.handler.repair_plans.trace_path
        original = b"x" * (1024 * 1024)
        path.write_bytes(original)
        request = native.request(changes=[{"target": {"kind": "attribute", "attribute_id": 935},
                                          "value": "F90"}])
        async with Client(self.url, timeout=10) as client:
            blocked = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(blocked["state"], "journal_maintenance_required")
            self.assertTrue(blocked["user_confirmation_required"])
            hint = blocked["next_action"]
            self.assertEqual(hint["request"]["target"], "native_trace")
            preview = (await client.call_tool(hint["tool"], {"request": hint["request"]})).data
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(preview["state"], "confirmation_required")
            confirm = preview["after_user_confirmation"]
            missing = {key: value for key, value in confirm.items() if key != "acknowledgement"}
            invalid = await client.call_tool("fix_model_issues", {"request": missing}, raise_on_error=False)
            self.assertTrue(invalid.is_error)
            self.assertEqual(path.read_bytes(), original)
            # Journal maintenance runs without the active document or native SDK.
            reader = native.coord.GetInputViewDocument.side_effect
            native.coord.GetInputViewDocument.side_effect = AssertionError("cleanup cannot access model")
            archived = (await client.call_tool("fix_model_issues", {"request": confirm})).data
            native.coord.GetInputViewDocument.side_effect = reader
            self.assertEqual(archived["state"], "archived")
            self.assertFalse(archived["model_data_changed"])
            self.assertEqual((path.parent / "m4-native-probe-archive" / archived["archive"]).read_bytes(), original)
            fresh = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(fresh["state"], "preview_ready")
            native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    async def test_full_execution_journal_archives_and_replays_without_setters(self):
        native = self.native_fixture()
        executor = native.handler.repair_plans.executor
        request = native.request(changes=[{"target": {"kind": "attribute", "attribute_id": 935},
                                          "value": "F90"}])
        async with Client(self.url, timeout=10) as client:
            plan = (await client.call_tool("model_edit", {"request": request})).data
            shown = (await client.call_tool("model_edit", {"request": plan["next_action"]["request"]})).data
            apply = {**shown["next_action"]["request"], "execution_id": uuid4().hex}
            done = (await client.call_tool("model_edit", {"request": apply})).data
            self.assertEqual(done["state"], "completed")
            native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
            executor.MAX_RECORDS = 1
            full = (await client.call_tool("model_edit", {"request": {**apply, "execution_id": uuid4().hex}})).data
            self.assertEqual(full["next_action"]["request"]["target"], "repair_records")
            preview = (await client.call_tool("fix_model_issues", {"request": full["next_action"]["request"]})).data
            self.assertEqual(preview["eligible_count"], 1)
            cleanup = (await client.call_tool("fix_model_issues", {"request": preview["after_user_confirmation"]})).data
            self.assertEqual(cleanup["archived_count"], 1)
            replayed = (await client.call_tool("model_edit", {"request": apply})).data
            self.assertTrue(replayed["replayed"])
            self.assertTrue(replayed["archived"])
            self.assertEqual(replayed["outcomes"], done["outcomes"])
            native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
            inspected = (await client.call_tool("fix_model_issues", {"request": {"action": "inspect_journal"}})).data
            self.assertEqual(inspected["remaining_slots"], 1)


if __name__ == "__main__":
    unittest.main()
