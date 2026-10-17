"""Find and highlight single-tier Walls below 24 cm; save evidence for the owner."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import Client

from .column_layer_diagnostics import health
from .wall_diagnostics import save


async def run(url, path, *, drawing_file=101, query_only=False, exclude_model_uuids=None):
    report = {"schema_version": "m4-wall-filter-owner-1", "state": "collecting", "steps": [],
              "allplan_acceptance": "not_run", "model_setters_requested": False,
              "automatic_retry": False, "native_selection": "highlight_only" if not query_only else "not_requested",
              "native_trace_required": "Local/.allplan-mcp/logs/m4-native-probe.jsonl"}

    async def call(client, name, tool, request=None):
        step = {"name": name, "tool": tool, "request": request, "state": "request_pending"}
        report["steps"].append(step)
        save(path, report)
        response = (await client.call_tool(tool, {"request": request} if request is not None else {})).data
        step.update(state="response_received", response=response)
        save(path, report)
        return response

    try:
        async with Client(url, timeout=90) as client:
            session = health(await call(client, "health_before", "allplan_health"))
            request = {"action": "query" if query_only else "highlight", "drawing_file": drawing_file,
                       "threshold": {"value": 24, "unit": "cm"}, "max_walls": 20,
                       "exclude_model_uuids": exclude_model_uuids or []}
            result = await call(client, "wall_thickness_filter", "model_wall_filter", request)
            # A lost response escapes before health_after. A received blocked
            # result can be bracketed by same-session health without a retry.
            health(await call(client, "health_after", "allplan_health"), session)
            expected = "observed" if query_only else "submitted"
            if (result.get("state") != expected or result.get("criterion_complete") is not True
                    or result.get("model_data_changed") is not False
                    or result.get("usable_for_write") is not False):
                report.update(state="blocked", message="Filtr niekompletny lub podswietlenie niepotwierdzone odpowiedzia. Zachowaj raport; nie ponawiaj proby.")
            else:
                counts = result["counts"]
                report.update(state="awaiting_owner_observation", message=(
                    f"Sciany <24 cm: dopasowania {counts['matched']}, wykluczenia {counts['excluded']}. "
                    + ("Tylko odczyt. " if query_only else f"Do podswietlenia wyslano {counts['submitted_model_identities']} scian. ")
                    + "Porownaj wynik z UI: 20 cm pasuje, 24 cm nie pasuje. Model nie zostal zmieniony."))
    except Exception as exc:
        report.update(state="blocked", message=str(exc))
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drawing-file", type=int, default=101)
    parser.add_argument("--query-only", action="store_true")
    parser.add_argument("--exclude-model-uuid", action="append", default=[])
    parser.add_argument("--url", default="http://127.0.0.1:8888/mcp")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = Path("logs") / f"wall-filter-{stamp}.json"
    report = asyncio.run(run(args.url, path, drawing_file=args.drawing_file,
                             query_only=args.query_only, exclude_model_uuids=args.exclude_model_uuid))
    print(report["state"], report.get("message", ""), "\nRaport:", path.resolve())
    return 0 if report["state"] == "awaiting_owner_observation" else 1


if __name__ == "__main__":
    raise SystemExit(main())
