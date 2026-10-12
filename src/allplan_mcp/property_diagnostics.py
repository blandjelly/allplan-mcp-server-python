"""No-code M4 discovery/highlight observation. No Apply, setters or journal access."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from fastmcp import Client

def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["M4 metadata/highlight observation: " + report.get("state", "collecting"),
             "Allplan acceptance: not_run; native UI selection: BLOCKED in current interactor.",
             "No model setters requested."]
    lines.extend(step["name"] + ": recorded (see JSON)" for step in report["steps"])
    if report.get("message"):
        lines.append(report["message"])
    path.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


async def collect_property_probe(url, path, *, clear=False):
    report = {"schema_version": "m4-owner-probe-1", "status": "ready_for_owner_test",
              "allplan_acceptance": "not_run", "model_setters_requested": False, "steps": []}

    async def call(client, name, tool, request=None):
        result = (await client.call_tool(tool, {"request": request} if request is not None else {})).data
        report["steps"].append({"name": name, "tool": tool, "request": request, "response": result})
        save(path, report)
        return result

    def health_check(response, session=None):
        runtime = response.get("runtime", {})
        current = runtime.get("host_session_id")
        expected = version("allplan-mcp-server")
        if (response.get("ok") is not True or response.get("mcp_package_version") != expected
                or runtime.get("bridge_package", {}).get("version") != expected
                or runtime.get("installed_bridge_integrity", {}).get("status") != "verified"
                or runtime.get("compatibility", {}).get("major_matches") is not True
                or not current or (session is not None and current != session)):
            raise ValueError("Loaded bridge/package integrity or host session differs; restart the installed host before observing M4.")
        return current

    try:
        async with Client(url, timeout=30) as client:
            session = health_check(await call(client, "health_before", "allplan_health"))
            if clear:
                response = await call(client, "clear_highlight", "model_selection", {"action": "clear_highlight"})
                if response.get("state") != "submitted":
                    raise ValueError("Clear outcome is unknown; inspect Allplan before repeating.")
            else:
                properties = {"sample_limit": 20, "attribute_names": ["Odporność ogniowa", "Fire resistance"], "layer_short_names": ["W1"]}
                baseline = await call(client, "properties_before", "model_properties", properties)
                if baseline.get("usable_for_write") is not False or not baseline.get("sample", {}).get("elements"):
                    raise ValueError("No Column/Wall sample is available in open drawings.")
                query = {"action": "query", "component_kind": "top_level_component", "page_size": 1,
                         "predicate": {"field": "type_name", "op": "in", "value": ["Column_TypeUUID", "Wall_TypeUUID"]},
                         "fields": ["layer_id", "file_state", "bounding_box_mm"]}
                selected = await call(client, "query_first_page", "model_query", query)
                if not selected["coverage"]["requested_scope_complete"] or not selected["counts"]["matched_model_identities"]:
                    raise ValueError("Query coverage is incomplete or has no matches; retain omissions, narrow scope through local Codex.")
                highlight = await call(client, "highlight_full_selection", "model_selection", {"action": "highlight", "selection_id": selected["selection_id"]})
                if (highlight.get("state") != "submitted"
                        or highlight["counts"]["submitted_model_identities"] != selected["counts"]["matched_model_identities"]
                        or highlight["counts"]["selected"] is not None or highlight["counts"]["highlighted"] is not None):
                    raise ValueError("Highlight submission differs from the full query; observe UI before any repeat.")
                native = await call(client, "native_selection_capability", "model_selection", {"action": "select", "selection_id": selected["selection_id"]})
                if native.get("state") != "unsupported" or native.get("ui_calls_started") is not False:
                    raise ValueError("Native selection capability differs from the declared probe.")
                after = await call(client, "properties_after", "model_properties", properties)
                if after["probe_fingerprint"] != baseline["probe_fingerprint"]:
                    raise ValueError("Sampled properties changed during presentation; retain both reports.")
                reread = await call(client, "query_after", "model_query", query)
                if reread["source_fingerprint"] != selected["source_fingerprint"]:
                    raise ValueError("Query source/geometry changed during presentation; retain both reports.")
                report["native_selection_gate"] = "BLOCKED_current_interactor"
                report["metadata_observation"] = "owner_and_local_Codex_must_verify_actual_fire_resistance_field_and_W1_resolution"
            health_check(await call(client, "health_after", "allplan_health"), session)
            report["state"] = "awaiting_owner_observation"
    except Exception as exc:
        report.update(state="blocked", message=str(exc), recovery="Inspect the view and logs; clear highlights explicitly. No Apply or model writes were requested.")
    save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "clear"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = args.output or Path("logs") / f"m4-properties-{args.action}-{stamp}.json"
    result = asyncio.run(collect_property_probe(os.getenv("MCP_URL", "http://127.0.0.1:8888/mcp"), path, clear=args.action == "clear"))
    print("Report:", path.resolve())
    print("State:", result["state"])
    print("Observe Column/Wall highlights, then use M4 Clear Highlight.cmd. Native UI selection remains BLOCKED; no model changes requested.")
    return 1 if result["state"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
