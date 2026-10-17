# Current handoff

**Owner agent trial, 2026-10-17:** the owner confirms fire-classification edits,
highlighting and query operations worked. The transcript reports F120, then
F60/F90 for separate Column sets, and correct 11-root/22-identity counts in
foreground 101. It also records two unsuccessful thin-Wall layer writes
(readback stayed 3735), numeric `Wartość U` previews blocked on an undefined
string, and an unsupported native material request. This is owner-reported
evidence without raw payloads or an exact installed build, not full M4/native
acceptance. [Retained log and scope](test-results/m4-agent-observation-2026-10-17.md).
Do not repeat the successful fire/query/highlight slice; investigate only the
reported failed operations and keep all journal/revalidation guards.

**Canonical M4 branch: `develop/m4`.** Created from `cf3c4bb`; all heads of
`codex/m4-property-discovery`, `codex/m4-0.18.0`, `fix/m4-host-timeout` and
`fix/m4-wall-sample` are included. New topic branches/PRs target develop/m4.
PRs #5/#7/#8 are closed as superseded; #6 was already closed. Legacy refs and
package links remain available; `fix/m4-wall-sample` is a compatibility ref.
Main remains separate and was not updated by this consolidation. Read the
[branch layout](branch-layout.md) before continuing or opening a PR.

