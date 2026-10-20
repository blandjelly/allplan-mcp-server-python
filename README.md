# Allplan MCP Server

Allplan MCP connects a local Codex client to Allplan 2026 for model queries,
audits and reviewed model edits. Current M4 development uses
[`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4);
main remains separate.

The current candidate is **0.24.0**. It adds read-only component identity and
parent/child evidence, blocks ambiguous Slab/MultiSlab writes, and expands
single-drawing ownership/W1 contract checks. The owner reports PASS for 0.23.0
journal preview and confirmed archival; preserve its bounded evidence.
[Package and evidence](evaluation-packages/0.24.0/README.md) ·
[short native trial](docs/m4-single-drawing-0.24.0.pl.md) ·
[current handoff](docs/next-model-handoff.md).

M4 remains partially accepted. Native selection, native material updates,
complete support for all six families, multi-file writes and whole-project
access remain outside the accepted scope. Preserve the exact target binding,
revalidation, journal, replay and unknown-result safeguards. The
[office editing plan](docs/office-editing-development-plan.pl.md) records the
remaining development gates.

## Documentation

| Read | Purpose |
| --- | --- |
| [Current handoff](docs/next-model-handoff.md) | Branch, current scope, evidence and next action. |
| [Development plan](docs/office-editing-development-plan.pl.md) | M4 status, priorities and acceptance criteria. |
| [Validation status](docs/validation-status.md) | Historical accepted scope and retained native evidence. |
| [Implementation plan](docs/implementation-plan.md) | Accepted M0–M3 baseline and deferred stages. |
| [Windows setup](docs/windows-setup.md) / [diagnostics](docs/diagnostics.md) | Install, connect, preserve history and recover unknown results. |
| [Fixture guide](docs/fixture-guide.md) | Test geometry, resources and saved project state. |
| [Tool reference](docs/tool-reference.md) / [M3 execution contract](docs/m3-execution-contract.md) | MCP requests and operational boundaries. |
| [Architecture](docs/architecture.md) / [testing policy](docs/testing-policy.md) | Runtime boundary and required checks. |

## Local Windows setup

Use the [complete 0.24.0 evaluation package](evaluation-packages/0.24.0/README.md)
on the Windows machine running Allplan and Codex. External Python **3.11+**
and internet access for locked dependencies are required. Allplan, Python and
Codex are not bundled.

1. Extract the full ZIP into a writable versioned folder. Close Allplan and run
   `Setup.cmd`, selecting the actual user Local folder.
2. Open the retained test project. Start `StartPythonHost` from Library →
   Private → PythonHost and keep it running.
3. Run `Launch Allplan MCP.cmd`, then `Connect Codex.cmd` and restart Codex.
4. Run `Diagnostics.cmd` and retain its package logs.

Preserve `Local/.allplan-mcp/repairs`, diagnostic traces and archives, the
original project, package logs and execution IDs. A lost write reply is an
unknown result: recover with the original execution ID and do not retry Apply.
The cloud workspace cannot access Windows localhost.
