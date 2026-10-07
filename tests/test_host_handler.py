"""Fake-adapter checks only; these do not validate Allplan geometry or UI."""
import importlib
import json
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

HOST = Path(__file__).resolve().parents[1] / "python_host/PythonPartsScripts/PythonHost"


class HostHandlerTests(unittest.TestCase):
    def setUp(self):
        package = types.ModuleType("test_allplan_host")
        package.__path__ = [str(HOST)]
        self.settings = MagicMock()
        self.settings.AllplanVersion.Version.return_value = "2026.0"
        self.settings.AllplanVersion.MainReleaseName.return_value = "2026"
        self.settings.AllplanVersion.SubReleaseName.return_value = "2026.0"
        self.settings.AllplanVersion.WindowsReleaseName.return_value = ""
        self.geometry, self.base = MagicMock(), MagicMock()
        modules = {"test_allplan_host": package, "NemAll_Python_AllplanSettings": self.settings,
                   "NemAll_Python_Geometry": self.geometry, "NemAll_Python_BaseElements": self.base,
                   "NemAll_Python_BasisElements": MagicMock(), "NemAll_Python_IFW_Input": MagicMock()}
        # Isolate every import so fake adapters never leak into other tests.
        for name in list(sys.modules):
            if name.startswith("test_allplan_host."):
                modules[name] = None
        self.patch = patch.dict(sys.modules, modules)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for name in list(sys.modules):
            if name.startswith("test_allplan_host."):
                del sys.modules[name]
        self.module = importlib.import_module("test_allplan_host.PythonHostHandler")
        self.coord = MagicMock()
        self.handler = self.module.RequestHandler(self.coord)

    def test_runtime_reports_embedded_python_and_missing_hotfix_honestly(self):
        response = self.handler.handle("/get-allplan-version", {})
        self.assertEqual(response["version"], "2026.0")
        self.assertTrue(response["embedded_python"]["version"])
        self.assertEqual(response["hotfix"], {"status": "not_checked", "value": None})
        self.assertFalse(response["compatibility"]["runtime_verified"])
        json.dumps(response)

    def test_wrong_major_allows_diagnostics_but_rejects_model_operations(self):
        self.settings.AllplanVersion.MainReleaseName.return_value = "2027"
        self.assertFalse(self.handler.handle("/get-runtime-info", {})["compatibility"]["major_matches"])
        with self.assertRaises(self.module.BridgeError) as error:
            self.handler.handle("/create-box", {"length": 1000, "width": 1000, "height": 1000})
        self.assertEqual(error.exception.code, "incompatible_build")
        self.base.CreateElements.assert_not_called()

    def test_invalid_dimensions_never_write(self):
        for value in (None, True, "1000", -1, 0, float("nan"), float("inf")):
            with self.assertRaises(self.module.BridgeError) as error:
                self.handler.handle("/create-box", {"length": value, "width": 1000, "height": 1000})
            self.assertEqual(error.exception.code, "invalid_payload")
        self.base.CreateElements.assert_not_called()

    def test_current_document_is_resolved_for_each_box(self):
        first, second = object(), object()
        self.coord.GetInputViewDocument.side_effect = [first, second]
        payload = {"length": 1000, "width": 1000, "height": 1000}
        self.handler.handle("/create-box", payload)
        self.handler.handle("/create-box", payload)
        self.geometry.Polyhedron3D.CreateCuboid.assert_called_with(1000, 1000, 1000)
        self.assertEqual([c.args[0] for c in self.base.CreateElements.call_args_list], [first, second])

    def test_missing_session_and_disabled_exec_do_not_write(self):
        self.coord.GetInputViewDocument.return_value = None
        with self.assertRaises(self.module.BridgeError) as error:
            self.handler.handle("/get-all-object-names", {})
        self.assertEqual(error.exception.code, "session_unavailable")
        with patch.dict(os.environ, {"ALLPLAN_MCP_ENABLE_PYTHON_EXEC": "0"}):
            with self.assertRaises(self.module.BridgeError) as error:
                self.handler.handle("/execute-python", {"code": "result = 1"})
        self.assertEqual(error.exception.code, "development_disabled")
        self.base.CreateElements.assert_not_called()

    def prepare_context(self):
        self.base.ProjectService.GetCurrentProjectNameAndHost.return_value = ("Demo", "local")
        self.base.ProjectService.GetProjectPath.return_value = (0, "C:/Demo.prj")
        self.coord.GetInputViewDocument.return_value.GetDocumentID.return_value = 42
        self.base.DrawingFileService.GetActiveFileNumber.return_value = 101
        states = types.SimpleNamespace(ActiveForeground=3, ActiveBackground=2, PassiveBackground=1)
        self.base.DrawingFileLoadState = states
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(102, 1), (101, 3), (104, 2)]
        self.base.DrawingFileService.GetDrawingFileName.side_effect = lambda number: (True, f"File {number}")
        self.settings.GetLengthUnit.return_value = 3
        self.settings.GetAngleUnit.return_value = 0
        self.settings.AllplanGlobalSettings.GetOffsetPoint.return_value = types.SimpleNamespace(X=0, Y=250, Z=0)

    def test_context_is_read_only_includes_empty_loaded_files_and_honest_limits(self):
        self.prepare_context()
        response = self.handler.handle("/get-model-context", {})
        self.assertEqual(response["document_id"]["value"], 42)
        self.assertEqual(response["active_drawing_file"]["value"], 101)
        files = response["loaded_drawing_files"]["value"]
        self.assertEqual([f["state"] for f in files], ["active_foreground", "passive_background", "active_background"])
        self.assertEqual(response["project_offset"]["value"]["xyz"], [0, 250, 0])
        self.assertEqual(response["project_offset"]["value"]["unit"], "api_native")
        self.assertEqual(response["coverage"]["unloaded_files"], "not_enumerated")
        self.assertEqual(response["levels"]["status"], "not_checked")
        self.assertFalse(response["project"]["value"]["durable_identity_verified"])
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.CreateElements.assert_not_called()
        json.dumps(response, allow_nan=False)

    def test_context_missing_reads_are_not_empty_success_and_project_is_fresh(self):
        self.prepare_context()
        first = self.handler.handle("/get-model-context", {})
        self.base.ProjectService.GetCurrentProjectNameAndHost.return_value = ("Other", "local")
        second = self.handler.handle("/get-model-context", {})
        self.assertNotEqual(first["project"]["value"]["key"], second["project"]["value"]["key"])
        self.base.DrawingFileService.return_value.GetFileState.side_effect = RuntimeError("unavailable")
        self.base.ProjectService.GetProjectPath.return_value = (1, "")
        self.settings.AllplanGlobalSettings.GetOffsetPoint.return_value.X = float("nan")
        failed = self.handler.handle("/get-model-context", {})
        self.assertEqual(failed["project"]["value"]["name"], "Other")
        self.assertEqual(failed["project"]["value"]["key_status"], "not_checked")
        self.assertIsNone(failed["project"]["value"]["key"])
        for field in ("loaded_drawing_files", "project_offset"):
            self.assertEqual(failed[field]["status"], "not_checked")
            self.assertIsNone(failed[field]["value"])
        json.dumps(failed, allow_nan=False)

    def test_project_path_order_fallback_is_read_only_and_retains_failed_attempt(self):
        self.prepare_context()
        self.base.ProjectService.GetProjectPath.side_effect = lambda first, second: (
            ("Project not found", "") if first == "Demo" else ("", "C:/Demo.prj"))
        response = self.handler.handle("/get-model-context", {})
        project = response["project"]["value"]
        self.assertEqual(project["name"], "Demo")
        self.assertEqual(project["key_status"], "observed")
        attempts = project["path_lookup_attempts"]
        self.assertEqual(attempts[0]["value"]["error"], "Project not found")
        self.assertEqual(attempts[1]["argument_order"], "host_name_project_name")
        self.assertFalse(project["durable_identity_verified"])
        self.base.ProjectService.OpenProject.assert_not_called()

    def test_path_exception_and_boolean_status_do_not_hide_project_or_create_key(self):
        self.prepare_context()
        for behavior in (RuntimeError("unavailable"), (True, "C:/Demo.prj")):
            if isinstance(behavior, Exception):
                self.base.ProjectService.GetProjectPath.side_effect = behavior
            else:
                self.base.ProjectService.GetProjectPath.side_effect = None
                self.base.ProjectService.GetProjectPath.return_value = behavior
            response = self.handler.handle("/get-model-context", {})
            project = response["project"]["value"]
            self.assertEqual(project["name"], "Demo")
            self.assertIsNone(project["key"])
            self.assertEqual(project["path_lookup_attempts"][0]["status"], "not_checked")

    def test_identity_sample_is_bounded_raw_and_separates_model_and_view(self):
        self.prepare_context()
        adapter = MagicMock()
        adapter.GetDrawingfileNumber.return_value = -102
        adapter.GetModelElementUUID.return_value = "{12345678-1234-4234-8234-123456789012}"
        adapter.GetElementUUID.return_value = "87654321-4321-4321-8321-210987654321"
        adapter.GetDisplayName.return_value = "Column"
        adapter.IsInActiveDocument.return_value = False
        self.base.ElementsSelectService.SelectAllElements.return_value = [adapter, adapter, adapter]
        response = self.handler.handle("/get-model-context", {"identity_sample_size": 2})
        items = response["identity_sample"]["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["signed_drawing_file_number"]["value"], -102)
        self.assertNotEqual(items[0]["model_uuid"]["value"], items[0]["view_uuid"]["value"])
        self.assertFalse(items[0]["usable_for_write"])
        adapter.GetAttributes.assert_not_called()
        adapter.GetModelGeometry.assert_not_called()
        adapter.GetModelElementUUID.return_value = "<native object repr>"
        response = self.handler.handle("/get-model-context", {"identity_sample_size": 1})
        self.assertEqual(response["identity_sample"]["items"][0]["model_uuid"]["status"], "not_checked")

    def test_context_rejects_invalid_parameters_without_selecting_or_writing(self):
        for request in ({"identity_sample_size": True}, {"identity_sample_size": -1},
                        {"identity_sample_size": 21}, {"identity_sample_size": 1.5}, {"scope": "project"}):
            with self.assertRaises(self.module.BridgeError) as error:
                self.handler.handle("/get-model-context", request)
            self.assertEqual(error.exception.code, "invalid_payload")
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.CreateElements.assert_not_called()
