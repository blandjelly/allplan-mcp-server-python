# M4 material-path correction for candidate 0.31.0

Candidate `0.31.0` is under evaluation on `fix/m4-material-owner-0.31.0`.
This note describes the source correction. **87 unique focused checks passed**: 86 affected/dependent checks in
`wall_material_edit`, `wall_material_http`, `model_edit`, `native_model_edit`
and `edit_ownership`, plus one package version/lock check. The 25 overlapping
checks were not double-counted. See the [focused verification record](../evaluation-packages/0.31.0/focused-verification.json).
Both full CI unittest jobs passed on Windows and Ubuntu Python 3.12 in
[run 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481).
The Windows package job passed with 625 tests in each platform job. The
original artifact was unavailable, but one fallback ZIP from clean exact
source (`source_modified=false`) passed verification: 201 payload files, 43
bridge hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`.
The [package-verification record](../evaluation-packages/0.31.0/package-verification.json)
and [verified fallback ZIP](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip)
are available for the one planned native material trial. Native Allplan
acceptance is pending. It corrects a
same-model parent-wrapper defect reproduced by focused tests and associated with
the diagnostic reported in the 0.30.0 Wall material preview; the native cause
is unproven. It does not close priority 4 or priorities 1–5.

## Wall tier parent identity

The 0.30.0 preservation snapshot compared the tier's observed parent view UUID
with the Wall root's exact view UUID. A tier may return a different wrapper
view for the same native Wall. Focused tests reproduced that structural
same-model case being rejected by the strict view-UUID comparison. The guard
also returns `wall_material_tier_hierarchy_unsupported` when the lineage length
is not two or the tier has children. The owner's native diagnostic is
consistent with the wrapper case, but no raw lineage/children response
establishes which branch caused that Allplan result.

The 0.31.0 change compares the observed parent edge with
`same_model_identity` (drawing, model UUID and type). It records the actual
observed tier wrapper in `tier_hierarchy` and preserves that edge in the
snapshot used for revalidation and readback. The selected Wall target remains
bound to its exact drawing/model/view identity; the comparison change does not
weaken target binding.

Three parent-wrapper regressions passed within the 86 focused checks: a
same-model alternate parent is accepted with the actual edge bound and fresh
readback; parent-view drift conflicts at revalidation; and a different parent
model, type or drawing remains blocked.

The preservation path still requires a standalone Wall root, supported child
types and hierarchy shape: exactly one direct `WallTier_TypeUUID` child, no
children under that tier, no opening or other Wall children, valid tier
geometry and exactly one tier. A failed guard remains blocked before Apply.
This change updates snapshot identity evidence only; it adds no setter or
`SetWallTierProperties` API. The existing `WallElement` properties route and
its limits are recorded in the pinned
[`ModifyWall.py` example at immutable commit `e816b120`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/e816b120038ca121b51d80b78f22da561b5c6fda/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifyWall.py#L285)
and [M4 API note 0.25.0](m4-editing-api-0.25.0.md#narrow-native-wall-material-experiment).

The snapshot's complex-property representations are bounded drift evidence,
not exhaustive preservation codecs for hidden SDK state. See the
[coverage limitations](m4-single-drawing-coverage-0.24.0.md#native-selection-and-material-are-separate-gaps).

The 0.30.0 first Wall preview reported
`native_material_preservation_unavailable` with
`wall_material_tier_hierarchy_unsupported`. The 0.31.0 code fixes the
reproduced same-model parent-wrapper defect associated with that diagnostic;
native retest is pending, and the exact cause of the owner's 0.30.0 result is
not proven. A second Wall with an opening reported
`component_child_owner_mismatch`. Its cause is unresolved and this change does
not claim to fix it. Official `GetChildModelElements(adapter, hiddenElements)`
returns immediate children (`True` includes hidden immediate children);
recursive enumeration is the separate `GetChildModelElementsFromTree` API.
Therefore recursive enumeration alone does not explain the opening result.
See the [official child-elements API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapterChildElementsService/).

## Remaining prerequisites

| Priority | Achieved scope | Still missing |
| --- | --- | --- |
| 1 — journal | 0.30.0 owner-reported trial PASS; earlier bounded preview/archive scope remains accepted. | Trial substeps lack detailed raw evidence; preserve unknown/corrupt/unverifiable records. |
| 2 — field ownership | 0.30.0 identity/evidence trial reported PASS. `ModifySlab.py` demonstrates `SlabElement.Properties` editing through `SetProperties`/`ModifyElements`. | It does not prove M4 project-attribute ownership or a `ChangeAttributes` route for the conflicting Slab/MultiSlab lineage. Keep these writes blocked. |
| 3 — layer/no-op | 0.30.0 W1 no-op stage reported PASS. | Detailed raw log was not supplied; this does not expand W1 write/Undo acceptance. |
| 4 — typed delete, material and selection | 0.29.0 grouped Column delete/Undo remains accepted for its tested scope. 0.31.0 corrects same-model parent-wrapper matching in the material snapshot. | Native material trial for 0.31.0 is pending. Native UI selection has no arbitrary replace/clear/readback setter. |
| 5 — attribute types | 0.30.0 trial 5 confirms four scalar pairs with typed readback and Undo. | Full family/type coverage and non-scalar codecs. `AttributeDate` and `AttributeDoubleVec` constructors do not establish an adapter `ChangeAttributes` payload or typed readback contract. |

The remaining APIs and evidence are described in the
[0.30.0 API research note](m4-editing-api-0.30.0.md). These runtime/native
prerequisites cannot be completed by documentation or cloud-side reasoning;
do not guess setter payloads or lift the existing write guards without a
specific verified contract.
