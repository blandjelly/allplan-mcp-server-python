"""Confirmed archival of resolved execution records; never evict replay identity."""
import hashlib
import os
import re
from itertools import islice

from .query_contracts import fingerprint
from .transport import BridgeError

MAX_FILES = 1024
MAX_BYTES = 1024 * 1024 * 1024


def archive_path(executor):
    path = executor.path / "archive"
    if executor.path.is_symlink() or path.is_symlink() or (path.exists() and not path.is_dir()):
        raise BridgeError("repair_journal_unavailable", "Journal archive is not a regular directory.", 409)
    return path


def inventory(executor):
    """Complete bounded active inventory, including entries unsafe to archive."""
    archive = archive_path(executor)
    files = sorted(islice(executor.path.glob("*.json"), MAX_FILES + 1))
    if len(files) > MAX_FILES:
        raise BridgeError("journal_cleanup_limit", "Cleanup inventory exceeds 1024 records; no records changed.", 409)
    items, total = [], 0
    for path in files:
        item = {"execution_id": path.stem, "eligible": False}
        if path.is_symlink() or not path.is_file():
            item["reason"] = "unsafe_file"
        else:
            size = path.stat().st_size
            total += size
            if total > MAX_BYTES:
                raise BridgeError("journal_cleanup_limit", "Cleanup inventory exceeds 1 GiB; no records changed.", 409)
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(65536), b""):
                    digest.update(chunk)
            item.update(size_bytes=size, sha256=digest.hexdigest())
            if not re.fullmatch(r"[0-9a-f]{32}", path.stem):
                item["reason"] = "invalid_execution_id"
            else:
                try:
                    record = executor.load(path.stem)
                    ref = record["changes"][0]["ref"]
                    item["source_identity"] = {key: ref[key] for key in ("project_key", "document_id", "drawing_file")}
                    unresolved = record["state"] == "running" or any(
                        outcome["state"] == "unknown" for outcome in record["outcomes"])
                    if unresolved:
                        item["reason"] = "recovery_required"
                    elif (archive / path.name).exists() or (archive / path.name).is_symlink():
                        item["reason"] = "archive_collision"
                    else:
                        item.update(eligible=True, state=record["state"])
                except BridgeError:
                    item["reason"] = "unverifiable_or_oversized_record"
        items.append(item)
    snapshot = {"target": "repair_records", "records": items}
    eligible = [item for item in items if item["eligible"]]
    return {**snapshot, "snapshot_hash": fingerprint(snapshot), "read_only": True,
            "native_model_access": False, "records_modified": False,
            "record_count": len(items), "record_limit": executor.MAX_RECORDS,
            "full": len(items) >= executor.MAX_RECORDS,
            "cleanup_available": bool(eligible), "eligible_count": len(eligible),
            "protected_count": len(items) - len(eligible),
            "eligible_bytes": sum(item["size_bytes"] for item in eligible),
            "archive_policy": "preserve_exact_bytes_and_execution_id_replay; no deletion"}


def _sync_directory(path):
    if os.name != "nt":
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def preview(executor, target):
    if target == "native_trace":
        from .property_probe import NativeProbeTrace
        result = NativeProbeTrace.inspect_storage(executor.plans.trace_path)
    else:
        with executor.locked():
            result = inventory(executor)
    result.update(action="preview_journal_cleanup", user_confirmation_required=True,
                  model_data_changed=False, automatic_cleanup=False)
    if result["cleanup_available"]:
        result["state"] = "confirmation_required"
        result["confirmation_question"] = (
            "Czy zarchiwizować bieżący ślad diagnostyczny M4 i rozpocząć pusty plik?"
            if target == "native_trace" else
            f"Czy przenieść {result['eligible_count']} rozliczonych wykonań do archiwum? "
            f"Chronione wpisy pozostaną: {result['protected_count']}.")
        result["after_user_confirmation"] = {
            "action": "cleanup_journal", "target": target, "snapshot_hash": result["snapshot_hash"],
            "acknowledgement": "confirmed_journal_cleanup"}
    else:
        result["state"] = "nothing_to_archive"
    return result


def cleanup(executor, request):
    if request["target"] == "native_trace":
        from .property_probe import NativeProbeTrace
        result = NativeProbeTrace.rotate(executor.plans.trace_path, request["snapshot_hash"])
    else:
        moved = []
        with executor.locked():
            reviewed = inventory(executor)
            if reviewed["snapshot_hash"] != request["snapshot_hash"]:
                raise BridgeError("journal_cleanup_conflict", "Journal changed; preview again and ask for confirmation.", 409)
            archive = archive_path(executor)
            try:
                archive.mkdir(exist_ok=True)
                _sync_directory(executor.path)
                for item in reviewed["records"]:
                    if not item["eligible"]:
                        continue
                    source = executor.path / (item["execution_id"] + ".json")
                    destination = archive / source.name
                    if destination.exists() or destination.is_symlink():
                        raise OSError("Archive destination already exists")
                    os.replace(source, destination)
                    moved.append(item["execution_id"])
                    _sync_directory(archive)
                    _sync_directory(executor.path)
            except OSError:
                # A batch can stop between atomic moves. Every ID is still
                # available in active storage or archive; no setter can replay.
                return {"action": "cleanup_journal", "target": "repair_records", "state": "partial",
                        "archived_execution_ids": moved, "records_modified": bool(moved),
                        "native_model_access": False, "model_data_changed": False,
                        "read_only": False, "next_action": {"action": "preview_journal_cleanup", "target": "repair_records"},
                        "report_text": "Archival stopped; inspect a fresh preview before continuing. No data was deleted."}
            result = {"target": "repair_records", "state": "archived" if moved else "no_op",
                      "archived_execution_ids": moved, "archived_count": len(moved),
                      "protected_count": reviewed["protected_count"], "records_modified": bool(moved)}
    result.update(action="cleanup_journal", read_only=False, native_model_access=False,
                  model_data_changed=False, records_deleted=0, automatic_retry=False,
                  next_action={"action": "inspect_journal"})
    return result
