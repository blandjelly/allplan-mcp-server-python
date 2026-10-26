# Native material editing — candidate 0.38.0

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
`StructuralBeamElement` representation, checked at runtime. Their owners are
`BeamProperties.Material` and `StructuralBeamProperties.Material` respectively.
`Slab_TypeUUID` and `MultiSlab_TypeUUID` require `SlabElement` and use exactly
`SlabProperties.Material` / `SetMaterial` on the selected element. The Slab
route does not substitute `GetSlabTierProperties(1)` or redirect to another
adapter. A Slab child may have a directly observed MultiSlab parent; other
nested roots remain blocked. `tier_index=1` is retained for request compatibility
and selects a property tier only for Wall. All routes mutate the existing
represented native object, call `SetProperties` with its properties, then
submit that object through `ModifyElements`. A missing enumerated tier child
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
The 2026 references establish those property/setter APIs, not a universal
SkeletonBeam-to-class mapping. The selected MultiSlab's `SlabElement`
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
The full optional preservation snapshot is now captured only on the exact
wrapper reviewed as the setter target. Other live wrappers receive core reads
for native material and required owner, which must agree with that selected
wrapper. Preview observation, consensus and setter preflight each start a
separate 10-second material evidence budget, including trace I/O; they do not
reuse an expired M1 scan budget, which remains 5 seconds. Missing views, owner/material
disagreement, or unreadable required evidence remain blocked or unknown.

Completed Wall hierarchy/component observations remain in partial evidence if
a later optional detail fails. Property reads are independent. Across live
views, consensus covers the required native value and structural owner; the
chosen exact view retains its own preservation fingerprint. Other views'
different optional coverage does not invalidate the material value, but strict
preservation drift on the selected wrapper remains unknown in ordinary
revalidation and Apply readback. A failed complete
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

Candidate 0.38.0 permits a narrow review path when every remaining unknown
outcome is a native-material change and every exact live representation agrees
on the current material and original bound owner. An unacknowledged recover may
return `recovery.reconciliation` with `hash`, exact `targets`, `meaning`, and a
ready-to-submit `request`. Each representation includes `changed_sections`
and before/current preservation hashes. Missing views or owners, unreadable
evidence, material disagreement, or any unknown non-material operation
suppresses this proposal and preserves the journal lock.

The agent inspects each target and compares changed sections with the current
model, including UI or geometry review when needed. After review it submits
that returned request with `reconciliation_hash` and
`acknowledgement="reviewed_material_reconciliation"` in the same session. The
bridge rereads every exact view under the journal lock and accepts only an
unchanged proposal hash. Changed evidence requires a fresh unacknowledged
recover and a new review. Acceptance records reason
`reviewed_material_preservation_conflict`, retains `original_outcome`, and sets
`preservation_verified=false`; it also retains `reconciliation_evidence`, the
accepted `reconciliation_hash`, and the review acknowledgement. This is
read-only reconciliation; it proves
neither setter causality nor preservation, does not report applied success or
retry a setter, and does not delete journal history. Any new edit requires a
fresh preview after the recovery blocker clears.

The 0.35.0 evidence confirms one Column Apply/readback and three interrupted
Wall material previews followed by native access violations. Their underlying
cause remains unproven, and neither old heap-corruption dump diagnoses those
events. The supplied 0.36.0 trial reports no crash, Wall preview budget failures,
successful Column native Apply/readback, unsupported SkeletonBeam/MultiSlab
native material, and blocked Slab attribute ownership. The user's native Beam
success statement differs from the log and remains unresolved. The next
candidate's changed routes need the bounded trial after CI and exact-ZIP
verification in the [handoff](next-model-handoff.md). Prior material
observations and their limits remain in [validation status](validation-status.md).
