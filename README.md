# Allplan MCP Server

A local FastMCP bridge for working with Allplan 2026 through Codex. The project
extends an existing PythonPart host into 13 workflow tools for inspecting native
models, auditing quality, applying controlled repairs, generating structures and
preparing documentation. The first useful release is context → query → audit →
previewed attribute/layer repairs. Codex is the first client; MCP contracts stay
client-neutral for a later Claude integration.

## Project context

Read these files in order when continuing implementation:

1. [Current handoff](docs/next-model-handoff.md): verified state, limits and next work.
2. [Architecture](docs/architecture.md): runtime boundary and shared contracts.
3. [Features](docs/features.md): the 13 tools and demonstration fixture.
4. [Implementation stages](docs/implementation-plan.md): task IDs and exit gates.
5. [Validation schedule](docs/testing-policy.md): focused local work, publication
   checks, CI matrix and retained hash protections.

Current package: **0.11.0**, M1 read profile **1.0.2**, M2 audit profile **2.0.0**.
**M0 and bounded M1 are accepted** on Allplan **2026-1-7** with local Windows Codex; UAT-00–UAT-03 PASS.
The demo profile binds freshly for reads and remains inactive for writes.
[Acceptance and limits](docs/test-results/m1-acceptance-0.5.3.md) cover the known
fixture, display-unit invariance and nonzero XY offset. **M2.1–M2.3 / UAT-04
PASS within the retained read-only fixture scope**, package 0.6.1;
[acceptance and evidence](docs/test-results/m2-acceptance-0.6.1.md).
[Native 0.6.0 report/UI checks](docs/test-results/m2-audit-runtime-0.6.0.md) match
the fixture. 0.6.1 contains UI callback exceptions and rejects invalid audit scope
before contacting Allplan; [correction and limits](docs/test-results/m2-dispatch-fix-0.6.1.md).
Both repeated audits, scope rejection through MCP/host and post-error health
passed; the owner confirms Allplan and host remain running. The earlier crash's
precise cause remains unproven. The [completed stability card](docs/m2-stability-batch.md)
retains the test recipe; no further M2 owner batch is requested. `model_audit` returns read-only
findings, coverage and file/mark/location evidence. The
[UAT-04 card](docs/m2-audit-batch.md) records the original procedure.
The first M3 slice adds read-only `fix_model_issues` preview/revalidation for
explicit layer/status choices, with exact old/new values, bounded plans and stale
checks. **Bounded M3 preview gate PASS**;
[native evidence and limits](docs/test-results/m3-preview-acceptance-0.7.0.md),
[completed owner card](docs/m3-preview-batch.md);
[contract](docs/m3-repair-contract.md). Package 0.8.0 adds bounded disposable-copy
apply/readback, a durable execution journal and read-only recovery.
The first 0.8.0 native write was rejected before setters by
an overly broad IsInMacro check; [original evidence and correction](docs/test-results/m3-apply-rejection-0.8.0.md).
0.8.1 uses verified root hierarchy and reports explicit pre-write rejections.
[Execution contract](docs/m3-execution-contract.md),
[completed write/Undo owner card](docs/m3-apply-batch.md).
**Bounded 0.8.1 execution gate PASS**: both native repairs/readbacks, audited
collateral verification, exact-ID replay across host sessions, two separate
Undo steps, and recovery after owner-confirmed Redo;
[evidence and limits](docs/test-results/m3-execution-acceptance-0.8.1.md).
The UI interrupted the host in the subsequent manual-edit scenario;
[native old-plan rejection after restart PASS](docs/test-results/m3-plan-restart-acceptance-0.8.1.md).
Same-session manual-edit conflict is blocked in that observed lifecycle and
is not claimed as accepted.
[Native stale Apply rejection PASS](docs/test-results/m3-stale-apply-acceptance-0.8.1.md)
with identical complete before/after audits and unchanged owner-observed values/appearance.
Package **0.9.0** adds the first M3.3 read-only `apply_office_standard` and
predicate/exception `rule_based_edit` previews using the shared audit/planner.
[Contract](docs/m3-standards-contract.md),
[portable validation](docs/test-results/m3-standards-portable-0.9.0.md),
[native standard/selection preview PASS](docs/test-results/m3-standards-acceptance-0.9.0.md).
Package **0.10.0** adds exact-target mark repair previews and whole-scope
collision simulation, including excluded peers. Mark plans cannot use Apply.
[Mark contract](docs/m3-marks-contract.md),
[native marks-preview PASS](docs/test-results/m3-marks-acceptance-0.10.0.md),
[completed read-only owner card](docs/m3-marks-preview-batch.md).
All ten steps, positive proposals, selection exception, excluded-peer collision
and unchanged revalidations pass; owner confirms model unchanged and host
uninterrupted. No repeat is required.
Package **0.11.0** connects reviewed standard/selection plans to the shared
executor and supports 1–32 existing string-status/layer changes on Column roots
in one foreground file. It retains full source checks, exceptions, durable
deduplication and readback, with no fixed demo finding count.
[Execution contract and journal lifecycle](docs/m3-workflow-execution-contract.md),
[next owner test](docs/m3-workflow-apply-batch.md). Expanded native execution is
**not_run**. Mark writes/numbering, native same-session conflicts and unknown
recovery remain required open work; M3/UAT-05/UAT-06 are not closed.

