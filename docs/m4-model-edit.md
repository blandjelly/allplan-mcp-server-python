# M4 — typed model editing: operator guide

This guide describes the `model_edit` contract and its limits; it is not native
acceptance. Current state and priorities are in the
[handoff](next-model-handoff.md) and the [development plan](development-plan.md).
Also read the [Allplan 2026 API evidence](m4-attribute-api-evidence.md) and the
[tool contract](tool-reference.md).

## Instructions for the agent

The user states the intent in plain language (usually Polish); they do not
need to write JSON or know identifiers. The agent first resolves the requested
exact field with a single `model_property_probe` in the `attribute_name`
phase, then uses the returned ID and confirms the name–ID roundtrip. Never
guess an ID or pick a similar-sounding field. If the exact field, its type or
owner cannot be confirmed, stop the plan without writing.

To review attribute values on one element use the separate
`element_attributes` phase: it requires an active drawing and exact non-zero
`model_uuid` and `view_uuid`; it returns paged `ReadAll` values and targeted
name/type metadata. It is not a catalogue of project definitions. An attribute
missing from `ReadAll` stays unknown, and the list does not prove writability.
Paging and response details are in the
[phase contract](tool-reference.md#model_property_probe--isolated-read-phases).

Example user instructions (as the owner would type them):

- „W otwartych rysunkach znajdź słupy bez dokładnego atrybutu *Klasa odporności
  ogniowej*. Zaplanuj wartość `F120` i przypisz warstwę organizacyjną `W1`."
  (In open drawings find columns without the exact attribute *Fire resistance
  class*; plan the value `F120` and assign organizational layer `W1`.)
- „Na elementach z dokładnie nieobecnym atrybutem *Materiał konstrukcyjny*
  dodaj wartość `Beton C37`; nie zmieniaj natywnego materiału ściany."
  (Add `Beton C37` where *Structural material* is provably absent; do not
  change the wall's native material.)
- „Zmień istniejącą wartość atrybutu *Materiał* na `Beton C37` wyłącznie tam,
  gdzie obecna wartość została odczytana i filtr pasuje." (Replace an existing
  *Material* value only where the current value was read and the filter matches.)
- „Znajdź wyłącznie drzwi, nie okna, i zaplanuj zmianę wskazanego atrybutu."
  (Find doors only, not windows, and plan a change of the named attribute.)

In the first example the agent must resolve the attribute name before building
the `is_unset` criterion. An attribute predicate is passed as
`attribute:<ID from the current probe>`, not as the name text. For a missing
attribute the agent explicitly chooses the `all_and_computable` read; it
distinguishes absence from an attribute omitted by plain `ReadAll`. The read
must succeed for the full scope. An error, incomplete coverage or an unknown
state stays `unknown` and blocks Apply. Existing `ReadAll` paths are unchanged.

`is_unset` covers a read empty/`null` value and absence proven by
`ReadAllAndComputable`; it never equates a read error with absence. The known
value `<niezdefiniowany>` ("undefined") is text unless an explicit rule says
otherwise; the criterion must decide separately whether it means absence.
`model_query` also offers an explicit read-only
`attribute_read_mode=all_and_computable` for named IDs. It can return
`computed_only=true`; such a result is not a writable attribute. `stored`
remains the default, and the read mode is part of the source fingerprint.

## Targets and field separation

`model_edit` writes an explicitly bound attribute through
`ElementsAttributeService.ChangeAttributes`, the organizational layer through
`ElementsLayerService.ChangeLayer`, or the native material through the
properties of the existing SDK object and `ModifyElements`. Attribute names and
layers require a name–ID roundtrip. The tool does not create attribute or
layer definitions; it can add an existing attribute definition to an element.

The "Material" attribute, the native material, the visual surface and the
organizational layer have separate bindings. Native material uses
`target={"kind":"native_material","tier_index":1}` and an exact string.
Supported: Wall with one native tier, Column, Beam/SkeletonBeam and
Slab/MultiSlab. The SDK representation is checked at read time. The Wall owner
is `WallTierProperties(1)`; for the other families the selected object's
properties: `ColumnProperties`, `BeamProperties`, `StructuralBeamProperties` or
`SlabProperties`. For a slab there is no redirect to the parent, a child or
`SlabTierProperties`. A single Slab child under a MultiSlab is targeted with the
opt-in `exact_target` ([contract](m4-editing-api.md#exact-child-native-material-target-0420)).

A slab attribute can explicitly set `target.property_owner="selected_element"`.
Narrow `native_types` to the intended Slab or MultiSlab and check its exact
ref, view, lineage and children in the plan. The slab material shown in the
Allplan UI is the MultiSlab's attribute 508, so "change the slab material"
targets `MultiSlab_TypeUUID`. A Slab tier inside a MultiSlab is not shown in
the UI; without `exact_target` on its parent-edge view (one `attribute_id`
replace) it is blocked as `slab_tier_not_shown_in_ui_use_multislab`, and the
blocked row's `ui_owner` names the MultiSlab to preview instead (0.47.0,
[contract](m4-editing-api.md#slab-tier-attribute-writes-and-the-ui-material-owner-04500460-observations-0470-contract)). One plan must not cover both an
aggregate and its layer. **Correction (owner, 2026-11-04):** the tier is shown in the palette's
"Warstwa bieżąca" mode; the block name and this guidance are to be replaced by
a whole-object/current-layer choice ([plan item 3](development-plan.md#remaining-work-and-unresolved-errors)).
The code still behaves as described. A missing owner still blocks attributes of the
aggregate and its child slab; organizational layers keep separate ownership
limits.

Material read and safe-write availability are separate results.
`criteria.operation_eligibility_failures` shows owner/setter blockers and
`criteria.required_field_failures` unread required target fields. Geometry,
formatting and auxiliary metadata are observed independently when the SDK
exposes them. Unavailable optional evidence is explicitly `not_checked`; every
obtained piece of evidence is compared before the write and at fresh readback.
This does not prove preservation of all hidden properties.

A mismatch before the write blocks the setter. An unknown result after the
write requires recovery with the same `execution_id`, without repeating the
setter. Details are in the [API notes](m4-editing-api.md); acceptance state
and the next step are in the [handoff](next-model-handoff.md).

For every `model_edit` bind, the 0.27.0 resolver checks bounded name variants:
the given form, trim/NFC, first letter upper case, all upper case and all
lower case. Every hit must pass a real name–ID roundtrip; a casefold match is
accepted only with a single ID. A conflict rejects the binding. There is no
fuzzy search or catalogue. The read-only `attribute_name` probe still starts
with an exact lookup and uses the shared resolver only after a
`ValueError`/`TypeError` lookup miss.

A value has type `text`, `integer`, `real` or `boolean`. The default
`value_type=auto` picks it from the exactly bound attribute's type and the
loaded SDK; text is never parsed or converted. A manual type is also bound to
`GetAttributeType` for the exact ID and a real SDK member (`String`,
`Integer`, `Double` or `Boolean`); no guessed codes. Enums are handled only by
an explicit `value_type=enum` with an exact label. The SDK must confirm type
`Enum`, `Integer` or `String`; the label is resolved with
`GetEnumIDFromValueString` and `GetEnumValueStringFromID` with a label/key
back-check. There is no `GetEnumValues` or catalogue enumeration; the setter
value and readback remain the label, and the hash also binds the enum key and
label. `auto` never infers an enum from input text. Dates remain unsupported.
A matching type does not confirm writability in Allplan.

Attribute modes:

- `replace` requires a read existing value.
- `add` requires absence proven by `ReadAllAndComputable`.
- `upsert` replaces a read value or adds the attribute only with the same
  absence proof.

If absence must be handled, `replace` does not mean add. The plan shows
separate `add_attribute` and `set_attribute` operations; the layer is a
separate operation. The first example therefore has two changes: value `F120`
in the exact attribute and layer `W1`.

## Scope, plan and write

The default read covers `open_drawings`, including passive open files.
Supported semantic groups are Column, Beam (including SkeletonBeam), Wall,
Slab (including MultiSlab) and opening. The last group uses the documented
`WindowDoor_TypeUUID`; it means an opening but does not decide whether it is a
door or a window. Guessed `Window_TypeUUID` or `Door_TypeUUID` are not used.
The optional predicate `opening_kind=door|window` resolves the subtype through
`GetElement(adapter)` and the documented classes
`DoorOpeningElement`/`WindowOpeningElement`. If the native representation is
unavailable or does not match these classes, the result is `not_checked` and
the filter cannot be complete. This path relies on API documentation and needs
a separate native trial; it is not acceptance of door/window editing. The
agent restricts types to `WindowDoor_TypeUUID` and combines the predicate with
the `opening` family; it never substitutes independent guessed adapter types.
Other types are out of scope. Families, states and criterion fields are in the
[`model_edit` contract](tool-reference.md).

A plan is complete only with full scope coverage and criterion fields without
`unknown`. Limits: at most 32 real changes, 16 fields per request, 32 read
attributes, 10,000 adapters and a 5-second cooperative scan budget. Matched
elements without changes may remain highlight targets. Highlight presents
results; it is not a native selection and does not change the model.

Preview and revalidate are read-only. Before Apply the agent shows the scope,
number of changes, every field, old and new value, exceptions and coverage.
Apply requires the exact `plan_id`/`plan_hash`, a new `execution_id` and the
acknowledgement `disposable_copy_reviewed_plan`. Before setters the executor
resolves every target again and checks old values; it saves a durable record
ahead of the write and performs a fresh readback after the setter. Replaying
the same `execution_id` never repeats setters. A failure or lost reply gives
`unknown` until explicit recovery and a read.

After preview the agent judges Apply availability from the public
`apply_available`. `evaluation_apply_available` is its compatibility alias;
`production_apply_available=false` separately says production writes are not
available. Missing native acceptance does not by itself disable an eligible
Apply on this experimental path. Never present such a write as natively
accepted. After the user agrees, the agent proceeds when `apply_available=true`
and the exact plan binding, the `disposable_copy_reviewed_plan`
acknowledgement, fresh revalidation, execution ID and other Apply guards are
met. If a condition is not met, the agent names that specific gap; it does not
justify a block by the lack of production writes or native acceptance.

Writes are limited to one active foreground drawing. With several open files
the read may cover more files, but a multi-file Apply is blocked before
setters. There are no hidden partial writes or automatic batches. Only
`preview_ready` with 1–32 changes is allowed. Multi-file operations, batches
and results above 32 changes are not done (see the
[scaling analysis](implementation-plan.md#scaling-analysis-of-developm4-and-mcp-ergonomics)).

## MCP argument example

The user does not send these objects. The agent builds them from a natural
instruction after probing the exact name and uses the returned ID without
hard-coding. The fragment shows only two explicit write targets:

```json
{
  "schema_version": "m4-model-edit-1",
  "action": "preview",
  "scope": "open_drawings",
  "native_types": ["Column_TypeUUID"],
  "attribute_read_mode": "all_and_computable",
  "predicate": {
    "field": "attribute:<ID_RETURNED_BY_PROBE>",
    "op": "is_unset"
  },
  "changes": [
    {
      "target": {"kind": "attribute", "name": "Klasa odporności ogniowej"},
      "value_type": "text",
      "value": "F120",
      "mode": "upsert"
    },
    {"target": {"kind": "layer", "short_name": "W1"}}
  ]
}
```

`<ID_RETURNED_BY_PROBE>` is a placeholder filled in by the agent, not a
literal JSON value or an ID typed by the operator. MCP receives the numeric ID
from the exact probe in the same document. If the binding does not return one
certain result, no plan is created. The agent sets the value type; agreement
with type metadata and writability must be confirmed before a native trial.
