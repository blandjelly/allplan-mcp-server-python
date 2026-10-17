"""Dependency-free HTTP lifecycle; the Allplan API stays in UI-dispatched handlers."""
from __future__ import annotations

import json
import logging
import time
import traceback
from concurrent.futures import CancelledError, Future, TimeoutError as FutureTimeout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging.handlers import RotatingFileHandler
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread
from uuid import uuid4


class BridgeError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code, self.status = code, status


class UIRequestDispatcher:
    """Workers wait in Python; only the existing Allplan UI timer runs callbacks.

    A request that has not started within the budget is cancelled atomically.
    Running native work is never cancelled or retried by this dispatcher.
    """
    def __init__(self, start_timeout=3.0):
        self.start_timeout = start_timeout
        self.pending = Queue(maxsize=32)
        self._lock = Lock()
        self._closed = False
        self._processing = False

    @staticmethod
    def unavailable():
        return BridgeError("ui_dispatch_unavailable",
                           "Allplan UI did not start the request; no operation was executed. "
                           "Close modal dialogs, restore Allplan and restart StartPythonHost. "
                           "Collect Local/.allplan-mcp/logs/bridge.log if this persists.", 503)

    def __call__(self, callback):
        future = Future()
        with self._lock:
            if self._closed:
                raise BridgeError("session_unavailable", "Restart StartPythonHost in the current project.", 503)
            try:
                self.pending.put_nowait((future, time.monotonic() + self.start_timeout, callback))
            except Full:
                raise self.unavailable()
        try:
            return future.result(timeout=self.start_timeout)
        except FutureTimeout:
            if future.cancel():
                raise self.unavailable()
            # The UI has already claimed this request. Preserve its result/error;
            # a client-side lost reply still means execution_unknown for writes.
            return future.result()
        except CancelledError:
            raise self.unavailable()

    def process_pending(self):
        """Run at most one live callback per UI tick; never raise into WPF."""
        if self._processing:
            return  # Native code may pump a nested UI message loop.
        while True:
            try:
                future, deadline, callback = self.pending.get_nowait()
            except Empty:
                return
            if time.monotonic() >= deadline:
                future.cancel()
            if not future.set_running_or_notify_cancel():
                continue
            self._processing = True
            try:
                future.set_result(callback())
            except BaseException as exc:
                future.set_exception(exc)
            finally:
                self._processing = False
            return

    def close(self):
        with self._lock:
            self._closed = True
            while True:
                try:
                    future, _, _ = self.pending.get_nowait()
                except Empty:
                    return
                if future.set_running_or_notify_cancel():
                    future.set_exception(BridgeError("session_unavailable", "The host was stopped. Restart StartPythonHost.", 503))


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
        self.logger.info("host_started host_session_id=%s ui_dispatch_mode=%s", self.session_id,
                         "timer_queue_v1" if isinstance(self.dispatch, UIRequestDispatcher) else "custom")

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
        queued_at = time.monotonic()
        self.logger.info("ui_dispatch_queued request_id=%s path=%s", request_id, path)
        def on_ui():
            # Do not let a Python exception cross Func[Object] into WPF's UI
            # exception handling. Marshal only results or primitive error data;
            # raise the HTTP-facing error after dispatch returns to its worker.
            try:
                if not self.active.is_set():
                    raise BridgeError("session_unavailable", "The host was stopped. Restart StartPythonHost in the current project.", 503)
                self.logger.info("ui_dispatch_started request_id=%s path=%s wait_ms=%.1f", request_id, path,
                                 (time.monotonic() - queued_at) * 1000)
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
            finally:
                self.logger.info("ui_dispatch_finished request_id=%s path=%s elapsed_ms=%.1f", request_id, path,
                                 (time.monotonic() - queued_at) * 1000)
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
                result["ui_dispatch_mode"] = "timer_queue_v1" if isinstance(self.server.dispatch, UIRequestDispatcher) else "custom"
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
        send_started = time.monotonic()
        self.server.logger.info("response_started request_id=%s status=%s bytes=%s", request_id, status, len(data))
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Request-ID", request_id)
            self.end_headers()
            self.wfile.write(data)
            self.server.logger.info("response_sent request_id=%s status=%s send_ms=%.1f", request_id, status,
                                    (time.monotonic() - send_started) * 1000)
        except (OSError, TimeoutError) as exc:
            logging.getLogger("allplan.bridge").warning(
                "Response lost request_id=%s path=%s send_ms=%.1f error=%s; do not retry a write without inspecting the model",
                request_id, self.path, (time.monotonic() - send_started) * 1000, type(exc).__name__)
