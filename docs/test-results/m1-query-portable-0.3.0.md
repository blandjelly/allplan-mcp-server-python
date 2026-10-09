# M1 query implementation — 0.3.0 portable evidence

Recorded: 2026-10-07. Base: current `origin/main`
`d8bd1ef8388daa956e8b51863b17ac33d784dca9`. M0 remains closed and the 0.2.1
context correction remains accepted. Historical evidence uploads and their
archive hashes are unchanged.

Subsequent owner evidence: [three bounded query cases PASS](m1-query-runtime-0.3.0.md).
This report preserves the portable implementation evidence recorded before
that follow-up; no developer tests or original archives were repeated/rebuilt.

## Delivered slice and evidence levels

- **M1.1 partial:** explicit file/passive/visibility scope; session/project/file/
  model/type references and honest completeness. Geometry normalization,
  offsets, levels, durable references and writability remain pending.
- **M1.2 partial:** typed read-only `model_query`, type/layer/raw-attribute
  predicates, all/any/not, missing/null/unknown distinction and numeric/string
  rules. Spatial/dimensional queries are rejected.
- **M1.3 bounded implementation:** deterministic pages, complete cached
  selections, full-selection summaries, query-field/context revalidation,
  expiration, restart/eviction behavior and explicit budget failures.
- **M1.4 pending:** demo bindings/profile schema/fixture are still inactive.

Official 2026 API signatures were checked for SelectAllElements, adapter type
name/GUID, common-property Layer and GetAttributes(ReadAll). Documentation is
feasibility evidence. Fake adapters validate orchestration, never actual native
read behavior. This package has **no new Allplan runtime evidence**; the
[small owner batch](../m1-query-batch.md) is NOT_RUN. Full M1 remains unaccepted.

## Automated checks performed

Linux / external Python **3.12.14**, FastMCP **3.2.4**. Frozen dependency sync
and package build completed. Targeted validation: **24 checks PASS**:

- **21 new query tests:** malformed/deep contracts rejected before enumeration;
  scope/passive/sign handling, empty loaded files, unavailable context and
  identity, projections, raw attribute handling, null/missing/failed reads,
  predicate composition/tolerance/case/types, conflicting representations,
  deterministic pages and full-selection summary, rejected-candidate/addition/
  deletion/context staleness, irrelevant-field independence, TTL/eviction/
  restart/cursor ownership, enumeration/time/size/adapter failures and detached
  response state.
- **1 new real Streamable HTTP MCP test:** generated schemas and query/page/
  summary transport, recursive predicates including explicit null, default/opaque
  ID handling, schema rejection before bridge calls, no writes. The bridge is
  fake and returns an echo; semantic execution is covered by the host tests.
- **2 relevant package checks:** version/lock agreement and deterministic ZIP
  integrity plus installation from its extracted payload, now checking the new
  host query modules and public schema file.

An initial discovery run also executed the 11 existing host-handler checks
because the new test module imported the TestCase class. All passed. The import
was changed to a module reference to prevent duplicate CI discovery. That run
adds no new Allplan evidence and was not a repeat owner batch. Subsequent checks
were targeted; the full historical M0 suite was not rerun.

Developer commands for the relevant checks:

```bash
uv sync --frozen
PYTHONPATH=tests uv run --frozen python -m unittest test_model_query.QueryTests -v
PYTHONPATH=tests uv run --frozen python -m unittest test_mcp_smoke.MCPSmokeTests.test_model_query_schema_transport_predicates_pages_and_summary -v
PYTHONPATH=tests uv run --frozen python -m unittest test_package.PackageTests.test_deterministic_archive_integrity_and_fresh_install_from_extracted_payload test_package.PackageTests.test_version_and_lock_agree -v
uv build
uv run --frozen python utils/build_windows_package.py
```

Query checks were run incrementally as implementation changed, with the new
time/size/sign regression cases checked after addition. No Windows, GitHub
Actions, owner Codex or Allplan query execution is claimed. The existing CI
workflow will run the full suite on its next remote execution.

## Limits and next action

[Contracts](../tool-reference.md) specify the complete implemented behavior.
Counts are unique file/model UUIDs, not proven top-level native components.
Attribute numbers retain raw native units; there are no geometric conversions.
The native candidate-list API and individual calls cannot be interrupted by the
cooperative scan timer. Memory selections are read-only, field-bound snapshots,
not persisted edit targets or future write authorization.

Next: collect the 0.3.0 query/type/layer/attribute/paging batch, resolve runtime
adapter discrepancies, then prepare separate geometry/frame/unit/offset and
native hierarchy probes. Bind the demo only from actual metadata and validated
resources, retaining the fixed six-column/ten-component fixture expectations.
