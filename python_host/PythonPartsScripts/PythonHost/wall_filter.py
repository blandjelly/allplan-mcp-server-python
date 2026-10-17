"""Read-only, bounded whole-drawing Wall thickness filter and presentation."""
from __future__ import annotations

import importlib
import math
import re
from pathlib import Path

from .model_context import integer
from .property_probe import NativeProbeTrace
from .query_contracts import bounded_int, invalid, keys
from .transport import BridgeError
from .wall_probe import positive_length

SCHEMA = "m4-wall-filter-1"
WALL_TYPE = "Wall_TypeUUID"
UUID_RE = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
UNIT_TO_MM = {"mm": 1.0, "cm": 10.0, "m": 1000.0}


def validate_request(request):
    """Validate the complete wire contract before requesting a native document."""
    if not isinstance(request, dict) or request.get("schema_version") != SCHEMA:
        invalid("Expected m4-wall-filter-1 request.")
    keys(request, {"schema_version", "action", "drawing_file", "threshold", "exclude_model_uuids", "max_walls"},
         {"schema_version", "action", "drawing_file"})
    if request["action"] not in ("query", "highlight"):
        invalid("action must be query or highlight.")
    bounded_int(request["drawing_file"], 1, 2147483647, "drawing_file")
    threshold = request.get("threshold", {"value": 24, "unit": "cm"})
    if not isinstance(threshold, dict):
        invalid("threshold must contain a positive value and unit.")
    keys(threshold, {"value", "unit"}, {"value", "unit"})
    value, unit = threshold["value"], threshold["unit"]
    if type(value) not in (int, float) or not 0 < value <= 1_000_000 or not math.isfinite(value):
        invalid("threshold.value must be finite, positive and at most 1000000.")
    if not isinstance(unit, str) or unit not in UNIT_TO_MM:
        invalid("threshold.unit must be mm, cm or m.")
    if value * UNIT_TO_MM[unit] > 1_000_000:
        invalid("Converted threshold must be at most 1000000 mm.")
    ids = request.get("exclude_model_uuids", [])
    if (not isinstance(ids, list) or len(ids) > 100
            or any(not isinstance(item, str) or not UUID_RE.fullmatch(item)
                   or item == "00000000-0000-0000-0000-000000000000" for item in ids)
            or len(set(ids)) != len(ids)):
        invalid("exclude_model_uuids must contain distinct nonzero canonical UUIDs (at most 100).")
    bounded_int(request.get("max_walls", 20), 1, 100, "max_walls")


