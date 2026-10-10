"""Read-only bridge diagnostics; never create geometry or retry writes."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from allplan_mcp.allplan_client import AllplanHostClient, AllplanHostError


async def collect_diagnostics(host_url: str, mcp_url: str, query_request: dict | None = None, query_batch: list | None = None,
                              audit_request: dict | None = None, include_model_context: bool = True) -> dict:
    if sum(value is not None for value in (query_request, query_batch, audit_request)) > 1:
        raise ValueError("Choose a query request, a query batch or an audit request.")
    if audit_request is not None:
        from allplan_mcp.audit_models import AuditRequest
        audit_request = AuditRequest.model_validate(audit_request).model_dump(exclude_unset=True, exclude_none=True)
    if query_request is not None or query_batch is not None:
        from pydantic import TypeAdapter
        from allplan_mcp.query_models import QueryRequest
        adapter = TypeAdapter(QueryRequest)
        if query_request is not None:
            query_request = adapter.validate_python(query_request).model_dump(by_alias=True, exclude_unset=True)
        if query_batch is not None:
            if not isinstance(query_batch, list) or not 1 <= len(query_batch) <= 8:
                raise ValueError("Query batch must contain 1..8 requests.")
            query_batch = [adapter.validate_python(item).model_dump(by_alias=True, exclude_unset=True) for item in query_batch]
    report = {"schema_version": "m0-1", "captured_at": datetime.now(timezone.utc).isoformat(),
              "external_python": platform.python_version(), "platform": platform.system(),
              "package_version": version("allplan-mcp-server"),
              "host_url": host_url, "mcp_url": mcp_url,
              "allplan_acceptance": "not_run"}
    if query_request is not None:
        report["model_query_request"] = query_request
    if query_batch is not None:
        report["model_query_batch_requests"] = query_batch
    if audit_request is not None:
        report["model_audit_request"] = audit_request
    try:
        report["host"] = AllplanHostClient(host_url, timeout=5).post("/get-allplan-version")
    except AllplanHostError as exc:
        report["host"] = {"ok": False, "code": exc.code, "message": str(exc), "request_id": exc.request_id}
    from fastmcp import Client
    try:
        async with Client(mcp_url, timeout=30 if any(v is not None for v in (query_request, query_batch, audit_request)) else 5) as client:
            tools = await client.list_tools()
            report["mcp"] = {"ok": True, "discovered_tools": [t.name for t in tools]}
            for name in ("allplan_health", "get_allplan_version"):
                try:
                    result = await client.call_tool(name)
                    report["mcp"][name] = result.data
                except Exception as exc:
                    report["mcp"][name] = {"ok": False, "message": str(exc)}
            if include_model_context and "get_model_context" in report["mcp"]["discovered_tools"]:
                try:
                    context_request = {"identity_sample_size": 10}
                    if query_batch and any(item.get("profile_id") for item in query_batch):
                        context_request["profile_id"] = "native-model-qa-demo"
                    report["mcp"]["get_model_context"] = (await client.call_tool(
                        "get_model_context", context_request)).data
                except Exception as exc:
                    report["mcp"]["get_model_context"] = {"ok": False, "message": str(exc)}
            if query_request is not None:
                try:
                    report["mcp"]["model_query"] = (await client.call_tool(
                        "model_query", {"request": query_request})).data
                except Exception as exc:
                    report["mcp"]["model_query"] = {"ok": False, "message": str(exc)}
            if audit_request is not None:
                try:
                    report["mcp"]["model_audit"] = (await client.call_tool("model_audit", {"request": audit_request})).data
                except Exception as exc:
                    report["mcp"]["model_audit"] = {"ok": False, "message": str(exc)}
            if query_batch is not None:
                report["mcp"]["model_query_batch"] = []
                for request in query_batch:
                    record = {"request": request}
                    try:
                        record["response"] = (await client.call_tool("model_query", {"request": request})).data
                        response = record["response"]
                        if request["action"] == "query" and response.get("selection_id"):
                            record["summary"] = (await client.call_tool("model_query", {"request": {
                                "action": "summary", "selection_id": response["selection_id"]}})).data
                            pages = [response]
                            record["pages"] = pages
                            cursor = response.get("page", {}).get("next_cursor")
                            seen_cursors = set()
                            while cursor is not None:
                                if cursor in seen_cursors or len(pages) >= 50:
                                    raise ValueError("Diagnostic paging exceeded its bounded cursor budget")
                                seen_cursors.add(cursor)
                                page = (await client.call_tool("model_query", {"request": {
                                    "action": "page", "selection_id": response["selection_id"], "cursor": cursor, "page_size": 200}})).data
                                pages.append(page)
                                cursor = page.get("page", {}).get("next_cursor")
                    except Exception as exc:
                        record["error"] = {"ok": False, "message": str(exc)}
                    report["mcp"]["model_query_batch"].append(record)
    except Exception as exc:
        report["mcp"] = {"ok": False, "message": str(exc), "recovery": "Run Launch Allplan MCP.cmd and keep that window open."}
    return report


async def collect_m2_stability(host_url: str, mcp_url: str) -> dict:
    """Two explicit reads, validation rejection and health; stop on any lost read."""
    from allplan_mcp.demo_profile import load_audit_profile
    from fastmcp import Client
    scope = {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"}
    request = {"scope": scope, "profile_id": "native-model-qa-demo"}
    report = await collect_diagnostics(host_url, mcp_url, include_model_context=False)
    report["model_audit_request"] = request
    steps = []
    stability = {"checks_complete": False, "steps": steps, "allplan_acceptance": "not_run"}
    report["m2_stability"] = stability
    def complete_audit(response):
        return isinstance(response, dict) and response.get("schema_version") == "m2-audit-1" and response.get("read_only") is True
    runtime = report.get("host", {})
    mcp_health = report.get("mcp", {}).get("allplan_health", {})
    expected_version = version("allplan-mcp-server")
    package = runtime.get("bridge_package")
    integrity = runtime.get("installed_bridge_integrity")
    preflight = (isinstance(package, dict) and package.get("version") == expected_version
                 and isinstance(integrity, dict) and integrity.get("status") == "verified"
                 and runtime.get("ui_dispatch_exception_boundary") == "contained_result_error_v1"
                 and mcp_health.get("mcp_package_version") == expected_version)
    steps.append({"name": "host_boundary_preflight", "ok": preflight, "expected_package_version": expected_version})
    if not preflight:
        stability["stopped_reason"] = "Host/MCP version, installed integrity or loaded UI exception boundary not verified; no model reads/probes requested."
        return report
    step = "audit_1"
    try:
        async with Client(mcp_url, timeout=30) as client:
            for step in ("audit_1", "audit_2"):
                response = (await client.call_tool("model_audit", {"request": request})).data
                if step == "audit_1":
                    report["mcp"]["model_audit"] = response
                steps.append({"name": step, "ok": complete_audit(response), "response": response})
                if not steps[-1]["ok"]:
                    stability["stopped_reason"] = "Audit did not return a complete response; no further checks requested."
                    return report
            invalid_scope = {**scope, "drawing_files": [101, 102], "include_passive": True}
            step = "mcp_scope_rejection"
            result = await client.call_tool("model_audit", {"request": {**request, "scope": invalid_scope}}, raise_on_error=False)
            message = "\n".join(getattr(c, "text", "") for c in result.content)
            steps.append({"name": step, "ok": result.is_error and "Requested audit files exceed the explicit profile scope." in message,
                          "message": message})
            if not steps[-1]["ok"]:
                stability["stopped_reason"] = "Expected public scope rejection was not returned; no host probe requested."
                return report
        # Bypass the public preflight once to exercise the protected UI callback
        # with the incident's known-invalid, strictly read-only host payload.
        step = "host_scope_rejection"
        payload = {"schema_version": "m2-audit-1", "scope": invalid_scope, "profile": load_audit_profile()}
        host = AllplanHostClient(host_url, timeout=30)
        try:
            response = await asyncio.to_thread(host.post, "/model-audit", payload)
            steps.append({"name": step, "ok": False, "response": response})
        except AllplanHostError as exc:
            steps.append({"name": step, "ok": exc.code == "invalid_payload" and "Requested audit files exceed the explicit profile scope." in str(exc),
                          "code": exc.code, "message": str(exc), "request_id": exc.request_id})
        if not steps[-1]["ok"]:
            stability["stopped_reason"] = "Protected host rejection was not returned; no further checks requested."
            return report
        step = "host_health_after_rejection"
        runtime = await asyncio.to_thread(host.post, "/get-allplan-version")
        steps.append({"name": step, "ok": bool(runtime.get("version")), "response": runtime})
        stability["checks_complete"] = all(item["ok"] for item in steps)
    except Exception as exc:
        steps.append({"name": step, "ok": False, "message": str(exc)})
        stability["stopped_reason"] = "A check failed; no automatic retry was requested."
    return report


async def collect_m3_preview(host_url: str, mcp_url: str) -> dict:
    """Bounded read-only owner gate: preview, revalidate, unchanged audit, health."""
    from fastmcp import Client
    report = await collect_diagnostics(host_url, mcp_url, include_model_context=False)
    steps = []
    gate = {"checks_complete": False, "steps": steps, "allplan_acceptance": "not_run", "read_only": True}
    report["m3_preview"] = gate
    runtime = report.get("host", {})
    health = report.get("mcp", {}).get("allplan_health", {})
    expected = version("allplan-mcp-server")
    preflight = (runtime.get("bridge_package", {}).get("version") == expected
                 and runtime.get("installed_bridge_integrity", {}).get("status") == "verified"
                 and runtime.get("ui_dispatch_exception_boundary") == "contained_result_error_v1"
                 and health.get("mcp_package_version") == expected
                 and "fix_model_issues" in report.get("mcp", {}).get("discovered_tools", []))
    steps.append({"name": "host_boundary_preflight", "ok": preflight, "expected_package_version": expected})
    if not preflight:
        gate["stopped_reason"] = "Package/integrity/loaded boundary/tool preflight failed; no model reads requested."
        return report
    audit = {"scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"},
             "profile_id": "native-model-qa-demo"}
    request = {"action": "preview", "audit": audit,
               "repairs": [{"rule_id": "QA-003", "value": "structure"}, {"rule_id": "QA-004", "value": "NEW"}]}
    gate["request"] = request
    step = "preview"
    try:
        async with Client(mcp_url, timeout=30) as client:
            plan = (await client.call_tool("fix_model_issues", {"request": request})).data
            report["mcp"]["fix_model_issues"] = plan
            changes = plan.get("changes", [])
            expected_changes = (len(changes) == 2 and {c["rule_id"] for c in changes} == {"QA-003", "QA-004"}
                                and all(c["ref"]["drawing_file"] == 101 for c in changes)
                                and any(c["rule_id"] == "QA-004" and c["old_value"].get("value") == "NWE"
                                        and c["new_value"] == "NEW" for c in changes)
                                and any(c["rule_id"] == "QA-003" and c["resource"].get("short_name") == "SZ_OGÓ01"
                                        and c["old_value"].get("value") != c["new_value"] for c in changes))
            ok = (plan.get("schema_version") == "m3-repair-1" and plan.get("read_only") is True
                  and plan.get("apply_available") is False and plan.get("usable_for_write") is False
                  and plan.get("state") == "preview_ready" and plan.get("coverage", {}).get("audit_complete") is True
                  and plan.get("counts") == {"changes": 2, "excluded_findings": 3, "audit_findings": 5}
                  and expected_changes)
            steps.append({"name": step, "ok": ok, "response": plan})
            if not ok:
                gate["stopped_reason"] = "Preview differs from the retained fixture gate; no further reads requested."
                return report
            step = "revalidate"
            response = (await client.call_tool("fix_model_issues", {"request": {
                "action": "revalidate", "plan_id": plan["plan_id"], "plan_hash": plan["plan_hash"]}})).data
            steps.append({"name": step, "ok": response.get("state") == "unchanged" and response.get("source_unchanged") is True
                          and response.get("read_only") is True and response.get("apply_available") is False,
                          "response": response})
            if not steps[-1]["ok"]:
                gate["stopped_reason"] = "Plan revalidation failed; no further reads requested."
                return report
            step = "audit_after_preview"
            response = (await client.call_tool("model_audit", {"request": audit})).data
            report["mcp"]["model_audit"] = response
            steps.append({"name": step, "ok": response.get("report_fingerprint") == plan["audit_report_fingerprint"]
                          and response.get("source_fingerprint") == plan["source_fingerprint"]
                          and response.get("counts", {}).get("findings") == 5,
                          "response": response})
            if not steps[-1]["ok"]:
                gate["stopped_reason"] = "Audited evidence changed during the read-only batch; stop and inspect the model."
                return report
            step = "host_health_after_preview"
            response = await asyncio.to_thread(AllplanHostClient(host_url, timeout=5).post, "/get-allplan-version")
            steps.append({"name": step, "ok": bool(response.get("version"))
                          and response.get("host_session_id") == runtime.get("host_session_id"), "response": response})
            gate["checks_complete"] = all(s["ok"] for s in steps)
    except Exception as exc:
        steps.append({"name": step, "ok": False, "message": str(exc)})
        gate["stopped_reason"] = "A check failed; no automatic retry was requested."
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect read-only bridge and MCP diagnostics.")
    parser.add_argument("--output", type=Path)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--query-request", type=Path, help="JSON model_query request to capture together with its full response.")
    inputs.add_argument("--query-batch", type=Path, help="JSON list of 1..8 typed read-only requests; captures summaries and bounded pages.")
    inputs.add_argument("--audit-request", type=Path, help="Typed model_audit request; saves full JSON and a readable text report.")
    inputs.add_argument("--m2-stability", action="store_true", help="Two demo reads, public/host scope rejection and host health; stops on failure.")
    inputs.add_argument("--m3-preview", action="store_true", help="Read-only demo repair preview, revalidation, unchanged audit and health.")
    args = parser.parse_args()
    query_request = json.loads(args.query_request.read_text(encoding="utf-8")) if args.query_request else None
    query_batch = json.loads(args.query_batch.read_text(encoding="utf-8")) if args.query_batch else None
    audit_request = json.loads(args.audit_request.read_text(encoding="utf-8")) if args.audit_request else None
    host_url = os.getenv("ALLPLAN_HOST_URL", "http://127.0.0.1:5679")
    mcp_url = os.getenv("MCP_URL", "http://127.0.0.1:8888/mcp")
    report = asyncio.run(collect_m3_preview(host_url, mcp_url) if args.m3_preview else
                         collect_m2_stability(host_url, mcp_url) if args.m2_stability else
                         collect_diagnostics(host_url, mcp_url, query_request, query_batch, audit_request))
    path = args.output or Path("logs") / ("diagnostics-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Diagnostics saved to {path.resolve()}. No model changes were requested.")
    if args.m3_preview:
        gate = report["m3_preview"]
        plan = report.get("mcp", {}).get("fix_model_issues", {})
        content = plan.get("report_text", "Repair preview unavailable; preserve the JSON.")
        content += "\n\nM3 preview checks complete: " + str(gate["checks_complete"])
        for item in gate["steps"]:
            content += f"\n{item['name']}: {'OK' if item['ok'] else 'FAILED'}"
        if "stopped_reason" in gate:
            content += "\n" + gate["stopped_reason"]
        path.with_suffix(".txt").write_text(content + "\n", encoding="utf-8")
        print(content)
        print("Owner must compare the two proposed targets/values in Allplan and confirm the unchanged model.")
        if not gate["checks_complete"]:
            raise SystemExit(1)
    if audit_request is not None or args.m2_stability:
        audit = report.get("mcp", {}).get("model_audit", {})
        text_path = path.with_suffix(".txt")
        content = audit.get("report_text") or ("Audit failed or unavailable. Preserve the JSON for review.\n" + audit.get("message", report.get("mcp", {}).get("message", "No audit response.")))
        if args.m2_stability:
            checks = report["m2_stability"]
            content += "\n\nStability checks complete: " + str(checks["checks_complete"])
            for item in checks["steps"]:
                content += f"\n{item['name']}: {'OK' if item['ok'] else 'FAILED'}"
            if "stopped_reason" in checks:
                content += "\n" + checks["stopped_reason"]
        text_path.write_text(content + "\n", encoding="utf-8")
        print(content)
        print(f"Readable audit saved to {text_path.resolve()}. Native acceptance requires owner UI observations.")
        if args.m2_stability and not report["m2_stability"]["checks_complete"]:
            raise SystemExit(1)
    result = report.get("mcp", {}).get("model_query", {})
    if query_request and query_request.get("action") == "profile":
        if result.get("status") == "bound_for_read":
            print("Demo resources are ready for reading. Follow the fixture recipe next.")
        else:
            print("Demo resources are not ready. Send this JSON before building the fixture.")
    for index, record in enumerate(report.get("mcp", {}).get("model_query_batch", []), 1):
        response = record.get("response", {})
        if "error" in record:
            print(f"Read {index}: failed or incomplete. Preserve the JSON for review.")
        elif response.get("counts"):
            print(f"Read {index}: {response['counts']['matched_model_identities']} matches; {len(response.get('omissions', []))} omitted drawing files.")


if __name__ == "__main__":
    main()
