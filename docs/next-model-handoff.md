# Next-model handoff

Updated **2026-10-12 Europe/Warsaw**. Continue **codex/m3-repair-preview**,
package **0.15.0**, [draft PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
into main. M0–M2 / UAT-00–UAT-04 remain accepted within the recorded
Allplan **2026-1-7** fixture scope. **M3/UAT-05/UAT-06 and the first MVP remain open**.
No merge/release is requested by this handoff.

## Read first

[Architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [validation status](validation-status.md)
and [testing policy](testing-policy.md). Current changes:
[journal inspection](m3-journal-contract.md),
[new selected-mark owner gate](m3-selected-mark-owner-test.md) and
[workflow execution/journal limits](m3-workflow-execution-contract.md).

## Completed portable work — 0.15.0

- fix_model_issues/inspect_journal validates before native API/document access,
  locks installed Local history, verifies bounded records and reports capacity,
  unresolved original IDs and invalid-record blockers. It never reads the model,
  reconciles outcomes or deletes records. Available means storage checks passed,
  not current-model/native-write/copy-identity acceptance.
- Existing exact-ID replay/new-write scanning now also validate basic record
  identity, state, target-reference and outcome structure after content hashes.
  Existing m3-execution-1 history/schema and 128-record limit are retained.
- The new owner CLI exercises explicit **rule_based_edit C04 S02 → S04** with
  C02 explicitly excluded, full-scope collision/source checks, immutable
  pre-send execution identity, readback, read-only replay, journal summary and
  complete six-column snapshots. Separate Recover/Undo Check never send Apply.
  It refuses a second writing gate once a saved pointer exists.
- **219 portable tests PASS**, one final full run on Linux CPython **3.12.14**
  (90.899 seconds), after focused journal/executor/real-HTTP checks. Frozen sync
  PASS. Local fakes/HTTP checks execute no native Allplan. Final artifact/build,
  installation and source CI results are recorded with the
  [0.15.0 delivery](../evaluation-packages/0.15.0/README.md).

## Next required action — native owner test

0.15.0 is **ready_for_owner_test**; the new selected-mark/journal scope has no
native acceptance yet. Use only [the new bounded gate](m3-selected-mark-owner-test.md):
13 steps for one C04 change, owner UI observations, one Undo and six read-only
verification steps. Expected audits **3 → 1 → 3**. No previous gate needs repeat.

Use the same original disposable project retained after the accepted 0.14.1 Undo:
C02=S02, C03=`<niezdefiniowany>`, C04=S02; C05 structure/C06 NEW remain.
The prior final full snapshot matched baseline. Preserve that project, installed
**Local/.allplan-mcp/repairs** and all package logs. Install the complete new ZIP
against the same Local; old delivered artifacts stay unchanged. No Redo, new
copy, old writing launcher or invented execution ID is needed.

After the new gate, retain original owner JSON/TXT and UI/Undo/build evidence,
record bounded PASS/FAIL/BLOCKED, and leave/save the same copy after Undo.
A lost response uses the saved ID and Selected Mark Recover only. Native
Allplan is available only through local Windows Codex/UI, not this cloud workspace.

## Existing native acceptance — do not repeat

[Validation status](validation-status.md) retains all accepted boundaries:

- 0.11.0: two separately reviewed single-target layer/status workflows, readback,
  full audited-field verification, read-only replay, audits 5 → 4 → 3 and
  owner-confirmed two-step Undo.
- [0.12.0 numbering](m3-numbering-acceptance-0.12.0.md): two mark writes,
  deterministic unchanged previews, readback/replay/no-op and Undo/recovery,
  audits 3 → 0 → 3.
- [0.13.0 conflict](m3-conflict-acceptance-0.13.0.md): 12/12 same-session steps,
  one C03 write, stale C04 rejection before setters, real excluded-peer source
  conflict and Undo/recovery, audits 3 → 2 → 3. Invalidated plans remain
  inspectable once within original TTL/cache limits and never regain Apply.
- [0.14.1 controlled recovery](m3-recovery-acceptance-0.14.1.md): 13/13 + 6/6 +
  6/6, actual running/unknown C03 with skipped C04, rejected new identity,
  restart/reconciliation, no-resume replay and owner Undo, audits 3 → 2 → 3.
  Sessions are consistent within each phase; final Undo inspection used another
  session with unspecified cause. Ten original uploads/inspection remain in
  [the unchanged delivery](../evaluation-packages/0.14.1/README.md).

The previous 0.14.0 attempt blocked before Apply because UUID ordering put C04
before C03. 0.14.1 preserves spatial assignment order before hashing and has
since passed. Its original clean source **1810e4fa284311e204b9133deee3245f8427697b**,
207-test result, archive/installation and 6/6 source CI evidence retain that scope.
No archive rebuild or old evidence/hash verification is performed for this update.

## Remaining limits and continuation

The shared executor implements 1–32 existing-string mark/status or layer changes
on native Column roots in one explicit foreground file; native acceptance is
narrower. Other validated profiles/files, larger/mixed/same-target plans and
broader mark/workflow combinations are unaccepted. The demo remains
bound_for_read, active_for_write=false; evaluation Apply is an explicit bounded
route. Generic writable references/profiles, durable element/cross-copy identity,
manual UI active-plan conflicts, crash/power-loss durability and grouped Undo
remain unaccepted. Do not repeat UI editing known to cancel the host unchanged.

At 128 records, stop new execution. Saved replay/recovery remain available for
valid records; no automatic eviction/rollover/pruning is implemented. Inspection
is not a journal backup. Setup/Restore preserve records but bridge backups do
not back them up. Preserve complete Local history, original project and logs
before migration; deleting/restoring older history removes retry protection.
Historical outcomes do not establish current values after Undo.

Resolve remaining declared-scope acceptance/identity/journal limits before final
UAT/main integration. Graphic labels, file moves and universal native setters
are conditional extensions, not mandatory M3 closure scope. Follow
[testing-policy](testing-policy.md): focused affected checks during code work,
one final full suite per new owner-package candidate, change-dependent source
CI, no runtime reruns for documentation publication.

Repository documentation/API identifiers use English; owner walkthroughs may
use Polish. The implementation model owns code, checks, diagnostics and ready
packages. The owner observes through Allplan/local Codex; they do not edit
Python/JSON or discover API identifiers.
