# Implementation plan

Current acceptance and limits: [validation status](validation-status.md).
Use the [testing policy](testing-policy.md); stage IDs remain stable.

## Accepted fixture MVP

| Stage/tasks | Delivered scope | Gate |
| --- | --- | --- |
| M0.1–M0.5 | Runtime discovery, recursive installation/integrity/restore, health/version/box tools, host lifecycle and Windows package. | UAT-00/01 accepted, package 0.1.2. |
| M1.1–M1.4 | Context/identity/geometry, typed query, cached full selections/pages/summaries, metadata/profile binding and demo fixture. | UAT-02/03 accepted within the bounded read contract, package 0.5.3. |
| M2.1–M2.3 | Typed audit profile, fresh read-only reports, coverage/evidence and locatable deterministic findings. | UAT-04 accepted, package 0.6.1. |
| M3.1–M3.4 | Shared preview/apply/revalidate, layer/status/mark repairs and demo standards, stale guards, journal deduplication/readback and controlled unknown-result recovery. | Bounded UAT-05/06 accepted by the owner's test-project scope decision, package 0.15.0. |

M3 closure covers recorded one-/two-change scenarios in foreground file 101 of
the original copy. It is a fixture evaluation MVP. Manual UI active-plan conflicts,
wider identity/journal guarantees and arbitrary 1–32-change plans remain outside
acceptance; they are not silently declared complete by closing this stage.

## M4 — Property discovery, selection and native edits

