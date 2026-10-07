from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import shutil
import tempfile
import tomllib
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ALLPLAN_VERSION = "2026"
PYTHONPART_FOLDER = "PythonHost"
# The legacy tree is backed up and removed when upgrading from 0.1.1.
INSTALL_TREES = (Path("Library/PythonHost"), Path("PythonPartsScripts/PythonHost"),
                 Path("PythonParts/PythonHost"))
STATE_FOLDER = ".allplan-mcp"


def default_allplan_local(version: str) -> Path:
    """Use Windows' Documents known folder, including redirected locations."""
    documents = Path.home() / "Documents"
    if hasattr(ctypes, "windll"):
        buffer = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buffer) == 0:
            documents = Path(buffer.value)
    return documents / "Nemetschek" / "Allplan" / version / "Usr" / "Local"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_package(repo: Path) -> dict:
    """Verify a built package before any installation changes."""
    manifest_path = repo / "package-manifest.json"
    if not manifest_path.exists():
        return {"version": tomllib.loads((repo / "pyproject.toml").read_text())["project"]["version"],
                "source_commit": "source-checkout", "integrity": "source-checkout"}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        path = repo / name
        if not path.resolve().is_relative_to(repo.resolve()) or path.is_symlink():
            raise ValueError(f"Invalid package path: {name}")
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Package integrity check failed: {name}. Extract a fresh package.")
    actual = {p.relative_to(repo).as_posix() for p in repo.rglob("*")
              if p.is_file() and not excluded(p.relative_to(repo))
              and p.name != "package-manifest.json"}
    # Generated logs, venvs and installation records are not shipped payload.
    if actual != set(manifest["files"]):
        raise ValueError("Package has unexpected or missing files. Extract a fresh package.")
    return {"version": manifest["version"], "source_commit": manifest["source_commit"],
            "integrity": "sha256-verified"}


def excluded(relative: Path) -> bool:
    return any(part in {"__pycache__", ".venv", ".bootstrap", "logs", "dist", ".git"} for part in relative.parts) or relative.suffix in {".pyc", ".pyo"} or relative.name in {"registration_result.json", "utils_log.txt"}


def bridge_files(repo: Path) -> dict[Path, Path]:
    pyp = repo / "python_host/Library/PythonParts/StartPythonHost.pyp"
    scripts = repo / "python_host/PythonPartsScripts/PythonHost"
    files = {INSTALL_TREES[0] / pyp.name: pyp}
    for source in sorted(scripts.rglob("*")):
        if excluded(source.relative_to(scripts)):
            continue
        if source.is_symlink():
            raise ValueError(f"Bridge symlinks are not supported: {source}")
        if source.is_file():
            files[INSTALL_TREES[1] / source.relative_to(scripts)] = source
    for required in (pyp, scripts / "StartPythonHost.py", scripts / "PythonHostHandler.py",
                     scripts / "sandbox/__init__.py", scripts / "sandbox/executor.py",
                     scripts / "sandbox/validator.py", scripts / "sandbox/const.py"):
        if not required.is_file():
            raise FileNotFoundError(f"Incomplete bridge package: {required}")
    return files


def _replace(allplan_local: Path, staged: Path, metadata: dict) -> str:
    """Back up owned trees, including the legacy layout, and roll back on failure."""
    state = allplan_local / STATE_FOLDER
    backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
    backup = state / "backups" / backup_id
    backup.mkdir(parents=True)
    present = []
    for relative in INSTALL_TREES:
        target = allplan_local / relative
        if target.is_symlink():
            raise ValueError(f"Refusing to replace a symlink: {target}")
        if target.exists():
            if any(p.is_symlink() for p in target.rglob("*")):
                raise ValueError(f"Refusing to back up a tree containing symlinks: {target}")
            shutil.copytree(target, backup / relative)
            present.append(relative.as_posix())
    hashes = {p.relative_to(backup).as_posix(): sha256(p) for relative in INSTALL_TREES
              for p in (backup / relative).rglob("*") if p.is_file()}
    (backup / "backup.json").write_text(json.dumps({"present": present, "files": hashes, **metadata}, indent=2), encoding="utf-8")
    previous_record = (state / "current.json").read_bytes() if (state / "current.json").exists() else None
    replaced = []
    try:
        for relative in INSTALL_TREES:
            target = allplan_local / relative
            replaced.append(relative)
            if target.exists():
                shutil.rmtree(target)
            if (staged / relative).exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(staged / relative, target)
        (state / "current.json").write_text(json.dumps({"backup_id": backup_id, **metadata}, indent=2), encoding="utf-8")
    except Exception:
        for relative in replaced:
            target = allplan_local / relative
            if target.exists():
                shutil.rmtree(target)
            if (backup / relative).exists():
                shutil.copytree(backup / relative, target)
        if previous_record is None:
            (state / "current.json").unlink(missing_ok=True)
        else:
            (state / "current.json").write_bytes(previous_record)
        raise
    return backup_id


