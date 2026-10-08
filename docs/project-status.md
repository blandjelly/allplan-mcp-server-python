# Project status

Updated: 2026-10-09. **M0 CLOSED**, accepted on **Allplan 2026-1-7**, package
**0.1.2 evaluation**. **UAT-00 PASS; UAT-01 PASS**. The owner confirmed all
remaining tests work correctly. [Acceptance and evidence](test-results/m0-acceptance-0.1.2.md).

## Baseline and tested environment

- Fork: `blandjelly/allplan-mcp-server-python`; upstream: `AlejoDuarte23/allplan-mcp-server-python`. Implementation baseline `f98bef8a2fc030216408b2b7dbbba1ce02684f9f`; initial checkout fast-forwarded without discarding owner edits. No applicable AGENTS.md found.
- Owner Windows setup: Allplan UI build **2026-1-7**, API release **2026.1**, embedded CPython **3.13.13**, external Python **3.14.8**, local Windows Codex app. App/Windows version and project/file names not supplied.
- Portable validation: Linux, external Python **3.12.14**, FastMCP **3.2.4**, uv **0.12.19**; **25 tests passed**, wheel/sdist and ZIP built/verified. GitHub Actions matrix not executed here.
- Exact accepted archive and SHA-256 are recorded in the acceptance report. The original ZIP is unchanged; later evidence/closure docs are separate. No release has been published.

## Completed tasks

| Task | Status | Evidence |
| --- | --- | --- |
| M0.1 | Complete | Fork/upstream, baseline and license inspected; external/embedded runtimes recorded separately. Full UI build reported by owner; release/executable metadata observed through host. |
| M0.2 | Complete | Recursive registration, caches excluded, custom/redirected folder support, repeat install, version/integrity, backups, restore and rollback tested. Library-path defect in 0.1.1 fixed and accepted in 0.1.2. |
| M0.3 | Complete | Health/version/names and box called through local Windows Codex. Categorized errors and stopped-host recovery verified. Development execution disabled by default; docs reconciled. |
| M0.4 | Complete for tested setup | Owner confirms ESC/restart, minimize/restore and project switching. Logs prove stopped-host failure and a new host session. Portable queued-request cancellation probe retains UI dispatch without UI joins. |
| M0.5 | Complete | Versioned evaluation package, launcher, Codex setup, read-only diagnostics, restore instructions and portable checks delivered. Owner acceptance recorded. |

The integrated M0 exit gate is met. Automatic box readback and durable deduplication
are not implemented. The in-flight race is portable-probe evidence, separate from
owner UI tests. License/public redistribution remains unresolved; neither fork
nor upstream reports a license and none was invented. [Support matrix](support-matrix.md).

## Current M1 implementation and next action

