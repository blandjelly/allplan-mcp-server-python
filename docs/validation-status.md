# Validation status and limits

**0.18.2 correction:** the single-Wall read resolves consistent M1 root
wrappers by native file/model/view identity rather than Python object identity.
One Wall is read once; multiple views, conflicting fields and incomplete
hierarchy remain blocked. Native validation is **not_run / ready_for_owner_test**;
the 0.18.1 owner observations below retain their original scope.
[Change and Polish check](m4-wall-sample-0.18.2.pl.md),
[automated and exact-package evidence](../evaluation-packages/0.18.2/README.md).

Updated **2026-10-17 Europe/Warsaw**. **0.18.1** transport owner check passed
for health/response delivery; scoped Columns highlight visibility is owner
confirmed, while the Wall sample was blocked before native read. Clean source
`f477f138231f2a8f45690c03bd761364c7e94ab6` passed **306 portable tests**, frozen
sync, builds, exact ZIP installation/upgrade from 0.18.0/restore and
[6/6 Windows/Ubuntu × Python 3.11–3.13 CI jobs](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39026387338).
Thirty bridge hashes verified; journal, trace and bridge log preserved. The
owner subsequently confirmed the host was responsive on 0.18.1 and completed
two scoped M4 observations. The Columns highlight and health observation is
recorded below; the Wall sample was blocked before native read. This does not
accept M4 writes or the complete M4 workflow. [Observation report and original
uploads](m4-native-observation-0.18.1-2026-10-17.md). [Delivery](../evaluation-packages/0.18.1/README.md),
[timeout investigation](mcp-timeout-0.18.1.md).
The logs establish incomplete host replies, not a proven native root cause.

Prior 2026-10-15 record: **0.18.0**, **ready_for_owner_test** for the Wall read;
its source, CI and package checks passed. Its native wall observation did not
run on that package. The 0.17.2 owner observation was later exercised using the
same Column handler in package 0.18.1; see the scoped result below. The 0.17.2
source, artifacts and prior automated evidence remain unchanged. The **0.17.1**
partial native observation is recorded below.
The **0.16.0** property gate is **FAIL_CRASH / blocked_after_native_crash**.
**0.16.1** is ready_for_owner_test only for one isolated Column read, not accepted_on_build. M3 write acceptance below remains scoped to 0.15.0 evidence.
**M0–M3 / UAT-00–UAT-06 are accepted within the retained test-project scope.**
The owner explicitly narrowed M3/UAT-05/UAT-06 to existing demonstrated scenarios.
This closes the fixture evaluation MVP; it does not accept the original broader
gate or typical office-project writes. Main integration/release remain separate.

## 0.18.0 wall-property read candidate

Subsequent **source-only** work adds an offline saved-report analyzer; it is not
included in the frozen 0.18.0 package. **10 focused tests PASS** for strict
thresholds, exact labels, exclusions, source consistency, forged flags, invalid
JSON and dependency-free CLI input preservation. Source
**0c3a2987df164254d03cd749bcb72b71a79716ee** subsequently passed
[standard CI 38824865834](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38824865834):
**2/2 Windows/Ubuntu Python 3.12 jobs**, full **299-test** portable suite and
standard build steps. This is source verification, not a new owner package or
native result. No new native calls or material writes are enabled.
[Analyzer contract](m4-wall-report-analysis.md). The packaged-source
results below retain their original scope.

0.18.0 retains the 0.17.2 `column_layer.py` and
`column_layer_diagnostics.py` semantics unchanged, and adds a narrow
`model_property_probe` phase, `wall_sample`, plus **M4 Wall Properties.cmd**.
Clean source **5ea4bcfd88f500bbf137e361ba5d6cc3d83710b5** passed **289 portable
tests** (CPython 3.12.14), frozen sync, wheel/sdist and Windows ZIP builds.
[Source CI 38823160113](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38823160113)
passed **6/6** Windows/Ubuntu × Python 3.11–3.13 jobs, including tests/builds.
Exact ZIP installation, upgrade from 0.17.2 and restore passed with **30 bridge
hashes** and journal/trace preservation. Column runtime byte identity was checked.
[0.18.0 delivery and evidence](../evaluation-packages/0.18.0/README.md).
Later delivery/docs commits retain those frozen artifacts and source scopes.

