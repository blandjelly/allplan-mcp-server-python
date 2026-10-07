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


async def collect_diagnostics(host_url: str, mcp_url: str, query_request: dict | None = None) -> dict:
    if query_request is not None:
        from pydantic import TypeAdapter
        from allplan_mcp.query_models import QueryRequest
        query_request = TypeAdapter(QueryRequest).validate_python(query_request).model_dump(by_alias=True, exclude_unset=True)
    report = {"schema_version": "m0-1", "captured_at": datetime.now(timezone.utc).isoformat(),
              "external_python": platform.python_version(), "platform": platform.system(),
              "package_version": version("allplan-mcp-server"),
              "host_url": host_url, "mcp_url": mcp_url,
              "allplan_acceptance": "not_run"}
    if query_request is not None:
        report["model_query_request"] = query_request
    try:
        report["host"] = AllplanHostClient(host_url, timeout=5).post("/get-allplan-version")
    except AllplanHostError as exc:
        report["host"] = {"ok": False, "code": exc.code, "message": str(exc), "request_id": exc.request_id}
    from fastmcp import Client
    try:
        async with Client(mcp_url, timeout=30 if query_request is not None else 5) as client:
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
                    report["mcp"]["get_model_context"] = (await client.call_tool(
                        "get_model_context", {"identity_sample_size": 10})).data
                except Exception as exc:
                    report["mcp"]["get_model_context"] = {"ok": False, "message": str(exc)}
            if query_request is not None:
                try:
                    report["mcp"]["model_query"] = (await client.call_tool(
                        "model_query", {"request": query_request})).data
                except Exception as exc:
                    report["mcp"]["model_query"] = {"ok": False, "message": str(exc)}
    except Exception as exc:
        report["mcp"] = {"ok": False, "message": str(exc), "recovery": "Run Launch Allplan MCP.cmd and keep that window open."}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect read-only bridge and MCP diagnostics.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--query-request", type=Path, help="JSON model_query request to capture together with its full response.")
    args = parser.parse_args()
    query_request = json.loads(args.query_request.read_text(encoding="utf-8")) if args.query_request else None
    report = asyncio.run(collect_diagnostics(os.getenv("ALLPLAN_HOST_URL", "http://127.0.0.1:5679"),
                                             os.getenv("MCP_URL", "http://127.0.0.1:8888/mcp"), query_request))
    path = args.output or Path("logs") / ("diagnostics-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Diagnostics saved to {path.resolve()}. No model changes were requested.")


if __name__ == "__main__":
    main()
