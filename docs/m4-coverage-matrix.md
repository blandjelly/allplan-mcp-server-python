# M4 coverage matrix

Single status table of family × field/type × operation for the M4 goal: edit
every attribute the Allplan 2026 API exposes for Columns, Beams, Walls and
Slabs, and their native properties where the API allows. Update cells here
instead of repeating per-pair status in prose ([documentation policy](documentation-policy.md)).
Evidence and its limits are in [validation status](validation-status.md);
open work is in the [development plan](development-plan.md).

Status as of the 0.48.0 read-only trial (2026-11-04). One active drawing, 1–32 changes per Apply.

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
| Column | PASS (0.30.0) | PASS (0.30.0) | PASS (0.30.0) | CODE | BLOCKED (ID 49 `Status`, no confirmed label) | NONE |
| Wall | PASS (0.30.0) | CODE | CODE | PARTIAL (ID 1371: post-Undo read only) | PASS (ID 120, 0.31.0) | NONE |
| SkeletonBeam | REPORTED (ID 508, 0.39.0) | CODE | CODE | CODE | CODE | NONE |
| Beam | PASS (ID 508 `""`→`TEST-BEAM`, 0.44.0; `""`→`C30/37`, 0.45.0, UI, UI Undo and post-Undo read `""`) | CODE | CODE | CODE | CODE | NONE |
| Slab (MultiSlab child) | VALUE (tier storage, not shown in the UI): exact parent-edge route, ID 508 `TEST2`→`TEST1`, 0.47.0 execution `9b2e4d71…`, `applied` with both tier wrappers agreeing and inventory unchanged; no UI Undo. Non-exact tier writes are blocked and name the MultiSlab (`ui_owner`, 0.47.0 native PASS). Earlier REPORTED (0.27.0, 0.39.0) without owner binding | CODE | CODE | CODE | CODE | NONE |
| MultiSlab | PASS (ID 508, the slab material shown in the UI: 0.46.0 `04569db1…` `TEST1`→`TEST2`; 0.47.0 plain-language request `3f9c2a7e…` `TEST1`→`TEST3`, `applied` on view `b4a59b5b…`, UI, UI Undo and post-Undo read `TEST1`) | CODE | CODE | CODE | CODE | NONE |

Computed-only attributes are never written. Attribute definitions are never
created; an existing definition can be added to an element (`add`/`upsert`).

## Native properties and other operations

| Family | Native Material | Other native properties | Organizational layer | Delete |
| --- | --- | --- | --- | --- |
| Column | VALUE (0.35.0 record, 0.39.0) | NONE (write); getter read observed (0.48.0), native `CalculationMode` = attr 120 = UI | PARTIAL (no-op only) | PASS (grouped, 3 Columns + Undo, 0.29.0) |
| Wall (single tier) | VALUE (0.37.0/0.39.0, preservation unverified) | NONE (write); getter read observed (0.48.0), native `CalculationMode` = attr 120 = UI | REPORTED (`Ogólne03`, 0.27.0) | PARTIAL (subtree absent; no Undo) |
| Wall (multi tier) | BLOCKED (one tier only) | NONE | CODE (tier-aware route) | — |
| SkeletonBeam | BLOCKED (no successful write; view discrepancy) | NONE (write); getter-only read CODE (0.48.0), not read natively | CODE | FIXTURE (no disposable target) |
| Beam | PASS (0.46.0 execution `5a0bc366…`: `""`→`C30/37`, `applied` with `accepted_preservation_drift.accepted="auxiliary_children_regenerated"` on view `362f80d3…`; owner-reported UI and UI Undo, post-Undo preview old value `""`) | NONE (write); getter read observed on view `6035d406…` (0.48.0), native `CalculationMode` = attr 120 = UI | FIXTURE | FIXTURE |
| Slab (MultiSlab child) | PARTIAL, not the UI material (0.43.0 setter ran, readback `" "`; tier 0 also `" "`; 0.44.2 owner: UI shows `TEST1` = attribute 508). Use the MultiSlab's attribute 508 | NONE (write); getter read observed incl. tier `Thickness`, native = attr 120 `m2` (0.48.0) | BLOCKED (parented child) | BLOCKED (parented child) |
| Slab (standalone) | CODE | NONE (write); getter-only read CODE (0.48.0), no fixture read | FIXTURE | FIXTURE |
| MultiSlab | CODE | NONE (write); getter read observed (0.48.0): native `CalculationMode` `m2` ≠ attr 120/UI `m3`, native route not the UI owner | BLOCKED (aggregate owner) | FIXTURE |
| WindowDoor (opening) | — | NONE | CODE | CODE |

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
Standalone Slab and SkeletonBeam were not read.

Selection: native selection is unsupported for every family; highlight is
available and is not a selection ([selection API](m4-native-selection-api.md)).
