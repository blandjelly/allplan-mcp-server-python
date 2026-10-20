# M4 single-drawing coverage — 0.24.0

Updated 2026-10-21 (Europe/Warsaw). This is implementation and verification
coverage for priorities 2–5, not native acceptance. Existing scoped owner
observations remain in [validation status](validation-status.md).

| Requested family / adapter | Current guarded route and owner boundary | Remaining native evidence |
| --- | --- | --- |
| Columns / Column | Typed attributes and exact existing organizational layer; model/view binding, exclusions, fresh readback, replay and no-op. | Only remaining W1 readback/no-op/Undo gap; preserve accepted attributes. |
| Walls / Wall | Typed root attributes; organizational layer binds all direct WallTier owners with its own adapter. Single-tier native thickness/material read exists. | Native layer owner/readback/Undo for unaccepted case; native material writes unsupported. |
| Beams / Beam, SkeletonBeam | Typed attributes and organizational layer, exact target resolution; unrelated broken hierarchies do not redirect the owner. | Family/build-specific UI/readback/Undo; fakes and API availability are separate. |
| Slabs / Slab | Read-only direct identity probe; only standalone Slab permits typed attributes/layer with bound ancestry. | Resolve the owner's two Slab/MultiSlab results read-only. No new attribute trial on previously accepted targets. |
| Aggregate slab / MultiSlab | Direct parent/child evidence; all aggregate writes blocked pending an explicit property owner. Slab children are blocked independently of the type filter. | Explicit owner contract before enabling any aggregate/tier write. |
| Doors and windows / WindowDoor | Structural identity probe keeps parents visible; shared supported adapter remains `opening`, without guessing door/window from display name or parent. | Separate door/window, opening/inserted-object ownership and variant evidence. Current attributes/layer use the exact supported adapter, never its wall. |

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
| Date, vector, byte, other SDK objects | Unsupported and blocked before target enumeration; no scalar substitution. | Documented adapter setter payload, exact encode/decode/readback, then narrow native trial. |

## Native selection and material are separate gaps

`model_selection(action=select)` returns `status=unsupported`, starts no UI
calls, and never falls back to highlighting. The official **2026** example
[MultiSelection.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/e816b120038ca121b51d80b78f22da561b5c6fda/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/MultiSelection.py#L220)
starts an interactive `InputFunctionStarter.StartElementSelect` operation and
reads user-selected elements with `PostElementSelection.GetSelectedElements`.
It does not demonstrate setting a query's exact adapter list as the native UI
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
`native_material` request is rejected before enumeration/setters. A material
attribute, surface or organizational layer never substitutes for it.

Priorities 2–5 therefore remain partially open: the portable owner gate and
coverage checks are implemented, while native observations and the selection,
material and unsupported-codec adapters are still required. See the
[bounded next trial](m4-single-drawing-0.24.0.pl.md) and
[development plan](office-editing-development-plan.pl.md).
