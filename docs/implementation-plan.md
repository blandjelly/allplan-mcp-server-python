# Implementation stages

Current state and next action: [handoff](next-model-handoff.md).
Tool scope: [features](features.md). Shared contracts: [architecture](architecture.md).
Work in small, reviewable slices; task IDs remain stable. Dates depend on accepted
capabilities and API probes rather than a fixed completion promise.

## M0 — Installation and bridge baseline: complete

**M0.1–M0.5 complete, 2026-10-07**, package 0.1.2, Allplan 2026-1-7.

| Completed task | Delivered scope |
| --- | --- |
| M0.1 | Repository provenance and separate runtime/build discovery. |
| M0.2 | Recursive registration, integrity, backups and restore. |
| M0.3 | Health/version/names/box and readable connection errors. |
| M0.4 | Host lifecycle, ESC/restart, recovery and project switching. |
| M0.5 | Versioned Windows package, launchers, diagnostics and Codex configuration. |

**Exit gate met:** UAT-00/UAT-01 PASS for installation, one correctly sized box,
ESC/restart, minimize/restore and project switching. Evidence/limits are in the
handoff. Continue from M1; retest M0 only for relevant changes or a new defect.

## M1 — Context, identity, selections and query: complete within the bounded read contract

**M1.1–M1.4 complete, 2026-10-09**, package 0.5.3, profile 1.0.2,
Allplan 2026-1-7. [Acceptance and limits](test-results/m1-acceptance-0.5.3.md).

| Completed task | Delivered scope |
| --- | --- |
| M1.1 | Explicit session/project/file scope, model/view identity, canonical mm geometry and offset once; configured levels retain their provenance. |
| M1.2 | Typed scalar/dimension/AABB predicates and six supported top-level root families, with child deduplication and wall/slab tier unions. |
| M1.3 | Full cached selections, pages/summaries, relevant-source revalidation, TTL/eviction and restart invalidation. |
| M1.4 | Validated demo profile, fresh named resource read binding, metadata inspection and the owner-built fixture. |

**Exit gate met (UAT-02/UAT-03):** native A/B/C captures verify ten file-101
roots, six columns, two S02 and one C01 spatial/height match, complete pages/
summaries, display-unit invariance and offset (100000,200000,0) mm once.
Owner UI dimensions/coordinates and unchanged appearance agree. Static
runtime_verified flags are not an acceptance registry. Durable references,
write eligibility/Undo, native BWS, arbitrary framing families and nonzero Z
offsets remain outside acceptance. No further M1 owner batch is requested.

## M2 — Audits and profile foundations: closed; bounded UAT-04 PASS

Package **0.6.1**, audit profile **2.0.0**. Native 0.6.0 report and owner UI checks
match; a later invalid-scope request coincided with a managed-exception crash.
[Callback containment fix](test-results/m2-dispatch-fix-0.6.1.md) is portable-tested;
[native 0.6.1 acceptance](test-results/m2-acceptance-0.6.1.md) confirms two identical
complete audits, public/host scope rejection and continued host/Allplan operation.
The earlier crash's precise cause remains unproven. No repeated owner test is required.
[Contract](m2-audit-contract.md),
[portable evidence](test-results/m2-audit-portable-0.6.0.md) and
[completed owner test card](m2-audit-batch.md). Acceptance is limited to the recorded fixture.

- **M2.1** Versioned schema for typed attributes/layers, values, uniqueness and tolerances; validate bound resources.
- **M2.2** `model_audit` with severity, evidence, distinct unchecked states and readable/structured reports.
- **M2.3** Findings tied to session/project/document/model references and deterministic finding IDs; file/mark/model-local box and center for inspection. Durable references and native highlight remain unverified.

**Exit gate (UAT-04):** demo returns exactly 5 findings on 5 columns, correct
uniqueness scope, explicit unavailable data and locatable targets; no writes.

## M3 — Controlled repairs and standards: bounded preview and execution PASS

