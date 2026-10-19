"""Recover a lost Beam write and continue through the real MCP HTTP contract."""
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from fastmcp import Client

import test_mcp_smoke as smoke
import test_model_edit as fixtures


class BeamRecoveryHTTPTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = smoke.MCPSmokeTests.asyncSetUp
    stop_process = smoke.MCPSmokeTests.stop_process

    async def test_recover_exact_beam_targets_then_finish_attributes_and_layer(self):
        native = fixtures.ModelEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        beams = native.fixture(("", ""))
        native.attribute_catalog({935: "Klasa odporności ogniowej",
                                  20001: "Nazwa przekroju", 20002: "Długość"})
        native.attribute_type_names.update({20001: "String", 20002: "Double"})
        for beam in beams:
            beam.GetElementAdapterType.return_value.GetTypeName.return_value = "Beam_TypeUUID"
            beam.GetAttributes.return_value = [(935, ""), (20001, "300X500"), (20002, 6.0)]
        native.setter_fakes(beams)
        setter = native.base.ElementsAttributeService.ChangeAttributes.side_effect
        first = [True]

        def lose_first_reply(attributes, targets, *flags):
            setter(attributes, targets, *flags)
            if first[0]:
                first[0] = False
                raise RuntimeError("lost response after the first Beam setter")

        native.base.ElementsAttributeService.ChangeAttributes.side_effect = lose_first_reply
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
        request = native.request(native_types=["Beam_TypeUUID"], predicate=None, changes=[
            {"target": {"kind": "attribute", "name": "Nazwa przekroju"}, "value": "450X450"},
            {"target": {"kind": "attribute", "name": "Długość"}, "value": 5.0}])

        async with Client(self.url, timeout=10) as client:
            async def apply_preview(preview):
                highlighted = (await client.call_tool("model_edit", {
                    "request": preview["next_action"]["request"]})).data
                return (await client.call_tool("model_edit", {"request": {
                    **highlighted["next_action"]["request"], "execution_id": uuid4().hex}})).data

            preview = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(preview["counts"]["changes"], 4)
            stopped = await apply_preview(preview)
            self.assertEqual(stopped["outcomes"][0]["state"], "unknown")
            self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

            # Recovery must observe the journal's exact targets even if a new
            # global criterion scan cannot be completed. No setter is repeated.
            with patch.object(native.handler.repair_plans, "source_observation",
                              side_effect=RuntimeError("unrelated criterion scan is unavailable")):
                recovered = (await client.call_tool("model_edit", {"request": {
                    "action": "recover", "execution_id": stopped["execution_id"]}})).data
            self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
            self.assertTrue(recovered["read_only"])
            self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

            remaining = (await client.call_tool("model_edit", {"request": request})).data
            self.assertEqual(remaining["counts"]["changes"], 3)
            completed = await apply_preview(remaining)
            self.assertEqual(completed["state"], "completed")
            self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_count, 4)
            for beam in beams:
                values = dict(beam.GetAttributes.return_value)
                self.assertEqual((values[20001], values[20002]), ("450X450", 5.0))

            layer_request = {**request, "predicate": None,
                "exclude_model_uuids": [beams[1].GetModelElementUUID.return_value],
                "changes": [{"target": {"kind": "layer", "short_name": "W1"}}]}
            layer_plan = (await client.call_tool("model_edit", {"request": layer_request})).data
            layer_result = await apply_preview(layer_plan)
            self.assertEqual(layer_result["state"], "completed")
            native.base.ElementsLayerService.ChangeLayer.assert_called_once()

    async def test_full_polish_layer_name_catalog_then_confirmed_short_name_apply(self):
        native = fixtures.ModelEditTests()
        native.setUp()
        self.addCleanup(native.doCleanups)
        elements = native.fixture(("",))
        native.handler.property_probes.trace_path = Path(native.directory.name) / "layers.jsonl"
        names = {7: ("COL", "COL (Słupy)"), 8: ("SZ_OGÓ03", "SZ_OGÓ03 (Ogólne03)")}
        native.base.LayerService.GetNameByID.side_effect = lambda ident, doc: names[ident][1]
        native.base.LayerService.GetShortNameByID.side_effect = lambda ident, doc: names[ident][0]
        native.base.LayerService.GetIDByShortName.side_effect = lambda name, doc: next(
            (ident for ident, pair in names.items() if pair[0] == name), -1)
        del native.base.LayerService.GetIDByName

        def change_layer(targets, short_name):
            self.assertEqual(short_name, "SZ_OGÓ03")
            targets[0].GetCommonProperties.return_value.Layer = 8

        native.base.ElementsLayerService.ChangeLayer.side_effect = change_layer
        native.base.DrawingFileService.GetActiveFileNumber.return_value = 101
        original = self.bridge_handler.handle

        def handle(path, payload):
            if path in {"/model-edit", "/model-property-probe"}:
                self.bridge_handler.calls.append((path, payload))
                try:
                    return native.handler.handle(path, payload)
                except native.module.BridgeError as exc:
                    raise smoke.transport.BridgeError(exc.code, str(exc), exc.status) from exc
            return original(path, payload)

        self.bridge_handler.handle = handle
        async with Client(self.url, timeout=10) as client:
            lookup = (await client.call_tool("model_property_probe", {"request": {
                "phase": "layer_name", "layer_name": "ogólne03"}})).data
            self.assertEqual(lookup["next_action"]["request"]["phase"], "layer_catalog")
            page_request = {**lookup["next_action"]["request"], "limit": 32}
            page = (await client.call_tool("model_property_probe", {"request": page_request})).data
            self.assertEqual(page["next_action"]["action"], "ask_user_confirmation")
            candidate = page["next_action"]["candidates"][0]
            self.assertEqual((candidate["short_name"], candidate["long_name"]), ("SZ_OGÓ03", "Ogólne03"))
            native.base.ElementsLayerService.ChangeLayer.assert_not_called()
            # This simulates the user's explicit choice of the displayed pair.
            preview = (await client.call_tool("model_edit", {"request": native.request(
                predicate=None, changes=[{"target": {"kind": "layer", "short_name": candidate["short_name"]}}])})).data
            highlighted = (await client.call_tool("model_edit", {
                "request": preview["next_action"]["request"]})).data
            applied = (await client.call_tool("model_edit", {"request": {
                **highlighted["next_action"]["request"], "execution_id": uuid4().hex}})).data
            self.assertEqual(applied["state"], "completed")
            self.assertEqual(elements[0].GetCommonProperties.return_value.Layer, 8)
            native.base.ElementsLayerService.ChangeLayer.assert_called_once()
