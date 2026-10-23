# M4 editing API evidence for 0.29.0

Research date: 2026-10-23. This note records official examples that pass
multiple adapters to the base-elements module's `DeleteElements` function in
one call. It supports
the implementation choice for one reviewed plural delete plan. It does not
prove that Allplan groups those deletions into one UI Undo step, nor does it
establish successful deletion/readback for the M4 Column scenario.

## Plural `DeleteElements`

The immutable official
[`Fillet3D.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/GeometryExamples/Operations/Others/Fillet3D.py)
example appends two adapters to one list (lines 237–239), then passes that list
to a single `AllplanBaseElements.DeleteElements` call (lines 272–275). The official
[`PythonPartConnection.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/BasisExamples/PythonParts/PythonPartConnection.py)
also builds a list of adapters and passes it to `DeleteElements` (lines
103–106). These examples show that the API accepts a list of adapters for one
call. They do not document M4's preflight, transaction boundaries, per-target
result accounting, complete subtree ownership, fresh absence readback, or
recovery behavior; those remain M4 safeguards and must be verified separately.

## UI Undo

The SDK exposes `UndoRedoService` in `NemAll_Python_IFW_Input`, but the reviewed material does not define a
deletion collection contract that guarantees one Undo restores every element
passed to `DeleteElements`. API availability and a single plural call do not
prove UI behavior. The narrow 0.29.0 owner trial must confirm with fresh reads
that one UI Undo restores the exact three Column roots and all bound
descendants. Do not add a wrapper around an undocumented undo API or claim
grouped Undo before that trial passes.

## Remaining native/API priorities 2, 4, and 5

### Priority 2 — Slab and MultiSlab ownership

The pinned official
[`ModifySlab.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifySlab.py)
demonstrates an architectural property-editing route: it resolves a selected
adapter with `GetElement`, casts it to `SlabElement`, reads `Properties`, builds
new slab properties, assigns them to the element and calls `ModifyElements`.
It also gets and hides the selected adapter's parent while the edit interaction
is active. This is evidence for a Slab element property workflow. It does not
establish that a selected child adapter owns M4's project attributes, that a
`MultiSlab` owns the same fields, or which element is authoritative for the
reported Slab/MultiSlab lineage. No explicit MultiSlab property-owner contract
appears in the reviewed sources.
See the API references for [`SlabElement`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabElement/),
and [`SlabProperties`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabProperties/).

Keep aggregate and unresolved child writes blocked. To implement a route,
establish the exact target and lineage from fresh model/view identity reads,
document which element owns each requested property for the specific family,
and bind its property snapshot and preservation fields. A narrow native trial
must then show the intended value change, fresh typed readback, preservation
of unrelated tiers/geometry and UI Undo. A property API call alone cannot close
the ownership question.

### Priority 4 — native selection

The 0.28.0 research note records the distinction between
[`SelectElementsService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectElementsService/)
geometry queries, [`ElementsSelectService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsSelectService/)
document/IFC queries, [`PostElementSelection`](https://pythonparts.allplan.com/2025/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/PostElementSelection/)
for elements picked through a user interaction, and `HighlightService` for
visual highlighting. The pinned
[`GetObjectByAttributeValue.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ObjectAccessExamples/GetObjectByAttributeValue.py)
queries adapters and highlights them. The pinned
[`SelectObjectsByAttributeID.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/SelectObjectsByAttributeID.py)
uses an interactive user-pick path. These examples do not establish an API
that sets an arbitrary existing M4 query-result list as the native selection
and reads that exact set back.

Keep the existing highlight route described as highlighting. Before adding
native selection, document an exact set/replace operation, its clear behavior,
and a readback that distinguishes selected adapters from highlighted ones.
A narrow trial must verify the exact target count and identities, behavior
when replacing/clearing an existing selection, and that no model edit occurs.
The reviewed examples do not prove that no such API exists; they leave the
setter and readback contract unestablished.

### Priority 5 — date and vector attributes

The 2026 [`ElementsAttributeService` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
uses a generic `object` value parameter, while the
[`AttributeDate` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
documents a date value for the `AllplanElement.SetAttributes` path. The
[`AttributeDoubleVec` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
documents a vector attribute representation. Neither API signature by itself
establishes the accepted payload for M4's existing-adapter
`ChangeAttributes` route or an exact typed readback. The pinned generic
[`ChangeAttributes.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/InteractorExamples/GeneralModification/ChangeAttributes.py)
example does not show date or vector values, and no date/vector end-to-end
setter plus readback example was found in the reviewed pinned tree.

Keep date/vector writes blocked until a family-specific contract specifies the
input encoding, runtime type binding, native setter payload and fresh typed
readback. Then verify unrelated-field preservation and UI Undo on a narrow
native trial. These source and API findings delimit reviewed evidence; they do
not claim that other supported call paths cannot exist.

## Sources

- Official examples at immutable commit
  [`8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/tree/8e2c252477e20bc9afac8918f78a8eeabd473a81)
- [UndoRedoService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/UndoRedoService/)
