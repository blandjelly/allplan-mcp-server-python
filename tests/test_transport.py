import importlib.util
import json
import logging
import queue
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("transport", ROOT / "python_host/PythonPartsScripts/PythonHost/transport.py")
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)


def stop_test_server(test_case, server):
    # stop() is deliberately nonblocking on Allplan's UI thread. Test teardown
    # must also let the accept thread finish before interpreter shutdown.
    server.stop()
    server.thread.join(2)
    test_case.assertFalse(server.thread.is_alive(), "Bridge accept thread did not stop")


class Handler:
    def __init__(self):
        self.calls = []
    def handle(self, path, payload):
        self.calls.append((path, payload))
        return {"version": "fake-2026"}


class TransportTests(unittest.TestCase):
    def request(self, server, data=b"{}"):
        request = Request(f"http://127.0.0.1:{server.server_port}/get-allplan-version", data=data,
                          headers={"Content-Type": "application/json", "X-Request-ID": "test-id"})
        return build_opener(ProxyHandler({})).open(request, timeout=2)

    def server(self, handler=None, dispatch=lambda callback: callback(), log_path=None):
        server = transport.BridgeServer(("127.0.0.1", 0), handler or Handler(), dispatch, log_path=log_path)
        server.start()
        self.addCleanup(stop_test_server, self, server)
        return server

    def test_typed_errors_stay_inside_managed_callback_and_preserve_http_status(self):
        class RejectingHandler(Handler):
            def handle(self, path, payload):
                if payload.get("reject"):
                    raise transport.BridgeError("invalid_payload", "Scope exceeds profile.", 400)
                return super().handle(path, payload)
        escaped = []
        def managed_dispatch(callback):
            try:
                outcome = callback()
            except BaseException as exc:
                escaped.append(type(exc).__name__)
                raise RuntimeError("Unhandled managed UI delegate exception") from exc
            # No exception or traceback objects cross the callback boundary.
            json.dumps(outcome, allow_nan=False)
            return outcome
        server = self.server(RejectingHandler(), managed_dispatch)
        with self.assertRaises(HTTPError) as error:
            self.request(server, b'{"reject":true}')
        self.assertEqual(error.exception.code, 400)
        body = json.loads(error.exception.read())
        self.assertEqual(body["error"], {"code": "invalid_payload", "message": "Scope exceeds profile."})
        self.assertEqual(body["request_id"], "test-id")
        self.assertEqual(escaped, [])
        with self.request(server) as response:
            self.assertEqual(response.status, 200)

    def test_unexpected_and_exit_errors_are_marshaled_logged_and_do_not_escape_ui(self):
        class FailingHandler(Handler):
            def handle(self, path, payload):
                if payload.get("fail") == "exit":
                    raise SystemExit("fake exit")
                if payload.get("fail"):
                    raise RuntimeError("fake native failure")
                return super().handle(path, payload)
        escaped = []
        def managed_dispatch(callback):
            try:
                result = callback()
            except BaseException:
                escaped.append(True)
                raise
            json.dumps(result)
            return result
        server = self.server(FailingHandler(), managed_dispatch)
        for failure in ("runtime", "exit"):
            with self.assertLogs("allplan.bridge", level="ERROR") as logs:
                with self.assertRaises(HTTPError) as error:
                    self.request(server, json.dumps({"fail": failure}).encode())
                self.assertEqual(error.exception.code, 500)
                body = json.loads(error.exception.read())
            self.assertEqual(body["error"]["code"], "host_error")
            self.assertNotIn("traceback", body)
            self.assertNotIn("fake", body["error"]["message"])
            self.assertIn("request_id=test-id", "\n".join(logs.output))
        self.assertEqual(escaped, [])
        with self.request(server) as response:
            self.assertEqual(response.status, 200)

    def test_persistent_log_is_bounded_shared_and_failure_to_open_does_not_prevent_service(self):
        logger = logging.getLogger("allplan.bridge")
        original_handlers, level = set(logger.handlers), logger.level
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "logs/bridge.log"
            try:
                first = transport.configure_bridge_logging(path)
                second = transport.configure_bridge_logging(path)
                handlers = [h for h in first.handlers if getattr(h, "bridge_log_path", None) == path.resolve()]
                self.assertIs(first, second)
                self.assertEqual(len(handlers), 1)
                self.assertEqual(handlers[0].maxBytes, 1024 * 1024)
                self.assertEqual(handlers[0].backupCount, 2)
                first.info("request_started request_id=persistent-test path=/model-audit")
                self.assertIn("request_id=persistent-test", path.read_text(encoding="utf-8"))
                blocker = Path(directory) / "file"
                blocker.write_text("not a directory")
                with self.assertLogs("allplan.bridge", level="WARNING"):
                    transport.configure_bridge_logging(blocker / "bridge.log")
            finally:
                for handler in list(logger.handlers):
                    if handler not in original_handlers:
                        logger.removeHandler(handler)
                        handler.close()
                logger.setLevel(level)

    def test_http_dispatch_and_request_id(self):
        pending = queue.Queue()
        ran_on = []
        def dispatch(callback):
            done = threading.Event()
            output = []
            pending.put((callback, done, output))
            done.wait(2)
            return output[0]
        server = self.server(dispatch=dispatch)
        response = []
        worker = threading.Thread(target=lambda: response.append(self.request(server).read()))
        worker.start()
        callback, done, output = pending.get(timeout=2)
        ran_on.append(threading.get_ident())
        output.append(callback())
        done.set()
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(ran_on, [threading.get_ident()])
        self.assertEqual(json.loads(response[0])["request_id"], "test-id")
        self.assertEqual(server.handler.calls, [("/get-allplan-version", {})])

    def test_invalid_json_and_nonobject_never_reach_dispatch(self):
        server = self.server()
        for data in (b"not-json", b"[]", b"null"):
            with self.assertRaises(HTTPError) as error:
                self.request(server, data)
            self.assertEqual(error.exception.code, 400)
            body = json.loads(error.exception.read())
            self.assertEqual(body["error"]["code"], "invalid_payload")
        self.assertEqual(server.handler.calls, [])

    def test_cancel_does_not_wait_for_ui_and_rejects_queued_request(self):
        pending = queue.Queue()
        def dispatch(callback):
            done, outcome = threading.Event(), []
            pending.put((callback, done, outcome))
            if not done.wait(2):
                raise RuntimeError("dispatcher did not resume")
            if isinstance(outcome[0], Exception):
                raise outcome[0]
            return outcome[0]
        handler = Handler()
        server = self.server(handler, dispatch)
        errors = []
        def request():
            try:
                self.request(server)
            except HTTPError as exc:
                errors.append(json.loads(exc.read()))
        worker = threading.Thread(target=request)
        worker.start()
        callback, done, outcome = pending.get(timeout=2)
        started = time.monotonic()
        server.stop()
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertTrue(server.stopped.wait(2))
        # UI resumes after cancellation: the old operation must not execute.
        try:
            outcome.append(callback())
        except Exception as exc:
            outcome.append(exc)
        done.set()
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(handler.calls, [])
        self.assertEqual(errors[0]["error"]["code"], "session_unavailable")
        restarted = transport.BridgeServer(server.server_address, Handler(), lambda f: f())
        restarted.start()
        self.addCleanup(stop_test_server, self, restarted)
        with self.request(restarted) as response:
            self.assertEqual(response.status, 200)
        restarted.stop()
        restarted.stop()
        self.assertTrue(restarted.stopped.wait(2))
