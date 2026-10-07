"""Dependency-free M1.1 read probe; live APIs are injected by the UI handler."""
from __future__ import annotations

import hashlib
import json
import math
from itertools import islice
from uuid import UUID

from .transport import BridgeError


def observation(reader):
    """Keep failed reads distinct from empty, zero or false values."""
    try:
        value = reader()
        json.dumps(value, allow_nan=False)
        return {"status": "observed", "value": value}
    except Exception as exc:
        return {"status": "not_checked", "value": None, "reason": type(exc).__name__}


def integer(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Expected an integer")
    return value


def text(value):
    if not isinstance(value, str):
        raise ValueError("Expected text")
    return value


def boolean(value):
    if not isinstance(value, bool):
        raise ValueError("Expected a boolean")
    return value


def guid(value):
    # Never publish a native object's repr as a reusable model reference.
    result = UUID(str(value).strip("{}"))
    if result.int == 0:
        raise ValueError("Empty GUID")
    return str(result)


def context_probe(doc, base, settings, request):
    limit = request.get("identity_sample_size", 0)
    if set(request) - {"identity_sample_size"} or isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= 20:
        raise BridgeError("invalid_payload", "identity_sample_size must be an integer from 0 to 20; no other fields are accepted.")

    def project():
        name, host = base.ProjectService.GetCurrentProjectNameAndHost()
        name, host = text(name), text(host)
        if not name:
            raise ValueError("Empty project name")
        result = {"name": name, "host": host, "key": None, "key_status": "not_checked",
                  "key_kind": "name_host_path_sha256", "durable_identity_verified": False,
                  "path_lookup_attempts": []}
        # Published references disagree about positional argument order. Both
        # calls are reads. Preserve each result instead of hiding name/host when
        # path resolution fails; never manufacture a durable project identity.
        for order, arguments in (("project_name_host_name", (name, host)),
                                 ("host_name_project_name", (host, name))):
            def lookup(arguments=arguments):
                error, path = base.ProjectService.GetProjectPath(*arguments)
                if isinstance(error, bool) or not isinstance(error, (str, int)):
                    raise ValueError("Unexpected project-path error type")
                return {"error": error, "path": text(path)}
            attempt = {"argument_order": order, **observation(lookup)}
            result["path_lookup_attempts"].append(attempt)
            if attempt["status"] == "observed":
                value = attempt["value"]
                if value["error"] in (0, "") and value["path"]:
                    result["key"] = hashlib.sha256(json.dumps(
                        [name, host, value["path"]], ensure_ascii=False).encode()).hexdigest()
                    result["key_status"] = "observed"
                    break
        return result

    def files():
        service = base.DrawingFileService()
        states = base.DrawingFileLoadState
        mapping = ((states.ActiveForeground, "active_foreground"),
                   (states.ActiveBackground, "active_background"),
                   (states.PassiveBackground, "passive_background"))
        result = []
        for number, state in service.GetFileState():
            number = integer(number)
            if number <= 0:
                raise ValueError("Invalid drawing-file number")
            normalized = next((label for native, label in mapping if state == native), "unknown")
            def file_name(number=number):
                success, name = base.DrawingFileService.GetDrawingFileName(number)
                if not success:
                    raise ValueError("Drawing-file name unavailable")
                return text(name)
            result.append({"number": number, "state": normalized, "name": observation(file_name),
                           "write_eligibility": "not_checked"})
        return sorted(result, key=lambda item: item["number"])

    def offset():
        point = settings.AllplanGlobalSettings.GetOffsetPoint()
        values = [float(point.X), float(point.Y), float(point.Z)]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Non-finite project offset")
        return {"xyz": values, "unit": "api_native", "conversion_to_mm": "not_checked",
                "application_to_model_coordinates": "not_checked"}

    result = {
        "schema_version": "m1-context-probe-1", "read_only": True,
        "runtime_verified": False,
        "project": observation(project),
        "document_id": observation(lambda: integer(doc.GetDocumentID())),
        "active_drawing_file": observation(lambda: integer(base.DrawingFileService.GetActiveFileNumber())),
        "loaded_drawing_files": observation(files),
        "units": {"canonical_length": "mm", "canonical_angle": "deg",
                  "input_length": observation(lambda: integer(int(settings.GetLengthUnit()))),
                  "input_angle": observation(lambda: integer(int(settings.GetAngleUnit()))),
                  "input_unit_encoding": "Allplan 2026 LengthUnits/AngleUnits enum",
                  "geometry_conversion": "not_checked"},
        "project_offset": observation(offset),
        "levels": {"status": "not_checked", "value": None},
        "capabilities": {"context": "probe_only", "model_query": "implemented_runtime_pending",
                         "reusable_selections": "session_bound_read_only_runtime_pending", "model_write": "not_supported_by_this_tool"},
        "coverage": {"file_inventory": "loaded_only", "unloaded_files": "not_enumerated",
                     "visibility": "API_selection_semantics_not_verified",
                     "native_component_counts": "not_checked"},
        "identity_sample": {"requested": limit, "items": [], "coverage": "not_requested"},
    }
    if limit:
        def sample():
            items = []
            # Do not read geometry/attributes. This is a bounded raw-adapter sample,
            # not a deduplicated component query or an edit target.
            adapters = base.ElementsSelectService.SelectAllElements(doc)
            for adapter in islice(adapters, limit):
                items.append({
                    "signed_drawing_file_number": observation(lambda: integer(adapter.GetDrawingfileNumber())),
                    "model_uuid": observation(lambda: guid(adapter.GetModelElementUUID())),
                    "view_uuid": observation(lambda: guid(adapter.GetElementUUID())),
                    "display_name": observation(lambda: text(adapter.GetDisplayName())),
                    "in_active_document": observation(lambda: boolean(adapter.IsInActiveDocument())),
                    "usable_for_write": False,
                })
            return items
        sampled = observation(sample)
        result["identity_sample"].update({"items": sampled["value"] or [],
                                         "status": sampled["status"],
                                         "coverage": "bounded_raw_adapters_not_component_count"})
        if "reason" in sampled:
            result["identity_sample"]["reason"] = sampled["reason"]
    return result
