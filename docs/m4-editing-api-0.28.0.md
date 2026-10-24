# M4 editing API evidence for 0.28.0

Research date: 2026-10-23. This note records what the Allplan API material
and the official `NemetschekAllplan/PythonPartsExamples` repository document
for native selection, parent identity, and date/vector attributes. API
signatures and example code are evidence of a call path, not proof of its
runtime behavior, target ownership, readback, or safe Allplan acceptance.

## Selecting existing query results

The official
[`GetObjectByAttributeValue.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ObjectAccessExamples/GetObjectByAttributeValue.py)
gets adapters from `ElementsByAttributeService.GetElements`, then calls
`HighlightService.HighlightElements` and redraws. It documents a concrete way
to find and visually highlight attribute matches. It does not put those
adapters into Allplan's native UI selection state or read that state back.

The official
[`SlopedGeneralOpening.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/Objects/SlopedGeneralOpening.py)
uses `SelectElementsService.SelectByPolygon` with a user-created polygon and a
type query, then highlights the returned adapters. This is a documented
geometry-query path, not a general setter for an arbitrary adapter list in
the native selection state.

The official
[`SelectObjectsByAttributeID.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/SelectObjectsByAttributeID.py)
and
[`Equal.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/GeometryExamples/Operations/Comparison/Equal.py)
start `InputFunctionStarter.StartElementSelect`, consume the user's picks with
`PostElementSelection.GetSelectedElements`, and then use the adapters. The
attribute-ID example highlights those user-picked adapters. This is a
candidate for a separate user-driven interaction if that is the intended
product behavior; it does not select a previously computed M4 query result
list.

The examples reviewed here provide query, highlight, and user-pick paths. They
do not document a call that sets an arbitrary existing query-result list as
the native selected set and verifies that set. A negative example search is
not proof that the SDK has no such API. Until an exact setter, matching clear
and readback behavior, and a narrow native trial are documented, M4's existing
highlight route must not be described as native selection or used to enable it.

## Model identity and parent edges

M1's query groups adapter records by `(drawing_file, model_uuid)` and retains
each observed `view_uuid` separately. It coalesces records for one model only
when their returned fields agree; a disagreement is a representation
conflict. See [`model_query.py`](../python_host/PythonPartsScripts/PythonHost/model_query.py)
and [`identity_probe.py`](../python_host/PythonPartsScripts/PythonHost/identity_probe.py)
for the `model_identity` inventory contract.

The 0.28.0 typed-delete candidate uses the same distinction for parent edges:
`same_model_identity` compares drawing number, signed drawing number, model
UUID, and native type name/UUID while excluding view UUID. The exact selected
target view UUID remains bound separately, and each recorded edge retains the
actual parent view UUID observed from the SDK. The rule permits a parent edge
to match the same model-level identity through a different view UUID, while
preserving the observed edge identity. See [`component_ownership.py`](../python_host/PythonPartsScripts/PythonHost/component_ownership.py)
and [`model_delete.py`](../python_host/PythonPartsScripts/PythonHost/model_delete.py).

This comparator is consistent with M1's model-group/view-representation data
model; it does not establish durable physical identity or explain a particular
native mismatch. The
[0.27.0 owner log](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-owner-observation-0.27.0-2026-10-23.md)
reports `component_child_owner_mismatch` for three Column previews and a separate
Slab/MultiSlab lineage conflict, but it does not retain raw MCP responses or
an Allplan build identifier. The exact native cause remains unconfirmed. The
parent-edge comparison therefore needs the scoped 0.28.0 native Column trial
and complete fresh subtree readback before it can be treated as accepted.

## Date and vector values

The 2026 element-attributes manual documents an `AttributeDate(id, day, month,
year)` value in an `AttributeSet` passed to `AllplanElement.SetAttributes`.
The generated API also exposes writable day, month, and year fields on
[`AttributeDate`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/).
This documents a typed attribute-container path for an `AllplanElement`. It
does not show how a date is represented by the current M4 JSON contract or
accepted by adapter-based `ElementsAttributeService.ChangeAttributes`, and it
does not show a fresh readback of that date from an existing target.

The immutable official
[`ChangeAttributes.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/InteractorExamples/GeneralModification/ChangeAttributes.py)
example was fetched at commit
[`8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/commit/8e2c252477e20bc9afac8918f78a8eeabd473a81).
It demonstrates `ElementsAttributeService.ChangeAttributes` on adapters picked
by an interactive selector, with `(attribute ID, attribute value)` pairs
produced by `BuildingElementAttributeList`. The example does not identify a
date payload or read the changed value back. The existence of a generic
`object` value parameter is not a date conversion contract. The current M4
scalar/enum route relies on separate runtime type binding and exact readback;
it does not support a date value by implication.

The API reference documents
[`AttributeDoubleVec`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
with `VecDoubleList`. This is an attribute representation. Geometry
[`Vector3D`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_Geometry/Vector3D/)
and its coordinate access describe a geometric vector and do not prove a codec
for a vector-valued attribute. No `AttributeDoubleVec`/`VecDoubleList`
existing-adapter setter and exact readback example was found in the official
examples reviewed. That search result is limited evidence, not proof that no
such API exists.

Date and vector writes remain blocked until an exact supported owner and
adapter path, accepted native payload, and fresh typed readback are established
for a specific family. A candidate must also preserve unrelated fields and
geometry, retain the existing journal/recovery guards, and receive its own
narrow native trial including UI Undo. The documented payload classes alone
do not enable the current route.

## Sources

- [2026 element-attributes manual](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
- [ElementsAttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
- [AttributeDoubleVec API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
- [Official examples at immutable commit `8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/tree/8e2c252477e20bc9afac8918f78a8eeabd473a81)
