# M4 single-drawing coverage — current status for candidate 0.31.0

Updated 2026-10-23. This is implementation and verification coverage, not full
native acceptance. The latest completed candidate 0.30.0 source commit
`9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6` passed full
[CI run 39993048110](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39993048110):
622 tests on Windows and 622 on Ubuntu Python 3.12, plus the package job. Its
fallback ZIP from clean exact source passed verification: 196 payload files,
43 bridge hashes, SHA-256
`78b7b24c98749ebbd28814f84d70a2fc9cbeab80b477b9fd1585e5c10e63af8e`.

The owner later reported 0.30.0 trials 1, 2, 3 and 5 as PASS and trial 4's
Wall native-material preview as FAIL before Apply. The supplied raw log covers
trial 5 only: four scalar writes (Column text/integer/real and Wall text) each
had typed readback and one UI Undo/restoration read. Trial 4 had two blocked
previews with zero changes and setters; its owner-reported symptoms and limits
are in the [scoped observation](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-owner-observation-0.30.0-2026-10-23.md).
These outcomes are not bound to the exact ZIP because its installed manifest
was not supplied. See the [0.30.0 delivery record](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/evaluation-packages/0.30.0/README.md),
[trial 5 log](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md)
and [persisted Apply requests](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trial-apply-requests.jsonl).

