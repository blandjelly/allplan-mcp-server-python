"""Verify the exact delivered 0.28.0 ZIP without rebuilding it or calling Allplan."""
import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path


def _constant_expression(node):
    """Evaluate the small integer expression subset used by native-host limits."""
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _constant_expression(node.left) * _constant_expression(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _constant_expression(node.left) + _constant_expression(node.right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_constant_expression(node.operand)
    raise AssertionError(f"Unsupported limit expression: {ast.dump(node)}")


def _source_constant(path, name, class_name=None):
    """Read an integer module/class constant without importing native-host code."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    scope = tree.body
    if class_name is not None:
        cls = next((node for node in tree.body
                    if isinstance(node, ast.ClassDef) and node.name == class_name), None)
        assert cls is not None, f"Missing class {class_name} in {path}"
        scope = cls.body
    for statement in scope:
        if isinstance(statement, ast.Assign):
            targets = statement.targets
            value = statement.value
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]
            value = statement.value
        else:
            continue
        if value is None:
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return _constant_expression(value)
    raise AssertionError(f"Missing constant {name} in {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True,
                        help="Full source commit recorded in the package manifest.")
    args = parser.parse_args()

    artifacts = Path(__file__).resolve().parent
    repo = artifacts.parents[1]
    archive = artifacts / "allplan-mcp-0.28.0-windows-evaluation.zip"
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert checksum == archive.with_suffix(".zip.sha256").read_text().split()[0]
    with tempfile.TemporaryDirectory(prefix="m4-exact-zip-", dir="/tmp") as directory:
        work = Path(directory)
        with zipfile.ZipFile(archive) as payload:
            payload.extractall(work / "new")
        package = work / "new/allplan-mcp-0.28.0"
        manifest = json.loads((package / "package-manifest.json").read_text())
        assert manifest["source_modified"] is False
        assert manifest["source_commit"] == args.source_commit
        spec = importlib.util.spec_from_file_location("registration", package / "utils/register_python_host.py")
        registration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(registration)
        assert registration.verify_package(package)["integrity"] == "sha256-verified"
        local = work / "Local"
        local.mkdir()
        registration.register(package, local)
        bridge = json.loads((local / "PythonPartsScripts/PythonHost/package_info.json").read_text())
        assert bridge["version"] == "0.28.0"
        for name, digest in bridge["bridge_files"].items():
            assert hashlib.sha256((local / name).read_bytes()).hexdigest() == digest
        for name in ("model_edit.py", "model_edit_contracts.py", "native_model_edit.py", "wall_layer.py",
                     "wall_material.py", "property_probe.py", "identity_probe.py", "component_ownership.py",
                     "model_delete.py", "journal_maintenance.py", "repair_execution.py"):
            assert (local / "PythonPartsScripts/PythonHost" / name).is_file()

        host = local / "PythonPartsScripts/PythonHost"
        assert _source_constant(host / "repair_execution.py", "MAX_RECORDS", "RepairExecutor") == 512
        assert _source_constant(host / "repair_execution.py", "MAX_RECORD_BYTES", "RepairExecutor") == 1024 * 1024
        assert _source_constant(host / "property_probe.py", "MAX_BYTES", "NativeProbeTrace") == 8 * 1024 * 1024
        assert _source_constant(host / "property_probe.py", "MAX_INSPECT_BYTES", "NativeProbeTrace") == 32 * 1024 * 1024
        assert _source_constant(host / "journal_maintenance.py", "MAX_BYTES") == 1024 * 1024 * 1024

        with zipfile.ZipFile(repo / "evaluation-packages/0.27.0/allplan-mcp-0.27.0-windows-evaluation.zip") as payload:
            payload.extractall(work / "old")
        old = work / "old/allplan-mcp-0.27.0"
        registration.register(old, local)

        def snapshot():
            return {str(path.relative_to(local)): path.read_bytes()
                    for tree in registration.INSTALL_TREES
                    for path in (local / tree).rglob("*") if path.is_file()}

        original = snapshot()
        markers = {
            ".allplan-mcp/repairs/preserved.json": b"journal marker",
            ".allplan-mcp/logs/m4-native-probe.jsonl": b"trace marker",
            ".allplan-mcp/logs/bridge.log": b"bridge log marker",
            ".allplan-mcp/repairs/archive/preserved.json": b"archived execution marker",
            ".allplan-mcp/logs/m4-native-probe-archive/preserved.jsonl": b"archived trace marker",
        }
        for name, content in markers.items():
            path = local / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        upgrade = registration.register(package, local)
        assert json.loads((local / "PythonPartsScripts/PythonHost/package_info.json").read_text())["version"] == "0.28.0"
        for name, content in markers.items():
            assert (local / name).read_bytes() == content
        registration.restore(local, upgrade["backup_id"])
        assert snapshot() == original
        for name, content in markers.items():
            assert (local / name).read_bytes() == content

        subprocess.run(["uv", "sync", "--frozen"], cwd=package, check=True)
        imported = subprocess.check_output(["uv", "run", "--frozen", "python", "-c", """
from importlib.metadata import version
from allplan_mcp import __version__
from allplan_mcp.model_edit_models import ModelEditPreview
from allplan_mcp.property_models import DrawingIdentityProbeInput, PropertyProbeRequest
from pydantic import TypeAdapter, ValidationError

DrawingIdentityProbeInput(phase="drawing_identity", drawing_file=101)
TypeAdapter(PropertyProbeRequest).validate_python({"phase": "drawing_identity", "drawing_file": 101})
schema = DrawingIdentityProbeInput.model_json_schema()
assert schema["properties"]["offset"]["maximum"] == 9999
assert schema["properties"]["limit"]["maximum"] == 32
try:
    DrawingIdentityProbeInput(phase="drawing_identity", drawing_file=101, limit=33)
except ValidationError:
    pass
else:
    raise AssertionError("DrawingIdentityProbeInput accepted an oversized limit")
ModelEditPreview(action="preview", changes=[{"target": {"kind": "delete"}}])
ModelEditPreview(action="preview", changes=[{"target": {"kind": "native_material", "tier_index": 1}, "value": "C35/45"}])
assert __version__ == version("allplan-mcp-server") == "0.28.0"
print(__version__)
"""], cwd=package, text=True)
        assert imported.strip() == "0.28.0"

    result = {
        "source_commit": args.source_commit,
        "source_modified": False,
        "zip_sha256": checksum,
        "payload_files": len(manifest["files"]),
        "bridge_hashes_verified": len(bridge["bridge_files"]),
        "zip_checksum": "pass",
        "payload_integrity": "pass",
        "exact_zip_registration": "pass",
        "exact_zip_frozen_sync_and_import": "pass",
        "drawing_identity_schema_validation": "pass",
        "native_source_safety_limits": "pass",
        "upgrade_from_0.27.0": "pass",
        "restore_to_0.27.0": "pass",
        "journal_trace_and_bridge_log_preserved": "pass",
        "archived_execution_and_trace_markers_preserved": "pass",
        "native_Allplan": "not_run",
    }
    (artifacts / "package-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
