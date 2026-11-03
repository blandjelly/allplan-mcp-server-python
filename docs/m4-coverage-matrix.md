# M4 coverage matrix

Single status table of family × field/type × operation for the M4 goal: edit
every attribute the Allplan 2026 API exposes for Columns, Beams, Walls and
Slabs, and their native properties where the API allows. Update cells here
instead of repeating per-pair status in prose ([documentation policy](documentation-policy.md)).
Evidence and its limits are in [validation status](validation-status.md);
open work is in the [development plan](development-plan.md).

Status as of 0.46.0 trial and 0.47.0 candidate (2026-11-03). One active drawing, 1–32 changes per Apply.

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
| Slab (MultiSlab child) | PARTIAL: tier storage, not shown in the UI. 0.46.0 read: tier ID 508 `TEST2` (most likely the 0.45.0 write) while the UI shows the MultiSlab's `TEST1`. Non-exact tier writes are blocked and name the MultiSlab (`ui_owner`, 0.47.0); the exact parent-edge tier route is CODE (0.46.0 preview `no_op`). Earlier REPORTED (0.27.0, 0.39.0) without owner binding | CODE | CODE | CODE | CODE | NONE |
| MultiSlab | PASS (ID 508 `TEST1`→`TEST2`, 0.46.0 execution `04569db1…`: `applied` on view `b4a59b5b…`, UI `TEST2`, UI Undo and post-Undo read `TEST1`; this is the slab material shown in the UI) | CODE | CODE | CODE | CODE | NONE |

Computed-only attributes are never written. Attribute definitions are never
created; an existing definition can be added to an element (`add`/`upsert`).

## Native properties and other operations

| Family | Native Material | Other native properties | Organizational layer | Delete |
| --- | --- | --- | --- | --- |
| Column | VALUE (0.35.0 record, 0.39.0) | NONE | PARTIAL (no-op only) | PASS (grouped, 3 Columns + Undo, 0.29.0) |
| Wall (single tier) | VALUE (0.37.0/0.39.0, preservation unverified) | NONE | REPORTED (`Ogólne03`, 0.27.0) | PARTIAL (subtree absent; no Undo) |
| Wall (multi tier) | BLOCKED (one tier only) | NONE | CODE (tier-aware route) | — |
| SkeletonBeam | BLOCKED (no successful write; view discrepancy) | NONE | CODE | FIXTURE (no disposable target) |
| Beam | PASS (0.46.0 execution `5a0bc366…`: `""`→`C30/37`, `applied` with `accepted_preservation_drift.accepted="auxiliary_children_regenerated"` on view `362f80d3…`; owner-reported UI and UI Undo, post-Undo preview old value `""`) | NONE | FIXTURE | FIXTURE |
| Slab (MultiSlab child) | PARTIAL, not the UI material (0.43.0 setter ran, readback `" "`; tier 0 also `" "`; 0.44.2 owner: UI shows `TEST1` = attribute 508). Use the MultiSlab's attribute 508 | NONE | BLOCKED (parented child) | BLOCKED (parented child) |
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
