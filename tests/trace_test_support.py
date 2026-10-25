"""Scoped trace doubles for logic tests; persistence tests opt into real storage."""
import json
from threading import Lock
from unittest.mock import patch


def durable_trace(method):
    """Mark a material fixture test as requiring the production trace writer."""
    method.uses_durable_trace = True
    return method


def install_memory_trace(test_case, trace_class):
    """Replace only record storage, retaining the production call/error ordering.

    This double does not model fsync, locks, capacity or archival. Tests of those
    contracts must use the production writer. Execution journals are untouched.
    """
    records, lock = [], Lock()

    def record(trace, api, state, **details):
        entry = {"probe_id": trace.probe_id, "phase": trace.phase,
                 "api": api, "state": state, **details}
        # Keep serialization failures and detached evidence visible to logic tests.
        entry = json.loads(json.dumps(entry, ensure_ascii=False, allow_nan=False))
        with lock:
            records.append(entry)

    patcher = patch.object(trace_class, "record", record)
    patcher.start()
    test_case.addCleanup(patcher.stop)
    return records
