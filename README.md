# Allplan MCP Server

Allplan MCP connects a local Codex client to Allplan 2026 for model queries,
audits and reviewed edits. M4 development uses
[`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4);
main integration is separate.

Current source candidate: **0.38.0** on `fix/m4-material-recovery`; 177 unit
checks and 11 MCP/HTTP checks passed, with version consistency at 0.38.0. Full
CI, package verification and native Allplan validation are pending.
The most recently package-verified candidate remains **0.32.0**. Use the
[current handoff](docs/next-model-handoff.md) for version status and the next
task, and the
[development plan](docs/office-editing-development-plan.pl.md) for remaining
work and unresolved errors. M4 remains partially accepted.

## Documentation

| Read | Purpose |
| --- | --- |
| [Documentation policy](docs/documentation-policy.md) | Keep the handoff and backlog concise; avoid redundant files. |
| [Current handoff](docs/next-model-handoff.md) | Current version, delivery and next action. |
| [Development plan](docs/office-editing-development-plan.pl.md) | Remaining work, blockers and acceptance criteria. |
| [Validation status](docs/validation-status.md) | Concise accepted scopes and necessary source evidence. |
| [Implementation plan](docs/implementation-plan.md) | M0–M3 baseline and later stages. |
| [Windows setup](docs/windows-setup.md) / [diagnostics](docs/diagnostics.md) | Install, connect and recover unknown results. |
| [Fixture guide](docs/fixture-guide.md) | Test geometry, resources and retained project state. |
| [Tool reference](docs/tool-reference.md) / [M3 execution contract](docs/m3-execution-contract.md) | MCP requests and operational boundaries. |
| [M4 operator guide](docs/m4-model-edit.pl.md) / [attribute API evidence](docs/m4-attribute-api-evidence.md) / [type coverage](docs/m4-attribute-type-coverage.md) | API contracts and their documented limits. |
| [Architecture](docs/architecture.md) / [testing policy](docs/testing-policy.md) | Runtime boundary and required checks. |

Versioned API research notes retain the scope stated in each note; current
release status belongs in the handoff. Superseded release descriptions and
trial instructions are available in Git history, not as current work plans.

## Local Windows setup

Download the verified ZIP from the [current package record](evaluation-packages/0.32.0/README.md)
and follow [Windows setup](docs/windows-setup.md). External Python **3.11+**
and internet access for locked dependencies are required.
Allplan, Python and Codex are not bundled.

Preserve `Local/.allplan-mcp/repairs`, diagnostic traces and archives, the
original project, package logs and execution IDs. A lost write reply is an
unknown result: recover with the original execution ID and do not retry Apply.
For eligible native-material preservation conflicts, review the proposed
reconciliation against the current model before submitting its exact hash and
acknowledgement; this read-only action does not report an applied success.
The cloud workspace cannot access Windows localhost.
