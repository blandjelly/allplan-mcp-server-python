"""Verify the exact frozen ZIP; no native Allplan calls."""
import hashlib
import importlib.util
import json
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

artifacts = Path(__file__).resolve().parent
repo = artifacts.parents[1]
expected_source = "f477f138231f2a8f45690c03bd761364c7e94ab6"
archive = artifacts / "allplan-mcp-0.18.1-windows-evaluation.zip"
assert hashlib.sha256(archive.read_bytes()).hexdigest() == archive.with_suffix(".zip.sha256").read_text().split()[0]
(repo / "dist").mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=repo / "dist") as directory:
    work = Path(directory)
    with zipfile.ZipFile(archive) as payload:
        payload.extractall(work / "new")
    package = work / "new/allplan-mcp-0.18.1"
    manifest = json.loads((package / "package-manifest.json").read_text())
    assert manifest["source_modified"] is False
    assert manifest["source_commit"] == expected_source
    spec = importlib.util.spec_from_file_location("registration", package / "utils/register_python_host.py")
    registration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registration)
    assert registration.verify_package(package)["integrity"] == "sha256-verified"
    local = work / "Local"
    local.mkdir()
    registration.register(package, local)
    bridge = json.loads((local / "PythonPartsScripts/PythonHost/package_info.json").read_text())
    assert bridge["version"] == "0.18.1"
    for name, digest in bridge["bridge_files"].items():
        assert hashlib.sha256((local / name).read_bytes()).hexdigest() == digest
    start = (local / "PythonPartsScripts/PythonHost/StartPythonHost.py").read_text()
    assert "Dispatcher.Invoke" not in start
    assert "self.ui_dispatch.process_pending()" in start
    assert "time.sleep(0.001)" in start
    with zipfile.ZipFile(repo / "evaluation-packages/0.18.0/allplan-mcp-0.18.0-windows-evaluation.zip") as payload:
        payload.extractall(work / "old")
    old = work / "old/allplan-mcp-0.18.0"
    changed_native = []
    for path in (package / "python_host").rglob("*"):
        if path.is_file() and path.read_bytes() != (old / path.relative_to(package)).read_bytes():
            changed_native.append(path.name)
    assert sorted(changed_native) == ["StartPythonHost.py", "transport.py"]
    registration.register(old, local)
    def snapshot():
        return {str(p.relative_to(local)): p.read_bytes() for tree in registration.INSTALL_TREES
                for p in (local / tree).rglob("*") if p.is_file()}
    original = snapshot()
    markers = {".allplan-mcp/repairs/preserved.json": b"journal marker",
               ".allplan-mcp/logs/m4-native-probe.jsonl": b"trace marker",
               ".allplan-mcp/logs/bridge.log": b"bridge log marker"}
    for name, content in markers.items():
        path = local / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    upgrade = registration.register(package, local)
    assert json.loads((local / "PythonPartsScripts/PythonHost/package_info.json").read_text())["version"] == "0.18.1"
    for name, content in markers.items():
        assert (local / name).read_bytes() == content
    registration.restore(local, upgrade["backup_id"])
    assert snapshot() == original
    for name, content in markers.items():
        assert (local / name).read_bytes() == content
    subprocess.run(["uv", "sync", "--frozen"], cwd=package, check=True)
    installed = subprocess.check_output(["uv", "run", "--frozen", "python", "-c",
        "from importlib.metadata import version; from allplan_mcp import __version__; "
        "from allplan_mcp.server import mcp; "
        "assert __version__ == version('allplan-mcp-server') == '0.18.1'; print(__version__)"],
        cwd=package, text=True)
    assert installed.strip() == "0.18.1"
with zipfile.ZipFile(artifacts / "allplan_mcp_server-0.18.1-py3-none-any.whl") as wheel:
    assert "host_timeout" in wheel.read("allplan_mcp/allplan_client.py").decode()
    assert "Version: 0.18.1" in wheel.read("allplan_mcp_server-0.18.1.dist-info/METADATA").decode()
with tarfile.open(artifacts / "allplan_mcp_server-0.18.1.tar.gz") as source:
    assert not any("/evaluation-packages/" in name for name in source.getnames())
    content = source.extractfile("allplan_mcp_server-0.18.1/python_host/PythonPartsScripts/PythonHost/transport.py").read().decode()
    assert "class UIRequestDispatcher" in content
result = {"source_commit": expected_source, "source_modified": False,
          "payload_files": len(manifest["files"]), "bridge_hashes_verified": len(bridge["bridge_files"]),
          "zip_checksum": "pass", "payload_integrity": "pass", "exact_zip_registration": "pass",
          "exact_zip_frozen_sync_and_import": "pass", "upgrade_from_0180": "pass", "restore_to_0180": "pass",
          "journal_trace_and_bridge_log_preserved": "pass", "wheel_and_sdist_contents": "pass",
          "only_native_payload_changes": sorted(changed_native), "native_Allplan": "not_run"}
(artifacts / "package-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
