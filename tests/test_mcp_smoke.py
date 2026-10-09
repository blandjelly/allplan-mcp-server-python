"""Real Streamable HTTP transport with a fake bridge; no Allplan claims."""
import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fastmcp import Client
from allplan_mcp.diagnostics import collect_diagnostics
from test_transport import stop_test_server, transport


class FakeBridge:
    def __init__(self):
        self.calls = []
    def handle(self, path, payload):
        self.calls.append((path, payload))
        if path == "/get-allplan-version":
            return {"version": "2026.fake", "embedded_python": {"version": "fake"},
                    "compatibility": {"major_matches": True, "runtime_verified": False}}
        if path == "/get-all-object-names":
            return {"names": ["Fake column"]}
        if path == "/get-model-context":
            return {"schema_version": "m1-context-probe-1", "read_only": True,
                    "identity_sample": {"requested": payload["identity_sample_size"], "items": []}}
        if path == "/create-box":
            return {"ok": True}
        if path == "/model-query":
            return {"schema_version": "m1-query-1", "read_only": True, "request": payload,
                    "selection_id": "a" * 32, "source_fingerprint": "fake-only"}
        raise transport.BridgeError("unknown_route", "Unknown route", 404)


class MCPSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_final_batch_transports_geometry_profile_and_saves_summaries(self):
        from allplan_mcp.demo_profile import load_demo_profile
        request = {"action": "query", "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
                   "component_kind": "top_level_component", "coordinate_frame": "model_local", "profile_id": "native-model-qa-demo",
                   "fields": ["mark", "bounding_box_mm", "size_z_mm"],
                   "spatial_box": {"min": [-201,-201,-1], "max": [201,201,3001], "relation": "contained", "boundary": "exclusive", "frame": "model_local"}}
        requests = [{"action": "profile", "profile_id": "native-model-qa-demo"}, request]
        report = await collect_diagnostics(self.host_url, self.url, query_batch=requests)
        records = report["mcp"]["model_query_batch"]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["response"]["request"]["profile"], load_demo_profile())
        self.assertNotIn("profile_id", records[1]["response"]["request"])
        self.assertEqual(records[1]["summary"]["request"]["action"], "summary")
        self.assertEqual(len(records[1]["pages"]),1)
        self.assertNotIn("error", records[1])
        json.dumps(report, allow_nan=False)
        before = len(self.bridge_handler.calls)
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, query_batch=[request, {"action": "create_box"}])
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, query_batch=[{**request, "spatial_box": {
                **request["spatial_box"], "max": [float("inf"),1,1]}}])
        self.assertEqual(len(self.bridge_handler.calls), before)
        async with Client(self.url, timeout=5) as client:
            resource = await client.read_resource("allplan://profiles/native-model-qa-demo")
            self.assertEqual(json.loads(resource[0].text), load_demo_profile())
        self.assertFalse(any(route == "/create-box" for route, _ in self.bridge_handler.calls))

    async def test_diagnostic_repeated_cursor_is_bounded_and_preserves_partial_evidence(self):
        original = self.bridge_handler.handle
        def repeat_cursor(path, payload):
            response = original(path, payload)
            if path == "/model-query" and payload["action"] in {"query", "page"}:
                response["page"] = {"next_cursor": "b" * 32}
            return response
        self.bridge_handler.handle = repeat_cursor
        request = {"action": "query", "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"}}
        report = await collect_diagnostics(self.host_url, self.url, query_batch=[request])
        record = report["mcp"]["model_query_batch"][0]
        self.assertIn("cursor budget", record["error"]["message"])
        self.assertIn("response", record)
        self.assertEqual(len(record["pages"]), 2)
        pages = [payload for path, payload in self.bridge_handler.calls if path == "/model-query" and payload["action"] == "page"]
        self.assertEqual(len(pages),1)

    async def test_metadata_inspect_diagnostics_capture_and_invalid_request_no_native_call(self):
        request = {"action": "inspect", "scope": {"drawing_files": [1, 2], "include_passive": True, "visibility": "api_select_all"},
                   "attribute_ids": [498], "sample_limit": 10}
        report = await collect_diagnostics(self.host_url, self.url, request)
        self.assertEqual(report["model_query_request"], request)
        self.assertEqual(report["mcp"]["model_query"]["request"], {"schema_version": "m1-query-1", **request})
        self.assertTrue(report["mcp"]["model_query"]["request_id"])
        self.assertEqual(report["allplan_acceptance"], "not_run")
        before = len(self.bridge_handler.calls)
        with self.assertRaises(ValueError):
            await collect_diagnostics(self.host_url, self.url, {**request, "sample_limit": 21})
        self.assertEqual(len(self.bridge_handler.calls), before)
        async with Client(self.url, timeout=5) as client:
            bad = await client.call_tool("model_query", {"request": {**request, "attribute_ids": [True]}}, raise_on_error=False)
            self.assertTrue(bad.is_error)
        self.assertFalse(any(route == "/create-box" for route, _ in self.bridge_handler.calls))

    async def asyncSetUp(self):
        self.bridge_handler = FakeBridge()
        self.bridge = transport.BridgeServer(("127.0.0.1", 0), self.bridge_handler, lambda callback: callback())
        self.bridge.start()
        self.addCleanup(stop_test_server, self, self.bridge)
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        self.url = f"http://127.0.0.1:{port}/mcp"
        self.host_url = f"http://127.0.0.1:{self.bridge.server_port}"
        environment = os.environ.copy()
        environment.update({"MCP_HOST": "127.0.0.1", "MCP_PORT": str(port),
                            "MCP_PATH": "/mcp", "ALLPLAN_HOST_URL": self.host_url,
                            "ALLPLAN_MCP_ENABLE_PYTHON_EXEC": "0", "NO_PROXY": "127.0.0.1,localhost"})
        self.output = tempfile.TemporaryFile(mode="w+")
        self.addCleanup(self.output.close)
        self.process = subprocess.Popen([sys.executable, "-m", "allplan_mcp.server"],
                                        env=environment, stdout=self.output, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop_process)
        deadline = asyncio.get_running_loop().time() + 15
        while asyncio.get_running_loop().time() < deadline:
            if self.process.poll() is not None:
                self.output.seek(0)
                self.fail(f"MCP server exited: {self.output.read()}")
            try:
                async with Client(self.url, timeout=1):
                    return
            except Exception:
                await asyncio.sleep(0.1)
        self.fail("MCP server startup timed out")

    def stop_process(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    async def test_discovery_health_version_names_box_and_diagnostic_bundle(self):
        async with Client(self.url, timeout=5) as client:
            names = {t.name for t in await client.list_tools()}
            self.assertEqual(names, {"allplan_health", "get_allplan_version", "get_all_object_names", "create_cube", "create_box", "get_model_context", "model_query"})
            resources = await client.list_resources()
            self.assertIn("allplan://skills", {str(r.uri) for r in resources})
            health = (await client.call_tool("allplan_health")).data
            self.assertTrue(health["ok"])
            self.assertEqual(health["allplan_version"], "2026.fake")
            self.assertTrue(health["request_id"])
            self.assertEqual((await client.call_tool("get_allplan_version")).data, "2026.fake")
            self.assertEqual((await client.call_tool("get_all_object_names")).data, ["Fake column"])
            context = (await client.call_tool("get_model_context", {"identity_sample_size": 2})).data
            self.assertTrue(context["read_only"])
            self.assertEqual(context["identity_sample"]["requested"], 2)
            invalid = await client.call_tool("get_model_context", {"identity_sample_size": 21}, raise_on_error=False)
            self.assertTrue(invalid.is_error)
            box = (await client.call_tool("create_box", {"length": 1000, "width": 1000, "height": 1000})).data
            self.assertTrue(box["submitted"])
            self.assertFalse(box["readback_verified"])
        boxes = [p for route, p in self.bridge_handler.calls if route == "/create-box"]
        self.assertEqual(boxes, [{"length": 1000, "width": 1000, "height": 1000}])
        report = await collect_diagnostics(self.host_url, self.url)
        self.assertTrue(report["mcp"]["ok"])
        self.assertEqual(report["allplan_acceptance"], "not_run")
        self.assertEqual(report["mcp"]["get_allplan_version"], "2026.fake")
        self.assertEqual(report["mcp"]["get_model_context"]["identity_sample"]["requested"], 10)
        json.dumps(report)
        self.assertEqual(len([p for route, p in self.bridge_handler.calls if route == "/create-box"]), 1)
        self.bridge.stop()
        self.assertTrue(self.bridge.stopped.wait(2))
        async with Client(self.url, timeout=5) as client:
            result = await client.call_tool("allplan_health", raise_on_error=False)
            self.assertTrue(result.is_error)
            self.assertIn("host_absent", str(result.content))

    async def test_model_query_schema_transport_predicates_pages_and_summary(self):
        query = {"action": "query", "scope": {"drawing_files": [101, 102], "include_passive": True, "visibility": "api_select_all"},
                 "predicate": {"all": [{"field": "type_name", "op": "eq", "value": "Column_TypeUUID"},
                                       {"not": {"field": "attribute:83", "op": "eq", "value": None}}]},
                 "attribute_ids": [83], "page_size": 1}
        async with Client(self.url, timeout=5) as client:
            tool = next(t for t in await client.list_tools() if t.name == "model_query")
            self.assertIn("request", tool.inputSchema["properties"])
            result = (await client.call_tool("model_query", {"request": query})).data
            self.assertTrue(result["read_only"])
            self.assertEqual(result["request"], {"schema_version": "m1-query-1", **query})
            for action in ("page", "summary"):
                follow = {"action": action, "selection_id": result["selection_id"]}
                response = (await client.call_tool("model_query", {"request": follow})).data
                self.assertEqual(response["request"], {"schema_version": "m1-query-1", **follow})
            null_cursor = {"action": "page", "selection_id": result["selection_id"], "cursor": None}
            response = (await client.call_tool("model_query", {"request": null_cursor})).data
            self.assertNotIn("cursor", response["request"])
            before = len(self.bridge_handler.calls)
            for bad in ({"action": "query", "scope": {"drawing_files": [-101], "include_passive": False, "visibility": "api_select_all"}},
                        {"action": "query", "scope": query["scope"], "page_size": True},
                        {"action": "summary", "selection_id": "a" * 32, "scope": query["scope"]}):
                result = await client.call_tool("model_query", {"request": bad}, raise_on_error=False)
                self.assertTrue(result.is_error)
            self.assertEqual(len(self.bridge_handler.calls), before)
        self.assertFalse(any(path == "/create-box" for path, _ in self.bridge_handler.calls))
