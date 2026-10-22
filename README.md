# Allplan MCP Server

Allplan MCP connects a local Codex client to Allplan 2026 for model queries,
audits and reviewed model edits. Current M4 development uses
[`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4);
main remains separate.

Candidate **0.28.0** is source commit
`b59ef15d9bfd4dfb42476b240e31b5b300268d2d` on `fix/m4-owner-views-0.28.0`,
with [PR #26 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/26).
Focused verification passed 170 unique affected/dependent checks. Full CI run
[39871551499](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39871551499)
passed 601 tests on each Windows and Ubuntu Python 3.12 job plus the package
job. PR #26 targets `develop/m4`. The original CI ZIP was unavailable to the
executor, so one fallback ZIP was built from the exact clean source and passed
verification on its first attempt: 186 payload files, 42 bridge hashes, SHA-256
`74099ec341cdf8b2bc87def42487fafbbbcdb963ec6f4b8859a412f7b6d064ed`.

The candidate matches component parent edges by drawing, model UUID and type
across view wrappers, while retaining actual parent view UUIDs in the deletion
evidence and binding the selected target's exact view UUID. It also raises the
journal capacity limits while preserving the per-record bound and protection
for unresolved or unverifiable history. See the
[0.28.0 evaluation record](evaluation-packages/0.28.0/README.md),
[0.28.0 API evidence](docs/m4-editing-api-0.28.0.md),
[short native trial](docs/m4-single-drawing-0.28.0.pl.md), and
[current handoff](docs/next-model-handoff.md). Native 0.28.0 has not been run;
M4 priorities 1–5 remain incomplete. Exact ZIP checks include checksum/payload,
registration, frozen sync/import, `drawing_identity` schema, source safety
limits, upgrade/restore, and history markers. The scoped 0.27.0 native observations are
indexed in [validation status](docs/validation-status.md).

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

For the next native trial, use the exact verified 0.28.0 ZIP linked from the
[0.28.0 evaluation record](evaluation-packages/0.28.0/README.md) on the Windows
machine running Allplan and Codex. External
Python **3.11+** and internet access for locked dependencies are required.
Allplan, Python and Codex are not bundled.

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
