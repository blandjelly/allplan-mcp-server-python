# Allplan MCP Server

**M4 development: [`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4).**
New M4 PRs target this shared branch. Main remains a separate accepted baseline;
legacy M4 branches/PRs are historical references. [Branch layout and workflow](docs/branch-layout.md).

A local MCP bridge between Codex and Allplan 2026 for model queries, audits and
reviewed attribute/layer repairs. Current source candidate: **0.20.1** fixes typed numeric undefined values and
binds Wall layer edits to their actual tiers. [Focused fixes and native trial](docs/m4-agent-fixes-0.20.1.pl.md).
The preceding **0.20.0** adds typed criterion-based `model_edit`
with exact project bindings, attribute add/replace/upsert and organizational layer
changes through the shared guarded executor. New native behavior awaits a scoped
Allplan trial; [Polish workflow and limits](docs/m4-model-edit.pl.md).
The preceding **0.19.0** adds
`model_wall_filter`, a bounded read-only filter and highlight for single-tier
Walls in one explicit foreground drawing. Source **e455f35** passed **356 tests**
in each of six Windows/Ubuntu CI configurations; the exact delivered ZIP passed
installation, upgrade/restore and 31 bridge hashes. Native observation is
**PASS / accepted_on_build 0.19.0** for the two-Wall foreground-101 `<240 mm` workflow:
200 mm matches, 240 mm does not; the owner confirmed the 20 cm highlight,
its clear and uninterrupted host operation. All four health replies share one
session. [Observation and original uploads](docs/m4-wall-filter-observation-0.19.0.md).
This scoped trial is complete and needs no repeat. See the
[0.19.0 guide](docs/m4-wall-filter-0.19.0.pl.md) and
[tool contract](docs/tool-reference.md#model_wall_filter--m4-wall-thickness-filter).

The previous **0.18.2** package corrected the blocked
single-Wall sample when M1 resolves multiple Python wrappers of the same native
root. Conflicting identities/fields and multiple views still block reads.
[Windows package and checks](evaluation-packages/0.18.2/README.md),
[short Polish Wall check](docs/m4-wall-sample-0.18.2.pl.md).
The owner confirmed **PASS / accepted_on_build 0.18.2** for one native Wall
read: **240 mm**, material **`Beton`**, matching the UI. Two Walls were found;
only the first in model UUID order was sampled, as intended.
[Observation and original logs](docs/m4-wall-observation-0.18.2.md).
The owner confirmed responsive host transport and Columns no-op highlighting
on **0.18.1**; its 306 tests, six CI jobs and package checks remain recorded
with the [previous delivery](evaluation-packages/0.18.1/README.md).
The frozen **0.18.0** Wall package passed 289 portable tests, six CI configurations
and exact package installation. The Wall sample on 0.18.1 was **BLOCKED** by
ambiguous adapter representations before its native property read.
[Latest observations and original logs](docs/m4-native-observation-0.18.1-2026-10-17.md).

0.18.0 retains the 0.17.2 Columns runtime unchanged and adds one isolated,
read-only native wall-property sample plus **M4 Wall Properties.cmd**. It reads
one existing single-tier wall in foreground file 101 and reports its first
tier's raw material and thickness. The API millimetre assumption is not yet
runtime-verified; no material writes are enabled. The separate 0.17.2 package
and its source/CI evidence remain unchanged. The owner confirmed its no-op
highlight behavior through the same handler in 0.18.1; writes and complete M4
acceptance remain separate. See the [0.18.0 delivery README](evaluation-packages/0.18.0/README.md)
and [short Polish wall guide](docs/m4-wall-properties-0.18.0.pl.md).

Source development also includes an [offline saved-wall-report analyzer](docs/m4-wall-report-analysis.md).
It checks conditional thickness/material conclusions and missing evidence without
contacting Allplan. It is not in the frozen 0.18.0 ZIP and cannot authorize writes;
the 0.18.2 observation accepts one Wall read, not full-Wall filtering or writes.

**M0–M3 are accepted within the retained test project**, Allplan **2026-1-7**
with local Windows Codex. M3 covers recorded one-/two-change Column scenarios
in foreground file 101. This is a fixture evaluation MVP; whole-project office
use is planned. [Acceptance, tests and limits](docs/validation-status.md).

## Documentation

| Read | Purpose |
| --- | --- |
| [Current handoff](docs/next-model-handoff.md) | Current state and next action. |
| [Branch layout](docs/branch-layout.md) | Shared M4 branch, PR targets and retained historical refs. |
| [Validation status](docs/validation-status.md) | Accepted scope, test results, limits and original evidence. |
| [Implementation plan](docs/implementation-plan.md) | Completed stages and planned workflows. |
| [Owner development plan (Polish)](docs/office-editing-development-plan.pl.md) | M3 review and proposed query, selection and editing milestones for six element families. |
| [Windows setup](docs/windows-setup.md) / [diagnostics](docs/diagnostics.md) | Install, connect, preserve history and recover unknown results. |
| [Fixture](docs/fixture-guide.md) | Test geometry, resources and current saved state. |
| [Read/audit tools](docs/tool-reference.md) / [M3 execution](docs/m3-execution-contract.md) | Requests and current operational boundaries. |
| [Architecture](docs/architecture.md) / [testing policy](docs/testing-policy.md) | Runtime boundary and required checks. |

## Local Windows setup

Use the [0.19.0 evaluation package](evaluation-packages/0.19.0/README.md), with
the scoped Wall filter/highlight/clear trial accepted. Its delivery records the single clean
local fallback build after CI artifact transfer was blocked by the workspace
proxy. On the machine running Allplan, external
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

Read [AGENTS.md](AGENTS.md), the [testing policy](docs/testing-policy.md) and the
[current handoff](docs/next-model-handoff.md) before choosing checks. During
iteration, use focused affected/dependent tests, for example:

```bash
uv run --frozen python -m unittest discover -s tests -p 'test_wall_probe*.py' -v
```

Keep PRs in draft while iterating. Full candidate CI replaces a duplicate full
local run; one dependent job builds the package. Use its source-bound artifact
for the once-per-delivery installation check. See the policy for the two-job
standard candidate and six-job compatibility/main-integration gates.

Settings: ALLPLAN_HOST_URL, ALLPLAN_HOST_TIMEOUT, MCP_HOST, MCP_PORT and MCP_PATH.
Development Python execution requires opt-in on both runtimes. The evaluation
launcher disables it. Repository docs/API identifiers use English; owner
walkthroughs may use Polish. The model prepares code, diagnostics and packages;
the owner observes through Allplan/local Codex without editing Python/JSON.
