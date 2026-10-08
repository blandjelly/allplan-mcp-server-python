import importlib.util
import json
import queue
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

    def server(self, handler=None, dispatch=lambda callback: callback()):
        server = transport.BridgeServer(("127.0.0.1", 0), handler or Handler(), dispatch)
        server.start()
        self.addCleanup(stop_test_server, self, server)
        return server

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
