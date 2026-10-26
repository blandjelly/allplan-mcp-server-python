# Native material editing — API contracts

## Native Material, material attribute and Surface

Sources reviewed **2026-10-26** for the Python API **2026**; GUI references
below identify their 2026-0/2026-1 version explicitly. This section separates
published SDK contracts, native observations and hypotheses. Current delivery
and acceptance belong in the [handoff](next-model-handoff.md).

| Requested field | API owner and persistence route | What success establishes |
| --- | --- | --- |
| Native architectural Material | `ArchBaseProperties.Material: str`, `GetMaterial()` / `SetMaterial(str)` on the actual property owner. Reattach the properties to the existing element and submit it with `ModifyElements`. | Only a fresh native read from the same owner establishes the retained native value; method availability alone does not. |
| Element attribute named Material / Materiał | Resolve the element's exact name↔ID/type; `GetAttributes` reads ID/value pairs and `ElementsAttributeService.ChangeAttributes` writes them through the selected adapter. The official read-access example identifies standard Material as ID 508. | Typed attribute readback establishes that attribute value on that owner. The supplied 0.39.0 log omits its actual ID/payload. This is an element attribute, not the separate document/project-attributes API. |
| Rendering Surface | `ArchBaseProperties.Surface` / `SetSurface`, separate from Material; GUI surface controls affect animation appearance. | A surface/texture result, not a structural material assignment. The current native-material operation does not target Surface. |