The wall phase requests one foreground file (101) and optionally one canonical
nonzero model UUID; explicit null UUID is invalid. Its M1 query uses the
required `type_name`, `type_uuid`, and identity fields plus `display_name` and
`file_state`; it reads no attributes or geometry. It counts matched Wall roots,
then selects the exact requested UUID or, without one, the first accepted Wall
in deterministic UUID order. A requested UUID with no exact match has no
fallback. It imports the native Wall type, resolves only the selected element
and verifies it is a `WallElement` before reading `.Properties` and
`.TierCount`. Any tier count other than one stops as unsupported before tier
access. The only tier read is tier 1 `.Thickness` and `.Material`; thickness is
not read for every matched Wall. It performs no whole-model thickness filter,
highlight, Apply, metadata/enum discovery, resource lookup or model write.

For a valid positive finite thickness and bounded raw material string,
`sample.criterion.matches_assuming_native_mm` reports the strict `<240`
comparison under an explicit API-mm assumption. `units_runtime_verified=false`,
`material_target_binding=not_checked`, and `material_write_available=false`.
No missing/invalid value gets a fallback or retry. Native read acceptance is
required before material writes can be enabled. Persist the pending request
before the single MCP call, bracket it with same-host health replies, and retain
the flushed/fsynced native trace. A lost reply means no following native call;
the trace does not establish crash containment. See the
[0.18.0 wall guide](m4-wall-properties-0.18.0.pl.md).

## 0.17.2 candidate and 0.17.1 native observation

### 0.18.1 owner observations (2026-10-17)

The owner confirmed the host was responsive on 0.18.1. In one session,
`health_before` and `health_after` were healthy around the Columns preview and
highlight. The preview found six Columns: three F120 nonmatches and three
undefined fire-resistance values on W1 as targets; it produced a no-op with zero
changes. The highlight request submitted three adapters. The owner confirmed
the targets were visible highlighted in the UI. The JSON leaves `highlighted`
null and `allplan_acceptance=not_run`, so UI visibility rests on the owner's
observation. This accepts only scoped highlight visibility and health delivery;
there was no Apply or setter, and no write/Undo/recovery acceptance.

The Wall `model_property_probe` request for drawing file 101 was blocked before
returning a wall sample, with `probe_scope_unavailable` and the message “Wall
sample has ambiguous adapter representations.” Its report has a healthy
`health_before`, a pending request, and no `health_after`. No native wall read or
highlight is established, and the report does not show a crash or prove the
underlying cause. Wall read and material writes remain pending. See the
[observation report and original uploads](m4-native-observation-0.18.1-2026-10-17.md).

The 0.17.1 observation on **2026-10-15 at 20:06 Europe/Warsaw** confirmed the
attribute roundtrip to ID **935**, `Klasa odporności ogniowej`, and reported
two successful W1 changes with readback **65535** and audited fields matching
the plan. It exposed a highlight semantic gap: only the two planned changes were
submitted; the matching Column already on W1 was omitted. The owner identified
that already-W1 Column as Column 1; the raw preview record identifies the no-op
by UUID `eb88c850-0cac-408a-8091-f118872d74c2`. The owner reported Columns 5 and
6 highlighted and moved. Three Columns with F120 were nonmatching. The report
records healthy before/after replies from the same host session and no crash
reported by the owner. Undo, rerun/no-op verification, and geometry confirmation
were not reported, so the result is partial native evidence, not blanket
`accepted_on_build`.

0.17.2 separates hash-bound `highlight_targets` (all `change` and `no_op`
matches) from `changes` (only `set_layer`). A complete supported plan remains
highlightable when state is `no_op`; Apply is unavailable when there are zero changes.
The launcher checks counts against `highlight_targets`, highlights no-op plans
without offering confirmation/Apply, and clears stale highlights when there are
zero matches. Unknown values block the action; more than 32 changes remain
blocked. The bounded owner test is specified in the
[0.17.2 guide](m4-column-layer-0.17.2.pl.md).

