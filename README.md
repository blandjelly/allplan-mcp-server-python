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

Current package: **0.12.0**, M1 read profile **1.0.2**, M2 audit profile **2.0.0**.
**M0–M2 / UAT-00–UAT-04 are accepted within the recorded Allplan 2026-1-7 fixture scope**
with local Windows Codex. M3 has accepted layer/status preview and bounded writes,
standard/selection workflows and read-only mark collision previews.
The latest native workflow gate passed two single-target writes, exact readback,
read-only replay, complete audits **5 → 4 → 3** and owner-confirmed two-step Undo.
0.12.0 implements reviewed mark assignment and a deterministic versioned numbering
standard; the [bounded two-target native gate](docs/m3-numbering-acceptance-0.12.0.md)
passed writes, readback, replay/no-op and two-step Undo/recovery.
**M3/UAT-05/UAT-06 remain open**: remaining scope acceptance, native same-session
conflicts and controlled partial/unknown recovery are next.
[Validation status](docs/validation-status.md) defines the accepted boundaries.

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
