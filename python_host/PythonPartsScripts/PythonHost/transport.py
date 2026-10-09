"""Dependency-free HTTP lifecycle; the Allplan API stays in UI-dispatched handlers."""
from __future__ import annotations

import json
import logging
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Event, Lock, Thread
from uuid import uuid4


class BridgeError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code, self.status = code, status


def configure_bridge_logging(path):
    """Keep one bounded persistent log per Local folder, including host restarts."""
    logger = logging.getLogger("allplan.bridge")
    try:
        path = Path(path).resolve()
        if not any(getattr(h, "bridge_log_path", None) == path for h in logger.handlers):
            path.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(path, maxBytes=1024 * 1024, backupCount=2, encoding="utf-8")
            handler.bridge_log_path = path
            formatter = logging.Formatter("%(asctime)s.%(msecs)03dZ %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
            formatter.converter = time.gmtime
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    except (OSError, ValueError):
        # A diagnostic file failure must not escape a native UI entry point.
        logger.warning("Persistent bridge log unavailable", exc_info=True)
    return logger


class BridgeServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    block_on_close = False

    def __init__(self, address, handler, dispatch, log_path=None):
        self.handler, self.dispatch = handler, dispatch
        self.session_id = str(uuid4())
        self.logger = configure_bridge_logging(log_path) if log_path is not None else logging.getLogger("allplan.bridge")
        self.active = Event()
        self.active.set()
        self.stopped = Event()
        self._stop_lock = Lock()
        super().__init__(address, WebRequestHandler)
        self.thread = Thread(target=self._serve, name="allplan-http", daemon=True)

    def start(self):
        self.thread.start()
        self.logger.info("host_started host_session_id=%s", self.session_id)

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
            self.logger.info("host_stopped host_session_id=%s", self.session_id)

    def execute(self, path, payload, request_id=None):
        def on_ui():
            # Do not let a Python exception cross Func[Object] into WPF's UI
            # exception handling. Marshal only results or primitive error data;
            # raise the HTTP-facing error after dispatch returns to its worker.
            try:
                if not self.active.is_set():
                    raise BridgeError("session_unavailable", "The host was stopped. Restart StartPythonHost in the current project.", 503)
                return {"result": self.handler.handle(path, payload), "error": None}
            except BridgeError as exc:
                return {"result": None, "error": {"code": exc.code, "message": str(exc), "status": exc.status}}
            except BaseException:
                # SystemExit/KeyboardInterrupt from development code must also
                # stay inside this managed callback. Native fatal faults still
                # require native crash evidence; this is not process isolation.
                return {"result": None, "error": {"code": "host_error", "status": 500,
                        "message": "The Allplan operation failed. Keep this request ID and run Diagnostics."},
                        "traceback": traceback.format_exc()}
        outcome = self.dispatch(on_ui)
        if outcome["error"] is not None:
            error = outcome["error"]
            if outcome.get("traceback"):
                self.logger.error("host_handler_failed request_id=%s path=%s\n%s", request_id, path, outcome["traceback"])
            raise BridgeError(error["code"], error["message"], error["status"])
        return outcome["result"]


class WebRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        self.server.logger.info(format, *args)

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
            self.server.logger.info("request_started request_id=%s path=%s host_session_id=%s", request_id, self.path, self.server.session_id)
            result = self.server.execute(self.path, payload, request_id)
            result = result if result is not None else {"ok": True}
            result = {**result, "request_id": request_id, "host_session_id": self.server.session_id}
            if self.path in {"/get-allplan-version", "/get-runtime-info"}:
                # This marker comes from the loaded transport, not metadata on
                # disk that may have been replaced while old modules are live.
                result["ui_dispatch_exception_boundary"] = "contained_result_error_v1"
            json.dumps(result, allow_nan=False)
        except BridgeError as exc:
            status = exc.status
            result = {"ok": False, "error": {"code": exc.code, "message": str(exc)}, "request_id": request_id}
            self.server.logger.info("request_rejected request_id=%s code=%s status=%s", request_id, exc.code, status)
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
            self.server.logger.info("response_sent request_id=%s status=%s", request_id, status)
        except (OSError, TimeoutError):
            logging.getLogger("allplan.bridge").warning("Response lost request_id=%s; do not retry a write without inspecting the model", request_id)
