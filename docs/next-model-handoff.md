# Next-model handoff

Updated **2026-10-12 Europe/Warsaw**. Branch **codex/m3-repair-preview**,
package **0.15.0**, [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
into main. **M0–M3 / UAT-00–UAT-06 are accepted within the recorded fixture
scope**, Allplan **2026-1-7** with local Windows Codex. M3/UAT-05/UAT-06 use
the owner's explicitly narrowed scope and existing evidence; see
[closure and UAT mapping](m3-closure.md). The first MVP is a **fixture evaluation**,
not acceptance for typical office projects. Main integration and release are separate.

The owner resumed work and explicitly requested M3 closure within the retained
test project. This supersedes the earlier pause and open-M3 instructions.
Historical gate reports, archives, delivery records, embedded instructions and
raw evidence retain their as-recorded status. Do not repeat completed owner gates.

## Read first

[M3 closure](m3-closure.md), [architecture](architecture.md),
[features](features.md), [implementation stages](implementation-plan.md),
[validation status](validation-status.md), [testing policy](testing-policy.md)
and [office-project roadmap](office-project-roadmap.md). The shared
[execution contract](m3-workflow-execution-contract.md) and
[journal inspection](m3-journal-contract.md) retain runtime limits.

## Closed fixture milestone

Accepted writes are the recorded one-/two-change scenarios on C01–C06 Column
roots in foreground file **101** of the original **MCP_QA_DEMO** copy, using
read profile **1.0.2**, audit profile **2.0.0** and retained demo standards.
The executor implements 1–32 changes, but native acceptance is narrower. Do not
infer support for arbitrary combinations, other files/profiles or the fixture's
wall, beams and slab. General writable profiles remain inactive:
active_for_write=false; Apply remains the explicit bounded evaluation route.

- 0.11.0: separately reviewed layer/status workflow writes, exact readback,
  full audited-field verification, read-only replay, audits **5 → 4 → 3**,
  owner-confirmed host/UI/unchanged peers and two-step Undo.
- [0.12.0 numbering](m3-numbering-acceptance-0.12.0.md): two mark writes,
  deterministic preview, readback/replay/no-op and Undo/recovery,
  audits **3 → 0 → 3**.
- [0.13.0 conflict](m3-conflict-acceptance-0.13.0.md): **12/12** same-session
  steps, C03 write, stale C04 rejection before setters, changed excluded-peer
  comparison and Undo/recovery, audits **3 → 2 → 3**. Invalidated plans never
  regain Apply. This does not prove an active-plan manual UI edit conflict.
- [0.14.1 controlled recovery](m3-recovery-acceptance-0.14.1.md):
  **13/13 + 6/6 + 6/6**, actual C03 running/unknown with skipped C04, rejected
  new identity, restart/reconciliation, no-resume replay and owner Undo,
  audits **3 → 2 → 3**. This is not a native crash/power-loss test.
- [0.15.0 selected mark/journal](m3-selected-mark-acceptance-0.15.0.md):
  **13/13 A + 6/6 B**, C04 **S02 → S04** with C02 explicitly excluded,
  complete six-column snapshots/readback, read-only replay, healthy journal
  summaries **6 → 7 → 7** and owner Undo/recovery, audits **3 → 1 → 3**.
  Owner confirms UI in A/B and uninterrupted host in A. Each phase has a stable
  session; B uses another session of unspecified cause. Final pointer is
  undo_checked, execution **b5b397c7f7134b27b9304259e53e6bc4**.

The [eight original 0.15.0 uploads and independent inspection](../evaluation-packages/0.15.0/native-acceptance/20261012-owner/)
retain matching plan/request and five audit hashes, 19 MCP text/structured
responses, complete snapshots and 23 reported bridge hashes. No evidence or
archive rebuild is performed for closure.

## Preserved model and history

The owner confirms the test project is in its documented state. Leave/save
the same original copy after Undo: **C02/C04=S02, C03 undefined, C05 structure,
C06 NEW**. Preserve installed **Local/.allplan-mcp/repairs**, package logs and
saved execution identities. No Redo, repeat writing gate or new owner batch is
needed for fixture closure. A changed host requires a fresh preview.

At **128 records**, stop new execution. Valid saved replay/recovery remain
available; no automatic eviction/rollover/pruning exists. Inspection is not
a journal backup. Setup/Restore preserve records but their bridge backups do
not back them up. Do not delete identities to gain slots, restore older history
and retry newer writes, or replay/recover against another copy/Local/machine.
Historical outcomes do not establish current values after Undo.

## Delivered portable/source evidence

The unchanged [0.15.0 delivery](../evaluation-packages/0.15.0/README.md) records
clean source **7e3657bc33ecf913376d302da900af386b3b8a23**, **219 portable tests PASS**,
one final full run on Linux CPython **3.12.14** (90.899 seconds), after focused
journal/executor/real-HTTP checks. Frozen sync, wheel/sdist build and exact ZIP
installation/restore PASS: **23** bridge hashes, preserved journal bytes and
previous bridge restoration. Local fakes/HTTP checks execute no native Allplan.
[Source CI 38181795091](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38181795091)
is **6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including tests/builds.
These observations retain the original tested source, not a fresh closure run.
Documentation publication checks links/diff only; it does not rerun runtime
tests/builds or old hashes. Before actual main integration, run the final-candidate
checks/full matrix required by [testing policy](testing-policy.md).

## Next work: office-project property edits

The owner wants typical complex office-project use, particularly walls missing
a fire-resistance value and concrete-class changes for columns on a storey.
Prioritize **M4.1–M4.2** per the [office-project roadmap](office-project-roadmap.md):
one proven wall/property slice and one column/property slice before wider scope.
Distinguish empty/undefined from absent attributes and native material properties
from custom text. The M3 adapter does not add absent attributes or write walls.

Wider plans/profiles/files, durable/cross-copy identity, safe manual UI active-plan
conflicts, crash/power-loss, broader/grouped Undo and journal capacity/corruption/
migration/rollover remain unaccepted. They constrain office-project rollout but
do not reopen the explicitly narrowed fixture milestone. Do not repeat UI editing
known to cancel the host unchanged. Labels, file moves and universal setters
remain conditional extensions.

Repository documentation/API identifiers use English; owner walkthroughs may
use Polish. The implementation model owns code, checks, diagnostics and ready
packages. The owner observes through Allplan/local Codex; they do not edit
Python/JSON or discover API identifiers.
