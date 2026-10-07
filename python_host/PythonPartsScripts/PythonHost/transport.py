"""Dependency-free HTTP lifecycle; the Allplan API stays in UI-dispatched handlers."""
from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Lock, Thread
from uuid import uuid4


class BridgeError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code, self.status = code, status


class BridgeServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    block_on_close = False

    def __init__(self, address, handler, dispatch):
        self.handler, self.dispatch = handler, dispatch
        self.session_id = str(uuid4())
        self.active = Event()
        self.active.set()
        self.stopped = Event()
        self._stop_lock = Lock()
        super().__init__(address, WebRequestHandler)
        self.thread = Thread(target=self._serve, name="allplan-http", daemon=True)

    def start(self):
        self.thread.start()

    def _serve(self):
        try:
            self.serve_forever(poll_interval=0.05)
        finally:
            self.stopped.set()

    def stop(self):
        """Release the listener now; never join a dispatcher-dependent worker on UI."""
        with self._stop_lock:
            if not self.active.is_set():
                return
            self.active.clear()
            self.server_close()
            # shutdown() waits for the accept loop, so it must not run on UI.
            Thread(target=self.shutdown, name="allplan-http-stop", daemon=True).start()

    def execute(self, path, payload):
        def on_ui():
            # A queued request must not use the previous document after cancellation.
            if not self.active.is_set():
                raise BridgeError("session_unavailable", "The host was stopped. Restart StartPythonHost in the current project.", 503)
            return self.handler.handle(path, payload)
        return self.dispatch(on_ui)


class WebRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.getLogger("allplan.bridge").info(format, *args)

    def do_POST(self):
        request_id = self.headers.get("X-Request-ID") or str(uuid4())
        # Only bounded printable IDs are written to diagnostic output.
        if len(request_id) > 128 or any(not c.isalnum() and c not in "-_." for c in request_id):
            request_id = str(uuid4())
        status = 200
        try:
            self.connection.settimeout(10)
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise BridgeError("invalid_payload", "Content-Length must be an integer.")
            if length < 0 or length > 1024 * 1024:
                raise BridgeError("invalid_payload", "Request body must be at most 1 MiB.")
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
            except (ValueError, UnicodeError):
                raise BridgeError("invalid_payload", "Request body must be valid JSON.")
            if not isinstance(payload, dict):
                raise BridgeError("invalid_payload", "Request body must be a JSON object.")
            result = self.server.execute(self.path, payload)
            result = result if result is not None else {"ok": True}
            result = {**result, "request_id": request_id, "host_session_id": self.server.session_id}
            json.dumps(result, allow_nan=False)
        except BridgeError as exc:
            status = exc.status
            result = {"ok": False, "error": {"code": exc.code, "message": str(exc)}, "request_id": request_id}
        except Exception:
            status = 500
            logging.getLogger("allplan.bridge").exception("Host failure request_id=%s", request_id)
            result = {"ok": False, "error": {"code": "host_error", "message": "The Allplan operation failed. Keep this request ID and run Diagnostics."}, "request_id": request_id}
        result["host_session_id"] = self.server.session_id
        data = json.dumps(result, allow_nan=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Request-ID", request_id)
            self.end_headers()
            self.wfile.write(data)
        except (OSError, TimeoutError):
            logging.getLogger("allplan.bridge").warning("Response lost request_id=%s; do not retry a write without inspecting the model", request_id)
