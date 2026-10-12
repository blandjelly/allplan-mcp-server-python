# Current handoff

Updated **2026-10-12 Europe/Warsaw**. Working branch **codex/m4-property-discovery**,
based on **codex/m3-repair-preview**, package **0.16.0**; no main integration/release.
M3 [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2) remains separate.

**M0–M3 are closed within the retained test project.** Bounded UAT-05/06 uses
existing one-/two-change evidence, not broader native acceptance. The owner
resumed work and narrowed closure to this fixture; older pause instructions
are historical. [Scope, test results, limits and evidence](validation-status.md).

## Preserve current state

The owner confirms the original MCP_QA_DEMO copy is saved after Undo:
**C02/C04=S02, C03 undefined, C05 structure, C06 NEW**. Keep package logs,
saved execution identities and **Local/.allplan-mcp/repairs**. No Redo or repeated
writing gate is requested. After an unknown result use [read-only recovery](diagnostics.md),
never a new Apply. At 128 journal records stop new writes; do not delete history.

## Next action

For main integration, run the final-candidate checks/full compatibility matrix
in [testing policy](testing-policy.md). Documentation-only publication checks
links/diff without repeating runtime tests, builds or old hashes.

**M4.1a / early M4.1b is ready_for_owner_test, not accepted_on_build.**
0.16.0 delivers `model_properties` (project-native names/IDs, raw type/unit/enum
metadata, sampled owners and operation support), an `open_drawings` query default
including passive read files, and `model_selection` full-result highlight/clear.
Adapters stay within one UI-dispatched request; existing M3 write guards remain.

Native UI selection is **BLOCKED_current_interactor**: HighlightElements submission
does not prove visible highlighting or selection. Native material/thickness and
new writable adapters remain unavailable. K1/K2/K3 are not closed by this probe.

Next action: owner observes **Allplan 2026-1-7**, original **MCP_QA_DEMO**, following
the [short M4 guide](m4-properties-owner-test.pl.md) and [0.16.0 delivery](../evaluation-packages/0.16.0/README.md).
Record actual property definitions/fire-resistance/W1, full-result highlight/clear
and MCP health. Cloud execution cannot perform these Windows/UI checks.
Do not repeat M3 writing gates or edit the model for this observation.

After observation, map the actual property explicitly and design native selection
cooperation. Then implement an independent criterion-based ChangePlan through
the shared M3 mechanism: columns missing fire resistance → existing W1.
Next probe wall.total_thickness and native C35 material, then remaining families
and multi-file batches. Unresolved resources are BLOCKED, never guessed IDs.
Follow the [editing development plan](office-editing-development-plan.pl.md) and
[implementation plan](implementation-plan.md). The removed office-project roadmap
is historical; generation/exports are deferred. No office-project write is accepted.

Read [architecture](architecture.md), [read/audit tools](tool-reference.md) and
[M3 execution](m3-execution-contract.md) before coding. The model researches APIs,
implements checks and prepares packages; the owner observes through Allplan/local
Windows Codex without editing Python/JSON or finding attribute IDs.
