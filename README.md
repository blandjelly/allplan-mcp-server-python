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

Current package: **0.15.0**, M1 read profile **1.0.2**, M2 audit profile **2.0.0**.
**M0–M2 / UAT-00–UAT-04 are accepted within the recorded Allplan 2026-1-7 fixture scope**
with local Windows Codex. M3 has accepted layer/status preview and bounded writes,
standard/selection workflows and read-only mark collision previews.
The latest native workflow gate passed two single-target writes, exact readback,
read-only replay, complete audits **5 → 4 → 3** and owner-confirmed two-step Undo.
0.12.0 implements reviewed mark assignment and a deterministic versioned numbering
standard; the [bounded two-target native gate](docs/m3-numbering-acceptance-0.12.0.md)
passed writes, readback, replay/no-op and two-step Undo/recovery.
**M3 / bounded UAT-05/UAT-06 are closed for the retained test project** by the
owner's explicit scope decision. [Closure and evidence](docs/m3-closure.md) define
the fixture evaluation MVP and its one-/two-change scenarios. The executor's
1–32-change eligibility does not extend native acceptance. Typical office-project
use, manual UI active-plan conflicts and broader journal/identity guarantees
remain unaccepted; see the [office-project roadmap](docs/office-project-roadmap.md).
0.13.0 retains invalidated plans for one bounded read-only source comparison;
they remain unavailable to Apply. The [bounded same-session conflict gate](docs/m3-conflict-acceptance-0.13.0.md)
passed 12/12 steps, one C03 write, stale C04 rejection, actual excluded-peer
conflict and Undo/recovery. Leave/save the retained project after Undo.
0.14.1 corrects UUID-dependent write order in the
[controlled unknown-result/restart inspection gate](docs/m3-recovery-owner-test.md).
The 0.14.0 attempt blocked before Apply. The corrected
[bounded native recovery gate passed](docs/m3-recovery-acceptance-0.14.1.md):
13/13 + 6/6 + 6/6, audits 3 → 2 → 3, restart/replay without resume and owner Undo.
Leave/save the same project after Undo; no repeat is required.
[Validation status](docs/validation-status.md) defines the accepted boundaries.
0.15.0 adds [read-only journal inspection](docs/m3-journal-contract.md) and
[bounded native selected-mark acceptance](docs/m3-selected-mark-acceptance-0.15.0.md):
13/13 + 6/6 steps, C04 S02 → S04 with excluded C02, readback/replay, journal
history and Undo/recovery; audits 3 → 1 → 3. Owner confirms UI and uninterrupted
host in A. Leave/save the same copy after Undo. No repeat is required.
The owner resumed work to close M3 within this fixture scope; historical gate
reports and delivered archives retain their as-recorded status. Main integration
and release are separate from milestone acceptance.

Use [Windows setup](docs/windows-setup.md), [fixture definition](docs/fixture-guide.md),
[read tools](docs/tool-reference.md), [audit contract](docs/m2-audit-contract.md),
[workflow execution](docs/m3-workflow-execution-contract.md) and
[diagnostics/recovery](docs/diagnostics.md) for ongoing work.
Completed test cards, logs and previous handoffs are available in Git history.
Delivered archives retain their original contents; new source packages omit
completed test launchers and include current documentation.

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
