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
    lines.extend(step["name"] + ": " + step.get("state", "recorded") + " (see JSON)" for step in report["steps"])
    if report.get("message"):
        lines.append(report["message"])
    path.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


async def collect_property_probe(url, path, *, clear=False):
    report = {"schema_version": "m4-owner-probe-1", "status": "ready_for_owner_test",
              "allplan_acceptance": "not_run", "model_setters_requested": False, "steps": []}

    async def call(client, name, tool, request=None):
        step = {"name": name, "tool": tool, "request": request, "state": "request_pending"}
        report["steps"].append(step)
        # Save the exact pending tool/request before contacting the native host.
        # If the host/process dies, this evidence must not vanish with its reply.
        save(path, report)
        try:
            result = (await client.call_tool(tool, {"request": request} if request is not None else {})).data
        except Exception as exc:
            step.update(state="failed", message=str(exc))
            save(path, report)
            raise
        step.update(state="response_received", response=result)
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
                sample = await call(client, "isolated_column_sample", "model_property_probe", {"phase": "column_sample", "drawing_file": 101})
                if (sample.get("read_only") is not True or sample.get("usable_for_write") is not False
                        or sample.get("sample", {}).get("attributes", {}).get("status") != "observed"):
                    raise ValueError("Isolated Column raw attributes are unavailable; do not continue to another probe phase.")
                report["native_trace_required"] = "Local/.allplan-mcp/logs/m4-native-probe.jsonl"
                report["next_phase"] = "stop_and_return_evidence_no_automatic_metadata_or_UI_calls"
            health_check(await call(client, "health_after", "allplan_health"), session)
            report["state"] = "awaiting_owner_observation"
    except Exception as exc:
        report.update(state="blocked", message=str(exc), recovery="Preserve this report and Local/.allplan-mcp/logs/bridge.log. Do not repeat M4 Properties after the native crash. No Apply or model writes were requested.")
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
    if result["state"] == "blocked":
        print("M4 blocked. Preserve this report and bridge.log; do not repeat M4 Properties. No model setters requested.")
    else:
        print("Observe the UI. Native UI selection remains BLOCKED; no model setters requested.")
    return 1 if result["state"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