Clean source **6e87f56fc3e200c16d229d23e0bf85c483ce1220** passed **275 portable
tests** on CPython 3.12.14, frozen sync, wheel/sdist and Windows ZIP builds.
[Source CI 38785067377](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38785067377)
passed **6/6** Windows/Ubuntu × Python 3.11–3.13 jobs, including tests and builds.
Exact ZIP installation/upgrade from 0.17.1/restore passed with **29 bridge hashes**
and journal/trace bytes preserved. [Delivery and evidence](../evaluation-packages/0.17.2/README.md).
These checks qualified the 0.17.2 package for a bounded native observation.
The owner later tested the same Column handler in 0.18.1; scoped highlight
evidence is recorded above. This does not accept the whole M4 workflow or
repeat completed M3 gates. The frozen 0.17.2 artifacts remain unchanged.

[Original 0.17.1 observation and uploads](m4-column-layer-observation-0.17.1.md).

## Historical 0.17.1 delivery and 0.17.0 owner result

0.17.1 source tests, CI and builds/package verification are recorded with their
exact source scope in the [delivery record](../evaluation-packages/0.17.1/README.md).
The bounded native observation above confirms binding and two W1 writes;
complete workflow acceptance remains pending.
It corrects the criterion binding to exact names `Klasa odporności ogniowej` /
`Fire resistance classification`. The runtime resolves the ID and verifies the
name roundtrip; no fallback to 1398 or hardcoded binding to 935 is used.

The uploaded 0.17.0 owner report from **2026-10-15 at 19:40 Europe/Warsaw**
records **BLOCKED**. It resolved `Odporność ogniowa` to **1398**, which was absent
from the ReadAll response on all six Columns. All six criteria were unknown;
no highlighting, Apply or setters followed. The owner clarified the intended
field as **Klasa odporności ogniowej**, with F30/F60 choices. The guard correctly
blocked unknown reads, but the resolved field did not represent the requested
criterion: this is a semantic binding error, not successful criterion acceptance.
`health_before` was healthy and `journal_before` available with seven records
and no blockers. There is no `health_after`; full-run/after-run host health is
not established by this report.
[Original JSON](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.json),
[original TXT](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.txt).

Official [2026-1 attribute definitions](https://help.allplan.com/Allplan/2026-1/1034/Allplan/326206.htm)
identify **935** as **Fire resistance classification**, String. The
[official SDK example](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/BasisExamples/MacroWithElementGroup.py#L164)
sets 935 to **F30**; the [attribute tutorial](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
uses 1398 as **Fire risk factor** with **A1/A2**. These support the distinction;
the owner-confirmed Polish name is still checked against the actual project.
The existing ReadAll reader is retained. Genuine omissions remain unknown and
block Apply, as do actual read failures and unsupported values.

Historical 0.17.0 portable evidence remains **261 tests PASS** (2026-10-14),
with delivery/source CI evidence in its unchanged package; this does not establish
0.17.1 native acceptance. The 0.16.1 attachment confirms only one observed Column
attribute read and healthy same-session replies; the owner reports no crash.
The exact native cause of 0.16.0 remains unknown. Broad discovery stays blocked.
[Historical 0.17.1 workflow/limits](m4-column-layer-0.17.1.pl.md),
[historical 0.17.0 delivery and portable evidence](../evaluation-packages/0.17.0/README.md).

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
C05 structure/C06 NEW. Completed gates need no repeat. Continue the
[Column fire-resistance/W1 workflow](m4-column-layer-0.17.2.pl.md) within its
bounded owner test, then follow the
[editing development plan](office-editing-development-plan.pl.md) for thin-wall
native C35 material. Before main integration, perform the
final-candidate checks/full matrix in [testing policy](testing-policy.md).

## Historical records

Detailed contracts, completed walkthroughs and acceptance reports are available
in the [pre-cleanup documentation](https://github.com/blandjelly/allplan-mcp-server-python/tree/b0678da6d9d5565951c8576db8d83972331158c1/docs).
Their open/pause statements describe the original gate date, not current M3 status.
Raw uploads, manifests, checksums, logs and delivered archives remain in
[evaluation-packages](../evaluation-packages/); original removed baseline logs
remain in [Git history](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/evaluation-packages).
Do not rerun completed gates or rebuild old archives for documentation changes.
