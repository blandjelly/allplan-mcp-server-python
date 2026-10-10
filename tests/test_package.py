import importlib.util
import json
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load("builder", ROOT / "utils/build_windows_package.py")
registration = load("registration_package", ROOT / "utils/register_python_host.py")
actions = load("windows_actions", ROOT / "windows/actions.py")


class PackageTests(unittest.TestCase):
    def test_deterministic_archive_integrity_and_fresh_install_from_extracted_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            first = builder.build(ROOT, work / "first")
            second = builder.build(ROOT, work / "second")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                archive.extractall(work / "extracted")
            package = next((work / "extracted").iterdir())
            manifest = registration.verify_package(package)
            self.assertEqual(manifest["integrity"], "sha256-verified")
            for name in ("Setup.cmd", "Launch Allplan MCP.cmd", "Connect Codex.cmd",
                         "Diagnostics.cmd", "Restore bridge.cmd", "M3 Recover.cmd",
                         "M3 Workflow Recover.cmd", "M3 Numbering.cmd", "M3 Numbering Recover.cmd",
                         "M3 Conflict.cmd", "M3 Conflict Recover.cmd"):
                self.assertTrue((package / name).is_file())
            self.assertEqual({p.name for p in package.glob("M*.cmd")},
                             {"M3 Recover.cmd", "M3 Workflow Recover.cmd", "M3 Numbering.cmd", "M3 Numbering Recover.cmd",
                              "M3 Conflict.cmd", "M3 Conflict Recover.cmd"})
            self.assertEqual({p.name for p in (package / "windows").glob("m*.cmd")},
                             {"m3-recover.cmd", "m3-workflow-recover.cmd", "m3-numbering.cmd", "m3-numbering-recover.cmd",
                              "m3-conflict.cmd", "m3-conflict-recover.cmd"})
            for retired in ("test-results", "probes", "reviews"):
                self.assertFalse((package / "docs" / retired).exists())
            local = work / "Allplan Local"
            local.mkdir()
            registration.register(package, local)
            self.assertTrue((local / "PythonPartsScripts/PythonHost/sandbox/executor.py").is_file())
            for name in ("model_context.py", "query_contracts.py", "model_query.py", "model_metadata.py", "native_readers.py", "spatial_contracts.py", "profile_contracts.py", "model_audit.py", "audit_contracts.py", "model_repair.py", "repair_contracts.py", "native_repairs.py", "repair_execution.py", "mark_numbering.py"):
                self.assertTrue((local / "PythonPartsScripts/PythonHost" / name).is_file())
            self.assertTrue((package / "src/allplan_mcp/query_models.py").is_file())
            self.assertEqual((package / "src/allplan_mcp/profiles/native-model-qa.demo.json").read_bytes(),
                             (package / "profiles/examples/native-model-qa.demo.json").read_bytes())
            self.assertEqual((package / "src/allplan_mcp/profiles/native-model-qa.audit.json").read_bytes(),
                             (package / "profiles/examples/native-model-qa.audit.json").read_bytes())
            (package / "python_host/PythonPartsScripts/PythonHost/sandbox/const.py").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "integrity"):
                registration.register(package, local)

    def test_missing_or_extra_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            archive = builder.build(ROOT, work)
            with zipfile.ZipFile(archive) as payload:
                payload.extractall(work / "extracted")
            package = next((work / "extracted").iterdir())
            (package / "python_host/PythonPartsScripts/PythonHost/unexpected.py").write_text("extra")
            with self.assertRaisesRegex(ValueError, "unexpected"):
                registration.verify_package(package)
            (package / "python_host/PythonPartsScripts/PythonHost/unexpected.py").unlink()
            (package / "python_host/PythonPartsScripts/PythonHost/sandbox/executor.py").unlink()
            with self.assertRaisesRegex(ValueError, "integrity"):
                registration.verify_package(package)

    def test_codex_setup_preserves_settings_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / ".codex/config.toml"
            config.parent.mkdir()
            original = 'model = "owner-model"\n[mcp_servers.other]\nurl = "https://example.com/mcp"\n'
            config.write_text(original)
            result = actions.connect_codex(config)
            self.assertEqual(Path(result["backup"]).read_text(), original)
            parsed = tomllib.loads(config.read_text())
            self.assertEqual(parsed["model"], "owner-model")
            self.assertEqual(parsed["mcp_servers"]["other"]["url"], "https://example.com/mcp")
            self.assertEqual(parsed["mcp_servers"]["allplan_m0"]["url"], actions.MCP_URL)
            before = config.read_bytes()
            self.assertEqual(actions.connect_codex(config)["status"], "already_configured")
            self.assertEqual(config.read_bytes(), before)
            config.write_text('[mcp_servers.allplan_m0]\nurl = "https://other.invalid"\n')
            with self.assertRaisesRegex(ValueError, "not been overwritten"):
                actions.connect_codex(config)

    def test_version_and_lock_agree(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        locked = tomllib.loads((ROOT / "uv.lock").read_text())
        package = next(p for p in locked["package"] if p["name"] == project["name"])
        self.assertEqual(package["version"], project["version"])
        from allplan_mcp import __version__
        self.assertEqual(__version__, project["version"])
