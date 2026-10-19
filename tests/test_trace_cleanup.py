"""Native probe trace cleanup preserves exact bytes and binds reviewed snapshots."""
import hashlib
import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_host_handler as host_fixtures


class NativeTraceCleanupTests(unittest.TestCase):
    def setUp(self):
        host_fixtures.HostHandlerTests.setUp(self)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "native.jsonl"
        self.trace = importlib.import_module("test_allplan_host.property_probe").NativeProbeTrace

    def test_full_trace_rotates_verbatim_and_new_records_append_to_fresh_file(self):
        original = b"x" * self.trace.MAX_BYTES
        self.path.write_bytes(original)
        reviewed = self.trace.inspect_storage(self.path)
        self.assertEqual(reviewed["target"], "native_trace")
        self.assertTrue(reviewed["full"])
        self.assertTrue(reviewed["cleanup_available"])
        self.assertEqual(reviewed["bytes"], len(original))

        result = self.trace.rotate(self.path, reviewed["snapshot_hash"])
        archived = self.path.parent / "native-archive" / result["archive"]
        self.assertEqual(result["state"], "archived")
        self.assertEqual(archived.read_bytes(), original)
        self.assertFalse(self.path.exists())
        retry = self.trace.rotate(self.path, reviewed["snapshot_hash"])
        self.assertEqual(retry["state"], "already_archived")

        self.trace(self.path, "cleanup_test").record("test.api", "returned")
        current = self.trace.inspect_storage(self.path)
        self.assertTrue(current["exists"])
        self.assertFalse(current["full"])
        self.assertEqual(current["archive"]["count"], 1)
        record = json.loads(self.path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual((record["phase"], record["api"], record["state"]),
                         ("cleanup_test", "test.api", "returned"))

    def test_stale_snapshot_does_not_move_or_change_trace(self):
        self.path.write_bytes(b"reviewed\n")
        reviewed = self.trace.inspect_storage(self.path)
        self.path.write_bytes(b"changed\n")
        with self.assertRaises(self.trace_error()) as error:
            self.trace.rotate(self.path, reviewed["snapshot_hash"])
        self.assertEqual(error.exception.code, "cleanup_snapshot_stale")
        self.assertEqual(self.path.read_bytes(), b"changed\n")
        self.assertFalse((self.path.parent / "native-archive").exists())

    def trace_error(self):
        return importlib.import_module("test_allplan_host.transport").BridgeError

    def test_missing_and_empty_trace_are_noop(self):
        missing = self.trace.inspect_storage(self.path)
        self.assertFalse(missing["exists"])
        self.assertFalse(missing["cleanup_available"])
        self.assertEqual(self.trace.rotate(self.path, missing["snapshot_hash"])["state"], "unchanged_empty")
        self.path.write_bytes(b"")
        empty = self.trace.inspect_storage(self.path)
        self.assertTrue(empty["exists"])
        self.assertFalse(empty["cleanup_available"])
        self.assertEqual(self.trace.rotate(self.path, empty["snapshot_hash"])["state"], "unchanged_empty")
        self.assertEqual(self.path.read_bytes(), b"")

    def test_rotation_failure_keeps_original_trace(self):
        original = b"keep these exact bytes\n"
        self.path.write_bytes(original)
        reviewed = self.trace.inspect_storage(self.path)
        with patch.object(os, "replace", side_effect=OSError("blocked rename")):
            with self.assertRaises(self.trace_error()) as error:
                self.trace.rotate(self.path, reviewed["snapshot_hash"])
        self.assertEqual(error.exception.code, "cleanup_rotation_unavailable")
        self.assertEqual(self.path.read_bytes(), original)

    def test_competing_storage_lock_blocks_inspection(self):
        self.path.write_bytes(b"trace\n")
        with self.trace._storage_lock(self.path):
            with self.assertRaises(self.trace_error()) as error:
                self.trace.inspect_storage(self.path)
        self.assertEqual(error.exception.code, "cleanup_inspection_unavailable")
        self.assertEqual(self.path.read_bytes(), b"trace\n")

    def test_symlinked_trace_and_archive_directory_fail_closed(self):
        target = Path(self.directory.name) / "outside.jsonl"
        target.write_bytes(b"preserve\n")
        self.path.symlink_to(target)
        with self.assertRaises(self.trace_error()) as error:
            self.trace.inspect_storage(self.path)
        self.assertEqual(error.exception.code, "cleanup_inspection_unavailable")
        self.path.unlink()

        self.path.write_bytes(b"trace\n")
        archive_target = Path(self.directory.name) / "outside-dir"
        archive_target.mkdir()
        (self.path.parent / "native-archive").symlink_to(archive_target, target_is_directory=True)
        with self.assertRaises(self.trace_error()) as error:
            self.trace.rotate(self.path, self.trace.inspect_storage(self.path)["snapshot_hash"])
        self.assertEqual(error.exception.code, "cleanup_inspection_unavailable")
        self.assertEqual(self.path.read_bytes(), b"trace\n")
        self.assertEqual(list(archive_target.iterdir()), [])

    def test_archive_collision_is_checked_and_existing_archive_is_unchanged(self):
        original = b"archive me\n"
        self.path.write_bytes(original)
        reviewed = self.trace.inspect_storage(self.path)
        archive_dir = self.path.parent / "native-archive"
        archive_dir.mkdir()
        archive_name = hashlib.sha256(original).hexdigest() + ".jsonl"
        destination = archive_dir / archive_name
        destination.write_bytes(b"different data")
        with self.assertRaises(self.trace_error()) as error:
            self.trace.rotate(self.path, reviewed["snapshot_hash"])
        self.assertEqual(error.exception.code, "cleanup_archive_conflict")
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(destination.read_bytes(), b"different data")

    def test_identical_archive_collision_preserves_both_copies(self):
        original = b"same content\n"
        self.path.write_bytes(original)
        reviewed = self.trace.inspect_storage(self.path)
        archive_dir = self.path.parent / "native-archive"
        archive_dir.mkdir()
        destination = archive_dir / (hashlib.sha256(original).hexdigest() + ".jsonl")
        destination.write_bytes(original)
        with self.assertRaises(self.trace_error()) as error:
            self.trace.rotate(self.path, reviewed["snapshot_hash"])
        self.assertEqual(error.exception.code, "cleanup_archive_conflict")
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(destination.read_bytes(), original)

    def test_archive_preview_bounds_metadata_without_hashing_every_archive(self):
        archive_dir = self.path.parent / "native-archive"
        archive_dir.mkdir()
        for index in range(self.trace.MAX_ARCHIVE_PREVIEW + 2):
            name = f"{index:064x}.jsonl"
            (archive_dir / name).write_bytes(b"archive")
        self.path.write_bytes(b"current\n")
        result = self.trace.inspect_storage(self.path)
        self.assertFalse(result["archive"]["complete"])
        self.assertIsNone(result["archive"]["count"])
        self.assertIsNone(result["archive"]["bytes"])
        self.assertEqual(len(result["archive"]["archives"]), self.trace.MAX_ARCHIVE_PREVIEW)
        self.assertTrue(all(item["integrity"] == "not_rehashed"
                            and "sha256" not in item for item in result["archive"]["archives"]))


if __name__ == "__main__":
    unittest.main()
