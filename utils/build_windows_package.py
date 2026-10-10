"""Create a deterministic, source-only Windows evaluation package (no runtimes)."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
import zipfile
from pathlib import Path

ROOT_FILES = ("README.md", "pyproject.toml", "uv.lock")
TREES = ("src", "python_host", "utils", "windows", "docs", "profiles")


def payload_files(repo: Path) -> dict[str, bytes]:
    paths = [repo / name for name in ROOT_FILES]
    for name in TREES:
        paths.extend(p for p in (repo / name).rglob("*") if p.is_file()
                     and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"})
    files = {}
    for path in sorted(paths):
        if path.is_symlink():
            raise ValueError(f"Package symlinks are not supported: {path}")
        files[path.relative_to(repo).as_posix()] = path.read_bytes()
    # Place the no-code entry points at the top level for Explorer users.
    for name, action in {"Setup.cmd": "setup", "Launch Allplan MCP.cmd": "launch",
                         "Connect Codex.cmd": "connect", "Diagnostics.cmd": "diagnostics",
                         "M3 Workflow Recover.cmd": "m3-workflow-recover",
                         "M3 Numbering.cmd": "m3-numbering",
                         "M3 Numbering Recover.cmd": "m3-numbering-recover",
                         "M3 Recover.cmd": "m3-recover",
                         "Restore bridge.cmd": "restore"}.items():
        files[name] = (repo / "windows" / f"{action}.cmd").read_bytes()
    return files


def build(repo: Path, output: Path) -> Path:
    version = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    files = payload_files(repo)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    changed = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True).strip())
    manifest = {"schema_version": "m0-1", "version": version, "source_commit": commit,
                "source_modified": changed, "purpose": "local_evaluation",
                "license_status": "unresolved_no_upstream_license", "uv_version": "0.12.19",
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}}
    files["package-manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"allplan-mcp-{version}-windows-evaluation.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(f"allplan-mcp-{version}/{name}", date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            package.writestr(entry, data)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    print(build(Path(__file__).resolve().parent.parent, args.output).resolve())


if __name__ == "__main__":
    main()
