# Implementation stages

Validation follows the [shorter M3 test schedule](testing-policy.md): focused
checks during implementation, one full final-candidate run, change-dependent
CI and native checks for new/materially affected behavior. Explicit owner pauses
on testing take precedence; historic acceptance evidence remains unchanged.

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
Allplan 2026-1-7. [Acceptance and limits](validation-status.md).

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

Package **0.6.1**, audit profile **2.0.0**; [acceptance limits](validation-status.md).
The native fixture audit, public/host scope rejection and continued operation
pass. The dispatcher contains callback exceptions; the precise earlier CLR
crash cause remains unproven. [Audit contract](m2-audit-contract.md).

- **M2.1** Versioned schema for typed attributes/layers, values, uniqueness and tolerances; validate bound resources.
- **M2.2** `model_audit` with severity, evidence, distinct unchecked states and readable/structured reports.
- **M2.3** Findings tied to session/project/document/model references and deterministic finding IDs; file/mark/model-local box and center for inspection. Durable references and native highlight remain unverified.

**Exit gate (UAT-04):** demo returns exactly 5 findings on 5 columns, correct
uniqueness scope, explicit unavailable data and locatable targets; no writes.

## M3 — Controlled repairs and standards: closed within the retained test project

**Owner-selected bounded closure, 2026-10-12 Europe/Warsaw:**
[UAT mapping and support limits](m3-closure.md). M3.1–M3.4 are accepted only
within the recorded fixture scenarios; the [office-project roadmap](office-project-roadmap.md)
tracks wider capability and acceptance work.

Package **0.15.0** implements 1–32 reviewed existing string mark/status or layer changes on
Column roots in one explicit foreground file. Office-standard and rule-based
Apply/Revalidate/Recover reuse the executor, full-source/exception checks,
durable deduplication and audited readback.
[Current execution contract](m3-workflow-execution-contract.md).

[Bounded native acceptance](validation-status.md) covers the two single-target
workflow writes/readbacks, read-only replays, complete audits 5 → 4 → 3,
host survival, unchanged other elements and two-step Undo. Broader eligible
scope remains outside this gate. Layer/status preview, earlier two-target
execution/Redo recovery, restart invalidation/stale Apply rejection,
standard/selection no-op previews and explicit collision-aware mark previews
have separate bounded acceptance. Unchanged completed gates need no repetition.
0.13.0 adds bounded read-only inspection of invalidated evidence;
[bounded same-session native conflict gate](m3-conflict-acceptance-0.13.0.md) passed 12/12 steps and Undo/recovery.

Mark assignment and deterministic versioned-standard numbering are implemented;
[their bounded two-target native gate](m3-numbering-acceptance-0.12.0.md) passed
complete audits 3 → 0 → 3, readback, replay/no-op and two-step Undo/recovery.
[Controlled partial/unknown recovery](m3-recovery-acceptance-0.14.1.md) now has
bounded native PASS. Remaining native scope and manual UI active-plan conflict
are unaccepted and outside the narrowed milestone. Known UI editing cancelled
the host and must not be repeated unchanged. Journal maintenance, wider identity
guarantees and broader UAT move to office-project work; main integration remains
separate. Graphical labels, file moves and universal native properties are
conditional extensions.

- **M3.1** Shared preview/apply, stale checks, serialized writes, request identity, readback, partial outcomes and tested Undo limits.
- **M3.2** `fix_model_issues` for writable attributes/layers; data marks and graphical labels stay distinct.
- **M3.3** `apply_office_standard` and attribute/layer `rule_based_edit` reuse the same services.
- **M3.4** Persist/reconcile managed records where needed; prove retry deduplication and unknown-outcome recovery.

**Bounded exit gate met (UAT-05/UAT-06):** existing evidence verifies unchanged
preview, authorized fixture writes, layer/status repairs leaving 3 findings,
stale-plan rejection and excluded-peer source comparison, replay without repeat
writes, controlled unknown-result recovery and matching readback/re-audit/Undo.
Native manual UI active-plan conflicts are explicitly outside this narrowed gate;
the original broader gate is not retroactively labelled PASS.
**First fixture evaluation MVP = accepted M0–M3**, with versioned
install/update/restore and recorded support limits; office-project use remains planned.

## M4 — Native edits, frames and foundations

Prioritize **M4.1–M4.2** for the owner's requested wall fire-resistance and
storey-scoped column concrete-class workflows before frame/foundation generation.
The [office-project roadmap](office-project-roadmap.md) defines per-property
probes, writable profiles, identity, multi-file scope, batching and journal prerequisites.

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

## Controlled recovery evaluation — 0.14.1

The [explicit diagnostic stop](m3-recovery-contract.md) uses the normal durable
write-ahead marker after the first C03 setter, before readback or C04. It requires
a separate typed acknowledgement and the retained two-mark numbering fixture.
Ordinary Apply retains its guards; generated numbering writes follow spatial
assignment order. Recover/exact-ID replay never resume skipped targets.
The [bounded native gate](m3-recovery-acceptance-0.14.1.md) passed
13/13 + 6/6 + 6/6: controlled C03-only interruption, restart/reconciliation,
read-only replay/no-resume and owner Undo, with audits 3 → 2 → 3.
No repeat is required; broader crash/identity/scope guarantees remain open.

## Bounded selected-mark/journal acceptance — 0.15.0

[Native PASS / accepted_on_build](m3-selected-mark-acceptance-0.15.0.md):
13/13 + 6/6 steps, one rule_based_edit C04 S02 → S04 with excluded C02,
full audited-field/snapshot checks, read-only replay, healthy journal history
6 → 7 → 7 and owner-confirmed UI/Undo, audits 3 → 1 → 3. A has a stable,
owner-confirmed uninterrupted host; B uses another session with unspecified cause.
Leave/save the same copy after Undo. No repeat is requested. Broader 1–32-change
scope, journal rollover and cross-copy identity remain unaccepted.
[M3 is now closed within the retained fixture scope](m3-closure.md) by the
owner's later decision. No completed gate needs repetition; wider work follows
the [office-project roadmap](office-project-roadmap.md). Main integration is separate.
