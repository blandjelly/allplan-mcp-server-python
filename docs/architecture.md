# Architecture

## Runtime boundary

```text
Local MCP client (Codex)
  → FastMCP server: Streamable HTTP at 127.0.0.1:8888/mcp
  → AllplanHostClient: JSON POST, default 30-second timeout
  → PythonPart HTTP bridge at 127.0.0.1:5679
  → UI-thread dispatcher → typed handler → Allplan 2026 API
  → JSON observations and outcomes
```

All `NemAll_*` imports, live documents, adapters and writes stay inside the host.
UI callbacks contain exceptions and return result/error data; raise HTTP errors
on the worker after dispatch returns. Persist bounded request/error logs under
Local/.allplan-mcp/logs. Read the current document per request. Keep rules, profiles, query semantics and
change planning portable and testable without Allplan. Exchange JSON snapshots,
never live adapters or `repr()` strings as stable references. Keep the existing
UI dispatcher; shutdown must not join a worker waiting on that dispatcher.

| Existing location | Responsibility |
| --- | --- |
| `src/allplan_mcp/server.py` | MCP tools and skill resources. |
| `src/allplan_mcp/allplan_client.py` | Bridge requests, request IDs and error mapping; no automatic write retries. |
| `src/allplan_mcp/diagnostics.py` | Read-only connection, version and context diagnostics. |
| `python_host/PythonPartsScripts/PythonHost/StartPythonHost.py` | Interactor, listener lifecycle and UI dispatch. |
| Host `transport.py`, `PythonHostHandler.py`, `runtime_info.py`, `model_context.py` | JSON transport, typed routes, runtime metadata and bounded context probe. |
| `utils/`, `windows/` | Recursive registration, package integrity, launchers, Codex setup and restore. |
| Host `model_query.py`, `native_readers.py`, `model_metadata.py`, `query_contracts.py`, `spatial_contracts.py`, `profile_contracts.py` | Bounded model reads, geometry/hierarchy, metadata and validated read binding. |
| Host `audit_contracts.py`, `model_audit.py`; MCP `audit_models.py` | M2 profile validation, fresh full read-only audits and JSON/text findings; no writes. |
| `profiles/`, `tests/` | Versioned demo read/audit profiles and portable checks. |

Add `contracts/`, `services/`, host `handlers/` and `adapters/` only when needed.
Use versioned JSON contracts and validated profiles; do not assume external
Python dependencies are available inside Allplan.

Bundled API-reference, geometry, rebar and utilities skills remain runtime
resources in `src/allplan_mcp/allplan_skills/`. MCP exposes `allplan://skills`,
`allplan://skills/{skill_name}` and their `assets/{asset_name}` and
`scripts/{script_name}` resources. Template scripts guide development.

## Required contracts

M1 implements bounded context, scope, session-bound references/snapshots and
read-only selections; [read contracts](tool-reference.md) define their limits.
The table also includes future mutation, audit and registry contracts.

| Contract | Required fields and behavior |
| --- | --- |
| `ModelContext` | Session/project identity, installed build, active/loaded files and states, units, offset, levels, capabilities and omissions. |
| `Scope` | Explicit file IDs/references, filters, visibility, read/write eligibility and completeness. |
| `ElementRef` | Project/session, drawing file, model UUID and type; view UUID kept separately; re-resolve before writing. |
| `ElementSnapshot` | Typed attributes, layer, supported native properties, normalized geometry and relevant source fingerprints. |
| `SelectionResult` | Reusable ID, scope, snapshot, total counts, pages and omissions; a page is not the full edit scope. |
| `AuditReport` | Rule/severity, references, evidence, remedies, coverage; `pass`, `fail`, `not_checked`, `not_applicable`. |
| `ChangePlan` | Exact targets and old/new values, operations, exclusions, source fingerprints, profile version, expiry/session and hash. |
| `ExecutionResult` | Request ID, per-target applied/skipped/conflict/failed/unknown outcomes, readback and recovery/Undo limits. |
| `PackageRegistry` | Generation/package keys, owned roles, source fingerprints, files/layouts, issue metadata and output hashes. |

Canonical geometry uses explicit millimetres and degrees, preserving input units.
Verify conversion and apply project offset exactly once. Normalize signed passive
file numbers while preserving state. Names and `document_id` are not unique
project identities; `GetTimeStamp()` is not a universal modification counter.
Fingerprint the fields relevant to the operation. Visibility differs from screen
inclusion. Report omitted/unloaded/read-only scope explicitly.

## Shared mutation lifecycle

Package **0.8.0** adds the bounded evaluation executor `repair_execution.py`
and 2026 `native_repairs.py`: fresh target/eligibility checks, write-ahead Local
journal, serialized execution, readback/full audited-field verification and
read-only recovery. Exact execution-ID replay never repeats setters. General
writes remain bounded. Native 0.8.1 two-target writes and separate Undo are
accepted; see [execution contract](m3-execution-contract.md). Package 0.11.0
uses that shared executor for 1–32 existing status/layer changes and reviewed
standard/selection plans. [Expanded scope and journal lifecycle](m3-workflow-execution-contract.md)
have [bounded native workflow acceptance](test-results/m3-workflow-acceptance-0.11.0.md):
separate single-target writes, full audited verification, exact-ID read-only
replay and owner-observed two-step Undo. Wider supported scopes remain unaccepted.

The earlier M3 slice in 0.7.0 implements only explicit preview and fresh evidence
revalidation: host `repair_contracts.py` / `model_repair.py`, public
`repair_models.py` and `fix_model_issues`. Its bounded session-local cache stores
immutable returned-plan copies with ID/hash and expiry; no apply/writability,
durable mutation journal or Undo is claimed. See [contract](m3-repair-contract.md).

1. Resolve explicit scope and supported operations.
2. Produce a side-effect-free preview with targets, values, exclusions and counts.
3. Bind apply to the reviewed plan ID/hash and current user authorization.
4. Re-read identity, writability and relevant source fields; reject/report conflicts.
5. Serialize writes in a valid Allplan context, using only tested Undo grouping.
6. Read back actual results and record per-target outcomes.
7. Invalidate affected selections/plans and reconcile registry state.

A repeated request ID must not repeat an applied mutation. After timeout or host
restart, reconcile unknown outcomes before retrying. Prove durable deduplication
or document its recovery limits. Allplan Undo, multi-file changes, registry writes
and exported files are not one atomic transaction. Keep registry data outside
undocumented Allplan internals and define persistence, migration, backup,
project-copy and Undo reconciliation. Registry membership alone does not prove an
element still exists. Regeneration must detect conflicts with manual edits.

Production workflows use typed handlers. `execute_python` is development-only:
MCP requires `ALLPLAN_MCP_ENABLE_PYTHON_EXEC=1` and the host must separately opt in.
The evaluation launcher disables it. AST filtering blocks imports/private access
and restricts builtins, but is not process isolation. Retain loopback deployment.

Use [Allplan 2026 API documentation](https://pythonparts.allplan.com/2026/).
Validate exact signatures and read/create/update support on the installed build;
do not include 2027-only BuildingStructure/ReportService claims. Distinguish
ordinary native components from Structural Framing and single-/multi-layer walls.
Configured floor/grid/file mappings remain necessary until API behavior is proven.
