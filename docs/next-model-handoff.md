# Next-model handoff

## Current state

Continue **codex/m3-repair-preview**, package **0.13.0**, draft
[PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
M0–M2 / UAT-00–UAT-04 are accepted within the recorded Allplan **2026-1-7**
fixture scope. **M3/UAT-05/UAT-06 and the first MVP remain open**.
Integration with main and release are separate unfinished work.

Read [architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [validation status](validation-status.md)
and [testing policy](testing-policy.md). Details: [read tools](tool-reference.md),
[audit](m2-audit-contract.md), [repair preview](m3-repair-contract.md),
[standard/selection](m3-standards-contract.md), [marks](m3-marks-contract.md),
[numbering](m3-numbering-contract.md), [invalidated-plan inspection](m3-conflict-contract.md),
[new owner gate](m3-conflict-owner-test.md),
[execution](m3-execution-contract.md) and
[workflow execution/journal lifecycle](m3-workflow-execution-contract.md).

## Implemented and accepted boundaries

- Read profile **1.0.2** and audit profile **2.0.0** bind resources freshly;
  the demo remains bound_for_read, active_for_write=false.
- Native reads, six-column audits, explicit layer/status previews, selected
  standard previews and collision-aware mark previews have bounded acceptance.
- The shared executor supports **1–32 existing string mark/status or layer changes**
  on native Column roots in one explicit foreground file. Typed
  fix_model_issues, apply_office_standard and rule_based_edit reuse it.
  This implementation scope exceeds native acceptance.
- The latest 0.11.0 native gate passed two separately reviewed single-target
  writes: S05 layer 3701 → 3700 / SZ_OGÓ01, then S06 existing status attribute
  5002 NWE → NEW. Exact readbacks, full audited-field verification, read-only
  exact-ID replay and complete six-column audits **5 → 4 → 3** passed.
  Owner confirmed host survival, unchanged other elements and two separate Undo
  operations. No repeat of these completed gates is required.
- 0.12.0 implements explicit mark assignment and standard
  native-model-qa-demo-mark-numbering 1.0.0, preserving valid marks and assigning
  free S numbers in canonical center Y/X/Z/UUID order. Full-scope normalized
  collisions, excluded peers, immutable plans, fresh source/readback and durable
  execution identities are retained. **Bounded native two-target numbering gate PASS**: unchanged/deterministic
  previews, both writes/readbacks, audited verification, read-only replay/no-op,
  audits 3 → 0 → 3, owner-confirmed host survival/unchanged other elements and
  two-step Undo; Recover observed both old values after Undo.
  [Evidence](m3-numbering-acceptance-0.12.0.md). Wider mark request scope remains open.
  Grouped Undo and automatic rollback are unavailable.
- 0.13.0 retains execution-invalidated plan evidence for one fresh read-only
  comparison within the original shared cache/TTL limits. Apply stays blocked
  even if source values return to the old state. Its native gate is
  **ready_for_owner_test**, not accepted: two selected previews, one C03 write,
  rejected stale C04 Apply and a real excluded-peer source/report conflict in
  the same host session. [Owner instructions](m3-conflict-owner-test.md).

## Next implementation

1. Obtain the new 0.13.0 same-session conflict gate in the original disposable
   copy, with one C03 write and one Undo. The launcher uses a separately reviewed
   typed write instead of the UI edit known to cancel the host. It distinguishes
   execution invalidation from actual fresh source/report differences; it does
   not accept manual UI conflicts or partial/unknown outcomes by inference.
   Use that lifecycle evidence to prepare the separate controlled partial/unknown
   recovery gate next. No repeated 0.12.0 numbering or layer/status gate is requested.
2. Resolve remaining acceptance for the declared scope, journal maintenance and
   identity limits; integrate with main and complete UAT-05/UAT-06.

Graphical labels, file moves and universal native setters are conditional
extensions. They do not enlarge mandatory M3 closure scope.

## Resume safely

Current 0.13.0 final-candidate verification: **195 portable tests PASS** on
Linux CPython 3.12.14, frozen sync and wheel/sdist build PASS. The exact clean-source
ZIP passes extracted integrity and 23 installed bridge hashes; registration/restore
preserve the journal and restore the prior bridge fixture. Source
**752e54795a1cfa676217b5ffba0ce5d301383269**;
[delivery and source CI](../evaluation-packages/0.13.0/README.md).
Documentation publication repeats no tests/builds and preserves archives.
Source [CI 38079063575](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38079063575)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including tests and builds.
Native gate remains ready_for_owner_test, not accepted.

Previous 0.12.0 final-candidate verification: 187 portable tests PASS, frozen dependency
sync, wheel/sdist and exact extracted installation/23 bridge hashes PASS;
Setup/Restore preserved the journal. Source **fd78700378eceb6f217e4ca30a83b88004b73a57**,
[CI 38075847420](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38075847420)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13. Follow [testing-policy](testing-policy.md).
The delivery retains exact archive identity and source CI job/step observations.
Do not repeat the full suite or prior native batches for documentation publication.

The owner left the original disposable copy after **two Undo operations**:
C03 mark `<niezdefiniowany>`, C04=S02, C02=S02; C05 structure/C06 NEW remain.
Read-only Recover confirmed both old mark values and a complete audit with three
mark findings. **Leave/save this state until the new reviewed 0.13.0 gate; no Redo.**
The new launcher starts with fresh health/context and a full audit in that same copy.
Historical completed/replay outcomes do not establish current values after Undo.
Never reuse an old execution ID for a new repair.

Preserve installed **Local/.allplan-mcp/repairs**, original project copy and
local package logs. Setup/Restore preserve the journal but bridge backups do
not back it up. At 128 records stop new writes; deleting records removes
protection against repeated execution. See [recovery guidance](diagnostics.md)
and [journal limits](m3-workflow-execution-contract.md#journal-lifecycle-and-the-128-record-limit).

Use [Windows setup](windows-setup.md) and [fixture definition](fixture-guide.md)
when needed. Delivered [0.12.0 artifacts](../evaluation-packages/0.12.0/README.md)
identify the clean tested source and exact package. Delivered
[0.11.0 artifacts](../evaluation-packages/0.11.0/README.md) remain unchanged.
Future runtime changes need a new package version.
Historical test counts and CI results belong to their recorded source.

Repository documentation and API identifiers use English; owner walkthroughs
may use Polish. The implementation model owns code, checks and ready-to-use
packages; the owner observes Allplan through local Windows Codex and the UI.
The owner does not edit Python/JSON or discover API identifiers.
