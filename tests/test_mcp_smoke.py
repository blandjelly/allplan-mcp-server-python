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
from test_transport import transport


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
        raise transport.BridgeError("unknown_route", "Unknown route", 404)


class MCPSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bridge_handler = FakeBridge()
        self.bridge = transport.BridgeServer(("127.0.0.1", 0), self.bridge_handler, lambda callback: callback())
        self.bridge.start()
        self.addCleanup(self.bridge.stop)
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
            self.assertEqual(names, {"allplan_health", "get_allplan_version", "get_all_object_names", "create_cube", "create_box", "get_model_context"})
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