class WallFilterService:
    def __init__(self, queries, trace_path=None):
        self.queries = queries
        self.trace_path = trace_path or Path(__file__).resolve().parents[2] / ".allplan-mcp/logs/m4-native-probe.jsonl"

    def handle(self, document_reader, base, settings, ifw, request):
        validate_request(request)
        threshold_request = request.get("threshold") or {"value": 24, "unit": "cm"}
        trace = NativeProbeTrace(self.trace_path, "wall_filter_" + request["action"])
        started = self.queries.clock()
        threshold_mm = float(threshold_request["value"] * UNIT_TO_MM[threshold_request["unit"]])
        report = {"schema_version": SCHEMA, "action": request["action"], "state": "blocked",
                  "probe_id": trace.probe_id, "trace_file": "Local/.allplan-mcp/logs/m4-native-probe.jsonl",
                  "read_only": True, "model_data_changed": False, "usable_for_write": False,
                  "runtime_verified": False, "is_full_wall_filter": False,
                  "exclude_model_uuids": sorted(request.get("exclude_model_uuids", [])),
                  "material_write_available": False, "native_selection": "unsupported",
                  "ui_visibility": "requires_owner_observation", "units_runtime_verified": False,
                  "native_length_unit": "mm", "is_full_wall_filter": False,
                  "native_calls_not_automatically_retried": True, "ui_calls_started": False,
                  "threshold": {"property": "wall.total_thickness", "operator": "lt",
                                "value": threshold_mm, "unit": "mm"},
                  "scope": None, "coverage": {"m1_complete": False, "criteria_complete": False,
                                                "read_complete": False},
                  "criterion_complete": False,
                  "walls": [], "omissions": [],
                  "counts": {"walls": 0, "matched": 0, "excluded": 0, "unreadable": 0,
                             "unprocessed": 0, "not_editable": None, "requested_model_identities": 0,
                             "requested_adapters": 0, "submitted_model_identities": None,
                             "submitted_adapters": None, "selected": None, "highlighted": None,
                             "not_visible": None}}

        def budget():
            if self.queries.clock() - started >= self.queries.SCAN_SECONDS:
                raise BridgeError("scan_limit_exceeded", "Wall filter exceeded its five-second native read budget.", 409)

        def call(api, reader, **details):
            budget()
            result = trace.call(api, reader, **details)
            budget()
            return result

        def blocked(reason, *, state="blocked"):
            report["state"] = state
            report["message"] = reason
            report["coverage"]["criteria_complete"] = False
            report["criterion_complete"] = False
            report["is_full_wall_filter"] = False
            report["counts"]["matched"] = sum(w.get("match") is True for w in report["walls"])
            report["counts"]["excluded"] = sum(w.get("status") == "excluded" for w in report["walls"])
            report["counts"]["unreadable"] = sum(w.get("status") == "unreadable" for w in report["walls"])
            report["counts"]["unprocessed"] = max(0, report["counts"]["walls"] - len(report["walls"]))
            return report

        def complete():
            try:
                trace.record("wall_filter", "completed")
            except BridgeError as exc:
                if not report["ui_calls_started"]:
                    raise
                report.update(state="unknown", message="UI calls completed but the final trace record failed: " + exc.code)
            return report

        try:
            doc = call("CoordinateInput.GetInputViewDocument", document_reader)
            query = {"schema_version": "m1-query-1", "action": "query",
                     "scope": {"drawing_files": [request["drawing_file"]], "include_passive": False,
                               "visibility": "api_select_all"},
                     "component_kind": "top_level_component", "fields": ["display_name", "file_state"],
                     "predicate": {"field": "type_name", "op": "eq", "value": WALL_TYPE}}
            live, native_owners = {}, []
            snapshot = call("M1.wall_filter_scan", lambda: self.queries._scan(
                doc, base, settings, query, adapter_sink=live, adapter_owners=native_owners,
                native_type_gate=WALL_TYPE))
            report["scope"] = snapshot["scope"]
            report["coverage"]["m1_complete"] = bool(
                snapshot["coverage"]["requested_scope_complete"]
                and snapshot["coverage"]["returned_fields_complete"]
                and snapshot["scope"]["included_files"] == [{"drawing_file": request["drawing_file"],
                    "state": "active_foreground", "write_eligibility": "not_checked"}])
            report["omissions"] = snapshot["omissions"]
            elements = snapshot["elements"]
            report["counts"]["walls"] = len(elements)
            if not report["coverage"]["m1_complete"]:
                return blocked("A complete active-foreground Wall scope is required; no native Wall properties were read.")
            if len(elements) > request.get("max_walls", 20):
                return blocked("Wall count exceeds max_walls; no native Wall properties were read.")

            identities = {item["ref"]["model_uuid"] for item in elements}
            excluded = set(request.get("exclude_model_uuids", []))
            if excluded - identities:
                raise BridgeError("selection_stale", "An excluded UUID is absent from the complete Wall scope.", 409)

            # Resolve every root's view and adapter before starting any property read.
            adapters_by_uuid = {}
            for item in elements:
                ref = item["ref"]
                views = live.get((ref["drawing_file"], ref["model_uuid"]), {})
                if (item["view_identity_not_checked"] or len(views) != 1
                        or set(views) != set(item["view_uuids"]) or not next(iter(views.values()), [])):
                    return blocked("A Wall root has unresolved or ambiguous view adapters; no native Wall properties were read.")
                adapters_by_uuid[ref["model_uuid"]] = next(iter(views.values()))[0]

            to_read = [item for item in elements if item["ref"]["model_uuid"] not in excluded]
            arch = None
            if to_read:
                try:
                    arch = call("Python.import.NemAll_Python_ArchElements",
                                lambda: importlib.import_module("NemAll_Python_ArchElements"))
                except BridgeError as exc:
                    return blocked("Native Wall API import failed: " + exc.code)
                except Exception as exc:
                    trace.record("Python.import.NemAll_Python_ArchElements", "observation_recorded",
                                 observation_status="unreadable", reason=type(exc).__name__)
                    return blocked("Native Wall API import failed: " + type(exc).__name__)

            failed_api = None
            for item in elements:
                ref = item["ref"]
                uuid = ref["model_uuid"]
                if uuid in excluded:
                    report["walls"].append({"ref": ref, "status": "excluded", "thickness_mm": None,
                                            "criterion": None, "match": None})
                    continue
                try:
                    failed_api = "BaseElements.GetElement"
                    native = call("BaseElements.GetElement", lambda a=adapters_by_uuid[uuid]: base.GetElement(a),
                                  drawing_file=ref["drawing_file"], model_uuid=uuid)
                    if not isinstance(native, arch.WallElement):
                        report["walls"].append({"ref": ref, "status": "unsupported",
                                                "reason": "GetElement_did_not_return_WallElement",
                                                "thickness_mm": None, "criterion": None, "match": None})
                        return blocked("A Wall root did not resolve to WallElement; no remaining walls were read.")
                    failed_api = "WallElement.Properties"
                    props = call("WallElement.Properties", lambda: native.Properties,
                                 drawing_file=ref["drawing_file"], model_uuid=uuid)
                    failed_api = "WallProperties.TierCount"
                    tier_count = call("WallProperties.TierCount", lambda: integer(props.TierCount),
                                      drawing_file=ref["drawing_file"], model_uuid=uuid)
                    if tier_count != 1:
                        report["walls"].append({"ref": ref, "status": "unsupported",
                                                "reason": "requires_exactly_one_wall_tier",
                                                "tier_count": tier_count, "thickness_mm": None,
                                                "criterion": None, "match": None})
                        return blocked("Multi-tier or invalid-tier Wall encountered; no remaining walls were read.")
                    failed_api = "WallProperties.GetWallTierProperties(1)"
                    tier = call("WallProperties.GetWallTierProperties(1)",
                                lambda: props.GetWallTierProperties(1),
                                drawing_file=ref["drawing_file"], model_uuid=uuid)
                    failed_api = "WallTierProperties.Thickness"
                    thickness = call("WallTierProperties.Thickness", lambda: positive_length(tier.Thickness),
                                     drawing_file=ref["drawing_file"], model_uuid=uuid)
                    mm = float(thickness)
                    report["walls"].append({"ref": ref, "status": "observed",
                                            "tier_count": 1, "thickness_mm": mm,
                                            "criterion": {"operator": "lt", "threshold_mm": threshold_mm},
                                            "match": mm < threshold_mm,
                                            "source": "single_tier_native_Thickness"})
                except BridgeError as exc:
                    # A trace/budget failure forbids all subsequent native/UI calls.
                    report["walls"].append({"ref": ref, "status": "unreadable",
                                            "reason": exc.code, "failed_api": failed_api, "thickness_mm": None,
                                            "criterion": None, "match": None})
                    return blocked("A native call could not complete safely; no remaining walls were read.")
                except Exception as exc:
                    report["walls"].append({"ref": ref, "status": "unreadable",
                                            "reason": type(exc).__name__, "failed_api": failed_api, "thickness_mm": None,
                                            "criterion": None, "match": None})
                    trace.record("WallFilter.native_read", "observation_recorded",
                                 observation_status="unreadable", drawing_file=ref["drawing_file"],
                                 model_uuid=uuid, failed_api=failed_api)
                    return blocked("A native Wall read failed; no remaining walls were read.")

            read_complete = all(w["status"] in ("observed", "excluded") for w in report["walls"])
            report["coverage"]["read_complete"] = read_complete
            report["coverage"]["criteria_complete"] = report["coverage"]["m1_complete"] and read_complete
            report["criterion_complete"] = report["coverage"]["criteria_complete"]
            report["is_full_wall_filter"] = report["criterion_complete"]
            report["counts"].update({"matched": sum(w.get("match") is True for w in report["walls"]),
                                     "excluded": sum(w["status"] == "excluded" for w in report["walls"]),
                                     "unreadable": 0, "unprocessed": 0})
            report["state"] = "observed"
            if request["action"] == "query":
                return complete()

            # Only fully observed, nonexcluded matches can reach the UI.
            matches = [w for w in report["walls"] if w["status"] == "observed" and w["match"] is True]
            target_adapters = [adapters_by_uuid[w["ref"]["model_uuid"]] for w in matches]
            ui_started = False
            try:
                highlight_service = getattr(ifw, "HighlightService", None)
                cancel = getattr(highlight_service, "CancelAllHighlightedElements", None)
                submit = getattr(highlight_service, "HighlightElements", None)
                if not callable(cancel) or (target_adapters and not callable(submit)):
                    report.update(state="blocked", message="The loaded build lacks a required highlight API symbol.")
                    return report  # Completed filter evidence remains valid; no UI call started.
                report["clear_scope"] = "all_highlights_in_current_document_including_other_sources"
                adapter_module = call("Python.import.NemAll_Python_IFW_ElementAdapter",
                                      lambda: importlib.import_module("NemAll_Python_IFW_ElementAdapter"))
                adapter_list_type = adapter_module.BaseElementAdapterList
                adapters = call("BaseElementAdapterList.construct", adapter_list_type)
                for adapter in target_adapters:
                    adapters.append(adapter)
                doc_id = call("DocumentAdapter.GetDocumentID", lambda: integer(doc.GetDocumentID()))
                def cancel_highlights():
                    nonlocal ui_started
                    ui_started = True
                    return cancel(doc_id)
                call("HighlightService.CancelAllHighlightedElements", cancel_highlights, document_id=doc_id)
                if target_adapters:
                    def submit_highlights():
                        nonlocal ui_started
                        ui_started = True
                        return submit(adapters)
                    call("HighlightService.HighlightElements",
                         submit_highlights,
                         submitted_model_identities=len(matches), submitted_adapters=len(target_adapters))
            except Exception as exc:
                report["state"] = "unknown" if ui_started else "blocked"
                report["ui_calls_started"] = ui_started
                report["message"] = ("Highlight outcome is unknown after a UI call failed: " if ui_started
                                      else "No UI call started because tracing or budget preflight failed: ") + type(exc).__name__
                report["counts"]["requested_model_identities"] = len(matches)
                report["counts"]["requested_adapters"] = len(target_adapters)
                return report
            report["state"] = "submitted"
            report["ui_calls_started"] = True
            report["counts"].update({"requested_model_identities": len(matches),
                                     "requested_adapters": len(target_adapters),
                                     "submitted_model_identities": len(matches),
                                     "submitted_adapters": len(target_adapters)})
            return complete()
        except BridgeError as exc:
            return blocked("Wall filter stopped safely: " + exc.code)

