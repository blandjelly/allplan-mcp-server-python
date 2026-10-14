from __future__ import annotations

import math
import os

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_BaseElements as AllplanBaseEle

from .sandbox import SandboxExecutor
from .runtime_info import runtime_info
from .transport import BridgeError
from .model_context import context_probe
from .model_query import ModelQueryService
from .query_contracts import validate_request


class RequestHandler:
    """Handle bridge requests"""

    def __init__(self,
                 coord_input : AllplanIFW.CoordinateInput):
        """Build the handler"""

        self.coord_input = coord_input
        self.sandbox_executor = SandboxExecutor(coord_input)
        self.model_queries = ModelQueryService()
        from .property_probe import PropertyProbeService
        self.property_probes = PropertyProbeService(self.model_queries)
        from .model_repair import RepairPlanService
        self.repair_plans = RepairPlanService(self.model_queries)

    def handle(self, path: str, request : dict):
        """Route one bridge request"""

        if not isinstance(request, dict):
            raise BridgeError("invalid_payload", "Request body must be a JSON object.")
        if path == "/model-properties":
            from .property_contracts import validate_properties
            validate_properties(request)
            # 0.16.0 crashed natively on its first discovery request. Reject
            # before build/document/API reads until the offending operation is
            # isolated and a narrower native probe has been reviewed.
            raise BridgeError("native_probe_blocked", "M4 property discovery is suspended after the 0.16.0 native crash. Preserve bridge.log; do not repeat the broad probe.", 409)
        if path == "/column-layer":
            from .column_layer import validate_request as validate_column_layer
            validate_column_layer(request)
        if path == "/model-selection":
            from .property_contracts import validate_selection
            validate_selection(request)
        if path == "/model-property-probe":
            from .property_contracts import validate_probe
            validate_probe(request)
        if path == "/model-audit":
            from .audit_contracts import validate_audit_request
            validate_audit_request(request)
        if path == "/fix-model-issues":
            from .repair_contracts import validate_repair_request
            validate_repair_request(request)
            if request["action"] == "inspect_journal":
                return self.repair_plans.executor.inspect_journal()
        if path not in {"/get-allplan-version", "/get-runtime-info"}:
            major = AllplanSettings.AllplanVersion.MainReleaseName()
            if str(major) != "2026":
                raise BridgeError("incompatible_build", f"This evaluation package targets Allplan 2026; detected {major}.", 409)
        match path:
            case "/get-allplan-version":
                return self.handle_get_allplan_version(request)

            case "/get-runtime-info":
                return runtime_info(AllplanSettings.AllplanVersion)

            case "/get-all-object-names":
                return self.handle_get_all_object_names(request)

            case "/get-model-context":
                context = context_probe(self.current_document(), AllplanBaseEle, AllplanSettings, request)
                context["runtime"] = runtime_info(AllplanSettings.AllplanVersion)
                return context

            case "/model-query":
                validate_request(request)
                return self.model_queries.handle(self.current_document(), AllplanBaseEle, AllplanSettings, request)

            case "/column-layer":
                return self.repair_plans.handle_column_layer(self.current_document(), AllplanBaseEle, AllplanSettings, AllplanIFW, request)

            case "/model-property-probe":
                return self.property_probes.handle(self.current_document, AllplanBaseEle, AllplanSettings, request)

            case "/model-selection":
                if request["action"] != "select":
                    for entry in self.repair_plans.plans.values():
                        entry.pop("presentation", None)
                from .model_selection import present_selection
                return present_selection(self.model_queries, self.current_document(), AllplanBaseEle, AllplanSettings, AllplanIFW, request)

            case "/model-audit":
                from .model_audit import run_audit
                return run_audit(self.model_queries, self.current_document(), AllplanBaseEle, AllplanSettings, request)

            case "/fix-model-issues":
                return self.repair_plans.handle(self.current_document(), AllplanBaseEle, AllplanSettings, request)

            case "/create-box":
                return self.handle_create_box(request)

            case "/execute-python":
                return self.handle_execute_python(request)

            case _:
                raise BridgeError("unknown_route", f"Unknown request path: {path}", 404)

    def handle_get_allplan_version(self, request : dict):
        """Get the Allplan version"""

        return runtime_info(AllplanSettings.AllplanVersion)

    def handle_get_all_object_names(self, request : dict):
        """Get object names"""

        # get object names
        doc = self.current_document()
        base_elements = AllplanBaseEle.ElementsSelectService.SelectAllElements(doc)

        # create response
        names = [base_element.GetDisplayName() for base_element in base_elements]
        return { "names": names }

    def handle_create_box(self, request : dict):
        """Create a box"""

        # get request parameters
        values = [request.get(name) for name in ("length", "width", "height")]
        if any(isinstance(value, bool) or not isinstance(value, (float, int))
               or not math.isfinite(value) or value <= 0 for value in values):
            raise BridgeError("invalid_payload", "length, width and height must be finite positive numbers in mm.")
        length, width, height = values

        doc = self.current_document()

        # create cuboid in memory
        cuboid = AllplanGeo.Polyhedron3D.CreateCuboid(length, width, height)

        # place cuboid inside document
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        model_ele_list = [AllplanBasisElements.ModelElement3D(com_prop, cuboid)]
        AllplanBaseElements.CreateElements(doc, AllplanGeo.Matrix3D(), model_ele_list, [], None)

    def handle_execute_python(self, request: dict):
        """Run sandbox code"""

        if os.getenv("ALLPLAN_MCP_ENABLE_PYTHON_EXEC") != "1":
            raise BridgeError("development_disabled", "Python execution is disabled; use typed tools.", 403)
        self.current_document()
        return self.sandbox_executor.execute(request)

    def current_document(self):
        """Resolve the current document per request instead of caching a model."""
        try:
            doc = self.coord_input.GetInputViewDocument()
        except Exception as exc:
            raise BridgeError("session_unavailable", "Open a project and restart StartPythonHost.", 503) from exc
        if doc is None:
            raise BridgeError("session_unavailable", "No input document is available. Open a project and restart StartPythonHost.", 503)
        return doc
