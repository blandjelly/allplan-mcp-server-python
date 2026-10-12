"""Owner-operated disposable-copy M3 gate; persistence precedes mutation calls."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastmcp import Client

from .diagnostics import collect_m3_preview


def save(path: Path, report: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    lines = [f"M3 disposable-copy gate: {report['state']}. Execution: {report.get('execution_id', 'not_started')}."]
    for step in report.get("steps", []):
        lines.append(f"{step['name']}: {'OK' if step['ok'] else 'FAILED'}")
        response = step.get("response", {})
        if response.get("report_text"):
            lines.append(response["report_text"])
    if report.get("message"):
        lines.append(report["message"])
    path.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


async def apply_gate(host_url, mcp_url, path, confirm=input):
    report = {"state": "preflight", "steps": [], "allplan_acceptance": "not_run"}
    step = "preview_preflight"
    try:
        preview = await collect_m3_preview(host_url, mcp_url)
        report["preview"] = preview
        plan = preview.get("mcp", {}).get("fix_model_issues", {})
        ok = (preview["m3_preview"]["checks_complete"] and plan.get("evaluation_apply_available") is True
              and {c["locator"]["mark"].get("value") for c in plan.get("changes", [])} == {"S05", "S06"})
        report["steps"].append({"name": step, "ok": ok})
        save(path, report)
        if not ok:
            report.update(state="blocked", message="Preview/package/fixture differs. No mutation requested.")
            return report
        print(plan["report_text"])
        print("Sprawdz cele w UI: C05/S05 warstwa SZ_OGÓ02 -> SZ_OGÓ01; C06/S06 status NWE -> NEW.")
        print("Tylko jednorazowa kopia projektu, plik 101 na pierwszym planie. Undo dwoch napraw wymaga dwoch osobnych krokow w UI.")
        if confirm("Wpisz NAPRAW KOPIE po sprawdzeniu dwoch zmian i kopii projektu: ").strip() != "NAPRAW KOPIE":
            report.update(state="cancelled", message="Owner did not start apply. No mutation requested.")
            return report
        execution_id = uuid4().hex
        request = {"action": "apply", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"],
                   "execution_id": execution_id, "acknowledgement": "disposable_copy_reviewed_two_repairs"}
        report.update(state="apply_pending", execution_id=execution_id, apply_request=request)
        save(path, report)
        # Save a recovery pointer before the HTTP call; a lost response must not
        # make the owner invent a new ID or rerun the write launcher.
        save(path.parent / "m3-last-execution.json", report)
        async with Client(mcp_url, timeout=90) as client:
            step = "apply_readback"
            response = (await client.call_tool("fix_model_issues", {"request": request})).data
            if response.get("state") == "rejected" and response.get("native_setters_started") is False:
                report["steps"].append({"name": step, "ok": False, "response": response})
                report.update(state="rejected", native_setters_started=False,
                              message=response["report_text"] + ". No write/Undo/recovery is needed for this rejected request. Preserve logs.")
                save(path.parent / "m3-last-execution.json", report)
                return report
            ok = (response.get("state") == "completed" and response.get("execution_id") == execution_id
                  and [o["state"] for o in response.get("outcomes", [])] == ["applied", "applied"]
                  and response.get("audited_fields_match_plan") is True
                  and response.get("audit_after", {}).get("counts", {}).get("findings") == 3)
            report["steps"].append({"name": step, "ok": ok, "response": response})
            save(path, report)
            if not ok:
                report.update(state="stopped", message="Readback/verification failed. Run M3 Recover; inspect the copy. Do not rerun Apply.")
                return report
            step = "same_execution_replay"
            replay = (await client.call_tool("fix_model_issues", {"request": request})).data
            ok = (replay.get("replayed") is True and replay.get("read_only") is True
                  and replay.get("outcomes") == response.get("outcomes"))
            report["steps"].append({"name": step, "ok": ok, "response": replay})
            report.update(state="ready_for_ui_observation" if ok else "stopped",
                          message="Compare both values and unchanged other elements in UI, then perform native Undo and run M3 Check Undo.")
    except Exception as exc:
        report["steps"].append({"name": step, "ok": False, "message": str(exc)})
        report.update(state="unknown" if report.get("execution_id") else "blocked",
                      message="Operation stopped: " + str(exc) + ". No automatic retry. If apply started, use M3 Recover.")
    finally:
        save(path, report)
    return report


async def recovery_gate(host_url, mcp_url, path, previous, check_undo=False):
    execution_id = previous["execution_id"]
    report = {"state": "recovery_pending", "execution_id": execution_id, "read_only": True,
              "steps": [], "allplan_acceptance": "not_run"}
    if previous.get("state") == "rejected" and previous.get("native_setters_started") is False:
        report.update(state="rejected", native_setters_started=False,
                      message="Saved request was explicitly rejected before setters. Recovery/replay was not sent.")
        save(path, report)
        return report
    try:
        async with Client(mcp_url, timeout=90) as client:
            request = {"action": "recover", "execution_id": execution_id}
            response = (await client.call_tool("fix_model_issues", {"request": request})).data
            observations = response.get("recovery", {}).get("observations", [])
            ok = (response.get("read_only") is True and len(observations) == 2
                  and all(o["state"] in {"old_value_observed", "new_value_observed"} for o in observations))
            if check_undo:
                ok = (ok and all(o["state"] == "old_value_observed" for o in observations)
                      and response["recovery"]["audit"]["counts"]["findings"] == 5)
            report["steps"].append({"name": "undo_readback" if check_undo else "recover_read_only", "ok": ok, "response": response})
            # Replay after a host restart / Undo is read-only and never reapplies.
            replay = (await client.call_tool("fix_model_issues", {"request": previous["apply_request"]})).data
            report["steps"].append({"name": "persisted_execution_replay", "ok": replay.get("replayed") is True
                                    and replay.get("read_only") is True, "response": replay})
            health = (await client.call_tool("allplan_health")).data
            report["steps"].append({"name": "health", "ok": health.get("ok") is True, "response": health})
            report["state"] = "ready_for_ui_observation" if all(s["ok"] for s in report["steps"]) else "stopped"
    except Exception as exc:
        report.update(state="blocked", message=str(exc) + ". Recovery did not request a setter or rollback.")
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("apply", "recover", "check-undo"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--execution", type=Path, default=Path("logs/m3-last-execution.json"))
    args = parser.parse_args()
    path = args.output or Path("logs") / ("m3-" + args.action + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    host_url = os.getenv("ALLPLAN_HOST_URL", "http://127.0.0.1:5679")
    mcp_url = os.getenv("MCP_URL", "http://127.0.0.1:8888/mcp")
    if args.action == "apply":
        report = asyncio.run(apply_gate(host_url, mcp_url, path))
    else:
        previous = json.loads(args.execution.read_text(encoding="utf-8"))
        report = asyncio.run(recovery_gate(host_url, mcp_url, path, previous, args.action == "check-undo"))
    print(f"M3: {report['state']}. Logs: {path.resolve()} and TXT.")
    if report.get("message"):
        print(report["message"])
    if report["state"] not in {"ready_for_ui_observation", "cancelled"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
