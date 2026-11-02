import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from allplan_mcp.allplan_client import AllplanHostClient, AllplanHostError


class ClientErrorTests(unittest.TestCase):
    def setUp(self):
        self.client = AllplanHostClient("http://127.0.0.1:5679")

    def test_connection_refused_and_timeout_have_different_recovery(self):
        for cause, code in ((URLError(ConnectionRefusedError()), "host_absent"),
                            (TimeoutError(), "execution_unknown"),
                            (URLError(TimeoutError()), "execution_unknown")):
            with patch.object(self.client.opener, "open", side_effect=cause) as request:
                with self.assertRaises(AllplanHostError) as error:
                    self.client.post("/create-box", {"length": 1000})
                self.assertEqual(error.exception.code, code)
                self.assertTrue(error.exception.request_id)
                request.assert_called_once()  # Writes are never retried automatically.

    def test_structured_host_failure_keeps_code_and_request_id(self):
        body = json.dumps({"error": {"code": "session_unavailable", "message": "Restart host"}, "request_id": "from-host"}).encode()
        failure = HTTPError(self.client.base_url, 503, "unavailable", {}, io.BytesIO(body))
        with patch.object(self.client.opener, "open", side_effect=failure):
            with self.assertRaises(AllplanHostError) as error:
                self.client.post("/get-all-object-names")
        self.assertEqual(error.exception.code, "session_unavailable")
        self.assertEqual(error.exception.request_id, "from-host")

    def test_health_timeout_identifies_host_read_without_implying_a_write(self):
        for cause in (TimeoutError(), URLError(TimeoutError())):
            with patch.object(self.client.opener, "open", side_effect=cause) as request:
                with self.assertRaises(AllplanHostError) as error:
                    self.client.post("/get-allplan-version")
            self.assertEqual(error.exception.code, "host_timeout")
            self.assertIn("http://127.0.0.1:5679/get-allplan-version", str(error.exception))
            self.assertIn("read-only", str(error.exception))
            self.assertIn("bridge.log", str(error.exception))
            self.assertNotIn("Inspect the model", str(error.exception))
            request.assert_called_once()

    def test_nonfinite_payload_is_rejected_before_http(self):
        with patch.object(self.client.opener, "open") as request:
            with self.assertRaises(AllplanHostError) as error:
                self.client.post("/create-box", {"length": float("nan")})
        self.assertEqual(error.exception.code, "invalid_payload")
        request.assert_not_called()


class _Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class EvidenceCaptureTests(unittest.TestCase):
    def setUp(self):
        self.client = AllplanHostClient("http://127.0.0.1:5679")
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def lines(self):
        files = list(Path(self.folder.name).glob("evidence-*.jsonl"))
        if not files:
            return []
        self.assertEqual(len(files), 1)
        return [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines()]

    def test_disabled_by_default_writes_nothing(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ALLPLAN_MCP_EVIDENCE_DIR", None)
            with patch.object(self.client.opener, "open", return_value=_Reply(b'{"version": "2026"}')):
                self.client.post("/get-allplan-version")
        self.assertEqual(self.lines(), [])

    def test_request_is_recorded_before_send_and_response_after(self):
        seen = []
        def reply(*args, **kwargs):
            seen.append([entry["kind"] for entry in self.lines()])
            return _Reply(b'{"state": "stopped"}')
        with patch.dict(os.environ, {"ALLPLAN_MCP_EVIDENCE_DIR": self.folder.name}):
            with patch.object(self.client.opener, "open", side_effect=reply):
                data = self.client.post("/model-edit", {"action": "apply", "execution_id": "e1"})
        self.assertEqual(seen, [["request"]])
        request, response = self.lines()
        self.assertEqual(request["request"], {"action": "apply", "execution_id": "e1"})
        self.assertEqual(request["bridge_path"], "/model-edit")
        self.assertEqual(response["response"], data)
        self.assertEqual(request["request_id"], response["request_id"])

    def test_lost_reply_keeps_request_and_error_without_retry(self):
        with patch.dict(os.environ, {"ALLPLAN_MCP_EVIDENCE_DIR": self.folder.name}):
            with patch.object(self.client.opener, "open", side_effect=TimeoutError()) as request:
                with self.assertRaises(AllplanHostError):
                    self.client.post("/model-edit", {"action": "apply"})
        request.assert_called_once()
        kinds = [(entry["kind"], entry.get("error", {}).get("code")) for entry in self.lines()]
        self.assertEqual(kinds, [("request", None), ("error", "execution_unknown")])

    def test_capture_failure_never_changes_the_call(self):
        blocker = Path(self.folder.name) / "file"
        blocker.write_text("not a directory")
        with patch.dict(os.environ, {"ALLPLAN_MCP_EVIDENCE_DIR": str(blocker / "sub")}):
            with patch.object(self.client.opener, "open", return_value=_Reply(b'{"ok": true, "v": 1}')):
                self.assertEqual(self.client.post("/get-model-context")["v"], 1)
            with patch.object(self.client.opener, "open") as request:
                with self.assertRaises(AllplanHostError):
                    self.client.post("/create-box", {"length": float("nan")})
            request.assert_not_called()
