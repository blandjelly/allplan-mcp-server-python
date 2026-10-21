# M4 editing API evidence for 0.25.0

Research note, 2026-10-21. These are documented 2026 API surfaces, not native
Allplan acceptance. A method signature does not establish host integration,
transaction behavior, safety for a particular adapter, or successful readback.

## Deleting an exact target

The 2026 [Base Elements API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/)
documents `DeleteElements(doc: DocumentAdapter, elements: BaseElementAdapterList)`.
An exact adapter exposes its owning document through
[`BaseElementAdapter.GetDocument()`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/).
This supports a candidate path for deleting already-resolved adapters in their
document. The reference does not document a return value, cascade/child rules,
atomicity, or Undo behavior. Keep deletion bound to an explicit exact target
and treat those semantics as open until verified.

## Native selection remains interactive

[`InputFunctionStarter.StartElementSelect`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/InputFunctionStarter/)
starts a user selection in the viewport. The documented lifecycle pauses the
interactor's mouse processing until selection completes, stores results in
`PostElementSelection`, then removes the input function. Only one selection
function may be active; restart requires `RemoveFunction` first.
[`PostElementSelection.GetSelectedElements(doc)`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/PostElementSelection/)
returns the selected adapters and pops them from that result object. This is
selection made by the user; these APIs do not set the native UI selection to an
existing query result list. Bridging the user-input lifecycle and reporting
exact selection readback remains unimplemented and unaccepted.

## Narrow native Wall material experiment

The official 2026 [`WallElement`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallElement/)
API documents `GetProperties()` and `SetProperties(WallProperties)`. The
[`ArchBaseProperties`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ArchBaseProperties/)
API documents `SetMaterial(material: str)`. The pinned official
[`ModifyWall.py` example](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/e816b120038ca121b51d80b78f22da561b5c6fda/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifyWall.py#L285)
edits properties from an existing wall, reattaches them with
`SetProperties(wall_props)`, and submits `ModifyElements(doc, [wall_ele])`.
Together these sources justify a disposable-copy experiment for one precisely
bound Wall tier. They do not define a project material-catalog key, prove that
the string names a valid native material, or prove geometry/tier preservation,
successful fresh readback, or Undo. Do not enable writes based on the
signatures alone.

## Date and vector payload boundaries

The 2026 [attribute guide](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
documents typed `AttributeDate(id, day, month, year)` within an
`Attributes`/`AttributeSet` payload passed to `AllplanElement.SetAttributes`.
The API also exposes [`AttributeDate`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
with writable day, month, and year fields. This establishes a typed payload
for an Allplan element's attribute container. It does not specify how an
existing adapter's `ElementsAttributeService.ChangeAttribute(newValue: object)`
accepts that payload, nor does the existing-element guide show date write plus
readback. Do not coerce dates to integers or locale-dependent strings.

For vector values, the API documents [`AttributeDoubleVec`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
with `VecDoubleList` payload and [`Vector3D`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_Geometry/Vector3D/)
with coordinate access (`GetCoords() -> tuple[float, float, float]`). Those
are different representations: a double-vector attribute and a geometric
vector. Neither page establishes the applicable owner field or a write/readback
route for an arbitrary model property. [`Polyhedron3D.WriteToStream()`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_Geometry/Polyhedron3D/)
returns `(error_code, str)` for polyhedron geometry; it is not a general date
or vector-property codec.

Keep date, vector, and other object writes blocked until the exact property
owner, accepted setter payload, and fresh readback representation are all
documented for that adapter. The sources above narrow possible payload types;
they do not close these gaps. Native trial, geometry and unrelated-property
preservation, journaling, and Undo remain separate acceptance work.