def register(repo: Path, allplan_local: Path, *, dry_run: bool = False) -> dict:
    repo, allplan_local = repo.resolve(), allplan_local.resolve()
    if not allplan_local.is_dir():
        raise FileNotFoundError(f"Allplan Local folder does not exist: {allplan_local}. Select the actual user folder shown by Allmenu.")
    package = verify_package(repo)
    files = bridge_files(repo)
    result = {**package, "allplan_local": str(allplan_local), "dry_run": dry_run,
              "copied_files": [str(p) for p in files], "backup_id": None,
              "pythonpart_path": str(allplan_local / INSTALL_TREES[0] / "StartPythonHost.pyp"),
              "library_location": "Library > Private > PythonHost > StartPythonHost"}
    if dry_run:
        return result
    state = allplan_local / STATE_FOLDER
    state.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage-", dir=state) as directory:
        staged = Path(directory)
        for relative, source in files.items():
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        info = {**package, "bridge_files": {p.as_posix(): sha256(s) for p, s in files.items()}}
        (staged / INSTALL_TREES[1] / "package_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        result["backup_id"] = _replace(allplan_local, staged, package)
    return result


def restore(allplan_local: Path, backup_id: str = "latest") -> dict:
    allplan_local = allplan_local.resolve()
    state = allplan_local / STATE_FOLDER
    if backup_id == "latest":
        backup_id = json.loads((state / "current.json").read_text(encoding="utf-8"))["backup_id"]
    if not backup_id or Path(backup_id).name != backup_id or backup_id in {".", ".."} or "\\" in backup_id:
        raise ValueError("Invalid backup ID.")
    backup = state / "backups" / backup_id
    if backup.is_symlink():
        raise ValueError("Backup must not be a symlink.")
    record = json.loads((backup / "backup.json").read_text(encoding="utf-8"))
    actual = {}
    for relative in INSTALL_TREES:
        for path in (backup / relative).rglob("*"):
            if path.is_symlink():
                raise ValueError("Backup contains a symlink.")
            if path.is_file():
                actual[path.relative_to(backup).as_posix()] = sha256(path)
    present = [relative.as_posix() for relative in INSTALL_TREES if (backup / relative).is_dir()]
    if actual != record["files"] or set(present) != set(record["present"]):
        raise ValueError("Backup integrity check failed; the current installation was not changed.")
    # The current installation is also backed up, allowing a restore to be undone.
    safety_backup = _replace(allplan_local, backup, {"restored_from": backup_id})
    return {"allplan_local": str(allplan_local), "restored_from": backup_id, "backup_id": safety_backup}


def main() -> None:
    parser = argparse.ArgumentParser(description="Install or restore the complete Allplan MCP bridge. Close Allplan first.")
    parser.add_argument("--allplan-version", default=DEFAULT_ALLPLAN_VERSION)
    parser.add_argument("--allplan-local", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--restore", nargs="?", const="latest")
    args = parser.parse_args()
    if args.restore and args.dry_run:
        parser.error("--restore cannot be combined with --dry-run")
    repo = Path(__file__).resolve().parent.parent
    local = args.allplan_local or default_allplan_local(args.allplan_version)
    try:
        result = restore(local, args.restore) if args.restore else register(repo, local, dry_run=args.dry_run)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Registration failed: {exc}\n")
    (repo / "registration_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