Package **0.8.1** corrects 0.8.0's overly broad IsInMacro preflight rejection;
[original failed native gate and correction](test-results/m3-apply-rejection-0.8.0.md).
The rejected request called no setters. The corrected 0.8.1 gate now has
[bounded native acceptance](test-results/m3-execution-acceptance-0.8.1.md):
two native repairs/readbacks, verified audited fields, exact-ID replay across
host sessions, **two separate Undo steps**, and recovery after confirmed Redo.
The package retains bounded disposable-copy native layer/status apply,
fresh resolution/eligibility, per-target readback, collateral audited-field checks,
persistent execution identity and read-only recovery. Portable evidence is
[recorded separately](test-results/m3-execution-portable-0.8.1.md).
The [write/Undo gate](m3-apply-batch.md) is complete for this fixture; no repeated
Apply is requested. The manual-edit card's UI action interrupted the host;
[native old-plan revalidation after restart PASS](test-results/m3-plan-restart-acceptance-0.8.1.md).
Native same-session conflicts remain blocked; no repeat on this build is requested.
The [stale Apply card](m3-stale-apply-batch.md) now has
[native PASS](test-results/m3-stale-apply-acceptance-0.8.1.md), explicit pre-setter
rejection and identical complete audits/unchanged UI. Undo grouping and M3 closure remain
unclaimed. [Execution limits](m3-execution-contract.md).

Package **0.7.0** implements the first read-only M3.1/M3.2 slice:
`fix_model_issues` explicit layer/status preview and plan revalidation, full fresh
audit evidence, exact values/locators/exclusions, plan ID/hash, bounded cache and
stale/expiry/restart controls. [Contract](m3-repair-contract.md),
[portable checks](test-results/m3-preview-portable-0.7.0.md),
[completed owner gate](m3-preview-batch.md),
[native acceptance and limits](test-results/m3-preview-acceptance-0.7.0.md).
Owner confirms target/value correspondence and continued host/Allplan operation;
native revalidation/follow-up audit retain identical audited source. No repeated
preview batch is required. Manual-edit native conflicts remain unverified.
The 0.7.0 package invokes no setters. The 0.8.1 bounded M3.1/M3.2/M3.4
implementation has the native observations above. UAT-05/UAT-06 remain open
for broader required behavior. Native stale Apply rejection is accepted;
unknown-outcome recovery and broader mutation/registry guarantees remain
unaccepted. Current recovery evidence concerns a completed saved execution.

Package **0.9.0** implements the first M3.3 **preview-only** slice:
versioned demo layer/status `apply_office_standard` and predicate/UUID-exception
`rule_based_edit` over one shared full audit snapshot. Excluded-element edits
still conflict on full revalidation; unknown predicates block readiness.
Standard/selected plans cannot use native Apply, including through fix_model_issues.
[Contract](m3-standards-contract.md), [155 portable tests](test-results/m3-standards-portable-0.9.0.md),
[native new-tool preview PASS](test-results/m3-standards-acceptance-0.9.0.md).
All three zero-proposal plans, full before/after audits, revalidations and host
continuity pass; no repeat is needed.

Package **0.10.0** adds explicit per-model mark proposals under required/unique
mark rules and same-snapshot full-scope collision simulation. Unknown evidence
blocks readiness; excluded peers still participate. Mark metadata refuses Apply
even when filtering leaves the old layer/status pair.
[Contract](m3-marks-contract.md), [portable evidence](test-results/m3-marks-portable-0.10.0.md),
[completed read-only owner gate](m3-marks-preview-batch.md),
[native marks-preview PASS](test-results/m3-marks-acceptance-0.10.0.md).
Two explicit proposals, a selection exception, collision against an excluded peer,
three unchanged revalidations and identical audits pass; owner confirms unchanged
model and uninterrupted host. No repetition is required. Numbering, labels, wider
standards and selected/mark native writes remain deferred. M3 is open.

