import hashlib
import importlib.util
import json
import tarfile
import tempfile
import zipfile
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
artifacts = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('registration', repo / 'utils/register_python_host.py')
registration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registration)
archive = artifacts / 'allplan-mcp-0.18.0-windows-evaluation.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == archive.with_suffix('.zip.sha256').read_text().split()[0]
with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    with zipfile.ZipFile(archive) as z:
        z.extractall(work / 'new')
    package = work / 'new/allplan-mcp-0.18.0'
    manifest = json.loads((package / 'package-manifest.json').read_text())
    assert manifest['source_modified'] is False
    assert manifest['source_commit'] == '5ea4bcfd88f500bbf137e361ba5d6cc3d83710b5'
    assert registration.verify_package(package)['integrity'] == 'sha256-verified'
    assert 'Klasa odporności ogniowej' in (package / 'python_host/PythonPartsScripts/PythonHost/column_layer.py').read_text()
    assert 'GetWallTierProperties(1)' in (package / 'python_host/PythonPartsScripts/PythonHost/wall_probe.py').read_text()
    assert "'phase': 'wall_sample'" in (package / 'src/allplan_mcp/wall_diagnostics.py').read_text()
    assert (package / 'M4 Columns to W1.cmd').is_file()
    assert (package / 'docs/m4-wall-properties-0.18.0.pl.md').is_file()
    assert (package / 'M4 Wall Properties.cmd').is_file()
    local = work / 'Local'
    local.mkdir()
    registration.register(package, local)
    bridge = json.loads((local / 'PythonPartsScripts/PythonHost/package_info.json').read_text())
    for name, sha in bridge['bridge_files'].items():
        assert hashlib.sha256((local / name).read_bytes()).hexdigest() == sha
    assert bridge['version'] == '0.18.0'
    with zipfile.ZipFile(repo / 'evaluation-packages/0.17.2/allplan-mcp-0.17.2-windows-evaluation.zip') as z:
        z.extractall(work / 'old')
    old = work / 'old/allplan-mcp-0.17.2'
    for name in ('python_host/PythonPartsScripts/PythonHost/column_layer.py', 'src/allplan_mcp/column_layer_diagnostics.py'):
        assert (old / name).read_bytes() == (package / name).read_bytes()
    registration.register(old, local)
    original = {str(p.relative_to(local)): p.read_bytes() for tree in registration.INSTALL_TREES for p in (local / tree).rglob('*') if p.is_file()}
    markers = {'.allplan-mcp/repairs/preserved.json': b'journal preservation marker', '.allplan-mcp/logs/m4-native-probe.jsonl': b'trace preservation marker'}
    for name, content in markers.items():
        p = local / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    result = registration.register(package, local)
    assert json.loads((local / 'PythonPartsScripts/PythonHost/package_info.json').read_text())['version'] == '0.18.0'
    for name, content in markers.items():
        assert (local / name).read_bytes() == content
    registration.restore(local, result['backup_id'])
    restored = {str(p.relative_to(local)): p.read_bytes() for tree in registration.INSTALL_TREES for p in (local / tree).rglob('*') if p.is_file()}
    assert restored == original
    for name, content in markers.items():
        assert (local / name).read_bytes() == content
with zipfile.ZipFile(artifacts / 'allplan_mcp_server-0.18.0-py3-none-any.whl') as z:
    assert 'Klasa odporności ogniowej' in z.read('allplan_mcp/column_layer_models.py').decode()
    assert "'phase': 'wall_sample'" in z.read('allplan_mcp/wall_diagnostics.py').decode()
    assert 'Version: 0.18.0' in z.read('allplan_mcp_server-0.18.0.dist-info/METADATA').decode()
with tarfile.open(artifacts / 'allplan_mcp_server-0.18.0.tar.gz') as t:
    assert not any('/evaluation-packages/' in name for name in t.getnames())
    path = 'allplan_mcp_server-0.18.0/python_host/PythonPartsScripts/PythonHost/wall_probe.py'
    assert 'GetWallTierProperties(1)' in t.extractfile(path).read().decode()
result = {'source_commit': manifest['source_commit'], 'source_modified': False,
          'payload_files': len(manifest['files']), 'bridge_hashes_verified': len(bridge['bridge_files']),
          'archive_integrity': 'sha256-verified', 'install_from_exact_zip': 'pass',
          'upgrade_from_0172': 'pass', 'restore_to_0172': 'pass', 'journal_and_trace_preserved': 'pass',
          'wheel_wall_diagnostic': 'pass', 'column_runtime_identical_to_0172': 'pass', 'zip_checksum': 'pass', 'sdist_includes_host_and_excludes_historical_packages': 'pass',
          'native_Allplan': 'not_run'}
(artifacts / 'package-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
