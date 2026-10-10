# Next-model handoff

## Current state

Continue **codex/m3-repair-preview**, package **0.11.0**, draft
[PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
M0–M2 / UAT-00–UAT-04 are accepted within the recorded Allplan **2026-1-7**
fixture scope. **M3/UAT-05/UAT-06 and the first MVP remain open**.
Integration with main and release are separate unfinished work.

Read [architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [validation status](validation-status.md)
and [testing policy](testing-policy.md). Details: [read tools](tool-reference.md),
[audit](m2-audit-contract.md), [repair preview](m3-repair-contract.md),
[standard/selection](m3-standards-contract.md), [marks](m3-marks-contract.md),
[execution](m3-execution-contract.md) and
[workflow execution/journal lifecycle](m3-workflow-execution-contract.md).

## Implemented and accepted boundaries

- Read profile **1.0.2** and audit profile **2.0.0** bind resources freshly;
  the demo remains bound_for_read, active_for_write=false.
- Native reads, six-column audits, explicit layer/status previews, selected
  standard previews and collision-aware mark previews have bounded acceptance.
- The shared executor supports **1–32 existing string-status/layer changes**
  on native Column roots in one explicit foreground file. Typed
  fix_model_issues, apply_office_standard and rule_based_edit reuse it.
  This implementation scope exceeds native acceptance.
- The latest 0.11.0 native gate passed two separately reviewed single-target
  writes: S05 layer 3701 → 3700 / SZ_OGÓ01, then S06 existing status attribute
  5002 NWE → NEW. Exact readbacks, full audited-field verification, read-only
  exact-ID replay and complete six-column audits **5 → 4 → 3** passed.
  Owner confirmed host survival, unchanged other elements and two separate Undo
  operations. No repeat of these completed gates is required.
- Every mark plan remains preview-only. Mark assignment and automatic numbering
  are unimplemented. Grouped Undo and automatic rollback are unavailable.

## Next implementation

1. Implement actual mark assignment and deterministic numbering under an explicit
   versioned standard. Retain whole-scope collision checks including excluded
   peers, fresh source checks, reviewed plans, readback and durable execution IDs.
2. Design native same-session source-conflict checks in a supported host lifecycle,
   then controlled partial/unknown outcomes and read-only recovery. The observed
   manual UI edit cancelled StartPythonHost; repeating that scenario unchanged
   cannot establish a same-session conflict. Restart invalidation and stale Apply
   rejection already pass.
3. Resolve remaining acceptance for the declared scope, journal maintenance and
   identity limits; integrate with main and complete UAT-05/UAT-06.

Graphical labels, file moves and universal native setters are conditional
extensions. They do not enlarge mandatory M3 closure scope.

## Resume safely

The owner did not specify whether the model was left repaired, undone or redone
following the latest Undo observation. Start with current health/context and a
fresh full audit of the original disposable copy before another preview.
Historical completed/replay outcomes do not establish current values after Undo.
Never reuse an old execution ID for a new repair.

Preserve installed **Local/.allplan-mcp/repairs**, original project copy and
local package logs. Setup/Restore preserve the journal but bridge backups do
not back it up. At 128 records stop new writes; deleting records removes
protection against repeated execution. See [recovery guidance](diagnostics.md)
and [journal limits](m3-workflow-execution-contract.md#journal-lifecycle-and-the-128-record-limit).

Use [Windows setup](windows-setup.md) and [fixture definition](fixture-guide.md)
when needed. Delivered [0.11.0 artifacts](../evaluation-packages/0.11.0/README.md)
remain unchanged. Future runtime changes need a new package version.
Historical test counts and CI results belong to their recorded source.

Repository documentation and API identifiers use English; owner walkthroughs
may use Polish. The implementation model owns code, checks and ready-to-use
packages; the owner observes Allplan through local Windows Codex and the UI.
The owner does not edit Python/JSON or discover API identifiers.
