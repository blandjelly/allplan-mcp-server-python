# Current handoff

Updated **2026-10-12 Europe/Warsaw**. Branch **codex/m3-repair-preview**,
package **0.15.0**, [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
ready for review; no main merge/release performed.

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

Next implementation: **M4.1–M4.2**, one wall fire-resistance assignment and one
column concrete-class edit, then explicit storey/multi-file scope and batching.
Follow the [office-project roadmap](office-project-roadmap.md) and
[implementation plan](implementation-plan.md). No office-project write is accepted yet.

Read [architecture](architecture.md), [read/audit tools](tool-reference.md) and
[M3 execution](m3-execution-contract.md) before coding. The model researches APIs,
implements checks and prepares packages; the owner observes through Allplan/local
Windows Codex without editing Python/JSON or finding attribute IDs.
