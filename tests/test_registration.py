import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("registration", ROOT / "utils/register_python_host.py")
registration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registration)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.local = self.root / "redirected Documents/Allplan/Usr/Local"
        self.local.mkdir(parents=True)
        self.repo = self.root / "package"
        shutil.copytree(ROOT / "python_host", self.repo / "python_host")
        shutil.copy2(ROOT / "pyproject.toml", self.repo / "pyproject.toml")

    def test_fresh_install_contains_imported_sandbox_and_excludes_caches(self):
        scripts = self.repo / "python_host/PythonPartsScripts/PythonHost"
        (scripts / "sandbox/__pycache__").mkdir(exist_ok=True)
        (scripts / "sandbox/__pycache__/bad.pyc").write_bytes(b"cache")
        (scripts / "sandbox/other.pyo").write_bytes(b"cache")
        result = registration.register(self.repo, self.local)
        installed = self.local / "PythonPartsScripts/PythonHost"
        for filename in ("__init__.py", "executor.py", "validator.py", "const.py"):
            self.assertEqual((installed / "sandbox" / filename).read_bytes(), (scripts / "sandbox" / filename).read_bytes())
        self.assertTrue((self.local / "Library/PythonHost/StartPythonHost.pyp").is_file())
        self.assertFalse((self.local / "PythonParts/PythonHost").exists())
        self.assertFalse((installed / "sandbox/__pycache__").exists())
        self.assertFalse((installed / "sandbox/other.pyo").exists())
        self.assertEqual(json.loads((installed / "package_info.json").read_text())["version"], result["version"])
        registration.restore(self.local, result["backup_id"])
        self.assertFalse(installed.exists())
        self.assertFalse((self.local / "Library/PythonHost").exists())

    def test_repeat_install_removes_stale_files_and_restores_previous_package(self):
        registration.register(self.repo, self.local)
        installed = self.local / "PythonPartsScripts/PythonHost"
        (installed / "old-module.py").write_text("previous")
        (installed / "sandbox/const.py").write_text("previous constants")
        result = registration.register(self.repo, self.local)
        self.assertFalse((installed / "old-module.py").exists())
        self.assertNotEqual((installed / "sandbox/const.py").read_text(), "previous constants")
        registration.restore(self.local, result["backup_id"])
        self.assertEqual((installed / "old-module.py").read_text(), "previous")
        self.assertEqual((installed / "sandbox/const.py").read_text(), "previous constants")

    def test_incomplete_package_does_not_touch_existing_installation(self):
        registration.register(self.repo, self.local)
        installed = self.local / "PythonPartsScripts/PythonHost/sandbox/const.py"
        before = installed.read_bytes()
        (self.repo / "python_host/PythonPartsScripts/PythonHost/sandbox/executor.py").unlink()
        with self.assertRaises(FileNotFoundError):
            registration.register(self.repo, self.local)
        self.assertEqual(installed.read_bytes(), before)

    def test_failed_copy_rolls_back_both_trees(self):
        registration.register(self.repo, self.local)
        pyp = self.local / "Library/PythonHost/StartPythonHost.pyp"
        pyp.write_text("previous palette")
        scripts = self.local / "PythonPartsScripts/PythonHost"
        (scripts / "previous.py").write_text("previous script")
        current = self.local / registration.STATE_FOLDER / "current.json"
        before = current.read_bytes()
        original = registration.shutil.copytree
        def fail_second_tree(source, destination, *args, **kwargs):
            if Path(source).parent.parent.name.startswith("stage-") and Path(destination).resolve() == scripts.resolve():
                raise OSError("simulated copy failure")
            return original(source, destination, *args, **kwargs)
        with patch.object(registration.shutil, "copytree", side_effect=fail_second_tree):
            with self.assertRaisesRegex(OSError, "simulated"):
                registration.register(self.repo, self.local)
        self.assertEqual(pyp.read_text(), "previous palette")
        self.assertEqual((scripts / "previous.py").read_text(), "previous script")
        self.assertTrue((self.local / "PythonPartsScripts/PythonHost/sandbox/executor.py").exists())
        self.assertEqual(current.read_bytes(), before)

    def test_dry_run_does_not_create_installation_or_state(self):
        registration.register(self.repo, self.local, dry_run=True)
        self.assertEqual(list(self.local.iterdir()), [])

    def test_missing_user_path_and_invalid_restore_are_rejected(self):
        with self.assertRaises(FileNotFoundError):
            registration.register(self.repo, self.local / "does-not-exist")
        for name in ("../escape", "..", "..\\escape"):
            with self.assertRaises(ValueError):
                registration.restore(self.local, name)

    def test_incomplete_backup_does_not_replace_current_installation(self):
        registration.register(self.repo, self.local)
        result = registration.register(self.repo, self.local)
        backup = self.local / registration.STATE_FOLDER / "backups" / result["backup_id"]
        (backup / "PythonPartsScripts/PythonHost/sandbox/const.py").unlink()
        current = self.local / "PythonPartsScripts/PythonHost/sandbox/const.py"
        before = current.read_bytes()
        with self.assertRaisesRegex(ValueError, "Backup integrity"):
            registration.restore(self.local, result["backup_id"])
        self.assertEqual(current.read_bytes(), before)

    def test_runtime_diagnostic_checks_actual_installed_files(self):
        registration.register(self.repo, self.local)
        file = self.local / "PythonPartsScripts/PythonHost/runtime_info.py"
        spec = importlib.util.spec_from_file_location("installed_runtime_info", file)
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        class Versions:
            @staticmethod
            def Version(): return "2026.0"
            @staticmethod
            def MainReleaseName(): return "2026"
            @staticmethod
            def SubReleaseName(): return "2026.0"
            @staticmethod
            def WindowsReleaseName(): return ""
        self.assertEqual(runtime.runtime_info(Versions)["installed_bridge_integrity"]["status"], "verified")
        (file.parent / "sandbox/const.py").write_text("modified after installation")
        result = runtime.runtime_info(Versions)
        self.assertEqual(result["installed_bridge_integrity"]["status"], "mismatch")
        self.assertIn("PythonPartsScripts/PythonHost/sandbox/const.py", result["installed_bridge_integrity"]["mismatches"])
        (file.parent / "package_info.json").write_text("[]")
        self.assertEqual(runtime.runtime_info(Versions)["installed_bridge_integrity"]["status"], "not_checked")

    def test_upgrade_moves_legacy_library_item_and_restore_recovers_previous_layout(self):
        legacy = self.local / "PythonParts/PythonHost"
        legacy.mkdir(parents=True)
        (legacy / "StartPythonHost.pyp").write_text("previous PYP")
        scripts = self.local / "PythonPartsScripts/PythonHost"
        scripts.mkdir(parents=True)
        (scripts / "previous.py").write_text("previous script")
        other = self.local / "Library/OtherPart/Other.pyp"
        other.parent.mkdir(parents=True)
        other.write_text("unrelated")
        result = registration.register(self.repo, self.local)
        installed = self.local / "Library/PythonHost/StartPythonHost.pyp"
        self.assertTrue(installed.is_file())
        self.assertFalse(legacy.exists())
        # Windows may return the long name for a temporary path using an 8.3 alias.
        self.assertTrue(Path(result["pythonpart_path"]).samefile(installed))
        self.assertEqual(other.read_text(), "unrelated")
        backup = self.local / registration.STATE_FOLDER / "backups" / result["backup_id"]
        record_path = backup / "backup.json"
        record = json.loads(record_path.read_text())
        # 0.1.1 backup records listed legacy PYP before scripts; order is irrelevant.
        record["present"] = ["PythonParts/PythonHost", "PythonPartsScripts/PythonHost"]
        record_path.write_text(json.dumps(record))
        registration.restore(self.local, result["backup_id"])
        self.assertFalse(installed.exists())
        self.assertEqual((legacy / "StartPythonHost.pyp").read_text(), "previous PYP")
        self.assertEqual((scripts / "previous.py").read_text(), "previous script")
        self.assertEqual(other.read_text(), "unrelated")
