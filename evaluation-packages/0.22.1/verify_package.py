"""Verify a delivered candidate ZIP without native Allplan calls or rebuilding it."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

artifacts = Path(__file__).resolve().parent
repo = artifacts.parents[1]
archive = artifacts / 'allplan-mcp-0.22.1-windows-evaluation.zip'
expected_source = '35d4744bec47bf765116956a68a23bed1b6b199f'
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
assert checksum == archive.with_suffix('.zip.sha256').read_text().split()[0]
with tempfile.TemporaryDirectory(prefix='m4-exact-zip-', dir='/tmp') as directory:
    work = Path(directory)
    with zipfile.ZipFile(archive) as payload:
        payload.extractall(work / 'new')
    package = work / 'new/allplan-mcp-0.22.1'
    manifest = json.loads((package / 'package-manifest.json').read_text())
    assert manifest['source_modified'] is False
    assert manifest['source_commit'] == expected_source
    spec = importlib.util.spec_from_file_location('registration', package / 'utils/register_python_host.py')
    registration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(registration)
    assert registration.verify_package(package)['integrity'] == 'sha256-verified'
    local = work / 'Local'
    local.mkdir()
    registration.register(package, local)
    bridge = json.loads((local / 'PythonPartsScripts/PythonHost/package_info.json').read_text())
    assert bridge['version'] == '0.22.1'
    for name, digest in bridge['bridge_files'].items():
        assert hashlib.sha256((local / name).read_bytes()).hexdigest() == digest
    for name in ('model_edit.py', 'model_edit_contracts.py', 'native_model_edit.py', 'wall_layer.py', 'attribute_codecs.py', 'layer_names.py'):
        assert (local / 'PythonPartsScripts/PythonHost' / name).is_file()
    with zipfile.ZipFile(repo / 'evaluation-packages/0.22.0/allplan-mcp-0.22.0-windows-evaluation.zip') as payload:
        payload.extractall(work / 'old')
    old = work / 'old/allplan-mcp-0.22.0'
    registration.register(old, local)
    def snapshot():
        return {str(p.relative_to(local)): p.read_bytes() for tree in registration.INSTALL_TREES
                for p in (local / tree).rglob('*') if p.is_file()}
    original = snapshot()
    markers = {'.allplan-mcp/repairs/preserved.json': b'journal marker',
               '.allplan-mcp/logs/m4-native-probe.jsonl': b'trace marker',
               '.allplan-mcp/logs/bridge.log': b'bridge log marker'}
    for name, content in markers.items():
        path = local / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    upgrade = registration.register(package, local)
    assert json.loads((local / 'PythonPartsScripts/PythonHost/package_info.json').read_text())['version'] == '0.22.1'
    for name, content in markers.items():
        assert (local / name).read_bytes() == content
    registration.restore(local, upgrade['backup_id'])
    assert snapshot() == original
    for name, content in markers.items():
        assert (local / name).read_bytes() == content
    subprocess.run(['uv', 'sync', '--frozen'], cwd=package, check=True)
    imported = subprocess.check_output(['uv', 'run', '--frozen', 'python', '-c',
        "from importlib.metadata import version; from allplan_mcp import __version__; "
        "from allplan_mcp.server import mcp, model_edit; "
        "assert __version__ == version('allplan-mcp-server') == '0.22.1'; print(__version__)"],
        cwd=package, text=True)
    assert imported.strip() == '0.22.1'
result = {'source_commit': expected_source, 'source_modified': False,
          'zip_sha256': checksum, 'payload_files': len(manifest['files']),
          'bridge_hashes_verified': len(bridge['bridge_files']),
          'zip_checksum': 'pass', 'payload_integrity': 'pass', 'exact_zip_registration': 'pass',
          'exact_zip_frozen_sync_and_import': 'pass', 'upgrade_from_0220': 'pass',
          'restore_to_0220': 'pass', 'journal_trace_and_bridge_log_preserved': 'pass',
          'native_Allplan': 'not_run'}
(artifacts / 'package-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
