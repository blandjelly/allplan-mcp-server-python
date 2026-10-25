"""Keep fast fixture traces isolated from real persistence and execution journals."""
import importlib
import json
import unittest
from unittest.mock import patch

import test_wall_material_edit as fixtures


class TraceFixtureTests(unittest.TestCase):
    def fixture(self, durable=False):
        native = fixtures.WallMaterialEditTests()
        native.use_durable_trace = durable
        native.setUp()
        self.addCleanup(native.doCleanups)
        return native

    def test_logic_trace_keeps_events_in_memory_and_execution_journal_on_disk(self):
        native = self.fixture()
        plan = native.preview()
        self.assertTrue(native.trace_records)
        self.assertFalse(native.native.plans.trace_path.exists())
        self.assertTrue(any(r["api"] == "WallTierProperties.Material" for r in native.trace_records))
        native.native.highlight(plan)
        result = native.native.apply(plan)
        self.assertEqual(result["state"], "completed")
        record = native.native.plans.executor.path / (result["execution_id"] + ".json")
        self.assertEqual(json.loads(record.read_text())["state"], "completed")
        self.assertFalse(native.native.plans.trace_path.exists())

    def test_memory_writer_rejects_non_json_data_and_cleanup_restores_real_writer(self):
        native = self.fixture(durable=True)
        module = importlib.import_module(native.native.module.__package__ + ".property_probe")
        original = module.NativeProbeTrace.record
        from trace_test_support import install_memory_trace
        case = unittest.TestCase()
        records = install_memory_trace(case, module.NativeProbeTrace)
        trace = module.NativeProbeTrace(native.native.plans.trace_path, "test")
        try:
            trace.call("fixture", lambda: "ok", model_uuid="root")
            self.assertEqual([r["state"] for r in records], ["started", "returned"])
            with self.assertRaises(ValueError):
                trace.record("fixture", "started", invalid=float("nan"))
            self.assertFalse(native.native.plans.trace_path.exists())
        finally:
            case.doCleanups()
        self.assertIs(module.NativeProbeTrace.record, original)
        trace.record("fixture", "restored")
        self.assertTrue(native.native.plans.trace_path.exists())

    def test_durable_opt_in_uses_real_fsync_and_stored_events(self):
        native = self.fixture(durable=True)
        module = importlib.import_module(native.native.module.__package__ + ".property_probe")
        trace = module.NativeProbeTrace(native.native.plans.trace_path, "test")
        # Spy only: every call still reaches the real OS fsync.
        with patch.object(module.os, "fsync", wraps=module.os.fsync) as sync:
            trace.call("fixture", lambda: "ok")
        self.assertGreaterEqual(sync.call_count, 2)
        rows = [json.loads(s) for s in native.native.plans.trace_path.read_text().splitlines()]
        self.assertEqual([r["state"] for r in rows], ["started", "returned"])
