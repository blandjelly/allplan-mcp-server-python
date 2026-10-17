"""One native single-tier Wall read; never a material-edit adapter."""
from __future__ import annotations

import importlib
import math

from .model_context import integer
from .model_metadata import bounded_text
from .query_contracts import SCHEMA
from .transport import BridgeError


class _ReadStopped(Exception):
    pass


def positive_length(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 1_000_000:
        raise ValueError("Expected a finite positive native length in mm.")
    return float(value)


def sample_wall(queries, doc, base, settings, request, trace, budget):
    query = {"schema_version": SCHEMA, "action": "query",
             "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False, "visibility": "api_select_all"},
             "component_kind": "top_level_component", "fields": ["display_name", "file_state"],
             "predicate": {"field": "type_name", "op": "eq", "value": "Wall_TypeUUID"}}
    live, native_owners = {}, []
    snapshot = trace.call("M1.wall_scan", lambda: queries._scan(doc, base, settings, query,
        adapter_sink=live, adapter_owners=native_owners, native_type_gate="Wall_TypeUUID"))
    budget()
    if (not snapshot["coverage"]["requested_scope_complete"]
            or not snapshot["coverage"]["returned_fields_complete"]
            or snapshot["scope"]["included_files"] != [{"drawing_file": request["drawing_file"],
                    "state": "active_foreground", "write_eligibility": "not_checked"}]):
        raise BridgeError("probe_scope_unavailable", "Wall sample requires complete root evidence in one foreground drawing.", 409)
    candidates = [e for e in snapshot["elements"] if "model_uuid" not in request or e["ref"]["model_uuid"] == request["model_uuid"]]
    if not candidates:
        raise BridgeError("probe_scope_unavailable", "Requested Wall root is absent; no substitute was sampled.", 409)
    element = candidates[0]  # M1 orders by drawing file, then model UUID.
    ref = element["ref"]
    views = live.get((ref["drawing_file"], ref["model_uuid"]), {})
    if (element["view_identity_not_checked"] or len(views) != 1
            or set(views) != set(element["view_uuids"])):
        raise BridgeError("probe_scope_unavailable", "Wall sample requires one unambiguous root view.", 409)
    adapters = next(iter(views.values()))
    if not adapters:
        raise BridgeError("probe_scope_unavailable", "Wall sample has ambiguous adapter representations.", 409)
    # M1 resolves axes/tiers to roots, groups by drawing file/model/view UUID
    # and rejects conflicting root fields. Native calls may return distinct
    # Python wrappers for that same root. Python `is` cannot identify a native
    # Wall; choose one wrapper only after complete, single-view M1 evidence.
    adapter = adapters[0]
    report = {"state": "not_checked", "scope": snapshot["scope"], "coverage": snapshot["coverage"],
              "counts": {**snapshot["counts"], "sampled_walls": 1},
              "sample": {"ref": ref, "fields": element["fields"], "native_reads": [],
                         "adapter_resolution": {"method": "consistent_m1_root_identity",
                                                "view_uuid": next(iter(views)),
                                                "representations": len(adapters)}},
              "sample_order": "drawing_file_then_model_uuid", "is_full_wall_filter": False,
              "native_length_unit": "mm", "units_runtime_verified": False,
              "geometry_kind": "not_checked", "material_target_binding": "not_checked",
              "material_write_available": False, "attribute_reads": "not_requested",
              "definition_reads": "not_requested", "enum_reads": "not_requested"}
    sample = report["sample"]

    def read(api, reader):
        budget()
        try:
            value = trace.call(api, reader, drawing_file=ref["drawing_file"], model_uuid=ref["model_uuid"])
        except BridgeError:
            raise
        except Exception as exc:
            sample["native_reads"].append({"api": api, "status": "not_checked", "reason": type(exc).__name__})
            report["failed_api"] = api
            raise _ReadStopped from exc
        sample["native_reads"].append({"api": api, "status": "observed"})
        budget()
        return value

    try:
        arch = read("Python.import.NemAll_Python_ArchElements", lambda: importlib.import_module("NemAll_Python_ArchElements"))
        native = read("BaseElements.GetElement", lambda: base.GetElement(adapter))
        if not isinstance(native, arch.WallElement):
            report.update(state="unsupported", reason="GetElement_did_not_return_WallElement")
            return report
        props = read("WallElement.Properties", lambda: native.Properties)
        count = read("WallProperties.TierCount", lambda: integer(props.TierCount))
        sample["tier_count"] = count
        if count != 1:
            report.update(state="unsupported", reason="requires_exactly_one_wall_tier_no_tier_was_chosen")
            return report
        tier = read("WallProperties.GetWallTierProperties(1)", lambda: props.GetWallTierProperties(1))
        thickness = read("WallTierProperties.Thickness", lambda: positive_length(tier.Thickness))
        sample["total_thickness_mm"] = {"status": "observed", "value": thickness,
                                       "source": "single_tier_native_Thickness", "unit": "mm"}
        material = read("WallTierProperties.Material", lambda: bounded_text(tier.Material))
        sample["native_material"] = {"status": "observed", "value": material, "source": "WallTierProperties.Material"}
        sample["criterion"] = {"property": "wall.total_thickness", "operator": "lt", "threshold_mm": 240.0,
                               "matches_assuming_native_mm": thickness < 240.0, "usable_for_write": False}
        report["state"] = "observed"
    except _ReadStopped:
        pass  # First failed read stops; no fallback, retry or later property read.
    return report