The [ArchBaseProperties reference](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ArchBaseProperties/)
defines Material and Surface separately. The
[read-access manual](https://pythonparts.allplan.com/2026/manual/features/model_access/read_access/)
and [element-attributes manual](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
establish the attribute path. These are distinct API entry points; the sources
do not promise independent storage or universal bidirectional synchronization
of native Material and attribute 508. Equal displayed values may reflect the
same architectural information. Neither equality nor attribute-write success
proves that the native-property setter persisted on the same owner.

### Beam, StructuralBeam and Slab contracts

- **Ordinary Beam:** [BeamProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/BeamProperties/)
  derives from ArchBaseProperties, so Material is inherited even when absent
  from the page's own-member list. [BeamElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/BeamElement/)
  exposes `Properties` / `SetProperties`.
- **Structural framing beam:** [StructuralBeamProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/StructuralBeamProperties/)
  lists ArchBaseProperties among its bases. [StructuralBeamElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/StructuralBeamElement/)
  exposes `StructuralBeamProperties` / `GetStructuralBeamProperties()` /
  `SetStructuralBeamProperties`. This differs from the ordinary Beam accessor;
  a SkeletonBeam adapter still needs runtime class/owner confirmation.
- **Slab:** [SlabProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabProperties/)
  documents writable Material plus `GetMaterial` / `SetMaterial`.
  [SlabElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabElement/)
  exposes `Properties` / `SetProperties`. Neither this page nor Material on a
  property object establishes which MultiSlab/Slab adapter owns the stored
  value or that updating its aggregate updates a tier.

The [modification manual](https://pythonparts.allplan.com/2026/manual/features/model_access/element_modification/)
requires get properties → change → reassign → `ModifyElements`; mutating a
nested temporary property alone is insufficient. It also says ModifyElements
can do nothing when an internal modification function is absent. Thus a setter
on a Python object can exist without proving persistence of that particular
change in a particular Allplan build. This is a possible explanation to test,
not a diagnosed cause of the reported Slab failure.

### Why a missing palette field does not establish non-support

The [2026-1 Slab parameters help](https://help.allplan.com/Allplan/2026-1/1033/Allplan/10367.htm)
includes Material selection and links to
[Material/qualities](https://help.allplan.com/Allplan/2026-1/1033/Allplan/10314.htm),
whose choices depend on catalog/qualities configuration. The
[2026-0 Structural framing beam palette](https://help.allplan.com/Allplan/2026-0/1033/Allplan/276259.htm)
places Material/qualities on its Attributes tab and Surface on Representation.
The [2026-1 beam editing help](https://help.allplan.com/Allplan/2026-1/1033/Allplan/254647.htm)
opens that specialized palette by double-click or context Properties and notes
restrictions when editing several beams together. These controls need not be
named "native material". The owner's missing field could involve the palette,
selection, catalog/qualities or selected representation; the log does not
identify which. Do not infer any one cause or promise a UI setting will fix
the bridge's failed update.

### Native result and unresolved inference

The [0.39.0 owner log](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md),
summarized in [validation status](validation-status.md#latest-owner-observations), reports
zero native Beam/SkeletonBeam query matches with representation
conflicts, then successful Material-attribute writes on two SkeletonBeams.
This does not exercise a confirmed native Beam setter. Slab native readback
stayed blank after attempts; later attribute readback matched the requested value on MultiSlab
and its Slab. There is no paired native read after that attribute write, so
the log does not show whether it affected native Material. Owner, persistence
and discovery remain separate unresolved questions. Compare both read paths
on the same exact element/owner first, preserve raw values including blanks,
and retain unknown journal outcomes. Never silently substitute an attribute
write for a requested native-material change. Current closure work is in
[plan items 1–3](office-editing-development-plan.pl.md#dowody-potrzebne-do-zamknięcia-punktów-15).

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
`ColumnProperties.Material` / `SetMaterial`. `Beam_TypeUUID` and
`SkeletonBeam_TypeUUID` support the live `BeamElement` or
`StructuralBeamElement` representation, checked at runtime. `BeamElement` uses
`BeamProperties.Material`; `StructuralBeamElement` uses
`StructuralBeamProperties.Material`. Their element accessors differ: the
`BeamElement` route uses `Properties` / `SetProperties`; the
`StructuralBeamElement` route uses `.StructuralBeamProperties` /
`SetStructuralBeamProperties(properties)`. `GetStructuralBeamProperties()` is
an SDK alias for reading that property; `StructuralBeamElement` does not use
generic `Properties` / `SetProperties`.
`Slab_TypeUUID` and `MultiSlab_TypeUUID` require `SlabElement` and use exactly
`SlabProperties.Material` / `SetMaterial` on the selected element. The Slab
route does not substitute `GetSlabTierProperties(1)` or redirect to another
adapter. A Slab child may have a directly observed MultiSlab parent; other
nested roots remain blocked. `tier_index=1` is retained for request compatibility
and selects a property tier only for Wall. Each route mutates the existing
represented native object, reattaches properties through that element class's
documented setter (`SetProperties` for Wall, Column, Beam and Slab;
`SetStructuralBeamProperties` for StructuralBeamElement), then submits that
object through `ModifyElements`. A missing enumerated tier child
does not disqualify a single-tier Wall when its native properties report one
tier. Multi-tier Walls remain outside this candidate. Parent and child Slab
targets in one plan are blocked as overlapping owners.

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

Additional SDK contracts are [BeamElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/BeamElement/),
[BeamProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/BeamProperties/),
[StructuralBeamElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/StructuralBeamElement/),
[StructuralBeamProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/StructuralBeamProperties/),
[SlabElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabElement/)
and [SlabProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabProperties/).
The 2026 references establish those property/accessor APIs, not a universal
SkeletonBeam-to-class mapping. The [StructuralBeamElement reference](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/StructuralBeamElement/)
documents `.StructuralBeamProperties`, its getter alias, and
`SetStructuralBeamProperties(StructuralBeamProperties)`; do not infer generic
`Properties` / `SetProperties` support from the parallel BeamElement API. The
selected MultiSlab's `SlabElement`
representation was previously reported in the [retained owner log](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md);
runtime class checks remain mandatory. The root and tier Slab material fields
have separate documented owners and are not assumed equivalent.

## Required checks and optional preservation evidence

Eligibility requires the exact supported target lineage, identity and native type,
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
Before any setter, the exact reviewed view and bound property owner must be
available; no substitute view is eligible for the write. The full optional
preservation snapshot is captured on that exact wrapper. Other live wrappers
may contribute required core reads, but native material and bound owner must
agree with the selected wrapper. Preview observation, consensus and setter
preflight each start a separate 10-second material evidence budget, including
trace I/O; they do not reuse an expired M1 scan budget, which remains 5 seconds.
Missing views, owner/material disagreement, or unreadable required evidence
remain blocked or unknown.

After a setter has been issued, Apply readback and recovery remain read-only.
If the exact bound view is unavailable, the bridge attempts a full preservation
snapshot on every currently present wrapper for that same bound property owner.
Unavailable optional fields remain explicit `not_checked`: they neither block
otherwise complete required reads nor prove preservation. Missing/unreadable
required owner or material, or disagreement between wrappers, keeps the result
unknown and recovery blocked. A changed view or observed preservation drift
also stays unknown; the [reviewed reconciliation](#reviewed-reconciliation-of-native-material-preservation-drift)
is read-only. The bridge never binds a replacement setter target or retries
the write.

Completed Wall hierarchy/component observations remain in partial evidence if
a later optional detail fails. Property reads are independent. Across live
views, consensus covers the required native value and structural owner; the
chosen exact view retains its own preservation fingerprint. Other views'
different optional coverage does not invalidate the material value during
prewrite consensus. Ordinary prewrite revalidation remains bound to the exact
selected wrapper and treats its preservation drift as a conflict. After a
write, unavailable optional fields on current wrappers remain explicit
`not_checked` and do not establish preservation. A failed complete
Column child inventory reports a diagnostic; it cannot prove preservation of
unread children.

Slab child geometry and metadata are captured through the bounded owned child
tree when available. The selected Slab properties remain the mutation owner.
Completed detailed Wall scalars are reused from the final retained owners;
the two independent material reads and comparison remain intact. A simple
Wall fixture's durable trace went from 594 records / 0.0731 s total / 0.0393 s
trace storage to 454 records / 0.0427 s total / 0.0310 s storage locally on
Linux. These measurements do not predict Windows timing. Material evidence
has an explicit 10-second limit including trace I/O; M1 scans retain their
5-second limit, and the 30-second client timeout is unchanged. Excluded and
decisively nonmatching peers skip native material observations but remain in
the source fingerprint, including criteria fields, to detect new matches.

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

Project attribute edits on Slab/MultiSlab can now explicitly set
`target.property_owner="selected_element"`. The plan binds the selected exact
ref/view plus complete lineage and direct children as
`resource.component_ownership`. This selects the adapter passed to
`ChangeAttributes`; it does not infer equivalence or redirect a child to its
aggregate. A child requires a direct MultiSlab parent, and overlapping parent
and child changes block planning and execution. Omission preserves the old
aggregate/child block; organizational layer editing is unaffected. Attribute
name/type roundtrips, stored/computed distinction, complete absence evidence
for additions, fresh revalidation/readback and replay guards all still apply.

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

## Reviewed reconciliation of native-material preservation drift

Reviewed reconciliation applies only to remaining unknown native-material
outcomes. A proposal requires readable required material and owner evidence
with consensus; unknown non-material outcomes, missing current wrappers or
required evidence failures keep the journal lock. Optional reads that return
`not_checked` do not prove preservation or by themselves block required
material/owner consensus. Prewrite and setter binding remain on the exact
reviewed view. A proposal includes `hash`, exact `targets`, `meaning`, each
target's `reviewed_view_uuid` and `reviewed_view_present`, `changed_sections`,
before/current preservation hashes, and the exact request to submit after
review. The caller reviews those targets and submits the returned request
unchanged with `reconciliation_hash` and
`acknowledgement="reviewed_material_reconciliation"` in the same session. Under
the journal lock the bridge rereads each named wrapper and accepts only an
unchanged proposal hash with the same owner and material consensus. Changed
evidence requires a fresh unacknowledged recover and a new review. Acceptance records reason
`reviewed_material_preservation_conflict`, retains `original_outcome`, and sets
`preservation_verified=false`; it also retains `reconciliation_evidence`, the
accepted `reconciliation_hash`, and the review acknowledgement. This is
read-only reconciliation; it proves
neither setter causality nor preservation, does not report applied success or
retry a setter, and does not delete journal history. Any new edit requires a
fresh preview after the recovery blocker clears.

Historical native crashes and family-specific outcomes are retained with their
evidence in [validation status](validation-status.md). This SDK note describes
API contracts only; the current candidate and required owner trials are in the
[handoff](next-model-handoff.md).

