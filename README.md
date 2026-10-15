# Allplan MCP Server

A local MCP bridge between Codex and Allplan 2026 for model queries, audits and
reviewed attribute/layer repairs. Current candidate: **0.17.2**.

0.17.2 updates M4 highlighting so every Column matching “no fire resistance
classification” is highlighted, including Columns already on W1. Only actual
layer changes enter Apply; an all-no-op plan highlights its matches without
confirmation or setters. Unknown values still block the whole action, and plans
with more than 32 changes remain blocked. The exact default names are
`Klasa odporności ogniowej` / `Fire resistance classification`; the native ID
is resolved and checked by name roundtrip. No broad metadata/enum scan is used;
the 0.16.0 discovery route remains quarantined. The
[0.17.1 observation](docs/m4-column-layer-observation-0.17.1.md) found the
no-op highlighting gap after two layer updates. 0.17.2 is being prepared;
automated verification and package delivery will be recorded in its
[delivery README](evaluation-packages/0.17.2/README.md) before the owner test.
[Short Polish owner test](docs/m4-column-layer-0.17.2.pl.md).

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

Use the [0.17.2 evaluation package](evaluation-packages/0.17.2/README.md) on
the machine running Allplan after its delivery checks are recorded. External
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
