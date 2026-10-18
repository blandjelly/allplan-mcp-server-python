# M4 attribute type coverage and safe expansion

Research date: 2026-10-18. This note combines the official Allplan 2026 API
contracts cited in [the API evidence note](m4-attribute-api-evidence.md) with
the current M4 implementation. It describes representability and safety
boundaries; it is not native Allplan acceptance.

## What the current route represents

`model_edit.bind_changes` resolves an explicitly named or numbered attribute,
round-trips its ID and name, and compares `GetAttributeType` with members on
the loaded SDK. `value_type="auto"` selects a matching text, integer, real, or
boolean scalar type from that targeted metadata. Explicit scalar types are
also accepted when they match the same runtime members. At native execution,
the attribute read must also be a bounded JSON scalar and replacement must
agree with the bound type (with the existing narrow undefined-value
exception). The setter sends one `(attribute ID, value)` pair through
`ElementsAttributeService.ChangeAttributes`.

The four current value types therefore have a generic route only when the
runtime SDK exposes the corresponding `String`, `Integer`, `Double`, or
`Boolean` member and the observed old value can be handled under the same
contract. The code compares actual SDK members; it does not assume numeric enum
codes. The generated API reference documents `GetAttributeType` as returning
`AttributeType`, but does not publish its members or numeric values. Thus the
four names are an implementation binding to the installed SDK, not a complete
official enumeration of every Allplan attribute type.

`ChangeAttributes` is documented as taking `(attribute number, value)` pairs,
and the manual says it appends a missing attribute. This establishes the call
shape and add-or-set behavior, but does not establish that every Python scalar
is accepted for every attribute definition. The current path stays bounded to
types whose runtime enum member is checked and whose stored value is a scalar
already representable by the bridge. Readback, pre-write revalidation,
foreground and identity checks, journal safeguards, and the existing narrow
attribute count limits still apply.

## Officially documented value families beyond the current route

The 2026 element-attributes manual names `AttributeDate` and `AttributeEnum`
alongside `AttributeString`, `AttributeInteger`, and `AttributeDouble`. It
documents attribute reads as `(int, int | float | str)` and says an enum read
returns its display string rather than its key. The manual also documents
`GetEnumIDFromValueString`, `GetEnumValueStringFromID`, and
`BuildingElementAttributeList`. These are evidence that date and enumeration
values have typed handling and that targeted enum conversion helpers exist.
They are not a universal coercion contract for `ChangeAttributes`, and the
generated `AttributeType` page does not tell us the exact SDK enum members for
all those families.

| Value family | Evidence and representation | Safe generic status |
| --- | --- | --- |
| Text/string | Manual documents `AttributeString`; route compares to SDK `String` and supports bounded strings. | Representable under the current type and readback checks. |
| Integer | Manual documents `AttributeInteger`; route compares to SDK `Integer` and requires an exact Python `int` (not `bool`). | Representable under current checks. |
| Real/double | Manual documents `AttributeDouble`; route compares to SDK `Double`, requires finite numeric input, and supports numeric scalar reads. | Representable under current checks. |
| Boolean | Auto mode supports it only if the installed SDK exposes `AttributeType.Boolean`; the generated docs do not publish the complete enum member mapping. | Runtime-gated scalar support; do not claim universal availability. |
| Enumeration | Read value is display text, not enum key. The implementation accepts explicit `value_type="enum"` only when the targeted runtime type matches a loaded SDK `Enum`, `Integer`, or `String` member and the label/key helper round-trip succeeds. The manual's `ChangeAttributes` example passes the display label in the `(attribute ID, value)` pair. | Implemented as an explicit label codec. It retains the label as the setter payload, stores the key as binding evidence, and requires exact native readback. Auto mode does not infer enumeration values from strings. |
| Date | Manual names `AttributeDate`, but this route's JSON scalar schema and setter have no date format, timezone, calendar, or SDK-object conversion contract. | Not representable by the current scalar contract. Needs an explicit date codec and native evidence. |
| Other/unknown SDK types | `GetAttributeType` is targeted, but the generated docs provide no full member/value inventory; control type is UI metadata and does not prove writability. | Fail closed; never infer type from display text, control type, numeric code, or a failed lookup. |

## Computed and stored values are independent of type

Type compatibility does not establish editability. `ReadAll` omits computed
attributes; `ReadAllAndComputable` includes them. The current requested dual
read marks values present only in the computed-inclusive result as
`computed_only`, and the write adapter rejects them. For adding an attribute,
the explicit absence check requires successful absence from both results; an
omission from `ReadAll` alone is not proof of absence. Preserve those
distinctions for any new type codec. In particular, an enum/date value that is
readable or has metadata is not thereby writable, and neither a UI control
type nor a type enum member is a read-only/computed flag.

The API material cited here does not provide a generic per-attribute
writability query. The actual write attempt and exact readback are the only
available evidence for a supported target in the current flow; failures must
remain failures and must not trigger a fallback to another property route.

## Practical expansion boundary

Automatic type selection is limited to the four scalar codecs gated by the
actual SDK member and a fresh, type-compatible observed value or explicit
computed-inclusive absence evidence. Enumeration remains an explicit codec
because strings alone do not distinguish text from an enum label. Keep both
paths target-specific: resolve only requested IDs or exact names and never
scan the project's attribute definitions or enum tables.

The [attribute codec module](../python_host/PythonPartsScripts/PythonHost/attribute_codecs.py)
provides targeted scalar type resolution and the label→key→label→key binding
check used by the model-edit route. The enum key is evidence only; the API
manual's `ChangeAttributes` sample uses the exact display label as the pair
value. The executor and native adapter both require the enum binding, and the
setter sends the label. This is implemented API-backed behavior, while native
Allplan acceptance of the guarded M4 enum workflow remains separate.

The 2026 API defines `AttributeDate(id, day, month, year)` and the manual
demonstrates date objects in an `AttributeSet` assigned to an `AllplanElement`.
That proves a typed date representation for `SetAttributes`, but it does not
specify a date payload for adapter-based `ChangeAttributes`. Date editing is
unsupported on the current adapter route until a documented or native-verified
conversion and exact readback are established. Do not treat that route limit as
a claim that Allplan cannot edit dates through other API surfaces. Other SDK
families such as byte and vector attributes likewise need their own precise
input, output, and readback codecs; do not broaden JSON scalar validation to
make opaque SDK objects appear generic.

These conclusions do not authorize changing the current native write guards,
raising the 32-attribute read budget, adding broad discovery, editing computed
attributes, deleting or setting undefined values, or claiming office-wide
attribute edit coverage.

## Official references

- [ElementsAttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
- [AttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/)
- [Element-attributes manual](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
- [Attribute Enum API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeEnum/)
- [Attribute Date API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
- [Attribute read-state enum](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/eAttibuteReadState/)
- [Official ChangeAttributes example](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/main/PythonPartsExampleScripts/InteractorExamples/GeneralModification/ChangeAttributes.py)
