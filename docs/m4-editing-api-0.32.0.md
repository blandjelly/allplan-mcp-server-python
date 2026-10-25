# Native material editing — candidate 0.36.0

## Request and native property owner

The public request remains
`target={"kind":"native_material","tier_index":1}` with an exact nonempty
material string. It is an exclusive plan change. The result field is
`native.material`; the plan binds its native evidence as
`resource.native_material_state`.

The eligible root is a standalone `Wall_TypeUUID` represented by
`WallElement`, or a standalone `Column_TypeUUID` represented by
`ColumnElement`. A Wall must have `WallProperties.TierCount == 1` and uses
`GetWallTierProperties(1).Material` / `SetMaterial`. A Column uses its
`ColumnProperties.Material` / `SetMaterial`. Both routes mutate the existing
represented native object, call `SetProperties` with its properties, then
submit that object through `ModifyElements`. A missing enumerated tier child
does not disqualify a single-tier Wall when its native properties report one
tier. Multi-tier Walls and other element families are outside this candidate.

The API basis is the 2026 [WallElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallElement/),
[WallProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallProperties/),
[WallTierProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallTierProperties/),
[ColumnElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ColumnElement/),
[ColumnProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ColumnProperties/),
and shared [ArchBaseProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ArchBaseProperties/)
references. The general [element modification guide](https://pythonparts.allplan.com/2026/manual/features/model_access/element_modification/)
documents submitting an existing native element through `ModifyElements`.
These API contracts do not establish that a particular Allplan build accepts
the write or preserves every hidden property.

## Required checks and optional preservation evidence

Eligibility requires an exact standalone root identity and native type,
readable current material, the matching native setter, an active foreground
drawing, and the existing write, journal, revalidation and recovery guards.
Wall tier count must be exactly one. These are required even when optional
preservation observations are unavailable.

Tier geometry does not have to be a `Polyhedron3D` or report `IsValid()`. A
bounded `WriteToStream` digest is retained when available; unavailable or
unsupported geometry is recorded as `not_checked`. Formatting properties,
axis representation, metadata values and auxiliary hierarchy are also
observed independently where supported. An unavailable field becomes
diagnostic `not_checked` evidence rather than blocking the native material
preview. Available evidence remains in the state fingerprint and is compared
during revalidation and fresh readback. A changed observation conflicts before
setters; drift or incomplete required readback after a write leaves the result
unknown. Recovery uses the original execution ID and never retries setters.

Completed Wall hierarchy/component observations remain in partial evidence if
a later optional detail fails. Property reads are independent. Across live
views, consensus covers the required native value and structural owner; the
chosen exact view retains its own preservation fingerprint. Other views'
different optional coverage is not a material-value conflict. A failed complete
Column child inventory reports a diagnostic; it cannot prove preservation of
unread children.

The standard Material attribute ID 508 is excluded from unrelated metadata
invariants because it may mirror the native material being changed. This does
not write attribute 508 or bind an attribute target. Generic typed attribute
edits remain a separate `ChangeAttributes` route. Historical 0.27.0 owner
notes report changing `Materiał` on two Slab representations, but the stored
chat log has no request payload or attribute ID; later read-only evidence
shows ID 508 as a String with value `beton zbrojony` on Slabs without a live
name/ID roundtrip. This does not establish that a Material attribute changes
native material or that the attribute route was accepted for Wall or Column.
`Materiał łatwopalny` is a separate attribute (ID 1371).

## Execution and acceptance boundary

The Wall observation retains both native/property owner sets through the
optional reads and uses the tier returned with the detailed observation's
native object and properties. It retains the independent material comparison
between the two reads. This corrects mixed-owner use in 0.35.0; it does not
establish that borrowed-wrapper lifetime caused the native crash. Nested
material trace entries are described in [diagnostics](diagnostics.md).

The requested string is used exactly; there is no catalog lookup, existence
claim, alias resolution, surface edit or attribute substitution. The same
native root object is submitted with its updated properties. Exact target
binding, plan hashes, fresh pre-write revalidation, journal safeguards,
post-write readback and unknown-result recovery remain in force. Automated
checks and API availability do not establish native Allplan acceptance.

The 0.35.0 evidence confirms one Column Apply/readback and three interrupted
Wall material previews followed by native access violations. Their underlying
cause remains unproven, and neither old heap-corruption dump diagnoses those
events. The next check is limited to a Wall preview after CI and exact-ZIP
verification; see the [handoff](next-model-handoff.md). Prior material
observations and their limits remain in [validation status](validation-status.md).
