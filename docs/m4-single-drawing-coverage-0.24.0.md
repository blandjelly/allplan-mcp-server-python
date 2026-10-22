# M4 single-drawing coverage — current status through candidate 0.27.0

Updated 2026-10-22. This is implementation and verification coverage, not full
native acceptance. Earlier scoped owner observations remain in
[validation status](validation-status.md).

Candidate source `48e64b1a06bef005c26a143860d9257038cccde3` passed CI run
39822585188 (580 tests on Windows and 580 on Ubuntu, Python 3.12, plus package
job). The exact delivered fallback ZIP passed package verification; the CI ZIP
could not be transferred through the proxy. See the
[0.26.0 record](../evaluation-packages/0.26.0/README.md) for provenance and
verification artifacts. No owner observation existed at package delivery.
The later bounded owner observation is recorded below; full native acceptance
remains incomplete.

| Requested family / adapter | Current guarded route and owner boundary | Remaining native evidence |
| --- | --- | --- |
| Columns / Column | Typed attributes and exact existing organizational layer; model/view binding, exclusions, fresh readback, replay and no-op. | Only remaining W1 no-op/Undo gap; preserve accepted attributes. |
| Walls / Wall | Typed root attributes; organizational layer binds all direct WallTier owners with its own adapter. Single-tier native thickness/material read exists. Current layer IDs 0–65535 are valid; 0.26.0 fixes reading ID 0 and covers reviewed W1 plan/Apply from prior ID 0 in focused tests. 0.27.0 tightens material preservation to exactly one stable, direct WallTier lineage with no children; opening and all other child types fail closed with separate reasons. | Native layer owner/readback/Undo for unaccepted case; native material change remains unaccepted. The 0.27.0 preservation and diagnostic changes do not enable writes or substitute observed material for preservation evidence. |
| Beams / Beam, SkeletonBeam | Typed attributes and organizational layer, exact target resolution; unrelated broken hierarchies do not redirect the owner. | Family/build-specific UI/readback/Undo; fakes and API availability are separate. |
| Slabs / Slab | Read-only direct identity probe; only standalone Slab permits typed attributes/layer with bound ancestry. | Resolve the owner's two Slab/MultiSlab results read-only. No new attribute trial on previously accepted targets. |
| Aggregate slab / MultiSlab | Direct parent/child evidence; all aggregate writes blocked pending an explicit property owner. Slab children are blocked independently of the type filter. | Explicit owner contract before enabling any aggregate/tier write. |
| Doors and windows / WindowDoor | Structural identity probe keeps parents visible. Semantic family is `opening`; optional `opening_kind` resolves `door`/`window` only through the loaded DoorOpeningElement/WindowOpeningElement classes. Unknown classes stay not_checked. | Separate native door/window, opening/inserted-object ownership and variant evidence. Owner confirms the 0.25.0 run and one scoped subtree deletion PASS; broader typed-delete coverage and Undo remain unobserved. Do not repeat that deletion. |

`test_edit_ownership.py` adds parent/child blocking, standalone-slab exact
targets despite equal geometry, late reparenting, unreadable ancestry,
executor/final-setter guards and unknown readback without a repeated setter.
W1 checks cover Column, Beam, SkeletonBeam, standalone Slab and WindowDoor
adapters; Wall tier ownership has separate existing tests. These are native
fakes. They establish neither native family acceptance nor Undo behavior.

| Value family | Current binding | Remaining work |
| --- | --- | --- |
| Text, Integer, Double, Boolean | Exact loaded SDK member, compatible scalar/readback; no display-text coercion. | Target-specific native evidence, preserving previously accepted outcomes. |
| Integer + CheckBox | Targeted SDK CheckBox metadata, exact false/true → 0/1 binding. | Family/definition-specific native UI/readback/Undo. |
| Enum | Exact requested label → key → label → key round trip, label setter and exact readback. | Native codec evidence for that exact definition; no broad catalog enumeration. |
| Date, vector, byte, other non-scalar values | Explicitly unsupported and blocked before target enumeration; no scalar substitution. `AttributeDate` is a documented SDK payload for `SetAttributes`, but an accepted payload for the existing `ElementsAttributeService.ChangeAttribute` route and its exact readback are missing. | Implement/document the exact existing-adapter setter payload and fresh readback codec before a narrow native trial. |

## Native selection and material are separate gaps

