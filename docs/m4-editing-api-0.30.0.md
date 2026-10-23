# M4 API evidence and limits for candidate 0.30.0

Research date: 2026-10-23. Candidate 0.30.0 adds bounded read evidence for
requested attribute IDs and explicit zero-setter evidence for no-op
`model_edit` plans. It does not add a date/vector setter, native selection
set/clear/readback, or a Slab/MultiSlab field-owner adapter. It is deliberately
partial; full completion of priorities 1–5 remains the goal and is blocked by
the missing field-owner, date/vector payload, and selection set/clear/readback
contracts. The combined candidate gathers evidence to help establish them,
without claiming that evidence itself completes those contracts. Previously
accepted scopes remain accepted.

## `attribute_evidence` probe

The new `model_property_probe phase=attribute_evidence` is a diagnostic read
for one exact foreground drawing/model/view identity and 1–16 unique observed
attribute IDs. It binds a complete `model_identity` scan, considers at most 16
exact-view wrappers and may read the immediate parent when requested. It
reports ancestry and children observations independently; each wrapper has
separate stored `ReadAll` and `ReadAllAndComputable` observations, native
representation type, and runtime type binding for requested values. JSON
scalars/sequences remain values with runtime types; unknown objects are
type-only `not_checked`, without `repr`, coercion, or guessed codec. Output is
bounded to 512 KiB.

The probe can provide evidence about exact identities and currently observed
values. It does not prove that an adapter owns a field or that a setter accepts
the value. A matching loaded SDK member is type metadata, not writable-owner or
setter-payload evidence. In particular, a complete ancestry response plus a
failed children read must be reported as those independent observations; it
does not establish the Slab/MultiSlab field owner.

The response includes `evidence_complete`. `state=observed` requires wrapper
consensus and complete requested raw rows, metadata, ancestry, children, and
native representation reads. Partial data remains in the response with
`state=not_checked`; it is diagnostic evidence, not complete proof. Type
binding reports `binding_status=matched`, `ambiguous`, or `unresolved` against
actual loaded SDK members. The 512 KiB result budget and exact wrapper limit
remain in force.

## Slab and MultiSlab ownership

The pinned official
[`ModifySlab.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifySlab.py)
resolves a selected adapter, casts to `SlabElement`, reads and changes its
`Properties`, then calls `ModifyElements`. It demonstrates a Slab property
workflow. It does not say that a child adapter owns M4 project attributes or
that a MultiSlab aggregate owns the same fields. The new probe narrows structural
and value evidence for exact targets but cannot decide this ownership question.
Keep Slab-child and MultiSlab writes blocked until a specific owner and
preservation contract are established, followed by typed readback and Undo for
that route.

## Native UI selection

The documented surfaces remain distinct: `SelectElementsService` geometry
queries, `ElementsSelectService` document/IFC queries,
`PostElementSelection` for a user-pick interaction, and `HighlightService` for
visual highlighting. Pinned
[`GetObjectByAttributeValue.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ObjectAccessExamples/GetObjectByAttributeValue.py)
queries and highlights; pinned
[`SelectObjectsByAttributeID.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/SelectObjectsByAttributeID.py)
uses an interactive user-pick path. These examples do not establish a setter
that replaces/clears the arbitrary query-result set as native selection and
reads those exact selected adapters back. A response of `unsupported` for
`model_selection(action=select)` is not selection support; highlighting stays
a separate presentation operation. No setter is added in 0.30.0.

## Date and vector attribute payloads

The 2026 [`AttributeDate` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
documents a typed date representation for an `AllplanElement.SetAttributes`
path. The
[`AttributeDoubleVec` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
documents a vector-valued representation. Neither signature specifies an
accepted payload for the existing adapter-based
`ElementsAttributeService.ChangeAttributes` route or its fresh typed
readback. The pinned generic
[`ChangeAttributes.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/InteractorExamples/GeneralModification/ChangeAttributes.py)
does not demonstrate either value family. The new probe can report requested
IDs, matching SDK members, runtime types and raw JSON-representable values; it
cannot establish a date/vector encoder or setter contract. Keep these writes
blocked, and report an absent concrete definition as `fixture_missing` rather
than a pass.

## Bounded no-op evidence

For a complete eligible preview with no setters, `model_edit.preview` reports
`state=no_op`, `setter_calls_started=0`, and `no_op_evidence`: a reason
(`already_at_requested_values` or `no_matching_targets`), matched-target
count, up to 32 fresh field observations, `observations_complete`, and the
source fingerprint. A successful unchanged `revalidate` returns fresh no-op
evidence; changed criteria invalidate the plan and return conflict. There is
no Apply route for no-op. This provides explicit evidence that this plan did
not start setters;
it does not prove general setter safety or native acceptance of another
operation.

## Scope of acceptance

The trial plan at [0.30.0](m4-single-drawing-0.30.0.pl.md) exercises all
available priority 1–5 paths in one session and records blocked work
explicitly. Existing supported scalar/Enum writes may be tried on concrete,
previously unaccepted family/type fixtures when those definitions and safe
targets exist. The probe itself does not expand write support. This note is API
evidence, not CI, package, owner-trial, or native acceptance; the new probe,
no-op route and any newly exercised family still require their own results.

## Sources

- Official examples at immutable commit
  [`8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/tree/8e2c252477e20bc9afac8918f78a8eeabd473a81)
- [AttributeDate API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
- [AttributeDoubleVec API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
- [ElementsAttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
- [UndoRedoService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/UndoRedoService/)