Integration: completed M1 is pushed on `codex/m1-scope-model-query` in open draft
[PR #1](https://github.com/blandjelly/allplan-mcp-server-python/pull/1), not yet
merged into main at this handoff. Closure commit
`c6d82867e67342d2b145513bf816eea8bdfa8be7`; subsequent documentation updates
do not change the tested artifact. Continue from the latest branch/PR state.

**M1 CLOSED; UAT-02/UAT-03 PASS within the bounded read contract**, current
package **0.5.3**, profile revision **1.0.2**, Allplan **2026-1-7**.
[Acceptance and exact tested artifact](test-results/m1-acceptance-0.5.3.md).
Native resource preflight, A geometry/hierarchy, B display-unit invariance and C
nonzero XY offset pass. Counts remain ten roots in 101 plus one passive reference
in 102; column/S02/C01 filters 6/2/1. C adds (100000,200000,0) mm exactly once to
all ten global boxes, leaving local geometry and dimensions unchanged. Owner UI
offset 100/200 m and C01 base-section center 100/200/0 m agree. Owner confirms
A dimensions and A/B/C unchanged appearance, and retains the original baseline.
102 passive/C05 review-layer setup corrections were separately verified in B/C.

The original implementation's **56 targeted portable checks PASS** and the
native-family correction's **14 targeted portable checks PASS** remain separate
from owner Allplan verification. No accepted suite/batch was repeated for closure.
[Portable completion](test-results/m1-completion-portable-0.5.0.md),
[native-family correction and A/B evidence](test-results/m1-native-families-0.5.3.md),
[resource binding](test-results/m1-profile-correction-0.5.2.md).
The tested 0.5.3 ZIP and older archives are unchanged; no runtime code/profile
change or rebuild accompanies closure. Static runtime_verified annotations remain
unchanged; acceptance is recorded per build/fixture, not globally inferred.

Write eligibility remains not_checked; the demo is bound_for_read and inactive
for writes. Levels are profile configuration, not native BWS. Durable references,
arbitrary native trees, nonzero Z offsets, exact solid intersections and downstream
mutation/Undo are not accepted. Changed-source staleness/TTL/eviction/restart
retain portable evidence. M2 audit and M3 repair remain unimplemented/unrun.
Next: M2 profile/audit contracts and read-only findings; no further M1 owner test.

Earlier **0.4.0** metadata/evidence-capture slice remains bounded accepted.
**12 targeted portable checks PASS; bounded Allplan metadata batch PASS**.
[Runtime evidence](test-results/m1-metadata-runtime-0.4.0.md) verifies two stable
column identities, attribute 498 metadata (Nazwa obiektu, codes 67/69, empty unit
label), layer 3736 AR_SŁUP and complete response capture. File 2 omits raw 498
while passive and returns Słup while active background. Sessions also changed;
do not infer a universal state-only cause. Owner confirms columns unchanged,
file 2 restored to passive and the same Allplan 2026-1-7 build. No repeat needed.
[New implementation evidence](test-results/m1-metadata-portable-0.4.0.md) and
[two-capture owner card](m1-metadata-batch.md). `model_query` now includes typed
`inspect`; metadata is read per field, sample/layer coverage is bounded, passive
missing values do not establish native absence, and full responses are saved by
**M1 Metadata.cmd**. The 0.5.0 schema/read-binding implementation subsequently passed the bounded
0.5.2 owner preflight; write eligibility remains not_checked.

The earlier **0.3.0** scope/query slice remains bounded-runtime accepted.
Work started from
current `origin/main` **d8bd1ef8388daa956e8b51863b17ac33d784dca9**, preserving
accepted evidence and original archive hashes. The **0.2.1** context/identity probe
and its accepted reader correction are reused.
`get_model_context` is implemented as a bounded read-only probe; project/file
states, units, raw offset and optional model/view identity sampling are included
in diagnostics. **31 portable tests pass**. Owner 0.2.0 logs verify file-state
reads, passive inclusion and separate model/view GUIDs, but project lookup fails.
[Runtime findings and correction](test-results/m1-context-runtime-0.2.0.md).
**0.2.1 context correction batch PASS**: project names/keys resolved, file 2
excluded after unload, project switch reflected, readable separate model/view
GUIDs. Owner confirms names match and model unchanged.
[0.2.1 runtime evidence](test-results/m1-context-runtime-0.2.1.md).
[Implementation and limits](test-results/m1-context-probe-0.2.0.md).

No repeat of the correction batch is needed.

| Task | Current state | Evidence / remaining scope |
| --- | --- | --- |
| M1.1 | Complete for tested read scope | Explicit scope/session/model identity, passive handling, mm/frame transform and configured-level provenance. Raw context/session, native geometry and B display-unit reads accepted; nonzero XY offset C and independent UI coordinate check PASS. Durable/write authorization is not claimed. |
| M1.2 | Complete for tested read scope | Typed scalar/dimensional/AABB predicates and six-family top-level parent resolution. Native ten-component geometry/counts and display-unit invariance pass; C offset and owner UI observations PASS. |
| M1.3 | Complete for tested read scope | Full cached selections/page/summary and geometry/hierarchy/profile-sensitive revalidation implemented. Changed-source staleness, TTL/eviction/restart retain portable evidence. Downstream mutation/persistence is deferred. |
| M1.4 | Complete for tested read scope | Actual named resources bind for reads; B verifies both fixture layers/reference state. Configured levels are not native BWS. Write eligibility remains not_checked; C offset and owner UI observations PASS. |

**24 relevant portable checks PASS** on Linux/Python 3.12.14/FastMCP 3.2.4:
21 new query contract/fake-adapter checks, one new real MCP transport check,
and two package/version checks. Wheel/sdist and deterministic evaluation ZIP
build succeed. The full historical M0 suite was not rerun; a discovery import
initially repeated 11 handler checks and was corrected to avoid duplicate CI
discovery. Windows/CI automated execution is not claimed by that portable report;
owner Allplan evidence is recorded separately below.
[Portable report](test-results/m1-query-portable-0.3.0.md).

**Three bounded 0.3.0 owner query cases PASS**. The supplied query results report
matches the diagnostics' host session and column model/view UUIDs: two matched
identities, two distinct pages, full summary by file/type, exact type/layer and
raw attribute 498 predicates, and explicit passive-file omission with incomplete
requested scope. Native type Column_TypeUUID/GUID and layer 3736 are observed.
Attribute 498 is observed on file 1 and returned missing on passive file 2;
do not infer a bound mark or native absence under every access state.
The report states no model changes; independent geometry/visual readback is not
claimed. Static runtime_verified=false is not an acceptance registry.
[0.3.0 runtime record](test-results/m1-query-runtime-0.3.0.md).

Next: implement M2 audit/profile contracts and read-only findings. Keep C03's
literal undefined text as explicit native evidence while defining missing-value
semantics. Retain the accepted fixture/build and prepare only UAT-04 once runnable.
Do not repeat M1 batches, repackage 0.5.3 or begin native repairs for this step.

The capture history below describes earlier failed/partial attempts, superseded
by the linked 0.5.3 acceptance; it is not a request to repeat those steps.

## First final capture A — 2026-10-08

**Not accepted.** All five scans enumerate only one column from file 102;
file-101 queries return zero despite owner confirmation of the full visible
ten-component fixture. 102 is active background rather than recipe-passive;
103 unloaded omission is explicit. Resource binding remains successful.
The file-102 column AABB is 400x400x3000 mm with XY center (200,200),
not identified C01 evidence. Input-view/session enumeration cause remains
unresolved; no model rebuild, speculative API fix or automated rerun. Next:
fresh host/model view with 101 foreground/102 passive/103 unloaded and capture
A only. B/C remain pending. [Sanitized report](test-results/m1-final-runtime-0.5.2.md).

### Capture A after file reassignment — partial PASS

Latest report diagnostics-20261008T193947Z.json resolves enumeration of 101.
Six column geometries and two S02/one C01 matches pass; C01 agrees with owner
400x400x3000 mm and XY=(0,0). Full A is still pending: only seven supported
roots in 101, no supported beam/slab roots despite a raw slab context sample.
Next: raw type/parent probe via M1 Component Types.cmd add-on, no reinstall or
rebuild. Remaining setup discrepancies: 102 active background, C05 wrong demo
layer, C03 literal undefined text. B/C pending; no full M1 acceptance.
[Sanitized findings](test-results/m1-final-runtime-0.5.2.md).