Candidate 0.31.0 is on `fix/m4-material-owner-0.31.0`, source commit
`0f99863b7c11143d9f14ca12a1027aad5b009195`, with
[PR #29 to `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/29).
**87 unique focused checks passed**: 86 affected/dependent checks and one
package version/lock check. Both full CI unittest jobs passed on Windows and
Ubuntu Python 3.12 in
[run 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481).
Run 40012042481 passed 625 Ubuntu Python 3.12.15 tests, 625 Windows Python
3.12.10 tests, and the package job. Original artifact 12527730616 could not be
retrieved: the connector returned only a File Service ID and normal-proxy
download was forbidden. One fallback ZIP from clean exact source
(`source_modified=false`) passed verification: 201 payload files, 43 bridge
hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`. See the
[verification record](../evaluation-packages/0.31.0/package-verification.json),
[log](../evaluation-packages/0.31.0/package-verification.log) and
[verified ZIP](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip).
Only the native material trial remains for this candidate.
Focused tests reproduce and fix a same-model alternate-parent
wrapper defect in the Wall preservation snapshot. The exact native branch for
the first 0.30.0 diagnostic is unproven without raw lineage/children data. The
second Wall-with-opening diagnostic `component_child_owner_mismatch` remains
unresolved. See the [0.31.0 evaluation record](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/evaluation-packages/0.31.0/README.md),
[API note](m4-editing-api-0.31.0.md) and
[narrow native trial plan](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/m4-single-drawing-0.31.0.pl.md).

The 0.30.0 `attribute_evidence` probe and no-op evidence contract do not add
date/vector setters, native selection, or Slab/MultiSlab field ownership.
Neither candidate closes priorities 1–5. Runtime/native owner, payload and
selection contracts remain prerequisites to full completion. Earlier accepted
scope and historical evidence below remain in force. The owner reports PASS for
all steps of the 0.29.0 Column grouped-delete/Undo trial; its scope and evidence
limits are recorded in the [0.29.0 observation](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-owner-observation-0.29.0-2026-10-23.md).

Final 0.28.0 source `b59ef15d9bfd4dfb42476b240e31b5b300268d2d` is on PR #26
targeting `develop/m4`. CI run
[39871551499](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39871551499)
passed 601 Windows and 601 Ubuntu Python 3.12 tests and the package job; 170
unique focused checks passed. The original CI artifact was not delivered after
a normal-proxy transfer failed with `URLError` before an HTTP status. One
fallback build from clean exact source (`source_modified=false`) passed exact
ZIP verification on the first attempt: 186 payload files, 42 bridge hashes,
SHA-256 `74099ec341cdf8b2bc87def42487fafbbbcdb963ec6f4b8859a412f7b6d064ed`.
See the [0.28.0 evaluation record](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/evaluation-packages/0.28.0/README.md).

Final 0.27.0 source `e62a50c9c6c6b51978b6f1a55f9d9978eee5b1c3`, merged as
`23b8b2591d7be0721fe7a5651379408e7a2f5e76`, passed full CI
run [39841530841](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39841530841):
593 tests on each Windows and Ubuntu Python 3.12 job, plus package job. The
single exact fallback ZIP verification passed from clean source
(`source_modified=false`): 183 payload files; SHA-256
`eab80cd2c907e7fd90ba733f4f8d1335f097986b938c74ccdda6bf3382cdaa30`; 42
bridge hashes; registration, frozen sync/import, upgrade from and restore to
0.26.0; and journal/trace/log/archive marker preservation. The original CI ZIP
was not delivered. See the [0.27.0 package record](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/evaluation-packages/0.27.0/README.md).
The separate focused record reports 143 unique
affected/dependent tests across iterations. The later owner-reported 0.27.0
trial is limited and is not tied to this exact package; priorities 1–5 remain
partially open as described below. Historical CI logs remain dated 22 October.

Candidate source `48e64b1a06bef005c26a143860d9257038cccde3` passed CI run
39822585188 (580 tests on Windows and 580 on Ubuntu, Python 3.12, plus package
job). The exact delivered fallback ZIP passed package verification; the CI ZIP
could not be transferred through the proxy. See the
[0.26.0 record](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/evaluation-packages/0.26.0/README.md) for provenance and
verification artifacts. No owner observation existed at package delivery.
The later bounded owner observation is recorded below; full native acceptance
remains incomplete.

| Requested family / adapter | Current guarded route and owner boundary | Remaining native evidence |
| --- | --- | --- |
| Columns / Column | Typed attributes and exact existing organizational layer; model/view binding, exclusions, fresh readback, replay and no-op. Candidate 0.28.0 delete matching uses drawing/model/type identity while preserving actual parent view UUID edges and the exact selected target view UUID. Candidate 0.29.0 expands one reviewed plan to a plural native delete call. Trial 5 of 0.30.0 confirms Column text, integer and real attribute writes with fresh typed readback and UI Undo/restoration read. | Owner reports PASS for all steps of the 0.29.0 trial: three W1 Columns in drawing 101 were deleted, a fresh scan reported all three Columns and their attribute containers absent, and one UI Undo restored all three Columns. This meets the grouped-Undo repair goal for the tested operation. The log lacks raw MCP responses, target UUIDs and installed ZIP manifest; Undo was owner-observed, with tool result `undo: not_checked` and no automatic post-Undo readback. The 0.28.0 one-of-three Undo remains historical. Trial 3 in 0.30.0 is owner-reported PASS for W1 no-op; its detailed raw response was not supplied. |
| Walls / Wall | Typed root attributes; organizational layer binds all direct WallTier owners with its own adapter. Single-tier native thickness/material read exists. Current layer IDs 0–65535 are valid; 0.26.0 fixes reading ID 0 and covers reviewed W1 plan/Apply from prior ID 0 in focused tests. The 0.27.0 material guard requires one direct WallTier and blocks openings/other children. Candidate 0.31.0 compares a tier parent by drawing/model/type identity across view wrappers and binds the actual observed parent edge; its selected Wall target remains exact-view bound. | Trial 4 of 0.30.0 failed closed before Apply: the `Żelbet` preview reported `native_material_preservation_unavailable` / `wall_material_tier_hierarchy_unsupported`; a Wall with opening reported `component_child_owner_mismatch`. Both had zero changes/setters and no Apply. The first native branch is unproven without raw lineage/children data; the opening cause is unresolved. Candidate 0.31.0 has 87 focused checks passed, full Windows/Ubuntu CI passed, and its exact fallback ZIP passed verification. The native material trial remains pending; native material remains unaccepted. |
| Beams / Beam, SkeletonBeam | Typed attributes and organizational layer, exact target resolution; unrelated broken hierarchies do not redirect the owner. | Trial 5's Beam attribute read was blocked by `probe_scope_unavailable`; no Beam write was attempted. Family/build-specific UI/readback/Undo remains unaccepted. |
| Slabs / Slab | Read-only direct identity probe; only standalone Slab permits typed attributes/layer with bound ancestry. Trial 2 in 0.30.0 is owner-reported PASS for identity/evidence collection. | Resolve the conflicting Slab/MultiSlab ownership read-only. Trial 5 had no standalone Slab fixture. The SDK `ModifySlab.py` example does not establish M4 project-attribute ownership. Keep related writes blocked. |
| Aggregate slab / MultiSlab | Direct parent/child evidence; 0.30.0 adds separate requested-ID value/representation evidence. All aggregate writes remain blocked. | Trial 2 reported identity/evidence PASS but does not establish field owner. Explicit owner contract and native validation are required before aggregate/tier writes. |
| Doors and windows / WindowDoor | Structural identity probe keeps parents visible. Semantic family is `opening`; optional `opening_kind` resolves `door`/`window` only through the loaded DoorOpeningElement/WindowOpeningElement classes. Unknown classes stay not_checked. | Trial 5 opening attribute-list read was blocked; no opening write was attempted. The separate 0.30.0 Wall-with-opening material preview returned `component_child_owner_mismatch`; its cause remains unresolved. Native door/window ownership and variant evidence remain open. Owner confirms the 0.25.0 run and one scoped subtree deletion PASS; do not repeat that deletion. |

`test_edit_ownership.py` adds parent/child blocking, standalone-slab exact
targets despite equal geometry, late reparenting, unreadable ancestry,
executor/final-setter guards and unknown readback without a repeated setter.
W1 checks cover Column, Beam, SkeletonBeam, standalone Slab and WindowDoor
adapters; Wall tier ownership has separate existing tests. These are native
fakes. They establish neither native family acceptance nor Undo behavior.

| Value family | Current binding | Remaining work |
| --- | --- | --- |
| Text, Integer, Double, Boolean | Exact loaded SDK member, compatible scalar/readback; no display-text coercion. Trial 5 confirms text/integer/real writes on Column and text on Wall, each with typed readback and Undo/restoration read. | No Boolean fixture was observed; Integer 0/1 fields were not treated as Boolean. Other family/type pairs need their own evidence. |
| Integer + CheckBox | Targeted SDK CheckBox metadata, exact false/true → 0/1 binding. | Family/definition-specific native UI/readback/Undo. |
| Enum | Exact requested label → key → label → key round trip, label setter and exact readback. | Trial 5's Column `Status` (ID 49) was undefined; no label was guessed or written. Native codec evidence for an exact definition remains open. |
| Date, vector, byte, other non-scalar values | Explicitly unsupported and blocked before target enumeration; no scalar substitution. `AttributeDate` is a documented SDK payload for `SetAttributes`, but an accepted payload for the existing `ElementsAttributeService.ChangeAttributes` route and its exact readback are missing. | Implement/document the exact existing-adapter setter payload and fresh readback codec before a narrow native trial. |

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

The 0.30.0 owner trial later reported two material previews blocked before Apply
with zero changes/setters: the first reported
`native_material_preservation_unavailable` / `wall_material_tier_hierarchy_unsupported`,
and the opening Wall reported `component_child_owner_mismatch`. Raw hierarchy
responses were not supplied, so the exact cause of the first result is not
established; the opening cause remains unresolved. Candidate 0.31.0 fixes the
same-model alternate-wrapper defect reproduced by focused tests (87 unique
focused checks passed), while preserving exact selected-target identity and
all shape guards. Full Windows/Ubuntu CI and exact fallback ZIP verification
passed; the original CI artifact was unavailable. The native retest remains
pending.

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
[scoped observation](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-owner-observation-0.27.0-2026-10-23.md):
reported PASS for lowercase attribute lookup and material diagnostics; reported
W1 read/write with one element per UI Undo; one Wall 240 mm subtree deletion
with five descendants absent on a fresh complete scan; and two Beam readbacks
on W1. The log also reports three W1 Columns blocked at preview by
`component_child_owner_mismatch` and a Slab/MultiSlab parent-lineage conflict.
There is no explicit no-op/zero-setter result, no raw MCP payload, exact
installed manifest or Allplan build ID. The results are not tied to the exact
0.27.0 ZIP. Do not repeat accepted targets or actions. The earlier supplied
0.26.0 conversation log is recorded in the
[0.26.0 scoped observation](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-owner-observation-0.26.0-2026-10-22.md):
26/26 identities enumerated with 7 `observed` and 19 `not_checked`; two
confirmed layer changes/readbacks on one Column; and one Wall highlight
submission without a logged view result or native selected-element count.
The assistant's stated opening blocker conflicts with the later empty `blocked`
arrays and has no raw diagnostic, so the cause is unverified. No material
change, delete, no-op or Undo was recorded in that 0.26.0 log. The later
0.28.0 Column trial and its outcome are recorded in the
[0.28.0 trial record](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/m4-single-drawing-0.28.0.pl.md); its grouped-Undo failure
was superseded by the limited 0.29.0 owner-reported PASS above. The next
material-path trial is [0.31.0](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/m4-single-drawing-0.31.0.pl.md).

## Priority status

1. **Earlier accepted scope:** 0.23.0 bounded journal preview/archive and
   0.28.0 capacity limits are verified. Trial 1 in 0.30.0 is owner-reported
   PASS for the planned journal stage, but its raw substep evidence was not
   supplied; do not infer separate restart/replay acceptance from the summary.
   Unknown, corrupt and unverifiable records remain protected.
2. **Implemented, ownership unresolved:** structural identity and fail-closed
   write guards remain. Trial 2 in 0.30.0 is owner-reported PASS for
   identity/evidence collection. The evidence does not establish the conflicting
   Slab/MultiSlab field owner; keep these writes blocked.
3. **Scoped owner-reported PASS:** trial 3 in 0.30.0 reports the W1 no-op stage
   passed. Its detailed raw response was not supplied. Do not expand this to
   other W1 writes or grouped Undo; no-op has no Apply route.
4. **Typed delete accepted only for the tested scope; material/selection open:**
   the 0.29.0 grouped Column delete/Undo PASS remains accepted for that exact
   operation; the 0.28.0 one-of-three Undo is historical. Trial 4 in 0.30.0
   failed before Apply on two material previews, both with zero changes and
   setters. Candidate 0.31.0 changes parent-wrapper matching and has 87 unique
   focused checks passed, including three regressions, and full Windows/Ubuntu
   CI and exact fallback ZIP verification passed. The native retest is pending.
   The exact first native diagnostic branch is unproven,
   and the second opening case is unresolved. Native selection remains
   unsupported.
5. **Limited native scalar PASS:** trial 5 in 0.30.0 confirms Column text,
   integer and real, and Wall text writes with typed readback and Undo/restoration
   read. Enum was undefined; Boolean and standalone Slab fixtures were missing;
   Beam and opening reads were blocked. Full family/type coverage and
   date/vector/object payload and readback contracts remain open.

These scoped outcomes do not close priorities 1–5. See the
[development plan](office-editing-development-plan.pl.md),
[0.30.0 owner observation](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-owner-observation-0.30.0-2026-10-23.md),
[0.31.0 API note](m4-editing-api-0.31.0.md) and
[0.31.0 trial plan](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/m4-single-drawing-0.31.0.pl.md).
