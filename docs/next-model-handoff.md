# Next-model handoff

## Current state

Continue **codex/m3-repair-preview**, package **0.14.1**, draft into main
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
[completed conflict gate](m3-conflict-owner-test.md),
[controlled interruption](m3-recovery-contract.md), [new owner gate](m3-recovery-owner-test.md),
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
  even if source values return to the old state. Its bounded native gate is
  **PASS (2026-10-11)**: 12/12 steps, one C03 write, stale C04 rejection before
  setters and a real excluded-peer source/report conflict in one host session.
  Owner confirms UI/unchanged peers/host survival and one Undo; read-only Recover
  observes the old value and audits 3 → 2 → 3.
  [Evidence and boundaries](m3-conflict-acceptance-0.13.0.md).

- 0.14.1 [bounded controlled recovery gate](m3-recovery-acceptance-0.14.1.md)
  **PASS (2026-10-12)**: 13/13 + 6/6 + 6/6, one C03 setter leaves actual
  running/unknown and skipped C04; new-ID rejection before setters, host
  restart/reconciliation and exact-ID replay without resume. Owner confirms UI,
  no other changes and Undo; final complete snapshot matches baseline, audits
  3 → 2 → 3. Final pointer undo_checked. Host sessions remain consistent within
  each phase; Part C uses another session with unspecified cause. No repeat.

## Next implementation

1. Resolve remaining declared-scope acceptance and journal/identity limits.
   Do not repeat completed gates or the manual UI editing known to cancel the
   host unchanged. Crash/power-loss, cross-copy identity and grouped Undo remain
   outside accepted scope. No owner rerun is requested for the completed recovery gate.
2. Complete final UAT/main integration separately; PR #2 remains draft into main.

Graphical labels, file moves and universal native setters are conditional
extensions. They do not enlarge mandatory M3 closure scope.

## Resume safely

The 0.14.0 native attempt blocked at numbering_preview before Apply/ID creation:
health, audit and full snapshot passed. UUID order put C04 ahead of C03;
[diagnosis](m3-recovery-blocked-0.14.0.md). No native write or Undo occurred
in that attempt. 0.14.1 preserves generated spatial assignment order before
plan hashing, retains exact CLI/host guards and labels pre-Apply failures
explicitly. The corrected gate has now passed; preserve old journals/packages
and the same original project after its 0.14.1 Undo. Do not repeat the writing gate.
Final **207 portable tests PASS**, one full run on Linux CPython 3.12.14;
focused control/mark/HTTP checks, frozen sync and wheel/sdist builds PASS.
[0.14.1 delivery](../evaluation-packages/0.14.1/README.md) records the exact
clean-source package/installation checks and separate source CI.

0.14.0 final-candidate verification: **205 portable tests PASS**, one full run
on Linux CPython 3.12.14 after focused executor/real-HTTP checks. Frozen sync PASS.
The new runtime package, clean-source identity, builds, installation checks and
source CI are recorded in [0.14.0 delivery](../evaluation-packages/0.14.0/README.md).
The final candidate includes explicit pre-setter rejection reporting; its 205-test
run replaces the earlier 204-test candidate. That delivery predated the
0.14.0 preflight block and subsequent bounded 0.14.1 native PASS.
All old delivered artifacts remain unchanged.


Previous 0.13.0 final-candidate verification: **195 portable tests PASS** on
Linux CPython 3.12.14, frozen sync and wheel/sdist build PASS. The exact clean-source
ZIP passes extracted integrity and 23 installed bridge hashes; registration/restore
preserve the journal and restore the prior bridge fixture. Source
**752e54795a1cfa676217b5ffba0ce5d301383269**;
[delivery and source CI](../evaluation-packages/0.13.0/README.md).
Documentation publication repeats no tests/builds and preserves archives.
Source [CI 38079063575](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38079063575)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including tests and builds.
Bounded native conflict gate PASS; [owner evidence](m3-conflict-acceptance-0.13.0.md).

Previous 0.12.0 final-candidate verification: 187 portable tests PASS, frozen dependency
sync, wheel/sdist and exact extracted installation/23 bridge hashes PASS;
Setup/Restore preserved the journal. Source **fd78700378eceb6f217e4ca30a83b88004b73a57**,
[CI 38075847420](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38075847420)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13. Follow [testing-policy](testing-policy.md).
The delivery retains exact archive identity and source CI job/step observations.
Do not repeat the full suite or prior native batches for documentation publication.

The owner left the original disposable copy after the **0.14.1 recovery Undo**:
C03 mark `<niezdefiniowany>`, C04=S02, C02=S02; C05 structure/C06 NEW remain.
Read-only Recover observed both targets’ old values and a complete three-finding
audit; the full six-column snapshot matches the original baseline.
**Leave/save this state until a new separately reviewed gate; no Redo or new Apply.**
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

## Previous delivered 0.14.0 source

Clean source **7ead0e9798c6c93a843fbfc8e9b5e33a58763fdd** has final 205-test
portable PASS, frozen sync and wheel/sdist builds. The exact extracted ZIP verifies
23 installed bridge hashes, journal preservation and prior bridge restoration.
Source [CI 38175934542](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38175934542)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, tests/builds included.
[Delivery/artifact identities](../evaluation-packages/0.14.0/README.md) retain
original logs, CI steps, instructions and package. Documentation publication
repeats no tests/builds and leaves archives unchanged. Main ancestry was reconciled
in the M3 branch; PR #2 stays draft into main, without merge/release.
The original native attempt blocked before Apply; corrected 0.14.1 has since
passed with bounded native recovery acceptance. M3/UAT-05/UAT-06 are open.

## Delivered 0.14.1 correction and owner action

Clean source **1810e4fa284311e204b9133deee3245f8427697b**, final **207-test PASS**,
frozen sync and clean-source wheel/sdist builds PASS. Exact ZIP verification
passes all 23 bridge hashes, journal preservation and prior bridge restoration.
[Source CI 38179275055](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38179275055)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including tests and builds.
[0.14.1 delivery](../evaluation-packages/0.14.1/README.md) retains the exact
source/archive, local logs, installation check and CI job/step observations.
Documentation publication repeats no tests/builds and leaves old artifacts unchanged.

The 0.14.0 attempt blocked before Apply/ID creation; the corrected
[controlled recovery gate](m3-recovery-acceptance-0.14.1.md) has since passed.
Leave/save the copy after the completed 0.14.1 Undo, preserving Local journal
and all logs. No repeat is requested. M3/UAT-05/UAT-06 remain open.
PR #2 stays draft into main, with no merge/release.

## Latest native acceptance — 0.14.1

[Recorded recovery PASS](m3-recovery-acceptance-0.14.1.md) retains ten original
uploads, their hashes and independent response/plan/request/audit/snapshot
inspection. Package/source identity matches the delivered 0.14.1 manifest.
This documentation/evidence update runs no product tests/builds. The original
archives, delivery records and embedded instructions remain unchanged. Keep
the saved execution identity; do not repeat the writing launcher.
