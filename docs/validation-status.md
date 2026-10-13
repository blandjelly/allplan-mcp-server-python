# Validation status and limits

Updated **2026-10-13 Europe/Warsaw**. Package **0.15.0**.
The **0.16.0** property gate is **FAIL_CRASH / blocked_after_native_crash**.
**0.16.1** is ready_for_owner_test only for one isolated Column read, not accepted_on_build. M3 write acceptance below remains scoped to 0.15.0 evidence.
**M0–M3 / UAT-00–UAT-06 are accepted within the retained test-project scope.**
The owner explicitly narrowed M3/UAT-05/UAT-06 to existing demonstrated scenarios.
This closes the fixture evaluation MVP; it does not accept the original broader
gate or typical office-project writes. Main integration/release remain separate.

## Accepted scope

The original disposable **MCP_QA_DEMO** copy and installed Local history,
Allplan **2026-1-7** with local Windows Codex. M3 writes concern the six Column
roots in foreground file **101**, read profile **1.0.2**, audit profile **2.0.0**
and retained demo standards. Acceptance covers the recorded one-/two-change
layer/status, numbering, selected-mark and controlled-recovery scenarios;
it does not cover arbitrary combinations or writes to the wall/beams/slab.

| Stage | Accepted native behavior | Evidence |
| --- | --- | --- |
| M0 / 0.1.2, UAT-00/01 | Installation/restore, correctly sized box, ESC/restart, minimize/restore and project switching. | [Baseline history](https://github.com/blandjelly/allplan-mcp-server-python/blob/75e80bd65f678fce0c1a5eeafae07d3f3778883b/docs/validation-and-history.md) |
| M1 / 0.5.3, UAT-02/03 | Ten file-101 roots, counts 10/6/2/1, paging/summary, native geometry, display-unit invariance and XY offset (100000,200000,0) mm once. | [Original report](https://github.com/blandjelly/allplan-mcp-server-python/blob/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results/m1-acceptance-0.5.3.md) |
| M2 / 0.6.1, UAT-04 | Five findings on five of six columns, full coverage, scope rejection and continued operation after errors. | [Original report](https://github.com/blandjelly/allplan-mcp-server-python/blob/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results/m2-acceptance-0.6.1.md) |

## Accepted M3 slices

Together these establish bounded UAT-05/06: unchanged preview, authorized writes,
readback/audit agreement, stale rejection, replay without repeated writes and
controlled unknown-result recovery. Manual UI edits against an active plan are
explicitly outside the narrowed gate; invalidated-plan inspection does not prove
that case. Finding counts below are scenario-specific.

| Package | Native PASS | Original evidence |
| --- | --- | --- |
| 0.7.0–0.10.0 | Read-only previews/no-op, layer/status execution, replay across sessions, separate Undo, restart/stale rejection and mark-collision previews. | [Historical reports](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results) |
| 0.11.0 | Two separately reviewed single-target workflows, readback/whole audited-field checks, read-only replay, audits **5 → 4 → 3**, owner-confirmed host/peers/UI and two-step Undo. | [Workflow report](https://github.com/blandjelly/allplan-mcp-server-python/blob/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results/m3-workflow-acceptance-0.11.0.md) |
| 0.12.0 | C03/C04 deterministic numbering, readback/replay/no-op, two-step Undo/recovery, audits **3 → 0 → 3**. | [Report](https://github.com/blandjelly/allplan-mcp-server-python/blob/b0678da6d9d5565951c8576db8d83972331158c1/docs/m3-numbering-acceptance-0.12.0.md), [raw uploads/inspection](../evaluation-packages/0.12.0/native-acceptance/20261010-owner/) |
| 0.13.0 | **12/12** same-session steps: C03 write, stale C04 rejection before setters, changed excluded-peer comparison and Undo/recovery; audits **3 → 2 → 3**. | [Report](https://github.com/blandjelly/allplan-mcp-server-python/blob/b0678da6d9d5565951c8576db8d83972331158c1/docs/m3-conflict-acceptance-0.13.0.md), [raw uploads/inspection](../evaluation-packages/0.13.0/native-acceptance/20261011-owner/) |
| 0.14.1 | **13/13 + 6/6 + 6/6**: actual C03 running/unknown, skipped C04, new-ID rejection, restart/reconciliation, no-resume replay and Undo; audits **3 → 2 → 3**. Controlled stop, not crash/power-loss. | [Report](https://github.com/blandjelly/allplan-mcp-server-python/blob/b0678da6d9d5565951c8576db8d83972331158c1/docs/m3-recovery-acceptance-0.14.1.md), [raw uploads/inspection](../evaluation-packages/0.14.1/native-acceptance/20261012-owner/) |
| 0.15.0 | **13/13 A + 6/6 B**: selected C04 S02 → S04, excluded C02 preserved, full snapshots/readback, read-only replay, healthy journal **6 → 7 → 7**, Undo/recovery; audits **3 → 1 → 3**. | [Report](https://github.com/blandjelly/allplan-mcp-server-python/blob/b0678da6d9d5565951c8576db8d83972331158c1/docs/m3-selected-mark-acceptance-0.15.0.md), [eight raw uploads/inspection](../evaluation-packages/0.15.0/native-acceptance/20261012-owner/) |

In 0.15.0 the owner confirms A/B UI and uninterrupted host in A. Sessions are
stable within each phase; B uses another session of unspecified cause. The 0.14.1
Undo phase also used another session of unspecified cause. Do not infer continuous
host life across phases. The 0.14.0 attempt blocked before Apply because of UUID
write ordering; corrected spatial ordering passed in 0.14.1.

## Portable verification and delivery

The unchanged [0.15.0 delivery](../evaluation-packages/0.15.0/README.md) records:

- Clean source **7e3657bc33ecf913376d302da900af386b3b8a23**; **219 portable tests PASS**,
  one final full run on Linux CPython **3.12.14** after focused journal/executor/HTTP checks.
- Frozen sync, wheel/sdist builds and exact ZIP installation/restore **PASS**:
  **23** bridge hashes, journal bytes preserved and previous bridge restored.
- [Source CI 38181795091](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38181795091)
  **6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, tests/builds included.

Portable checks use native fakes; they do not run Allplan. Results belong to the
recorded source, not later documentation commits. Observed native API **2026.1**,
executable file/product **16.1617.8659.814 / 2026.0.1.0**, embedded Python **3.13.13**
and external Python **3.14.8** do not independently identify the owner-reported UI
hotfix. Static diagnostic runtime_verified/allplan_acceptance fields are not an
acceptance registry.

## Current limits and next work

### M4 discovery/presentation delivery

[0.16.0 delivery](../evaluation-packages/0.16.0/README.md), source
**8ac5e97563c881f3427fc47ef752b5c5362786ee**, records **233 portable tests PASS**,
frozen sync, wheel/sdist builds and exact ZIP install/restore simulation (27 host
hashes; journal bytes preserved). Source compatibility CI is recorded in that
delivery. These checks use native fakes/portable filesystem simulation.

On 2026-10-13 the first /model-properties request crashed Allplan **2026-1-7**
169 ms after request_started, with healthy 0.16.0 installation reported. No
metadata response, highlight, Apply or setter request followed. The uploaded XML
has no native stack and bridge.log has no Python traceback. Exact API/root cause
remain unknown. [Incident](m4-native-crash-0.16.0.md),
[inspection](../evaluation-packages/0.16.0/native-acceptance/20261013-owner/inspection.json).
The portable/CI PASS above does not override this native **FAIL_CRASH**.

The broad property route is blocked before native access. **0.16.1** offers
only a first isolated Column read with durable native boundaries and saved pending
client requests. [Owner guide](m4-isolated-probe-owner-test.pl.md).
The [0.16.1 delivery](../evaluation-packages/0.16.1/README.md) records **243 portable
tests PASS**, frozen sync, wheel/sdist and exact ZIP install/restore simulation
(28 bridge hashes; journal/trace bytes preserved). Final runtime source
**e06a605c2ab1f1a70170072a61f2280c82658aed** has Windows/Ubuntu Python 3.12 CI
**2/2 PASS**; package/launcher source **7b239b26342c60067ac7e0d4b790901916f36c40**
has the six-job compatibility matrix **6/6 PASS**. These source scopes are distinct.
Metadata/enum/UI/writable support remains pending; no K1/K2/K3 completion or new
write acceptance is inferred. Existing completed M3 native gates need no repeat.

### Retained M3 limits

- Executor eligibility **1–32** is broader than accepted one-/two-change scenarios.
  Other profiles/files, mixed/larger plans, walls, native concrete properties,
  attribute addition, labels and file moves have no accepted M3 write support.
- General writable profiles remain disabled. Durable/cross-copy identity,
  manual UI active-plan conflicts, crash/power-loss and broader/grouped Undo
  remain unaccepted. Do not repeat the UI scenario known to cancel the host unchanged.
- Journal limit: **128 records**, no rollover/import/pruning. Healthy inspection
  passed; native capacity/corruption/migration handling is unaccepted. Stop at
  capacity, preserve Local history, and never transfer/retry IDs against another copy.
- M1 lacks native BWS, arbitrary trees/Structural Framing and nonzero Z-offset
  acceptance. Baseline box tools lack durable deduplication/readback. The precise
  earlier CLR crash cause and long-term/concurrent stability remain unproven.

Keep the [fixture](fixture-guide.md) saved after Undo: C02/C04=S02, C03 undefined,
C05 structure/C06 NEW. Completed gates need no repeat. Follow the
[editing development plan](office-editing-development-plan.pl.md) for column
fire-resistance discovery/W1 and thin-wall native C35 material. Before main integration, perform the
final-candidate checks/full matrix in [testing policy](testing-policy.md).

## Historical records

Detailed contracts, completed walkthroughs and acceptance reports are available
in the [pre-cleanup documentation](https://github.com/blandjelly/allplan-mcp-server-python/tree/b0678da6d9d5565951c8576db8d83972331158c1/docs).
Their open/pause statements describe the original gate date, not current M3 status.
Raw uploads, manifests, checksums, logs and delivered archives remain in
[evaluation-packages](../evaluation-packages/); original removed baseline logs
remain in [Git history](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/evaluation-packages).
Do not rerun completed gates or rebuild old archives for documentation changes.
