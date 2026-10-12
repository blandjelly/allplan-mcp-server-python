# Next-model handoff

Updated **2026-10-12 Europe/Warsaw**. Branch **codex/m3-repair-preview**,
package **0.15.0**, [draft PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
into main. M0–M2 / UAT-00–UAT-04 remain accepted within the recorded
Allplan **2026-1-7** fixture scope. **M3/UAT-05/UAT-06 and the first MVP remain open**.
**Work is paused at the owner's explicit request after reviewing native 0.15.0
logs. Only evidence/documentation publication is authorized for this update.
Do not continue implementation, run tests, request a new owner batch or integrate
main until the owner explicitly resumes work.** No merge/release is requested.

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

## Latest native result — 0.15.0; work paused

[Bounded PASS / accepted_on_build](m3-selected-mark-acceptance-0.15.0.md):
13/13 A + 6/6 B. One explicit rule_based_edit C04 S02 → S04 with excluded C02,
fresh revalidation, full readback/audited-field checks, read-only exact-ID replay,
healthy journal inspection and Undo/recovery pass. Full six-column snapshots
show only the authorized mark/attribute change and exact baseline restoration;
audits **3 → 1 → 3**. Owner confirms matching UI in A/B and uninterrupted host
in A. Sessions are stable within each phase; B uses another session of unspecified
cause. Final pointer undo_checked, execution b5b397c7f7134b27b9304259e53e6bc4.

Eight original uploads and independent inspection are retained in the
[0.15.0 native evidence](../evaluation-packages/0.15.0/native-acceptance/20261012-owner/).
Plan/request hashes, five audit hashes, 19 MCP text responses, complete snapshots
and reported bridge/source identity match. Journal summaries are 6 → 7 → 7
verified records with no blockers. This is healthy-journal inspection acceptance,
not native capacity/corruption/migration or wider identity acceptance.

Leave/save the same original copy after Undo: C02/C04=S02, C03 undefined,
C05 structure/C06 NEW retained. Preserve Local/.allplan-mcp/repairs and all logs.
No Redo, repeat writing gate or new owner test is requested. The owner explicitly
asked for documentation updates only and no continued task work. Runtime tests,
builds and main integration remain paused.

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

## Delivered 0.15.0 owner gate

Clean source **7e3657bc33ecf913376d302da900af386b3b8a23**, one final
219-test portable PASS, frozen sync and wheel/sdist builds PASS. Exact
ZIP installation verifies 23 bridge hashes, journal preservation and previous
bridge restoration. [Source CI 38181795091](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38181795091)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, tests/builds included.
[Delivery/artifacts](../evaluation-packages/0.15.0/README.md) retain source/archive
identity, logs, installation verification, CI observations and Polish instructions.
Publication repeats no product checks/builds or old artifact hash verification.
[Selected-mark/journal bounded native PASS](m3-selected-mark-acceptance-0.15.0.md)
is recorded separately from the unchanged delivery/embedded instructions.
No completed gate needs repetition. Further work is paused; PR #2 stays draft
into main and M3 remains open.
