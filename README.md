# Allplan MCP Server

Allplan MCP connects a local Codex client to Allplan 2026 for model queries,
audits and reviewed model edits. Current M4 development uses
[`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4);
main remains separate.

Latest package-verified candidate **0.31.0** is source commit
[`0f99863b7c11143d9f14ca12a1027aad5b009195`](https://github.com/blandjelly/allplan-mcp-server-python/commit/0f99863b7c11143d9f14ca12a1027aad5b009195)
on `fix/m4-material-owner-0.31.0`, with [PR #29 to `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/29).
It passed 87 unique focused checks and full
[CI 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481):
625 tests on Ubuntu Python 3.12.15 and 625 on Windows Python 3.12.10, plus the
package job. The original CI artifact was unavailable, so one fallback ZIP
built from clean exact source (`source_modified=false`) passed verification:
201 payload files, 43 bridge hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`. Native
Allplan material trial remains pending. See the [0.31.0 evaluation record](evaluation-packages/0.31.0/README.md),
[verified ZIP](evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip),
[ZIP verification](evaluation-packages/0.31.0/package-verification.json) and
[source CI provenance](evaluation-packages/0.31.0/source-ci.json).

Retained completed candidate **0.30.0** is source commit
`9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6` on
`feat/m4-combined-evidence-0.30.0`, with [PR #28 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/28).
It passed 142 unique focused checks and full
[CI 39993048110](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39993048110):
622 tests on each Windows and Ubuntu Python 3.12 job plus the package job. The
original CI artifact was unavailable, so one fallback ZIP from the exact clean
source passed verification on its first attempt: 196 payload files, 43 bridge
hashes, SHA-256 `78b7b24c98749ebbd28814f84d70a2fc9cbeab80b477b9fd1585e5c10e63af8e`.

The candidate adds read-only `attribute_evidence` and fresh no-op evidence with
zero-setter accounting. In the owner's reported Allplan session, trials 1–3
and 5 passed, while trial 4's native material stage failed closed before Apply:
two Wall previews reported unsupported hierarchy/child ownership, with zero
changes, zero setters and no Apply. Trial 5 has detailed evidence for four
scalar writes with fresh readback and UI Undo/restoration (Column text/integer/
real and Wall text). Other families, Slab/MultiSlab ownership, native selection,
and date/vector writes remain incomplete. The owner log identifies bridge
0.30.0 and verified bridge integrity, but does not include the installed ZIP
manifest, so outcomes are not attributed to that exact ZIP. See the
[0.30.0 evaluation record](evaluation-packages/0.30.0/README.md),
[scoped Allplan observation](docs/test-results/m4-owner-observation-0.30.0-2026-10-23.md),
[trial 5 log](docs/test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md),
[development plan](docs/office-editing-development-plan.pl.md), and
[current handoff](docs/next-model-handoff.md). Priorities 1–5 remain partial.
The 0.31.0 material fix preserves the selected Wall's exact target binding and
strict single-tier/no-opening guards. Its focused parent-wrapper regression
passes, while the 0.30.0 opening case's `component_child_owner_mismatch`
remains unresolved. Native Allplan material acceptance is pending. See the
[0.31.0 API note](docs/m4-editing-api-0.31.0.md) and
[bounded native trial plan](docs/m4-single-drawing-0.31.0.pl.md). Earlier scoped
observations are indexed in [validation status](docs/validation-status.md).

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

To reproduce the recorded 0.30.0 evaluation, use its verified ZIP linked from
the [0.30.0 evaluation record](evaluation-packages/0.30.0/README.md). For the
new 0.31.0 material trial, use the [verified fallback ZIP](evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip)
and follow the [one-path trial plan](docs/m4-single-drawing-0.31.0.pl.md). Use the Windows
machine running Allplan and Codex for the recorded trial. External Python
**3.11+** and internet access for locked dependencies are required.
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
