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

## M2 — Audits and profile foundations

- **M2.1** Versioned schema for typed attributes/layers, values, uniqueness and tolerances; validate bound resources.
- **M2.2** `model_audit` with severity, evidence, distinct unchecked states and readable/structured reports.
- **M2.3** Findings tied to stable references; supported highlight or marks/file/location for inspection.

**Exit gate (UAT-04):** demo returns exactly 5 findings on 5 columns, correct
uniqueness scope, explicit unavailable data and locatable targets; no writes.

## M3 — Controlled repairs and standards: first MVP

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
