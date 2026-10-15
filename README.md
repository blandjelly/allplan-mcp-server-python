# Allplan MCP Server

A local MCP bridge between Codex and Allplan 2026 for model queries, audits and
reviewed attribute/layer repairs. Current candidate: **0.18.0**, **ready_for_owner_test**.
289 portable tests, six CI configurations and exact package installation passed;
native wall observation remains pending.

0.18.0 retains the 0.17.2 Columns runtime unchanged and adds one isolated,
read-only native wall-property sample plus **M4 Wall Properties.cmd**. It reads
one existing single-tier wall in foreground file 101 and reports its first
tier's raw material and thickness. The API millimetre assumption is not yet
runtime-verified; no material writes are enabled. The separate 0.17.2 package
and its source/CI evidence remain unchanged, and its native observation was not
run. The owner may test either package first; neither native test is a
prerequisite for the other. See the [0.18.0 delivery README](evaluation-packages/0.18.0/README.md)
and [short Polish wall guide](docs/m4-wall-properties-0.18.0.pl.md).

**M0–M3 are accepted within the retained test project**, Allplan **2026-1-7**
with local Windows Codex. M3 covers recorded one-/two-change Column scenarios
in foreground file 101. This is a fixture evaluation MVP; whole-project office
use is planned. [Acceptance, tests and limits](docs/validation-status.md).

## Documentation

| Read | Purpose |
| --- | --- |
| [Current handoff](docs/next-model-handoff.md) | Current state and next action. |
| [Validation status](docs/validation-status.md) | Accepted scope, test results, limits and original evidence. |
| [Implementation plan](docs/implementation-plan.md) | Completed stages and planned workflows. |
| [Owner development plan (Polish)](docs/office-editing-development-plan.pl.md) | M3 review and proposed query, selection and editing milestones for six element families. |
| [Windows setup](docs/windows-setup.md) / [diagnostics](docs/diagnostics.md) | Install, connect, preserve history and recover unknown results. |
| [Fixture](docs/fixture-guide.md) | Test geometry, resources and current saved state. |
| [Read/audit tools](docs/tool-reference.md) / [M3 execution](docs/m3-execution-contract.md) | Requests and current operational boundaries. |
| [Architecture](docs/architecture.md) / [testing policy](docs/testing-policy.md) | Runtime boundary and required checks. |

## Local Windows setup

Use the [0.18.0 evaluation package](evaluation-packages/0.18.0/README.md) on
the machine running Allplan. External
Python **3.11+** and internet access for locked dependencies are required;
Allplan, Python and Codex are not bundled.

1. Extract the complete package. Close Allplan and run **Setup.cmd**, selecting
   the actual user Local folder.
2. Open the original test project; start Library → Private → PythonHost →
   **StartPythonHost** and keep it running.
3. Run **Launch Allplan MCP.cmd**, then **Connect Codex.cmd** and restart Codex.
   Use local Windows execution; cloud localhost cannot reach this bridge.
4. Run **Diagnostics.cmd**. Preserve package logs and Local/.allplan-mcp/repairs.

Completed writing gates need no repeat. After a lost reply, preserve the saved
execution identity and use read-only recovery; do not send a new Apply.

## Source development

```bash
uv sync --frozen
uv run --frozen allplan-mcp
uv run --frozen python -m unittest discover -s tests -v
uv build
uv run --frozen python utils/build_windows_package.py
```

Settings: ALLPLAN_HOST_URL, ALLPLAN_HOST_TIMEOUT, MCP_HOST, MCP_PORT and MCP_PATH.
Development Python execution requires opt-in on both runtimes. The evaluation
launcher disables it. Repository docs/API identifiers use English; owner
walkthroughs may use Polish. The model prepares code, diagnostics and packages;
the owner observes through Allplan/local Codex without editing Python/JSON.
