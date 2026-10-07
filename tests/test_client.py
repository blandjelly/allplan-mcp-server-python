import io
import json
import unittest
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

    def test_nonfinite_payload_is_rejected_before_http(self):
        with patch.object(self.client.opener, "open") as request:
            with self.assertRaises(AllplanHostError) as error:
                self.client.post("/create-box", {"length": float("nan")})
        self.assertEqual(error.exception.code, "invalid_payload")
        request.assert_not_called()