Follow the [owner's editing development plan](office-editing-development-plan.pl.md),
K1–K7. First: columns without fire resistance → existing W1 organizational layer.
Next: walls with native total thickness <240 mm → native concrete material C35,
with a separate explicitly requested attribute variant. Property ownership,
project metadata and actual resources must resolve before enabling new edits.

**M4.1a / early M4.1b:** the first 0.16.0 discovery crashed natively and is blocked.
0.16.1 isolates one Column read with durable trace; metadata/enum/UI stages remain pending.
Native selection is BLOCKED by the current interactor; K1/K2 are not closed.
[Native observation guide](m4-isolated-probe-owner-test.pl.md). The bounded
Column workflow below advances K3 without closing broad discovery or native selection.

**M4.1 criterion-based Column layer workflow:** 0.17.1 established the exact
fire-resistance attribute binding and two W1 writes, but its highlight request
excluded a matching Column already on W1. 0.17.2 changes the plan contract to
hash-bound `highlight_targets` for both `change` and `no_op`, with `changes`
containing only `set_layer` operations. A complete supported plan can highlight
all matches even when every match is already on W1; no-op plans do not offer
Apply. Unknown criteria still block highlighting and writes, and more than 32
changes remain blocked. The separate 0.17.2 package has 275 portable tests, six
CI jobs and exact package verification recorded in its unchanged
[delivery README](../evaluation-packages/0.17.2/README.md); the owner later
observed its no-op highlight behavior through the same Column handler in
0.18.1 and confirmed UI visibility. This supports only scoped highlight
acceptance, without writes or complete M4 acceptance. See the
[0.18.1 observation report](m4-native-observation-0.18.1-2026-10-17.md),
[0.17.2 walkthrough](m4-column-layer-0.17.2.pl.md) and
[0.17.1 observation](m4-column-layer-observation-0.17.1.md).

**M4.1a isolated wall-property read, 0.18.0:** the candidate adds a single
`wall_sample` phase and **M4 Wall Properties.cmd**. Its source, CI and package
checks passed ([evidence](../evaluation-packages/0.18.0/README.md)). A later
0.18.1 owner request was blocked before native read with
`probe_scope_unavailable` (“Wall sample has ambiguous adapter representations”);
no sample was returned and the cause is not established by the observation.
See the [0.18.1 observation report](m4-native-observation-0.18.1-2026-10-17.md).
The intended observation is limited to one Wall in foreground file
101. M1 uses required type/identity fields plus display name/file state, counts
matched Wall roots, and reads no attributes or geometry. The host selects one
exact UUID (or the first Wall in UUID order), verifies a native `WallElement`,
reads `Properties` and `TierCount`, and proceeds to tier 1 only when
`TierCount == 1`. It reads positive finite `.Thickness` and bounded raw
`.Material` only from that sample; the predicate
`sample.criterion.matches_assuming_native_mm` uses an explicitly unverified API
millimetre assumption. It does not read thickness from every matched Wall or read
metadata/enums, highlight, or write. Read acceptance is required before any
material write support is enabled. The 0.18.0 observation can be performed
without first testing 0.17.2. See the [wall guide](m4-wall-properties-0.18.0.pl.md)
and the pinned official SDK example at
[ModifyWall.py, 8e2c252477e20bc9afac8918f78a8eeabd473a81](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifyWall.py).

Source-only preparation for **K4 / M4.2b** adds an offline analyzer for one saved
wall report, with strict threshold/exact-label/exclusion semantics and explicit
missing-evidence states. It does not construct an executable ChangePlan or close
native read/material-binding/write gates. [Contract and usage](m4-wall-report-analysis.md).

- **M4.1:** Probe ordinary columns/beams versus Structural Framing and wall
  materials/attributes; establish read/write support per build, type and property.
- **M4.2:** Extend `rule_based_edit` only through proven native-property/attribute
  adapters, preserving dependencies/exceptions; expand storey and multi-file scope.
- **M4.3:** `generate_structural_frame` from explicit grids/elevations,
  native columns/beams and owned generation keys; detect manual-edit conflicts.
- **M4.4:** `generate_foundations_from_structure`: native pads under selected
  base columns, then straight-wall strips, with profile dimensions/elevations.

UAT-07–09: native types/counts/geometry/levels/links/exceptions and repeat
update/no-op/conflict behavior. Never silently replace manual work.
Generation M4.3/M4.4 and subsequent layouts/exports are deferred until the editing
workflows in K1–K6 are usable and accepted; the task IDs below remain historical.

## M5 — Layouts and issue exports

- **M5.1:** Probe one-sheet insertion, paper scale/crop/margins, title blocks
  and PDF/DWG; native revisions require separate evidence.
- **M5.2:** `populate_layouts` using prepared files/templates, reserved areas,
  numbering, occupied-sheet policy and deterministic overflow.
- **M5.3:** `documentation_audit` for declared requirements with explicit
  unchecked/manual-review states.
- **M5.4:** `prepare_issue_package` with preflight, issue metadata, a new output
  directory, exact verified file/hash list and partial-export recovery.

UAT-10/12: correct contents/scales/fields and readable PDF/DWG; critical audit
failures block readiness, existing issues stay preserved. Export recovery is
separate from model Undo. M5 may precede generation work in M4.

## M6 — Managed documentation workflow

- **M6.1:** Probe UVS create/update, labels/dimensions and source changes.
- **M6.2:** `create_documentation_package`: one foundation plan, two sections,
  dimension chains, marks and a schedule with declared checked quantities.
- **M6.3:** Owned roles/dependencies, missing/stale audits and preservation
  of manual adjustments or explicit conflict.
- **M6.4:** Compose with M5 layouts/exports without duplicate content/numbering.

UAT-11: initial/repeat/source-change behavior, missing dimension detection and
manual-edit preservation/conflict. General third-party drawing completeness is deferred.

## M7 — Coordination openings

- **M7.1:** Feasibility spike: one pipe/wall and one pipe/slab crossing with
  real host modification/link and repeat prevention.
- **M7.2:** `generate_coordination_openings`: proven crossings, geometric
  intersection/clearance, source links and edge/support exceptions.
- **M7.3:** Imports, oblique/merged openings and documentation only with demand/evidence.
- **M7.4:** Probe native revisions, building structure and file moves separately.

UAT-13: correct modified hosts/clearances, no duplicate openings and explicit
ambiguity/unsupported cases. DN is not outer/insulation geometry; a spike is not
production acceptance. Generic-solid fallbacks need explicit agreement/labels;
structural/geotechnical design calculations remain outside tool scope.
