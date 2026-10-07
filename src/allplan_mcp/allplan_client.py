from __future__ import annotations

import json
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4


class AllplanHostError(RuntimeError):
    """Categorized bridge failure; a lost response never authorizes a write retry."""
    def __init__(self, message: str, *, code: str = "host_error", request_id: str | None = None):
        self.code, self.request_id = code, request_id
        super().__init__(f"{message} [code={code}, request_id={request_id}]")


class AllplanHostClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        # This bridge is local. A corporate proxy must not intercept loopback calls.
        self.opener = build_opener(ProxyHandler({})) if urlparse(base_url).hostname in {"127.0.0.1", "localhost", "::1"} else build_opener()

    def post(self, path: str, payload: dict[str, Any] | None = None,
             headers: dict[str, str] | None = None) -> dict[str, Any]:
        request_headers = {"Content-Type": "application/json", "X-Request-ID": str(uuid4())}
        if headers:
            request_headers.update(headers)
        request_id = request_headers["X-Request-ID"]
        try:
            body = json.dumps(payload or {}, allow_nan=False).encode("utf-8")
        except (ValueError, TypeError) as exc:
            raise AllplanHostError("Request must contain finite JSON values.", code="invalid_payload", request_id=request_id) from exc
        request = Request(urljoin(self.base_url, path.lstrip("/")), data=body,
                          headers=request_headers, method="POST")
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                raw_body = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            try:
                error = json.loads(error_body)
                detail = error["error"]
                code, message = detail["code"], detail["message"]
                request_id = error.get("request_id", request_id)
            except (ValueError, KeyError, TypeError):
                code, message = "host_error", f"Allplan host returned HTTP {exc.code} for {path}. Restart the host or collect diagnostics."
            raise AllplanHostError(message, code=code, request_id=request_id) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise AllplanHostError("Allplan host timed out. Execution may have occurred. Inspect the model before retrying a write.", code="execution_unknown", request_id=request_id) from exc
        except URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                code, message = "execution_unknown", "Allplan host timed out. Inspect the model before retrying a write."
            else:
                code, message = "host_absent", "Could not reach the Allplan host. Open a project and start StartPythonHost in the Library palette."
            raise AllplanHostError(message, code=code, request_id=request_id) from exc
        except (OSError, UnicodeError) as exc:
            raise AllplanHostError("The host response was lost or unreadable. Inspect the model before retrying a write.", code="execution_unknown", request_id=request_id) from exc
        if not raw_body:
            return {"request_id": request_id}
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AllplanHostError("Allplan host returned invalid JSON. Inspect the model before retrying a write.", code="invalid_response", request_id=request_id) from exc
        if not isinstance(data, dict):
            raise AllplanHostError("Allplan host returned a non-object response.", code="invalid_response", request_id=request_id)
        if data.get("ok") is False:
            detail = data.get("error", {})
            raise AllplanHostError(detail.get("message", "Host request failed."), code=detail.get("code", "host_error"), request_id=data.get("request_id", request_id))
        data.setdefault("request_id", request_id)
        return data
