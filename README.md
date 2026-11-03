# Allplan MCP Server

Allplan MCP connects a local MCP client (Codex or Claude Code) to Allplan 2026
for model queries, audits and reviewed edits. M4 development uses
[`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4);
main integration is separate. Agent instructions: [AGENTS.md](AGENTS.md)
(Claude Code: [CLAUDE.md](CLAUDE.md)).

M4 goal: typed, reviewed editing of every API-exposed attribute, and where
possible native properties, of Columns, Beams, Walls and Slabs. Installed
baseline **0.44.1**, candidate **0.44.2**; M4 remains
partially accepted. Version, delivery, native evidence and the next task are
kept only in the [current handoff](docs/next-model-handoff.md); remaining work
and blockers in the [development plan](docs/development-plan.md).

## Documentation

| Read | Purpose |
| --- | --- |
| [Documentation policy](docs/documentation-policy.md) | Keep the handoff and backlog concise; avoid redundant files. |
| [Current handoff](docs/next-model-handoff.md) | Current version, delivery and next action. |
| [Development plan](docs/development-plan.md) | Remaining work, blockers and acceptance criteria. |
| [Coverage matrix](docs/m4-coverage-matrix.md) | Family × field/type × operation status. |
| [Validation status](docs/validation-status.md) | Concise accepted scopes and necessary source evidence. |
| [Implementation plan](docs/implementation-plan.md) | M0–M3 baseline and later stages. |
| [Windows setup](docs/windows-setup.md) / [diagnostics](docs/diagnostics.md) | Install, connect and recover unknown results. |
| [Fixture guide](docs/fixture-guide.md) | Test geometry, resources and retained project state. |
| [Tool reference](docs/tool-reference.md) / [M3 execution contract](docs/m3-execution-contract.md) | MCP requests and operational boundaries. |
| [M4 operator guide](docs/m4-model-edit.md) / [editing API notes](docs/m4-editing-api.md) / [attribute API evidence](docs/m4-attribute-api-evidence.md) / [type coverage](docs/m4-attribute-type-coverage.md) | API contracts and their documented limits. |
| [Architecture](docs/architecture.md) / [testing policy](docs/testing-policy.md) | Runtime boundary and required checks. |

Versioned API research notes retain the scope stated in each note; current
release status belongs in the handoff. Superseded release descriptions and
trial instructions are available in Git history, not as current work plans.

## Local Windows setup

Use the ZIP produced by the GitHub Actions package job for the version in the
[handoff](docs/next-model-handoff.md) and follow [Windows setup](docs/windows-setup.md).
[`evaluation-packages/`](evaluation-packages/) is a historical archive (0.7.0–0.33.0;
0.32.0 is the last package verified there). External Python **3.11+**
and internet access for locked dependencies are required.
Allplan, Python and the MCP client are not bundled.

Preserve `Local/.allplan-mcp/repairs`, diagnostic traces and archives, the
original project, package logs and execution IDs. A lost write reply is an
unknown result: recover with the original execution ID and do not retry Apply.
For eligible native-material preservation conflicts, review the proposed
reconciliation against the current model before submitting its exact hash and
acknowledgement; this read-only action does not report an applied success.
The cloud workspace cannot access Windows localhost.

