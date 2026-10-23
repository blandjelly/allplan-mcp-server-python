# M4 single-drawing coverage — current status through candidate 0.30.0

Updated 2026-10-23. This is implementation and verification coverage, not full
native acceptance. Candidate 0.30.0 source commit
`9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6` passed full
[CI run 39993048110](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39993048110):
622 tests on Windows and 622 on Ubuntu Python 3.12, plus the package job. The
original CI artifact was not delivered after one normal-proxy transfer failed
before HTTP; one fallback build from clean exact source (`source_modified=false`)
passed exact ZIP verification on its first attempt: 196 payload files and 43
bridge hashes, SHA-256
`78b7b24c98749ebbd28814f84d70a2fc9cbeab80b477b9fd1585e5c10e63af8e`. Native
trial has not been run. See the [0.30.0 candidate record](../evaluation-packages/0.30.0/README.md),
[verified ZIP](../evaluation-packages/0.30.0/allplan-mcp-0.30.0-windows-evaluation.zip),
[verification result](../evaluation-packages/0.30.0/package-verification.json)
and [verification log](../evaluation-packages/0.30.0/package-verification.log).
Its partial
`attribute_evidence` probe and no-op evidence contract do not add date/vector
setters, native selection, or Slab/MultiSlab field ownership. The combined
[0.30.0 trial plan](m4-single-drawing-0.30.0.pl.md) covers priorities 1–5 in
one session; blocked work and missing fixtures remain explicit. Full completion
remains the goal and is blocked until those owner, payload and selection
contracts are established. The owner
reports PASS for all steps of the 0.29.0 Column group-delete/Undo trial; its
scope and evidence limits are recorded in the
[0.29.0 observation](test-results/m4-owner-observation-0.29.0-2026-10-23.md).
Scoped 0.27.0 owner-reported observations are retained in
[this observation](test-results/m4-owner-observation-0.27.0-2026-10-23.md)
and [validation status](validation-status.md). Candidate 0.28.0 source and its
exact fallback ZIP are verified. Its limited owner trial reported PASS for
preview/delete/absence readback, but one Undo restored only one of three
Columns. That historical grouped-Undo failure is superseded for the tested
scope by the owner-reported 0.29.0 PASS.

Final 0.28.0 source `b59ef15d9bfd4dfb42476b240e31b5b300268d2d` is on PR #26
targeting `develop/m4`. CI run
[39871551499](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39871551499)
passed 601 Windows and 601 Ubuntu Python 3.12 tests and the package job; 170
unique focused checks passed. The original CI artifact was not delivered after
a normal-proxy transfer failed with `URLError` before an HTTP status. One
fallback build from clean exact source (`source_modified=false`) passed exact
ZIP verification on the first attempt: 186 payload files, 42 bridge hashes,
SHA-256 `74099ec341cdf8b2bc87def42487fafbbbcdb963ec6f4b8859a412f7b6d064ed`.
See the [0.28.0 evaluation record](../evaluation-packages/0.28.0/README.md).

Final 0.27.0 source `e62a50c9c6c6b51978b6f1a55f9d9978eee5b1c3`, merged as
`23b8b2591d7be0721fe7a5651379408e7a2f5e76`, passed full CI
run [39841530841](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39841530841):
593 tests on each Windows and Ubuntu Python 3.12 job, plus package job. The
single exact fallback ZIP verification passed from clean source
(`source_modified=false`): 183 payload files; SHA-256
`eab80cd2c907e7fd90ba733f4f8d1335f097986b938c74ccdda6bf3382cdaa30`; 42
bridge hashes; registration, frozen sync/import, upgrade from and restore to
0.26.0; and journal/trace/log/archive marker preservation. The original CI ZIP
was not delivered. See the [0.27.0 package record](../evaluation-packages/0.27.0/README.md).
The separate focused record reports 143 unique
affected/dependent tests across iterations. The later owner-reported 0.27.0
trial is limited and is not tied to this exact package; priorities 1–5 remain
partially open as described below. Historical CI logs remain dated 22 October.

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
| Columns / Column | Typed attributes and exact existing organizational layer; model/view binding, exclusions, fresh readback, replay and no-op. Candidate 0.28.0 delete matching uses drawing/model/type identity while preserving actual parent view UUID edges and the exact selected target view UUID. Candidate 0.29.0 expands one reviewed plan to a plural native delete call. | Owner reports PASS for all steps of the 0.29.0 trial: three W1 Columns in drawing 101 were deleted, a fresh scan reported all three Columns and their attribute containers absent, and one UI Undo restored all three Columns. This meets the grouped-Undo repair goal for the tested operation. The log lacks raw MCP responses, target UUIDs and installed ZIP manifest; Undo was owner-observed, with tool result `undo: not_checked` and no automatic post-Undo readback. The 0.28.0 one-of-three Undo remains historical. No explicit W1 no-op/zero-setter evidence. |
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

## 0.27.0 candidate scope (CI and package verification passed; later limited owner report)