`model_selection(action=select)` returns `status=unsupported`, starts no UI
calls, and never falls back to highlighting. The official **2026** example
[MultiSelection.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/e816b120038ca121b51d80b78f22da561b5c6fda/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/MultiSelection.py#L220)
starts an interactive `InputFunctionStarter.StartElementSelect` operation and
reads user-selected elements with `PostElementSelection.GetSelectedElements`.
It demonstrates user-driven selection only, not setting a query's exact adapter list as the native UI
selection. Integrating that asynchronous user-input lifecycle with this host,
including cancel/restart and exact selection readback, remains implementation
work; an API symbol alone is not support.

The official **2026**
[ModifyWall.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/e816b120038ca121b51d80b78f22da561b5c6fda/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifyWall.py#L285)
demonstrates mutating tiers from existing `wall_ele.Properties`, reattaching
with `SetProperties(wall_props)` and submitting `ModifyElements` on cancel.
This resolves the reattachment question in the earlier API note for that
example. It does not demonstrate the requested material change, project
catalog binding, geometry/other-tier preservation or Undo. A dedicated material
adapter still needs those invariants, typed immutable binding, write-ahead
journaling, revalidation and exact native material readback. The current
`native_material` route is experimental and unaccepted natively; its 0.25.0
owner attempt was blocked before a setter because safe edit evidence was
unavailable. Candidate 0.26.0 diagnoses the missing property; it does not
repair or enable the setter. In the 2026 API, `ArchBaseProperties.Surface` is a
string and Filling/Hatch/Pattern values are integers; these are typed scalar
properties, not opaque SDK objects. The candidate's `Axis`, `PlaneReferences`,
and `SurfaceElementProperties` values provide bounded `repr` drift evidence
only, not exhaustive preservation codecs. A material attribute, surface or
organizational layer never substitutes for native material.

## 0.27.0 candidate scope (CI pending; no new native acceptance)

The attribute resolver checks a bounded set of spelling variants: supplied
name, trimmed NFC, first-character uppercase, all uppercase and all lowercase.
It verifies the actual project name/ID round trip for every successful
variant, compares names by NFC casefold and rejects results that map to
multiple IDs. The `attribute_name` probe retains exact lookup first and uses
the shared fallback only on `ValueError`/`TypeError` lookup miss; `model_edit`
bindings use the shared resolver. No fuzzy search or project catalog scan is
added. This is intended to address the lowercase `mcp_qa_mark` lookup while
preserving the canonical project ID; native verification is pending.

For native Wall material, preview now reports a readable old string separately
from operation eligibility. `criteria.required_field_failures` lists only
unreadable required destination fields; predicate/criterion failures remain in
`report.criterion_failures`. It may be empty when the operation remains
blocked. `criteria.operation_eligibility_failures` currently carries Wall
native-material preservation blockers and their observation. A Wall is
eligible for preservation only with exactly one
`WallTier_TypeUUID` child, lineage `[tier, Wall root]`, no tier children, and
stable bounded enumeration. `WindowDoor_TypeUUID` uses
`wall_material_openings_unsupported`; every other child type uses
`wall_material_child_type_unsupported`. Stable bounded component read errors
do not expose exception text. Post-write observation still requires the full
preservation snapshot. No new material write or native Undo is accepted.

The supplied 0.26.0 conversation log is recorded in the
[scoped observation](test-results/m4-owner-observation-0.26.0-2026-10-22.md):
26/26 identities enumerated with 7 `observed` and 19 `not_checked`; two
confirmed layer changes/readbacks on one Column; and one Wall highlight
submission without a logged view result or native selected-element count.
The assistant's stated opening blocker conflicts with the later empty `blocked`
arrays and has no raw diagnostic, so the cause is unverified. No material
change, delete, no-op or Undo was recorded. See the [0.27.0 trial](m4-single-drawing-0.27.0.pl.md)
for the strictly limited next native evidence.

## Priority status

1. **Limited journal-cleanup PASS remains accepted.** The 0.23.0 preview and
   confirmed archival are retained in the owner record; do not repeat that
   trial. It does not close broader single-drawing acceptance.
2. **Identity inventory is not field ownership.** Candidate 0.26.0 adds a
   bounded `drawing_identity` inventory across pages. Model/view UUID, lineage
   and native type do not prove attribute/material/layer ownership or resolve
   the owner's Slab/MultiSlab relationship.
3. **Layer 0 is handled in read and reviewed W1 plan/Apply.** Legal IDs include
   0 through 65535; focused tests cover a reviewed W1 change from old ID 0.
   This does not establish that ID 0 caused the earlier `repair_conflict`;
   its raw trace is unavailable. Native W1 no-op/Undo remains missing.
4. **Selection unsupported; deletion limited; material unaccepted.** Official
   Allplan 2026 APIs show interactive user selection only. The owner confirms
   the 0.25.0 run and its scoped single-subtree deletion PASS; do not repeat
   that successful deletion. Broader family/Undo evidence remains missing.
   Candidate 0.26.0 diagnoses blocked delete/material properties; it does not
   repair the native blockers, enable the material setter or relax any guard.
5. **Date/vector writes unsupported on the existing adapter.** `AttributeDate`
   exists as a typed SDK payload for `SetAttributes`, but an accepted payload
   for `ElementsAttributeService.ChangeAttribute` and exact fresh readback are
   missing. Vector and other non-scalar routes likewise require an exact
   adapter contract; SDK representations alone do not provide one.

All five priorities remain open where their acceptance conditions are unmet.
See the [0.26.0 bounded trial](m4-single-drawing-0.26.0.pl.md) and
[development plan](office-editing-development-plan.pl.md).
