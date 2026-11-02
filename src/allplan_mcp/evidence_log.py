"""Opt-in raw evidence capture of bridge requests and responses.

Native Allplan trials need the exact requests and responses, not a chat
summary. When ``ALLPLAN_MCP_EVIDENCE_DIR`` is set (the Windows launcher sets
it to the package ``logs/evidence`` folder), every bridge call appends a
``request`` line before sending and a ``response`` or ``error`` line after it
to a daily JSON Lines file. The request line is written first so that a lost
reply still leaves the submitted payload and its request ID.

Capture is best effort and strictly observational: an I/O failure disables
nothing, raises nothing and never changes a request, a response or a retry
decision. It is not a journal; execution journals in Local/.allplan-mcp
remain the authority for write outcomes.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENV = "ALLPLAN_MCP_EVIDENCE_DIR"
SCHEMA = "allplan-mcp-evidence-1"
MAX_FILE_BYTES = 256 * 1024 * 1024

_lock = threading.Lock()


def directory() -> Path | None:
    value = os.getenv(ENV, "").strip()
    return Path(value) if value else None


def record(kind: str, path: str, request_id: str | None, **content: Any) -> None:
    folder = directory()
    if folder is None:
        return
    now = datetime.now(timezone.utc)
    entry = {"schema_version": SCHEMA, "kind": kind, "time_utc": now.isoformat(timespec="milliseconds"),
             "pid": os.getpid(), "bridge_path": path, "request_id": request_id, **content}
    try:
        line = json.dumps(entry, ensure_ascii=False, allow_nan=False, default=repr) + "\n"
        with _lock:
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / f"evidence-{now:%Y%m%d}.jsonl"
            if target.exists() and target.stat().st_size + len(line.encode("utf-8")) > MAX_FILE_BYTES:
                return
            with target.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.flush()
                os.fsync(handle.fileno())
    except (OSError, ValueError, TypeError):
        return