**Testing procedure approved 2026-10-17:** read [AGENTS.md](../AGENTS.md) and
[the testing policy](testing-policy.md) at the start of every chat. Iterate with
affected/dependent tests and draft PRs; do not repeat the full local suite or
builds after each edit. Ready candidates use full CI instead of a full local
run: two Python 3.12 platforms normally, six for compatibility/main integration.
Project-version-only bumps do not expand the matrix. Build once after tests;
documentation/evidence updates skip product checks. Preserve accepted native
observations. [Procedure PR #9](https://github.com/blandjelly/allplan-mcp-server-python/pull/9)
is merged into main at `b91c471`, so future chats receive these instructions
from the default branch as well. [Verification](test-results/testing-policy-2026-10-17.md)
records the one-time six-job workflow check, one build and the confirmed M4
draft skip. M4 runtime integration remains separate.

**New source candidate: 0.20.1 — fixes from the owner agent log.**
Branch `fix/m4-undefined-values-wall-layer` starts from develop/m4 `7493ed3`;
PRs still target develop/m4 and main remains separate. Typed numeric/boolean
replacements accept only the exact observed undefined strings with a bound
old_value_state marker; original raw values/fingerprints remain intact.
The preview and low-level executor/adapter enforce the same narrow policy.
Wall layer changes bind real WallTier owners, check all tiers before setters
and read them freshly afterward, instead of treating the Wall root's raw layer
as proof of its component layer. Existing journal set_layer semantics remain
unchanged. New query layer_resolution=component is explicit and semantic-only;
the default adapter reader and successful owner fire/query/highlight slice
remain preserved. Mixed-tier layers/unknown hierarchy block before mutation.

Focused numeric, hierarchy, replay/recovery, target-writability and MCP HTTP
regressions pass with native fakes. Final source CI and package evidence are
pending for this candidate; **new native behavior is not_run**. Next owner
trial is only the numeric Wartość U from undefined and the Wall tier layer path.
Do not repeat accepted fire/query/highlight or historical read gates. Native
material edits remain unavailable and must not be substituted with an arbitrary
attribute. [Short trial and limits](m4-agent-fixes-0.20.1.pl.md).

**Previous source candidate: 0.20.0 — typed criterion `model_edit`, native acceptance pending.**
Topic `topic/m4-universal-attribute-edit` starts from develop/m4 `cc062bc` and
must target develop/m4; main integration remains separate. The new MCP route
plans direct attribute/layer edits without audit findings, resolves exact
project names/IDs and SDK type members, and reuses the shared executor,
write-ahead journal, revalidation, highlight binding, fresh native writability,
readback, replay and read-only recovery. Attribute replace/add/upsert supports
explicit text/integer/real/boolean values only when the loaded SDK's matching
type exists. Unknown/special types fail closed. Stored omissions remain unknown;
the new opt-in computed-inclusive dual read can prove absence and rejects
computed-only destinations. The broad property discovery quarantine remains.

Query adds semantic component owners, family and optional opening_kind:
`WindowDoor_TypeUUID` remains a common opening owner; defensive GetElement
class checks distinguish documented DoorOpeningElement/WindowOpeningElement
when available. Unresolved opening kinds remain not_checked, never a claimed
zero-match set. Ordinary Column/Wall/Slab/Beam variants retain exact API UUIDs.
Native selection remains unsupported; the explicit presentation is highlight.
New writes still require a reviewed disposable copy, exact highlighted plan
and execution ID, one foreground drawing and at most 32 setters. Multi-drawing
write batches, enum/date codecs and native property/material updates are not
implemented. The complete office-editing plan is **not** accepted or complete.

Runtime source **ec2aeae832c2ac017c07c4af71b7c7a6ff47f9d9** passed
[CI 39049036363](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39049036363):
**387 tests on each Windows/Ubuntu Python 3.12 job**, then one package job.
Workspace artifact transfer returned HTTP 403; one allowed local fallback build
used that exact clean source. The delivered ZIP passed exact payload/checksum,
registration, frozen sync/import, upgrade from 0.19.0 and restore, with **34 bridge
hashes** and journal/trace/bridge-log preservation.
[Package, checksums and evidence](../evaluation-packages/0.20.0/README.md).
These are portable checks, not native Allplan results. Next owner
trial is only the NEW typed attribute add/replace + layer path (including
readback/replay/Undo), and optional opening-kind recognition on representative
objects. Do not repeat accepted historical Wall/Column/M3 trials. See the
[Polish workflow](m4-model-edit.pl.md) and [API evidence](m4-attribute-api-evidence.md).

**Current runtime: 0.19.0, `model_wall_filter`, scoped native PASS / accepted_on_build.**
Runtime source **e455f35cf4d546d9b77cf6ae5f59edcc026cc875** passed
[CI 39033571910](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39033571910):
**6/6 Windows/Ubuntu × Python 3.11–3.13**, **356 tests** per job and one
package job. Workspace transfer of the CI artifact was blocked by proxy
CONNECT HTTP 403; the permitted single local fallback build used a clean
detached checkout of the same source. Exact delivered ZIP installation,
frozen sync/import, upgrade from 0.18.2 and restore passed, with **31 bridge
hashes** and journal/trace/bridge-log preservation.
[Delivery, hashes and evidence](../evaluation-packages/0.19.0/README.md).
Native observation on **2026-10-17 Europe/Warsaw** is **PASS / accepted_on_build
0.19.0** for the two single-tier Walls in active foreground drawing 101:
**200 mm matches `<240 mm`; 240 mm does not**. Complete M1/read/criterion
coverage, two Walls, one match, no exclusions/omissions/unreadable/unprocessed
records, and one submitted highlight adapter. The owner confirmed the 20 cm
Wall highlighted correctly, then cleared, with no host interruption. Separate
filter/clear reports contain **four healthy replies in the same host session**.
[Observation and four original uploads](m4-wall-filter-observation-0.19.0.md).
The original JSON flags (`not_run`, `awaiting_owner_observation`, null visible
counts and runtime/unit flags) remain unchanged; owner confirmation supplies
scoped UI acceptance. Reports request no setters and report no model data change;
there was no independent geometry comparison or write/Undo test.

**Do not repeat this completed trial or the accepted one-Wall/Column/M3 slices.**
The [Polish guide](m4-wall-filter-0.19.0.pl.md) is retained as a historical procedure.
This does not complete K2 or M4: native selection, exceptions/zero-match and
rotated/multi-tier/large/multiple-drawing cases remain unaccepted. Next Wall work
is material target binding and a separately validated native update/readback
path under the [editing plan](office-editing-development-plan.pl.md), without
inferring write support from this read-only PASS.
See [tool contract](tool-reference.md#model_wall_filter--m4-wall-thickness-filter).

Last native single-Wall read acceptance: **0.18.2**, originally delivered through
`fix/m4-wall-sample`, based on the verified
0.18.1 delivery at `0860438`. The documentation/evidence update was committed
first (`194088c`), before runtime edits. `wall_sample` now accepts distinct
Python wrappers only within one complete, consistent M1 root identity and view.
It still rejects multiple views, conflicting fields and incomplete hierarchy.
No other native handler changes; no material setter or Wall highlight is added.
The native gate is **PASS / accepted_on_build 0.18.2** for the single Wall read:
the owner confirmed **240 mm** and raw material **`Beton`** against UI. M1 found
two Walls and sampled one, the first in model UUID order. Both health replies
were healthy in one session; no setters were requested or model changes reported.
The selected root had four adapter representations. The strict `<240 mm`
criterion correctly returned false. The 20 cm Wall's properties were not read.
[Observation and original uploads](m4-wall-observation-0.18.2.md),
[short Polish guide](m4-wall-sample-0.18.2.pl.md) and
[delivery evidence](../evaluation-packages/0.18.2/README.md).
Clean runtime source **47ec1ad5ccc494452d2bdcd5c7252f8969facbd5** passed
**312 portable tests**, frozen sync, builds and exact ZIP installation/upgrade
from 0.18.1/restore (30 bridge hashes; journal/trace/bridge log preserved).
Only `wall_probe.py` changes in the native payload.
[Source CI 39027996719](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39027996719)
passed **6/6 Windows/Ubuntu × Python 3.11–3.13** jobs, including tests/builds.
[Historical PR #8](https://github.com/blandjelly/allplan-mcp-server-python/pull/8)
is closed as superseded by develop/m4; main integration remains separate.

Previous transport delivery, 2026-10-17 Europe/Warsaw: **0.18.1** on
`fix/m4-host-timeout`, based on `codex/m4-0.18.0` at `0dbe7cf`.
The supplied MCP and bridge logs correlate a health timeout with an incomplete
HTTP 200 response. A timer-driven Python UI queue, cooperative worker scheduling,
pre-start cancellation and stage timing replace the synchronous CLR dispatch
round trip. The underlying native scheduling/socket cause remains unproven.
[Incident evidence, changes and short Polish health-only check](mcp-timeout-0.18.1.md).
Clean source **f477f138231f2a8f45690c03bd761364c7e94ab6** passed **306 portable
tests**, frozen sync, builds, exact ZIP installation/upgrade from 0.18.0/restore,
and [source CI 39026387338](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39026387338),
**6/6 Windows/Ubuntu × Python 3.11–3.13**. Thirty bridge hashes verified;
journal/trace/bridge log preserved. [Frozen delivery](../evaluation-packages/0.18.1/README.md).
The owner subsequently confirmed the host was responsive on 0.18.1 and completed
scoped Columns highlight and Wall sample observations. Columns highlight
visibility and same-session health are owner-confirmed; the Wall sample blocked
before native read. Neither result accepts writes or the complete M4 workflow.
[Observation report](m4-native-observation-0.18.1-2026-10-17.md).
[Historical PR #7](https://github.com/blandjelly/allplan-mcp-server-python/pull/7)
originally targeted `codex/m4-0.18.0` and is now closed as superseded by develop/m4.
All original 0.18.0 artifacts remain frozen. The preceding Wall/Columns work and
its limits below remain applicable after transport verification.

Prior 2026-10-15 Europe/Warsaw record: **0.18.0**, **ready_for_owner_test** for its Wall read.
Clean source **5ea4bcfd88f500bbf137e361ba5d6cc3d83710b5** passed **289 portable
tests**, six Windows/Ubuntu × Python 3.11–3.13 CI jobs, frozen sync, builds and
exact ZIP install/upgrade from 0.17.2/restore verification (30 bridge hashes;
journal/trace preserved). The package carries the
0.17.2 `column_layer.py` and `column_layer_diagnostics.py` runtime unchanged,
and adds the isolated wall-property phase, its diagnostic and
**M4 Wall Properties.cmd**. The [0.18.0 delivery README](../evaluation-packages/0.18.0/README.md)
and [short owner guide](m4-wall-properties-0.18.0.pl.md) record the bounded next observation.
No main integration.

Source-only work after that delivery adds `wall_report_analysis`, a stdlib-only
CLI for an already saved 0.18.0 report. It recomputes strict `<240`, compares the
exact native material text and applies file+UUID exceptions. It checks complete
same-reported-host steps, source/ref agreement and field provenance, but never
proves report authenticity, live model state, native units or material binding.
Every result is non-executable: no plan/Apply IDs, no native/HTTP calls, and
`usable_for_write=false`. **10 focused tests PASS**; this is not a full-suite
result. Source **0c3a2987df164254d03cd749bcb72b71a79716ee** additionally passed
[standard Windows/Ubuntu Python 3.12 CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38824865834),
**2/2 jobs**, with the full **299-test** portable suite and standard builds.
[Usage and limits](m4-wall-report-analysis.md). No new owner package,
version bump or rebuild of the frozen archives is needed for this source-only
step. The supported material setter remains blocked pending native evidence.

The 0.17.2 artifacts, README, source and CI evidence remain unchanged. Its
deferred native observation was later run through the same Column handler in
0.18.1; the 0.18.1 report records the result and owner-confirmed UI visibility.
The blocked 0.18.1 Wall request was followed by the successful, scoped 0.18.2
observation recorded above.

The new `wall_sample` phase is limited to one existing, single-tier native Wall
in foreground drawing 101. It reads the first tier's thickness and raw material
after confirming the object type and `TierCount == 1`. Without an explicit
UUID it selects the first model UUID, not the thinnest Wall. A valid 200 mm
sample yields `matches_assuming_native_mm=true`; the observed 240 mm sample
correctly yielded false. The guide's earlier expectation of always sampling
200 mm was incorrect. Runtime unit verification and material target binding
remain false/not checked; no material write is available. This one confirmed
sample does not establish full-Wall filtering or material-write support.

The owner requested the full first scenario and explicitly accepted highlighting:
Columns without fire resistance classification → matching targets highlighted →
existing W1. The owner clarified the field as **Klasa odporności ogniowej**, with
F30/F60 values. The [0.17.1 observation](m4-column-layer-observation-0.17.1.md)
confirmed the exact binding and two writes but exposed that the already-W1
matching no-op was omitted from highlighting.

The retained 0.17.2 runtime assigns hash-bound `highlight_targets` to all matched `change` and
`no_op` Columns, while `changes` contains only layer setters. A full plan with
no changes can still highlight all matches; it cannot be confirmed or applied.
Unknown values block the action, and more than 32 changes remain blocked.
The owner later confirmed highlight visibility for the no-op scenario through
the same handler in 0.18.1. This does not accept writes, Undo or full M4; see
the [observation report](m4-native-observation-0.18.1-2026-10-17.md).
The 0.18.1 Wall sample was blocked before read and remains pending.

The 0.17.0 owner run on **2026-10-15 at 19:40 Europe/Warsaw** was **BLOCKED**.
It bound `Odporność ogniowa` (1398), absent from ReadAll on all six Columns;
the six unknown states blocked before highlighting/Apply/setters. This is a
semantic field-binding error, not acceptance of the requested criterion merely
because the write guard stopped. `health_before` was healthy; `journal_before`
was available with seven records and no blockers. There is no `health_after`, so
the report does not establish host health throughout or after the run.
[Original JSON](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.json),
[original TXT](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.txt).

0.17.1 defaults to exact names `Klasa odporności ogniowej` /
`Fire resistance classification`, with runtime ID/name roundtrip and no fallback
to 1398. Official 2026-1 documentation identifies 935 as Fire resistance
classification and the SDK uses 935 with F30; 935 is evidence, not a hardcoded
runtime binding. Keep the existing ReadAll reader and genuine omissions unknown.
Do not add computed reads or broad metadata discovery to compensate for the wrong name.

The uploaded 0.16.1 report contains one successful raw Column read bracketed by
healthy replies from the same host. The owner reports no crash. Names, layers,
UI and writes were not requested, so this is not acceptance of the new workflow.
The 0.16.0 native root cause is still unknown; retain its FAIL_CRASH record and
quarantine. New workflow avoids broad definition/enum calls and retains native
container owners through writes/readback. Do not infer native crash containment.

`column_layer` previews criteria directly, without fake audit findings, and uses
the shared RepairExecutor/journal. Unknown/absent-from-ReadAll values block the
action; matched Columns already on W1 are no-op. 0.17.2 highlights all matched
Columns (changes plus no-ops), but applies setters only for changes. Full
source/resource revalidation, native writability, readback and bounded journal
guards remain. The old isolated probe launcher remains available, but the new
task uses **M4 Columns to W1.cmd** and **M4 Columns Recover.cmd**.

The bounded single-Wall observation is complete; do not ask the owner to repeat
it. The scoped two-Wall filter/highlight/clear trial is also complete on 0.19.0;
see the current acceptance above. Preserve reports, existing traces and repair
journal. Broader filtering cases and material binding/write/readback remain
unverified; the 0.18.2 sample alone does not accept the broader M4 workflow.
See the [corrected guide](m4-wall-sample-0.18.2.pl.md).

M3 acceptance remains limited to its historical fixture/build/single- and
two-change cases. See [validation](validation-status.md) and [testing policy](testing-policy.md).
