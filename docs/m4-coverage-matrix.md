# M4 coverage matrix

Single status table of family × field/type × operation for the M4 goal: edit
every attribute the Allplan 2026 API exposes for Columns, Beams, Walls and
Slabs, and their native properties where the API allows. Update cells here
instead of repeating per-pair status in prose ([documentation policy](documentation-policy.md)).
Evidence and its limits are in [validation status](validation-status.md);
open work is in the [development plan](development-plan.md).

Status as of the 0.51.1 native trial (2026-11-08,
[evidence](test-results/evidence/0.51.1-2026-11-08/evidence-20261108.jsonl),
[observations](m4-editing-api.md#native-observations-0511-trial-2026-11-08));
0.51.2 code changes marked CODE. One active drawing, 1–32 changes per Apply.
One UndoRedoService step per Apply with two or more changes: PASS in the
0.51.0 trial (one UI Undo restored both places of a paired write).

## Legend

| Status | Meaning |
| --- | --- |
| **PASS** | Native Apply + typed readback + UI Undo/restoration observed for this pair (scope in validation status). |
| **VALUE** | Native write reached the intended value, but preservation, Undo or exact owner binding is not established. |
| **REPORTED** | Owner reported success without raw payload/readback evidence. |
| **PARTIAL** | Some steps observed (for example readback only); no complete cycle. |
| **CODE** | Implemented and covered by automated tests; no native trial yet. |
| **UNKNOWN** | A native write ended with an unresolved unknown outcome; recovery pending. |
| **BLOCKED** | Contract, label or owner unresolved; writing is refused by design. |
| **FIXTURE** | No test element of this kind in the owner's project (`fixture_missing`). |
| **NONE** | No code path; needs API research first. |

## Attributes (`ElementsAttributeService.ChangeAttributes`)

| Family | Text | Integer | Real | Boolean (Integer+CheckBox) | Enum (label) | Date / vector / object |
| --- | --- | --- | --- | --- | --- | --- |
| Column | PASS (0.30.0) | PASS (0.30.0) | PASS (0.30.0) | CODE | CODE (ID 49 `Status`: owner-confirmed UI labels 2026-11-08 — Inny, Nieokreślony, Nieznany, Nowo projektowane, Rozbiórka, Tymczasowy, Wybudowane; `<niezdefiniowany>` is not a list label; label round trip and trial pending) | FIXTURE (Date: none in the project, owner 2026-11-08); vector/object NONE |
| Wall | PASS (0.30.0) | PASS (ID 1442, CheckBox control, 0.51.1: 1→0 `9bf9d05d…` with UI check, the next preview read 1 again; 1→2 `360930f8…` with UI check, one UI Undo, read 1; from 0.51.2 a CheckBox takes only 0/1, CODE) | PASS (ID 230 "Współczynnik" 1→2, 0.51.1 `3be71e58…`, UI, one UI Undo, read 1). ID 220 "Długość" is stored but not writable (`readback_unchanged`, `052283c9…`) | PASS (ID 1371 0→`true`, `integer_checkbox_boolean`, 0.51.1 `56739a30…`, UI, one UI Undo, read 0) | PASS (ID 120, 0.31.0; `m3`→`m` 0.49.0 `c41d8e2a…`, UI Undo, post-Undo read `m3`) | FIXTURE (no Date attribute); vector/object NONE |
| SkeletonBeam | REPORTED (ID 508, 0.39.0) | CODE | CODE | CODE | CODE | FIXTURE (Date); NONE |
| Beam | PASS (ID 508 `""`→`TEST-BEAM`, 0.44.0; `""`→`C30/37`, 0.45.0, UI, UI Undo and post-Undo read `""`) | CODE (candidates listed by the 0.51.1 discovery, 44 attributes) | CODE | CODE | PASS for the value (ID 120 `m3`→`m`, 0.51.1 `8cc1e687…`, enum round trip, UI, one UI Undo restored both places), but native `CalculationMode` followed 0→2: a single-place 120 request is blocked from 0.51.2 (CODE, `attribute_write_also_changes_native_property`); use the paired request | FIXTURE (Date); NONE |
| Slab (MultiSlab child) | PASS (exact parent-edge route, ID 508 `TEST2`→`TEST4`, 0.51.1 `1a019448…`: `applied`, both tier wrappers agree, `exact_inventory` unchanged, MultiSlab 508 `TEST1` unchanged, owner UI check, one UI Undo, read `TEST2`; the UI check did not report the two palette modes separately). Earlier VALUE 0.47.0 `9b2e4d71…`. Non-exact tier writes are blocked and name the MultiSlab (`ui_owner`, `slab_tier_requires_exact_layer_target`); MultiSlab attribute previews report the tier value as `slab_tier_values` (PASS 0.49.0, 0.51.1) | CODE | CODE | CODE | CODE | FIXTURE (Date); NONE |
| MultiSlab | PASS (ID 508, the slab material shown in the UI: 0.46.0 `04569db1…` `TEST1`→`TEST2`; 0.47.0 plain-language request `3f9c2a7e…` `TEST1`→`TEST3`, `applied` on view `b4a59b5b…`, UI, UI Undo and post-Undo read `TEST1`) | PASS (ID 110 "Priorytet" 200→201, 0.51.1 `1ca552c6…`, tier and native `Priority` unchanged, UI, one UI Undo, read 200) | PASS (ID 981 "Wartość U" `<niezdefiniowany>`→0.25, 0.51.1 `0a7fc6d5…`, UI, one UI Undo, read `<niezdefiniowany>`) | CODE | PASS (ID 120 calculation mode `m3`→`m`, 0.49.0 `e27b9d4f…`, `property_owner=selected_element`, tier `m2` reported and unchanged, UI Undo, post-Undo read `m3`) | FIXTURE (Date); NONE |

Computed-only attributes are never written. Attribute definitions are never
created; an existing definition can be added to an element (`add`/`upsert`).

## Native properties and other operations

| Family | Native Material | Other native properties | Organizational layer | Delete |
| --- | --- | --- | --- | --- |
| Column | PASS (0.51.1 paired material `TEST1`→`C35/45`, `7c1e4a92…`: native `applied` with AttributeContainer + root view `cc752bda…`→`55509cf2…` renamed, 508 followed without a setter, owner UI check, one UI Undo restored `TEST1` and the identities) | PASS (`CalculationMode` 2→0: 0.50.0 `1214d281…` as `native_calculation_mode`, and 0.50.1 `341415e4…` with the plain request routed as `paired_property`: native `applied` with AttributeContainer + root view `cc752bda…`→`86a9536a…` renamed, attr 120 followed without a setter, owner UI check, one UI Undo restored 2/`m` and view `cc752bda…`) | PARTIAL (no-op only; 0.51.1 no-op on `4f3cc27e…` `SZ_OGÓ01`: 0 setters, no Apply) | PASS (grouped, 3 Columns + Undo, 0.29.0) |
| Wall (single tier) | PASS (0.51.0 paired material `Cegła`: Wall 240 `c6183d71…` native + 508 `applied` with 2 × AttributeContainer + WallAxis renamed; Wall with door `9109d250…` native only, 508 follows; owner UI check, one UI Undo each). Wall with window: VALUE (0.51.1 `3c5df3d9…` reached `Cegła` with complete evidence but stayed `unknown`: only the WindowTier/WindowReveal geometry streams were re-serialized; reconciled after UI Undo); 0.51.2 CODE: shape-equal re-serialization accepted | PASS on the plain Wall (`CalculationMode` 0→2, 0.50.0 paired `e4de1f73…`: `applied` with 2 × AttributeContainer + WallAxis renamed, owner UI check, one UI Undo restored 0). Wall with door: paired `CalculationMode` 0→2 `applied` with 2 × AttributeContainer, Door, DoorSill renamed and attr 120 written, **one UI Undo** (0.51.0 `6e6c83d2…`). Wall with window: VALUE (0.51.1 `5008fcbe…`, `c1395fe6…` reached native 2, Window, Sill, WallAxis, 3 × AttributeContainer renamed, `unknown` on the re-serialized WindowTier/WindowReveal geometry, attr 120 skipped; UI Undo, reconciled); 0.51.2 CODE. Attr 120 is not mirrored reliably on Walls (did not follow on the door and window Walls) | PASS (0.51.1 `b3e8d1f4…`, Wall 200 65535→3701 `SZ_OGÓ02` through `set_wall_layer` on root + tier, owner UI check, one UI Undo, read 65535); earlier REPORTED (`Ogólne03`, 0.27.0) | PARTIAL (subtree absent; no Undo) |
| Wall (multi tier) | BLOCKED (one tier only) | NONE | CODE (tier-aware route) | — |
| SkeletonBeam | BLOCKED (no successful write; view discrepancy) | NONE (write); getter-only read CODE (0.48.0), not read natively | CODE | FIXTURE (no disposable target) |
| Beam | PASS (0.46.0 execution `5a0bc366…`: `""`→`C30/37`, `applied` with `accepted_preservation_drift.accepted="auxiliary_children_regenerated"` on view `362f80d3…`; owner-reported UI and UI Undo, post-Undo preview old value `""`) | PASS (`CalculationMode` 0→2, 0.50.0 paired `d129c7c1…`: native `applied` with AttributeContainer + WallAxis renamed, attr 120 `paired_attribute_already_set_by_native_write` without a setter, owner UI check, one UI Undo restored 0/`m3`). Native and attr 120 change together in both directions (0.51.1 `8cc1e687…`) | FIXTURE | FIXTURE |
| Slab (MultiSlab child) | PARTIAL, not the UI material (0.43.0 setter ran, readback `" "`; tier 0 also `" "`; 0.44.2 owner: UI shows `TEST1` = attribute 508). Use the MultiSlab's attribute 508 | BLOCKED for native `CalculationMode` (0.49.0: `slab_calculation_mode_uses_multislab_attribute_120`); getter read observed incl. tier `Thickness`, native = attr 120 `m2` (0.48.0) | BLOCKED (parented child) | BLOCKED (parented child) |
| Slab (standalone) | CODE | NONE (write); getter-only read CODE (0.48.0), no fixture read | FIXTURE | FIXTURE |
| MultiSlab | CODE | BLOCKED for native `CalculationMode` (native route not the UI owner: 0.48.0 native `m2` ≠ attr 120/UI `m3`); calculation mode goes through attribute 120 with `property_owner="selected_element"` (PASS: 0.49.0 `e27b9d4f…`, 0.50.0 `1dac121c…`, UI Undo, tier `m2` unchanged) | BLOCKED (aggregate owner) | FIXTURE |
| Opening (`Door_TypeUUID`, `Window_TypeUUID` in Allplan 2026.1; SDK `WindowDoor_TypeUUID`) | — | NONE | CODE | Window: PASS (0.51.1 `d5a79c20…`, window `268dec66…` with its 7-adapter subtree absent, Wall 300 and neighbours kept, owner UI check, one UI Undo restored the window and WindowTier with their identities; other parts inferred from counts). Door: CODE. `component_identity` on the window Wall's WallTier reports `shared_children` (0.51.1 read PASS) |

"Other native properties" means members of `WallTierProperties`,
`ColumnProperties`, `BeamProperties`, `StructuralBeamProperties` and
`SlabProperties` other than Material (thickness, height/plane references,
surface, priority, calculation mode, trade, hatch/filling). The preservation
snapshot already reads many of them; writing them is plan item 5. The
[API note](m4-editing-api.md#native-properties-beyond-material--api-note-plan-item-5)
names `CalculationMode` as the first write candidate per family; 0.48.0 reports
`CalculationMode`, `Priority`, `Trade` and tier `Thickness` through
`material_comparison` without any setter. The 0.48.0 trial observed them on
Wall, Column, Beam, MultiSlab and Slab child: native `CalculationMode` equals
attribute 120 and the UI on Wall/Column/Beam, but not on the MultiSlab (native
`m2`, UI/attribute `m3`); see the [API note](m4-editing-api.md#native-observations-0480-read-only-precheck-2026-11-04).
Standalone Slab and SkeletonBeam were not read. 0.49.0 adds the
`native_calculation_mode` write for Column, single-tier Wall and
`Beam_TypeUUID` only (SkeletonBeam and slabs are blocked). The 0.49.0 trial
showed that attribute 120 is not one storage with the native value
([observations](m4-editing-api.md#native-observations-0490-trial-2026-11-07)).
0.50.0 (CODE) adds `paired_property` (native value + same-named attribute in
one plan: `CalculationMode`/120 and `Material`/508; attribute only on slabs and
SkeletonBeam) and accepts the observed identity regeneration after a
`CalculationMode` setter. Its 0.50.0 trial made the Column, plain Wall and
Beam writes `applied`; the Wall with a door also regenerated the Door and
DoorSill, which 0.50.1 accepts (native PASS of the renaming in the 0.50.1
trial, two UI Undo steps). 0.51.0 grouped the setters of one Apply in one
undo step and applied the family renaming rule to Material (both PASS in its
trial); the window Wall stayed `unknown` on partial evidence. With 0.51.1's
complete evidence it stays `unknown` only on the re-serialized
WindowTier/WindowReveal geometry, which 0.51.2 (CODE) accepts when shape and
structure are equal. Native `Trade`: 78 UI labels without codes (owner
screenshots 2026-11-08), so a write needs per-label code readback first.
Geometric native properties (thickness, length, height) are not pursued
(owner, 2026-11-08); MultiSlab attribute 110 "Priorytet" is not coupled to
native `Priority`.

Selection: native selection is unsupported for every family; highlight is
available and is not a selection ([selection API](m4-native-selection-api.md)).
