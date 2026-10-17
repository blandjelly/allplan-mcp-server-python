# M4 agent test: Allplan API evidence

This note records public Allplan 2026 Python API documentation relevant to the
uploaded agent-test conversation. It is documentation research, not a native
Allplan experiment. The upload contains assistant/user prose but no bridge
request/response payloads or native trace, so the reported values and setter
behavior cannot be independently established from it.

## Wall layer target

The [2026 read-access guide](https://pythonparts.allplan.com/2026/manual/features/model_access/read_access/)
describes the hierarchy services `BaseElementAdapterParentElementService` and
`BaseElementAdapterChildElementsService`. It says an unfiltered selection of a
wall commonly yields a `WallTier_TypeUUID` adapter; the tier's parent is the
whole `Wall_TypeUUID` wall. It demonstrates `GetParentElement(selected_wall_tier)`
and `GetChildModelElements(...)`, and separately notes that wall geometry is
accessed through its tiers. The same guide warns that not every adapter type
has a Python object representation.

The [2026 ElementsLayerService reference](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsLayerService/)
documents only:

```python
ChangeLayer(elements: BaseElementAdapterList, newValue: str) -> BaseElementAdapterList
```

It does not document an `inclChildren` option. The [format properties guide](https://pythonparts.allplan.com/2026/manual/features/format_properties/)
also says existing `BaseElementAdapter` common properties can currently be
modified generically only for layer, using a `BaseElementAdapterList` and the
target layer short name.

**Candidate diagnosis, inferred from those docs:** passing a wall root adapter
to `ChangeLayer` can address the wrong hierarchy node for a multi-tier wall.
The evidence-based candidate is to identify the wall's actual tier adapters
through the documented hierarchy and submit the intended tier adapter(s) to
`ChangeLayer`, while retaining the wall's model UUID as the transaction owner.
Read back each tier's common-property layer from freshly resolved adapters.
Do not target a `WallAxis_TypeUUID` child or reconstruct wall geometry. The docs
do not prove this candidate will write successfully on the user's model; it
needs a narrowly scoped disposable-copy native trial. There is no documented
root-to-child propagation flag on `ChangeLayer`.

The [2026 `WallElement` reference](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallElement/)
documents `SetCommonProperties(CommonProperties)` and `SetProperties(WallProperties)`.
The general [element modification guide](https://pythonparts.allplan.com/2026/manual/features/model_access/element_modification/)
describes getting an API object from an adapter and persisting specific object
changes with `AllplanBaseElements.ModifyElements(doc, [element])`. Neither page
documents that rebuilding/replacing a wall's common properties is required to
change its layer, nor does it establish that path as safe for preserving wall
tiers and axis. Treat it as a separate native experiment, not the immediate
fix for the root-adapter no-op.

## Explicit undefined attribute values

The [2026 ElementsAttributeService reference](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
documents these exact signatures:

```python
ChangeAttribute(
    attributeNumber: int,
    newValue: object,
    elements: BaseElementAdapterList,
    setUndefAttrib: bool = False,
    setDeleteAttrib: bool = False,
) -> BaseElementAdapterList

ChangeAttributes(
    attributeDataList: list,
    elements: BaseElementAdapterList,
    setUndefAttrib: bool = False,
    setDeleteAttrib: bool = False,
) -> BaseElementAdapterList
```

The [2026 element-attributes guide](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
distinguishes setting an attribute to `<undefined>` (`setUndefAttrib=True`)
from deleting the attribute (`setDeleteAttrib=True`). For example, the single
attribute call uses an empty string value with `setUndefAttrib=True`. These are
native attribute-service operations, documented for existing model-element
adapters; they are not a Python `None` value or an inferred numeric sentinel.

## Material scope

The read-access guide's example lists attribute **508 Material** among a wall's
readable attributes. That establishes an attribute value exists, not that
changing that attribute changes the native construction/material definition
used by an architectural element. The [2026 ALLPLAN elements guide](https://pythonparts.allplan.com/2026/manual/features/allplan_elements/)
models a multilayer wall using `WallElement` and wall-tier properties. The
documentation found here does not provide a general existing-wall native
material setter applicable to “set material to Stal.” Attribute 508 should
therefore remain distinct from native material binding; require a specific
documented tier/material property path and readback in Allplan before enabling
that operation.

## Supplied log: scope of evidence

The uploaded [agent test log](test-results/evidence/m4-agent-test-2026-10-17.md)
reports two layer attempts against a 200 mm wall and readback layer 3735 after
requests for `W1` and `SZ_OGÓ02` (ID 3701). It also reports `<niezdefiniowany>`
for numeric attribute “Wartość U” on two walls. This supports the investigation
targets only; it is not raw API evidence, does not identify exactly which
adapter UUID(s) were submitted, and does not demonstrate the cause of either
result. Keep the existing broad native metadata/property-discovery quarantine
unchanged.