- **M3.1** Shared preview/apply, stale checks, serialized writes, request identity, readback, partial outcomes and tested Undo limits.
- **M3.2** `fix_model_issues` for writable attributes/layers; data marks and graphical labels stay distinct.
- **M3.3** `apply_office_standard` and attribute/layer `rule_based_edit` reuse the same services.
- **M3.4** Persist/reconcile managed records where needed; prove retry deduplication and unknown-outcome recovery.

**Exit gate (UAT-05/UAT-06):** preview leaves the model unchanged, only authorized
writable targets change, demo repairs leave 3 findings, stale/manual edits conflict,
repeated requests do not repeat writes, and re-audit/readback match the model.
**First MVP = accepted M0–M3**, with versioned install/update/restore and support limits.

## M4 — Native edits, frames and foundations

- **M4.1** Probe ordinary columns/beams versus Structural Framing and wall materials; record read/create/update support per type/property/build.
- **M4.2** Extend native-property `rule_based_edit` only for proven combinations, preserving dependencies and exceptions.
- **M4.3** Native explicit-grid frame generation, generation keys and manual-edit conflicts; framing/bracing only after probes.
- **M4.4** Pads under selected base columns, then straight-wall strips; profile dimensions/elevations and update/no-op/conflict on repeat.

**Exit gate (UAT-07–UAT-09):** native types, counts, geometry, levels, exceptions,
links and repeat behavior verified. No silent deletion/recreation of manual work.

## M5 — Prepared layouts and issue exports

- **M5.1** Probe insertion, paper scale/crop/margins, title blocks and PDF/DWG on one sheet; native revisions separate.
- **M5.2** `populate_layouts` with template reserved areas, numbering, occupied-sheet policy and deterministic overflow.
- **M5.3** Limited `documentation_audit` for known requirements and explicit unchecked/manual-review states.
- **M5.4** `prepare_issue_package` with preflight, metadata, new output directory, verified files/hashes and partial-export recovery.

**Exit gate (UAT-10/UAT-12):** contents, scale, fields and exact output list match;
PDF/DWG opens correctly, critical audit failures block issue readiness, existing
issues stay preserved. Export recovery is separate from model Undo.
M5 may follow M3 before M4; it does not require full structural generation.

## M6 — One managed documentation workflow

- **M6.1** Probe UVS creation/update using `ViewSectionElement` / `CreateSectionsAndViews()`, labels/dimensions and source changes.
- **M6.2** Foundation plan, two sections, dimension chains, marks and own schedule with declared checked quantities.
- **M6.3** Owned roles/dependencies, missing/stale audit and manual-adjustment preservation or explicit conflict.
- **M6.4** Compose with M5 layouts/exports without duplicate numbering/content.

**Exit gate (UAT-11):** initial generation, repeat and source change work; missing
dimension roles are detected and manual edits preserved or surfaced for review.

## M7 — Coordination openings and extensions

- **M7.1** Early spike after M1: one pipe/wall and one pipe/slab crossing, actual host link and repeat prevention.
- **M7.2** Proven crossings, broad-phase candidates plus geometric intersection, clearance, source links and edge/support exceptions.
- **M7.3** Extend imports, oblique/merged openings, native edits and documentation only with demand and evidence.
- **M7.4** Probe native revisions, building structure and file moves before claiming 2026 support.

**Exit gate (UAT-13):** openings modify correct hosts, have expected clearances,
do not duplicate and report ambiguity/unsupported cases. DN does not replace
actual outer/insulation geometry. A feasibility spike is not production acceptance.

## Validation and delivery

The model runs relevant portable checks and prepares the runtime package; the
owner receives only the applicable small batch with exact version/build, prompts,
expected counts/visual results, reset/recovery and PASS/FAIL/BLOCKED reporting.
Portable tests, documented APIs and actual Allplan evidence are separate.
Record supported operations/builds, limits and the next action in the handoff.
Use `ready_for_owner_test` before runtime acceptance and `accepted_on_build` only
with evidence. Do not repeat accepted batches without a relevant change/defect.
