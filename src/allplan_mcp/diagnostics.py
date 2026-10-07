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


async def collect_diagnostics(host_url: str, mcp_url: str, query_request: dict | None = None, query_batch: list | None = None) -> dict:
    if query_request is not None and query_batch is not None:
        raise ValueError("Choose a single request or a batch.")
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
    try:
        report["host"] = AllplanHostClient(host_url, timeout=5).post("/get-allplan-version")
    except AllplanHostError as exc:
        report["host"] = {"ok": False, "code": exc.code, "message": str(exc), "request_id": exc.request_id}
    from fastmcp import Client
    try:
        async with Client(mcp_url, timeout=30 if query_request is not None or query_batch is not None else 5) as client:
            tools = await client.list_tools()
            report["mcp"] = {"ok": True, "discovered_tools": [t.name for t in tools]}
            for name in ("allplan_health", "get_allplan_version"):
                try:
                    result = await client.call_tool(name)
                    report["mcp"][name] = result.data
                except Exception as exc:
                    report["mcp"][name] = {"ok": False, "message": str(exc)}
            if "get_model_context" in report["mcp"]["discovered_tools"]:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect read-only bridge and MCP diagnostics.")
    parser.add_argument("--output", type=Path)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--query-request", type=Path, help="JSON model_query request to capture together with its full response.")
    inputs.add_argument("--query-batch", type=Path, help="JSON list of 1..8 typed read-only requests; captures summaries and bounded pages.")
    args = parser.parse_args()
    query_request = json.loads(args.query_request.read_text(encoding="utf-8")) if args.query_request else None
    query_batch = json.loads(args.query_batch.read_text(encoding="utf-8")) if args.query_batch else None
    report = asyncio.run(collect_diagnostics(os.getenv("ALLPLAN_HOST_URL", "http://127.0.0.1:5679"),
                                             os.getenv("MCP_URL", "http://127.0.0.1:8888/mcp"), query_request, query_batch))
    path = args.output or Path("logs") / ("diagnostics-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Diagnostics saved to {path.resolve()}. No model changes were requested.")
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