Repository documentation and API identifiers use English. Owner-facing
walkthroughs may use Polish. The implementation model owns coding, diagnostics,
packages and automated checks; the owner tests through Codex and the Allplan UI.
The owner does not edit Python/JSON or research API identifiers.

## Local Windows setup

Use a versioned evaluation ZIP on the Windows machine running Allplan and Codex.
It requires external Python 3.11+ and internet access for locked dependencies;
it does not bundle Allplan, Python or Codex. See the [Windows setup guide](docs/windows-setup.md).

1. Extract the complete ZIP into a writable, versioned folder. Close Allplan.
2. Run **Setup.cmd** and select the actual Allplan user `Local` folder, commonly
   `Documents\Nemetschek\Allplan\2026\Usr\Local`. The installer checks hashes,
   installs the full bridge and backs up its previous version.
3. Open Allplan and the intended project. In Library → Private → PythonHost,
   start **StartPythonHost** and keep it running.
4. Run **Launch Allplan MCP.cmd**, then **Connect Codex.cmd** and restart Codex.
   Use a local Windows chat; cloud localhost cannot reach the Windows bridge.
5. Run **Diagnostics.cmd** for a read-only report in `logs`.

The bridge listens at `http://127.0.0.1:5679`; MCP uses
`http://127.0.0.1:8888/mcp`. The connection helper preserves existing Codex settings
and adds `[mcp_servers.allplan_m0]` with that URL. For updates, close Allplan and
the MCP console, extract a new package and run Setup again. To roll back, close
both and run **Restore bridge.cmd**, then use the previous package's launcher.

For `host_absent` or `session_unavailable`, open the intended project and restart
StartPythonHost. For a lost write response (`execution_unknown`), inspect/reconcile
the model before retrying. Never mix files from different versioned packages.

## Source development

```bash
uv sync --frozen
uv run --frozen allplan-mcp
uv run --frozen python -m unittest discover -s tests -v
uv build
uv run --frozen python utils/build_windows_package.py
```

For source registration on Windows, use `utils\register_python_host.cmd`.
External-server dependencies stay outside Allplan's embedded Python. Environment
settings: `ALLPLAN_HOST_URL`, `ALLPLAN_HOST_TIMEOUT`, `MCP_HOST`, `MCP_PORT`,
`MCP_PATH`. Development Python execution requires opt-in on both runtimes; see
[architecture](docs/architecture.md).
