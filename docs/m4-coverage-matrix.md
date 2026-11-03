# M4 coverage matrix

Single status table of family × field/type × operation for the M4 goal: edit
every attribute the Allplan 2026 API exposes for Columns, Beams, Walls and
Slabs, and their native properties where the API allows. Update cells here
instead of repeating per-pair status in prose ([documentation policy](documentation-policy.md)).
Evidence and its limits are in [validation status](validation-status.md);
open work is in the [development plan](development-plan.md).

Status as of 0.44.2 trial and 0.45.0 candidate (2026-11-03). One active drawing, 1–32 changes per Apply.

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
| Slab (MultiSlab child) | CODE (0.46.0 exact parent-edge target). ID 508 is the UI material (0.44.2). 0.45.0 non-exact write: false `applied`, UI unchanged; that route is now blocked. Earlier REPORTED (0.27.0, 0.39.0) without owner binding | CODE | CODE | CODE | CODE | NONE |
| MultiSlab | REPORTED (0.39.0; owner binding open) | CODE | CODE | CODE | CODE | NONE |

Computed-only attributes are never written. Attribute definitions are never
created; an existing definition can be added to an element (`add`/`upsert`).

## Native properties and other operations

| Family | Native Material | Other native properties | Organizational layer | Delete |
| --- | --- | --- | --- | --- |
| Column | VALUE (0.35.0 record, 0.39.0) | NONE | PARTIAL (no-op only) | PASS (grouped, 3 Columns + Undo, 0.29.0) |
| Wall (single tier) | VALUE (0.37.0/0.39.0, preservation unverified) | NONE | REPORTED (`Ogólne03`, 0.27.0) | PARTIAL (subtree absent; no Undo) |
| Wall (multi tier) | BLOCKED (one tier only) | NONE | CODE (tier-aware route) | — |
| SkeletonBeam | BLOCKED (no successful write; view discrepancy) | NONE | CODE | FIXTURE (no disposable target) |
| Beam | VALUE (0.44.2: `""`→`C30/37` on all views, UI `C30/37`, reviewed reconciliation of regenerated AttributeContainer/WallAxis; UI Undo restored `""` and the original children). 0.45.0 accepts that regeneration after the setter: `applied` not yet native-observed (the 0.45.0 trial wrote attribute 508 instead) | NONE | FIXTURE | FIXTURE |
| Slab (MultiSlab child) | PARTIAL, not the UI material (0.43.0 setter ran, readback `" "`; tier 0 also `" "`; 0.44.2 owner: UI shows `TEST1` = attribute 508). Use attribute 508 | NONE | BLOCKED (parented child) | BLOCKED (parented child) |
| Slab (standalone) | CODE | NONE | FIXTURE | FIXTURE |
| MultiSlab | CODE | NONE | BLOCKED (aggregate owner) | FIXTURE |
| WindowDoor (opening) | — | NONE | CODE | CODE |

"Other native properties" means members of `WallTierProperties`,
`ColumnProperties`, `BeamProperties`, `StructuralBeamProperties` and
`SlabProperties` other than Material (thickness, height/plane references,
surface, priority, calculation mode, trade, hatch/filling). The preservation
snapshot already reads many of them; writing them is plan item 5.

Selection: native selection is unsupported for every family; highlight is
available and is not a selection ([selection API](m4-native-selection-api.md)).