The 0.27.0 attribute resolver checks a bounded set of spelling variants: supplied
name, trimmed NFC, first-character uppercase, all uppercase and all lowercase.
It verifies the actual project name/ID round trip for every successful
variant, compares names by NFC casefold and rejects results that map to
multiple IDs. The `attribute_name` probe retains exact lookup first and uses
the shared fallback only on `ValueError`/`TypeError` lookup miss; `model_edit`
bindings use the shared resolver. No fuzzy search or project catalog scan is
added. This is intended to address the lowercase `mcp_qa_mark` lookup while
preserving the canonical project ID. The later limited 0.27.0 owner report records
a PASS for the lowercase lookup; it is not bound to this exact package.

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
preservation snapshot. No native material write is accepted.

The 0.27.0 owner report and attached chat log are recorded in the
[scoped observation](test-results/m4-owner-observation-0.27.0-2026-10-23.md):
reported PASS for lowercase attribute lookup and material diagnostics; reported
W1 read/write with one element per UI Undo; one Wall 240 mm subtree deletion
with five descendants absent on a fresh complete scan; and two Beam readbacks
on W1. The log also reports three W1 Columns blocked at preview by
`component_child_owner_mismatch` and a Slab/MultiSlab parent-lineage conflict.
There is no explicit no-op/zero-setter result, no raw MCP payload, exact
installed manifest or Allplan build ID. The results are not tied to the exact
0.27.0 ZIP. Do not repeat accepted targets or actions. The earlier supplied
0.26.0 conversation log is recorded in the
[0.26.0 scoped observation](test-results/m4-owner-observation-0.26.0-2026-10-22.md):
26/26 identities enumerated with 7 `observed` and 19 `not_checked`; two
confirmed layer changes/readbacks on one Column; and one Wall highlight
submission without a logged view result or native selected-element count.
The assistant's stated opening blocker conflicts with the later empty `blocked`
arrays and has no raw diagnostic, so the cause is unverified. No material
change, delete, no-op or Undo was recorded in that 0.26.0 log. The later
0.28.0 Column trial and its outcome are recorded in the
[0.28.0 trial record](m4-single-drawing-0.28.0.pl.md); its grouped-Undo failure
was superseded by the limited 0.29.0 owner-reported PASS above. The next
combined session is [0.30.0](m4-single-drawing-0.30.0.pl.md).

## Priority status

1. **Implemented and accepted:** bounded journal cleanup and the 0.23.0
   archival scope. Candidate 0.28.0 raises limits to 512 active records, 1 MiB
   per record, 8 MiB active trace, 32 MiB trace-inspection limit and an archive
   inventory bounded at 1 GiB / 1024 files. Focused checks, full CI, and exact
   ZIP verification passed. Native restart/replay is unobserved. Unresolved
   and unverifiable records remain protected.
2. **Implemented:** structural identity inventory and fail-closed ownership
   guards. **Unresolved:** the 0.27.0 log retains model/view identities and a
   parent-lineage conflict for the Slab child, but does not establish field
   ownership. Candidate 0.30.0 adds exact requested-ID `attribute_evidence`
   with separate ancestry/children/value reads; even complete evidence does not
   establish a field owner. Keep unresolved writes blocked.
3. **Implemented:** layer 0 read and reviewed W1 plan/Apply. **Limited
   owner-reported native PASS:** W1 read/write works, with one changed element
   reverted per UI Undo step. Earlier reports lack explicit no-op/zero-setter
   evidence. Candidate 0.30.0 implements bounded fresh `no_op_evidence` and
   revalidation with zero setters, but this candidate behavior has no recorded
   native trial result yet. No-op has no Apply path.
4. **Implemented in candidate 0.28.0/0.29.0:** typed subtree delete matches
   owner edges by drawing/model/type identity while preserving actual parent
   view UUIDs on bound child/descendant edges and the selected target's exact
   view UUID; 0.29.0 sends the reviewed group in one plural native call.
   Focused checks, full CI, and exact ZIP verification passed. The owner reports
   PASS for all steps of the 0.29.0 trial, including one UI Undo restoring all
   three Columns after the fresh absence scan. This meets the grouped-Undo
   repair goal for that tested operation. The log lacks raw MCP responses,
   target UUIDs and installed ZIP manifest; Undo was owner-observed, and the
   tool reported `undo: not_checked` without automatic post-Undo readback.
   See the [0.29.0 observation](test-results/m4-owner-observation-0.29.0-2026-10-23.md).
   The 0.28.0 one-of-three Undo remains historical. Native material has no
   owner acceptance; its existing guarded experimental evaluation setter may
   be exercised in the 0.30.0 session when an exact target passes every Apply
   guard. Native selection remains unsupported.
5. **Implemented:** scalar/Enum contracts and family/value inventory. The
   0.27.0 lowercase lookup and material diagnostics have reported PASS, but
   date/vector/object codecs and per-family owner, value roundtrip and Undo
   evidence remain open. Candidate 0.30.0 can inspect exact observed IDs and
   SDK type bindings through `attribute_evidence`; it adds no date/vector
   setter or codec, and unknown native objects remain type-only `not_checked`.
