# Architecture

```text
Local Windows MCP client
  → FastMCP, 127.0.0.1:8888/mcp
  → AllplanHostClient, JSON POST (default 30-second timeout)
  → PythonPart HTTP bridge, 127.0.0.1:5679
  → UI-thread dispatcher → typed handler → Allplan 2026 API
  → JSON observations/outcomes
```

All NemAll imports, live documents/adapters and writes stay inside the host.
Resolve the current document per request; exchange JSON snapshots, not retained
adapters. Contain callback exceptions and raise HTTP errors on the worker after
dispatch. Shutdown must not join a worker waiting on the UI dispatcher.

| Location | Responsibility |
| --- | --- |
| `src/allplan_mcp/server.py`, `allplan_client.py` | Typed MCP tools, JSON bridge, request IDs/error mapping; no automatic write retries. |
| Host `StartPythonHost.py`, `PythonHostHandler.py`, `transport.py` | Interactor/listener lifecycle, UI dispatch and typed routes. |
| Host `model_context.py`, `model_query.py`, `native_readers.py`, `model_metadata.py` | Context, bounded reads/geometry/hierarchy and profile/metadata inspection. |
| Host `model_scope.py`, `model_properties.py`, `model_selection.py`, `property_contracts.py`, `property_probe.py` | Open-file read scope, sampled property support registry and full-result UI highlight probe. |
| Host `model_audit.py`, `model_repair.py`, `mark_numbering.py` | Fresh audits, immutable plans, source/collision checks and numbering. |
| Host `native_repairs.py`, `repair_execution.py` | Native preflight/setters, OS lock, durable journal, readback and recovery. |
| `profiles/`, MCP `*_models.py`, host `*_contracts.py` | Versioned profiles and typed contracts; host remains dependency-free. |
| `utils/`, `windows/`, `tests/` | Installation/integrity/restore, launchers and portable checks. |

Shared contracts: explicit Scope/ModelContext, session-bound ElementRef,
typed ElementSnapshot, full SelectionResult, AuditReport, immutable ChangePlan
and per-target ExecutionResult. PackageRegistry for owned generated content is
future work. See [read/audit tools](tool-reference.md) and [M3 execution](m3-execution-contract.md).

Canonical geometry uses mm/degrees and applies project offset once. Preserve raw
attribute units and observation provenance. Names/document IDs are not unique
project identities; timestamps are not universal change counters. Coverage,
omissions and not_checked states must remain explicit.

M4 discovery/highlight resolves live adapters only inside the current UI request;
the query cache retains JSON only. Presentation revalidates full-source evidence
including rejected peers before obtaining all matched adapters, checks TTL again
after reads and never converts a highlight into write authorization. Symbol
availability, submission, native observation and accepted_on_build are separate.

Bundled API-reference/geometry/rebar/utilities skills are MCP resources under
allplan://skills. `execute_python` is development-only: both runtimes must opt
in; the evaluation launcher disables it. AST filtering is not process isolation.
Keep loopback deployment and Local/.allplan-mcp/logs. Validate signatures against
[Allplan 2026 documentation](https://pythonparts.allplan.com/2026/), then prove
native behavior; do not infer 2027 API support or generic writable properties.

Broad M4 property discovery is quarantined after the 0.16.0 native crash. The
isolated property service traces each new reader before invocation with flush/fsync;
its inherited M1 scan is a coarse service boundary. Tracing does not isolate
native faults from the process. External pending requests are saved before send,
and no new phase or retry follows a lost reply.

M4 0.17.0 `column_layer.py` builds criterion-based plans independently of audits.
RepairPlanService supplies source observations to the same RepairExecutor for
both audit and criterion plans. Journal records keep either audit_request or
criterion_request; recovery remains read-only. A submitted exact highlight is
required for Column-layer Apply and clearing/replacing highlights invalidates it.
The native resolver retains enumeration owners through caller reads/setters.
