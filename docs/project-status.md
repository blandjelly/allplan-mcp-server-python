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

**M1 implementation complete for the bounded read contract**, current package
**0.5.3**, **ready_for_owner_test**. The 0.5.0 implementation has **56 targeted portable checks PASS**.
The 0.5.2 native resource preflight **PASS**: profile 1.0.2 bound_for_read;
MCP_QA_MARK/MCP_QA_STATUS IDs 5001/5002 with exact names and string type 67;
SZ_OGÓ01/SZ_OGÓ02 IDs 3700/3701 with exact short-name round trips. Installed
integrity and transport verified. The group-versus-definition/full-versus-short-
name setup issue is resolved. These IDs are context observations, not constants.
Write eligibility remains not_checked; geometry/hierarchy/display-unit/offset
and full M1 runtime acceptance remain pending. The owner type probe identified
SkeletonBeam and MultiSlab roots excluded by the old family list. 0.5.3 adds
these exact families and slab-tier geometry; keep the existing model/resources.
Next: install 0.5.3, restore 102 passive/C05 review layer, then A for changed
component/solid reads; B/C afterward. No standalone profile/type probe repeat.
[Native-family correction](test-results/m1-native-families-0.5.3.md).
[Correction and bounded runtime evidence](test-results/m1-profile-correction-0.5.2.md).
[Follow-up evidence](test-results/m1-profile-followup-0.5.1.md).
New mm geometry and dimensional/AABB predicates, declared local/global transform,
parent-chain native component counts, profile schema/resource resolution and
configured level provenance are implemented. Source fingerprints cover queried
geometry/hierarchy/profile changes and retain read-only session binding.
[Completion evidence](test-results/m1-completion-portable-0.5.0.md),
[final UAT-02/UAT-03 card](m1-final-batch.md).

**M1 exit gate remains pending**: 0.5.0 native geometry/frame behavior, ten-
component geometry/hierarchy fixture and frame/unit captures must pass in
Allplan; bounded demo resource binding already passed in 0.5.2.
Persistence/write eligibility belong to downstream mutation work; no write
profile is activated. The server resolves real project IDs after UI setup;
missing resources block the query instead of guessing.

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
| M1.1 | Implemented; final runtime gate pending | Explicit scope/session/model identity, passive handling, mm/frame transform and configured-level provenance. Raw context/session behavior accepted; nonzero-offset/native geometry still needs owner evidence. Durable/write authorization is not claimed. |
| M1.2 | Implemented; bounded old batch PASS | Typed scalar/dimensional/AABB predicates and four-family top-level parent resolution implemented. New geometry/native counts have portable evidence and final Allplan gate pending. |
| M1.3 | Implemented; unchanged-source runtime PASS | Full cached selections/page/summary and geometry/hierarchy/profile-sensitive revalidation implemented. Changed-source staleness, TTL/eviction/restart retain portable evidence. Downstream mutation/persistence is deferred. |
| M1.4 | Implemented read binding; fixture runtime pending | Versioned demo schema and fresh name/type/ID/layer round trips, configured levels, exact UI recipe and diagnostic batch implemented. Actual named resources and full fixture need owner evidence; write eligibility remains not_checked. |

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

Next: obtain the remaining 0.5.0 final fixture/display-unit/nonzero-offset
captures, interpret them against the documented gate, and fix any native read
failures before accepting full M1. Then proceed to M2 audit. The
[0.4.0 metadata batch](m1-metadata-batch.md) is complete within its scope; no
repeat or extra capture is required. Do not repeat the passed
[0.3.0 query batch](m1-query-batch.md) without a relevant change or defect. Complete
M1.4 binding from verified resources before the six-column/ten-component UAT.
The demo profile remains **unbound and inactive**; **M1 is not accepted**.

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
