# M4 — Allplan 2026 attribute API evidence

Research date: 2026-10-17. Sources are the official [Allplan 2026 Python API
documentation](https://pythonparts.allplan.com/2026/). This note records public
API contracts; it is not native Allplan acceptance.

## Attribute reads and writes

`ElementsAttributeService.ChangeAttributes(attributeDataList, elements,
setUndefAttrib=False, setDeleteAttrib=False)` accepts a list of `(attribute
number, value)` pairs and a `BaseElementAdapterList`, and returns the modified
adapters. The element-attributes manual explicitly says that an attribute not
already on an element is appended. Thus the service is a documented add-or-set
path for a requested ID/value pair. `setUndefAttrib` and `setDeleteAttrib` are
separate modes; ordinary setting leaves both false.

The read state enum is spelled `eAttibuteReadState` in the API. Its documented
values are `DoNotRead`, `ReadAll`, `ReadAllAndComputable`, and
`ReadWithoutGeometry`. `ReadAll` reads attributes without computed ones;
`ReadAllAndComputable` includes computed attributes. Consequently, a missing
key in a successful `ReadAll` result alone is ambiguous: the key may be
computed. If both reads succeed and a key is absent from both lists, it was not
returned in either read. The docs do not specify a status/result that proves
why an attribute was omitted, whether every attribute is applicable to every
element, or how read failures are represented. Therefore absence from a read
must not be inferred after a failed read, an incomplete element snapshot, or
from `ReadAll` alone. An undefined/empty value that is present is also distinct
from an absent key.

This supports an opt-in, requested-attribute presence read using
`ReadAllAndComputable`, provided the caller explicitly permits computed-value
reads and successful completeness is reported. It does not justify changing an
existing `ReadAll` route or converting errors, applicability uncertainty, or
missing adapter coverage into “absent.”

## Opening adapter boundary

The 2026 read-access manual demonstrates one `WindowDoor_TypeUUID` adapter
query for the set of window and door openings. The ALLPLAN-elements manual
separately lists GUI door openings as `DoorOpeningElement` and window openings
as `WindowOpeningElement`. The published pages do not document a mapping from
the shared adapter type to either class or a discriminator that would
reliably classify an opening after adapter resolution. Therefore the generic
query family can be named `opening`; separate door/window targeting remains
unverified. Do not infer undocumented `Door_TypeUUID` or `Window_TypeUUID`
names. A class-based split would need a narrowly scoped native experiment that
resolves a `WindowDoor_TypeUUID` adapter, calls the documented element access
path, and verifies the returned class and owner on representative door and
window instances.

## Targeted metadata and value typing

`AttributeService.GetAttributeID(doc, attributeName)` resolves an attribute by
name; `GetAttributeName`, `GetAttributeType`, and `GetAttributeControlType`
provide targeted metadata for an ID. `GetAttributeType` returns an
`AttributeType` enum, but the generated 2026 API reference documents no enum
members or numeric values. It also exposes no writable, computed, or
read-only flag. `GetAttributeControlType` returns the UI control type, which
does not establish that an element accepts a write. Do not enumerate all
attribute definitions or infer write permission from these methods.

The candidate implementation avoids guessed numeric type codes: after a
targeted `GetAttributeType` call, it compares the result with the corresponding
member exposed by the loaded SDK (`String`, `Integer`, `Double`, or `Boolean`).
That is a runtime compatibility guard for the requested scalar type, not an
officially documented enum-value mapping or proof of writability.

The element-attributes manual documents value representations including
`AttributeString`, `AttributeInteger`, `AttributeDouble`, `AttributeDate`, and
`AttributeEnum`. Adapter reads are typed as `(int, int | float | str)`; the
manual specifically notes that an enumeration read yields its display value,
not its key. Targeted enum helpers (`GetEnumIDFromValueString` and
`GetEnumValueStringFromID`) are documented, as is `BuildingElementAttributeList`
for constructing typed attributes. These APIs provide pieces for conversion,
but do not document a universal input-coercion or writability contract for
`ChangeAttributes`. A write path should resolve the exact requested name in the
current document, inspect its returned type, convert only known supported
types, and treat any type/metadata/read failure as unknown and block the write.
The examples “missing fire resistance → F120 + W1” and “missing material
attribute → Beton C37” must resolve the field names in the active document;
they must not assume attribute IDs from another sample or turn a failed lookup
into absence.

## Native Wall material property path

The official API describes a `WallElement` with a writable `Properties`
property, plus `GetProperties()` / `SetProperties(WallProperties)`. Its
`WallProperties` exposes `GetWallTierProperties(tierIndex)`. A wall tier is a
`WallTierProperties`, which inherits `ArchBaseProperties`; the latter exposes
a writable string `Material` property and `SetMaterial(material: str)`.
Separately, the model-access manual documents the general sequence of getting
the represented Python element from a `BaseElementAdapter` with
`AllplanBaseElements.GetElement(adapter)`, changing a property on that object,
and persisting it with `ModifyElements(doc, [element])`.

This is a plausible isolated route for a simple existing Wall: start with the
existing object returned from its adapter, change only its intended tier
material, and submit that same element object. Preserving all untouched fields
and geometry is an implementation inference from that sequence, not a promise
of the API documentation. The docs do not explain how a changed tier returned
by `GetWallTierProperties` is reattached to `WallProperties`; and they warn
that `ModifyElements` does nothing when no internal modification function is
implemented for the requested change. So this documents an API surface to
probe, not successful material update, geometry preservation, or undo.

## Evidence boundary in this repository

The current handoff records 0.19.0 as accepted for a scoped two-Wall filter and
highlight observation. That run had no setters and reported no model change;
material target binding, writes, readback, and undo remain unverified. The
0.16.0 broad property-discovery native crash remains `FAIL_CRASH` with unknown
root cause, and broad discovery remains blocked. These API findings do not
change either native record or authorize weakening current write guards.

Keep existing accepted `ReadAll` paths and field bindings unchanged. Any new
typed generic attribute route should use narrowly requested names/IDs and
targeted metadata; any computed-inclusive presence check must be an explicit
new option. Keep missing, undefined, computed-only, unreadable, inapplicable,
and unknown states distinct in planning. A native Wall material property trial
is separate from the attribute append route and requires scoped readback and
geometry evidence before being described as supported.

## Primary sources

- [ElementsAttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
- [Attribute read-state enum](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/eAttibuteReadState/)
- [AttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/)
- [Element-attributes manual](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
- [ArchBaseProperties API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ArchBaseProperties/)
- [WallElement API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallElement/)
- [WallProperties API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallProperties/)
- [WallTierProperties API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallTierProperties/)
- [Read-access manual](https://pythonparts.allplan.com/2026/manual/features/model_access/read_access/)
- [ALLPLAN element types and capabilities](https://pythonparts.allplan.com/2026/manual/features/allplan_elements/)
- [Element-modification manual](https://pythonparts.allplan.com/2026/manual/features/model_access/element_modification/)
- [ALLPLAN element types and capabilities](https://pythonparts.allplan.com/2026/manual/features/allplan_elements/)

