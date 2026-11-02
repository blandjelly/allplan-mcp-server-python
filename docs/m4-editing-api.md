# M4 editing API notes


This file collects the editing API findings for `model_edit` in one place.
The first part is the current native-material contract; the second part keeps
earlier version-scoped findings with the scope stated in each section.
Current release status belongs in the [handoff](next-model-handoff.md).


## Native material editing — API contracts

### Native Material, material attribute and Surface

Sources reviewed **2026-10-26** for the Python API **2026**; GUI references
below identify their 2026-0/2026-1 version explicitly. This section separates
published SDK contracts, native observations and hypotheses. Current delivery
and acceptance belong in the [handoff](next-model-handoff.md).

| Requested field | API owner and persistence route | What success establishes |
| --- | --- | --- |
| Native architectural Material | `ArchBaseProperties.Material: str`, `GetMaterial()` / `SetMaterial(str)` on the actual property owner. Reattach the properties to the existing element and submit it with `ModifyElements`. | Only a fresh native read from the same owner establishes the retained native value; method availability alone does not. |
| Element attribute named Material / Materiał | Resolve the element's exact name↔ID/type; `GetAttributes` reads ID/value pairs and `ElementsAttributeService.ChangeAttributes` writes them through the selected adapter. The official read-access example identifies standard Material as ID 508. | Typed attribute readback establishes that attribute value on that owner. The 0.39.0 write log omits its actual ID/payload; the read-only 0.40.0 probe later observed live ID 508 ↔ `Materiał`, SDK `String`, on two SkeletonBeams and a MultiSlab. This is an element attribute, not the separate document/project-attributes API. |
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

#### Beam, StructuralBeam and Slab contracts

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

#### Why a missing palette field does not establish non-support

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

#### Native result and unresolved inference

The [0.39.0 owner log](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md),
summarized in [validation status](validation-status.md#latest-owner-observations), reports
zero native Beam/SkeletonBeam query matches with representation conflicts,
then reported Material-attribute writes on two SkeletonBeams and on a
MultiSlab/Slab representation pair. These reports do not establish native Beam
setter success or the owner/payload of the attribute writes. The historical
Slab native readback stayed blank after attempts; its exact owner and execution
IDs are not established by that summary. Preserve the unknown outcomes and do
not attribute an earlier Slab write to an execution without direct evidence.

The earlier read-only comparison of 2026-10-27 is preserved in the
[0.39.0 comparison log](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md).
The 0.40.0 getter-only comparison now supplies paired native-material and
attribute observations on the two SkeletonBeams and the MultiSlab. The exact
values and limits are summarized in the [current handoff](next-model-handoff.md)
and [validation status](validation-status.md#latest-owner-observations), with raw
responses under [the preserved evidence directory](test-results/evidence/0.40.0-2026-10-27/). These observations do not establish that those wrappers were the
write owners for earlier attribute Apply reports, shared storage, or persistence.
The [0.41.0 request and response](test-results/evidence/0.41.0-2026-10-27/02-slab-child.json)
now separately read the exact Slab child and its actual immediate MultiSlab
parent using explicit `parent_ref` and `include_parent=true`. Both return
`SlabElement.Properties.Material` exactly `" "` and attribute 508 `"TEST1"` in
both read modes; metadata confirms `Materiał` / SDK `String`. The preserved
edge and separate parent read retain their exact model/view identities.
The [trace](test-results/evidence/0.41.0-2026-10-27/03-trace.jsonl) completes
without setters. This resolves the earlier `probe_scope_unavailable` for the
retained exact request, without establishing its native cause, a writable
owner, shared storage or persistence. The diagnostic route does not change
query membership, write guards or setter resolution.

#### Exact-child native Material target (0.42.0)

The `model_edit` preview request accepts optional `exact_target` only for one
native Material edit to a Slab child in one foreground drawing. It requires
`native_types=["Slab_TypeUUID"]`, no predicate, attribute IDs or exclusions,
and the `scope` must be `{drawing_files:[target drawing],
include_passive:false,visibility:"api_select_all"}`.
The exact target contains the child's drawing/model/view and its parent's
model/view. Exact refs are canonical nonzero UUIDs; the parent model must differ
from the child. This mode does not silently extend ordinary predicate-based
selection.

The resolver first retains the complete direct `SelectAllElements` inventory,
then uses the exact MultiSlab parent to resolve the child and verifies the
immediate parent edge. It includes the explicitly resolved child in the scoped
inventory for this opt-in while preserving every direct peer in the M1 scan.
Limits are 10,000 direct adapters, at most 16 parent wrappers and 16 child
target wrappers, 256 child visits, and the existing bounded operation/trace
budgets. The plan binds the exact target and child inventory fingerprint. The
same bounded identity, view, inventory and edge checks run on revalidation,
Apply target preflight and at the final write boundary. Missing, stale, duplicate
or conflicting identities, changed views/parent edges, or changed inventory
stop the write. The selected Slab child remains the `SlabProperties` owner; the
parent is a locator, never a replacement target.

Highlight re-resolves the exact child first, then presents all representations
of the selected child model UUID; it never targets the parent. Fresh readback
and recovery stay bound to the exact reviewed target view, child type and
parent edge. If the reviewed view is absent or regenerated, the exact-target
path remains unknown; it does not fall back to a replacement view.

**Post-setter inventory drift (0.43.0).** Pre-setter resolution, Apply
preflight and the final mutation boundary require the reviewed inventory
fingerprint exactly. The post-setter observation (fresh readback and recovery)
cannot: `ModifyElements` can regenerate MultiSlab child representations, and
the readback path already tolerated regenerated views. It now records
`representation_consensus.exact_inventory` = `{status: unchanged|changed,
expected_fingerprint, current_fingerprint, diff}` instead of raising. The diff
lists scalar changes (`parent_representation_count`, `child_visits`,
`target_in_direct_scan`), children and edges added/removed (bounded to 32 items
each) against the `inventory_summary` bound in the plan; plans from 0.42.x
have no summary and report `expected_summary_unavailable` with the current
inventory. Apply keeps a changed inventory as `unknown`
(`exact_inventory_changed_after_setter`) with the readback; read-only recovery
reconciles from the observed value. A drift report is evidence only and never
authorizes a write. Recovery is read-only under the
original execution ID and never retries a setter. Existing material setter,
preservation, journal, overlap, stale and replay guards remain in force.

Native-material previews report `criteria.native_material_ownership` from the
same selected `native_material_state` used by the planner: the native class,
property owner and exact hierarchy, including the reviewed view. Unavailable
required evidence or disagreeing material representations remain `not_checked`
and block planning. The generic `criteria.component_ownership` remains for
other operations and is empty on the exclusive native-material route. Its
attribute/layer checks compare complete adapter observations, including view
UUIDs, and must not be used as a second native-material owner verdict. The
selected native state still retains its component-tree preservation evidence.

The [installed 0.42.0 preview evidence](test-results/evidence/0.42.0-2026-10-27/allplan-042-native-test-evidence.json)
reports one usable exact Slab plan with old Material `" "`, requested `C35/45`
and zero setters. Its ancillary `slab_ownership_representation_conflict` can be
reproduced by comparing different view identities in a fixture; the log does
not include the individual generic observations needed to prove that was the
native cause. The native material owner checks passed. Candidate 0.42.1
separates those reports. The supplied
log contains no highlight, Apply or readback, and the owner confirmed the agent
stopped before highlight. It does not demonstrate a failed native write.

The [0.42.1 native trial](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
confirms the native owner report and highlight API submission, but Apply stops
at `fresh_resolve` with `Exact child inventory or parent edge changed.`
Recovery repeats the conflict and leaves execution
`a8a31c72975541feb1c36a2e8cbb8f65` unknown with writes blocked. Preflight
material consensus across two views is not proof of identical exact inventory.
The log does not identify which inventory/edge changed or establish native
write acceptance, preservation or Undo. Diagnosis (0.43.0): `fresh_resolve`
is the first observation after `SetMaterial` + `ModifyElements`; the
pre-setter resolve and the final mutation boundary had both passed with the
reviewed fingerprint, so the inventory changed across the native submission.
The setter may therefore have run. See the post-setter drift contract above.
The 0.41.0 getter PASS, including `target_in_direct_scan=false` for its exact
requested view, neither proves that the model edit scan loses the Slab nor
diagnoses the earlier write failure.

The [0.43.0 native trial](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)
(native observation, Allplan 2026.1) confirms that diagnosis. A new Apply
(`9c6a0d32…`) ran `SetMaterial` + `ModifyElements` without a native error; the
only inventory change was one `AttributeContainer_TypeUUID` child of the
MultiSlab replaced by a new UUID (edges, parent and scalars equal;
`diff.child_type_changes` names it from 0.43.1). The exact child's Material
readback stayed `" "` after the setter, in recovery and in later previews, and
did not become `C35/45`; after UI Undo the inventory fingerprint equals the
pre-Apply one. Why the value does not change (property owner, tier-level
storage, or a setter that is accepted but not applied in this build) is an open
question, not a diagnosed cause. A drift report never authorizes a write.

Example using the retained 0.41.0 target refs; replace the value with the exact
reviewed native material string. Do not apply this sample to repeat historical
Slab writes:

```json
{
  "schema_version": "m4-model-edit-1",
  "action": "preview",
  "scope": {"drawing_files": [101], "include_passive": false, "visibility": "api_select_all"},
  "native_types": ["Slab_TypeUUID"],
  "exact_target": {
    "drawing_file": 101,
    "model_uuid": "8a693925-ae20-4dda-91d1-3951af3c0a52",
    "view_uuid": "a0fcd7b3-85c8-4f83-99b7-59e8a3463c94",
    "parent_ref": {
      "model_uuid": "bf097d95-8275-4229-ac74-27bbea26c211",
      "view_uuid": "b4a59b5b-c0ae-4c1e-9d59-df5761390eb9"
    }
  },
  "changes": [{
    "target": {"kind": "native_material", "tier_index": 1},
    "value": "EXACT_REVIEWED_MATERIAL"
  }]
}
```

Current closure work is in [plan items 1–3](development-plan.md#evidence-needed-to-close-items-18).

### Request and native property owner

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

### Required checks and optional preservation evidence

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

### Execution and acceptance boundary

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

### Reviewed reconciliation of native-material preservation drift

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



## Earlier findings by version

Each section below retains the scope and build stated in its original note.


### M4 material-path correction for candidate 0.31.0

Candidate `0.31.0` is under evaluation on `fix/m4-material-owner-0.31.0`.
This note describes the source correction. **87 unique focused checks passed**: 86 affected/dependent checks in
`wall_material_edit`, `wall_material_http`, `model_edit`, `native_model_edit`
and `edit_ownership`, plus one package version/lock check. The 25 overlapping
checks were not double-counted. See the [focused verification record](../evaluation-packages/0.31.0/focused-verification.json).
Both full CI unittest jobs passed on Windows and Ubuntu Python 3.12 in
[run 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481).
The Windows package job passed with 625 tests in each platform job. The
original artifact was unavailable, but one fallback ZIP from clean exact
source (`source_modified=false`) passed verification: 201 payload files, 43
bridge hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`.
The [package-verification record](../evaluation-packages/0.31.0/package-verification.json)
and [verified fallback ZIP](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip)
are available for the one planned native material trial. Native Allplan
acceptance is pending. It corrects a
same-model parent-wrapper defect reproduced by focused tests and associated with
the diagnostic reported in the 0.30.0 Wall material preview; the native cause
is unproven. It does not close priority 4 or priorities 1–5.

#### Wall tier parent identity

The 0.30.0 preservation snapshot compared the tier's observed parent view UUID
with the Wall root's exact view UUID. A tier may return a different wrapper
view for the same native Wall. Focused tests reproduced that structural
same-model case being rejected by the strict view-UUID comparison. The guard
also returns `wall_material_tier_hierarchy_unsupported` when the lineage length
is not two or the tier has children. The owner's native diagnostic is
consistent with the wrapper case, but no raw lineage/children response
establishes which branch caused that Allplan result.

The 0.31.0 change compares the observed parent edge with
`same_model_identity` (drawing, model UUID and type). It records the actual
observed tier wrapper in `tier_hierarchy` and preserves that edge in the
snapshot used for revalidation and readback. The selected Wall target remains
bound to its exact drawing/model/view identity; the comparison change does not
weaken target binding.

Three parent-wrapper regressions passed within the 86 focused checks: a
same-model alternate parent is accepted with the actual edge bound and fresh
readback; parent-view drift conflicts at revalidation; and a different parent
model, type or drawing remains blocked.

The preservation path still requires a standalone Wall root, supported child
types and hierarchy shape: exactly one direct `WallTier_TypeUUID` child, no
children under that tier, no opening or other Wall children, valid tier
geometry and exactly one tier. A failed guard remains blocked before Apply.
This change updates snapshot identity evidence only; it adds no setter or
`SetWallTierProperties` API. The existing `WallElement` properties route and
its limits are recorded in the pinned
[`ModifyWall.py` example at immutable commit `e816b120`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/e816b120038ca121b51d80b78f22da561b5c6fda/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifyWall.py#L285)
and [M4 API note 0.25.0](m4-editing-api.md#narrow-native-wall-material-experiment).

The snapshot's complex-property representations are bounded drift evidence,
not exhaustive preservation codecs for hidden SDK state. See the
[coverage limitations](m4-single-drawing-coverage-0.24.0.md#native-selection-and-material-are-separate-gaps).

The 0.30.0 first Wall preview reported
`native_material_preservation_unavailable` with
`wall_material_tier_hierarchy_unsupported`. The 0.31.0 code fixes the
reproduced same-model parent-wrapper defect associated with that diagnostic;
native retest is pending, and the exact cause of the owner's 0.30.0 result is
not proven. A second Wall with an opening reported
`component_child_owner_mismatch`. Its cause is unresolved and this change does
not claim to fix it. Official `GetChildModelElements(adapter, hiddenElements)`
returns immediate children (`True` includes hidden immediate children);
recursive enumeration is the separate `GetChildModelElementsFromTree` API.
Therefore recursive enumeration alone does not explain the opening result.
See the [official child-elements API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapterChildElementsService/).

#### Remaining prerequisites

| Priority | Achieved scope | Still missing |
| --- | --- | --- |
| 1 — journal | 0.30.0 owner-reported trial PASS; earlier bounded preview/archive scope remains accepted. | Trial substeps lack detailed raw evidence; preserve unknown/corrupt/unverifiable records. |
| 2 — field ownership | 0.30.0 identity/evidence trial reported PASS. `ModifySlab.py` demonstrates `SlabElement.Properties` editing through `SetProperties`/`ModifyElements`. | It does not prove M4 project-attribute ownership or a `ChangeAttributes` route for the conflicting Slab/MultiSlab lineage. Keep these writes blocked. |
| 3 — layer/no-op | 0.30.0 W1 no-op stage reported PASS. | Detailed raw log was not supplied; this does not expand W1 write/Undo acceptance. |
| 4 — typed delete, material and selection | 0.29.0 grouped Column delete/Undo remains accepted for its tested scope. 0.31.0 corrects same-model parent-wrapper matching in the material snapshot. | Native material trial for 0.31.0 is pending. Native UI selection has no arbitrary replace/clear/readback setter. |
| 5 — attribute types | 0.30.0 trial 5 confirms four scalar pairs with typed readback and Undo. | Full family/type coverage and non-scalar codecs. `AttributeDate` and `AttributeDoubleVec` constructors do not establish an adapter `ChangeAttributes` payload or typed readback contract. |

The remaining APIs and evidence are described in the
[0.30.0 API research note](m4-editing-api.md#m4-api-evidence-and-limits-for-candidate-0300). These runtime/native
prerequisites cannot be completed by documentation or cloud-side reasoning;
do not guess setter payloads or lift the existing write guards without a
specific verified contract.


### M4 API evidence and limits for candidate 0.30.0

Research date: 2026-10-23. Candidate 0.30.0 adds bounded read evidence for
requested attribute IDs and explicit zero-setter evidence for no-op
`model_edit` plans. It does not add a date/vector setter, native selection
set/clear/readback, or a Slab/MultiSlab field-owner adapter. It is deliberately
partial; full completion of priorities 1–5 remains the goal and is blocked by
the missing field-owner, date/vector payload, and selection set/clear/readback
contracts. The combined candidate gathers evidence to help establish them,
without claiming that evidence itself completes those contracts. Previously
accepted scopes remain accepted.

#### `attribute_evidence` probe

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

#### Slab and MultiSlab ownership

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

#### Native UI selection

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

#### Date and vector attribute payloads

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

#### Bounded no-op evidence

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

#### Scope of acceptance

The trial plan at [0.30.0](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/m4-single-drawing-0.30.0.pl.md) exercises all
available priority 1–5 paths in one session and records blocked work
explicitly. Existing supported scalar/Enum writes may be tried on concrete,
previously unaccepted family/type fixtures when those definitions and safe
targets exist. The probe itself does not expand write support. This note is API
evidence, not CI, package, owner-trial, or native acceptance; the new probe,
no-op route and any newly exercised family still require their own results.

#### Sources

- Official examples at immutable commit
  [`8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/tree/8e2c252477e20bc9afac8918f78a8eeabd473a81)
- [AttributeDate API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
- [AttributeDoubleVec API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
- [ElementsAttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
- [UndoRedoService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/UndoRedoService/)


### M4 editing API evidence for 0.29.0

Research date: 2026-10-23. This note records official examples that pass
multiple adapters to the base-elements module's `DeleteElements` function in
one call. It supports
the implementation choice for one reviewed plural delete plan. It does not
prove that Allplan groups those deletions into one UI Undo step, nor does it
establish successful deletion/readback for the M4 Column scenario.

#### Plural `DeleteElements`

The immutable official
[`Fillet3D.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/GeometryExamples/Operations/Others/Fillet3D.py)
example appends two adapters to one list (lines 237–239), then passes that list
to a single `AllplanBaseElements.DeleteElements` call (lines 272–275). The official
[`PythonPartConnection.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/BasisExamples/PythonParts/PythonPartConnection.py)
also builds a list of adapters and passes it to `DeleteElements` (lines
103–106). These examples show that the API accepts a list of adapters for one
call. They do not document M4's preflight, transaction boundaries, per-target
result accounting, complete subtree ownership, fresh absence readback, or
recovery behavior; those remain M4 safeguards and must be verified separately.

#### UI Undo

The SDK exposes `UndoRedoService` in `NemAll_Python_IFW_Input`, but the reviewed material does not define a
deletion collection contract that guarantees one Undo restores every element
passed to `DeleteElements`. API availability and a single plural call do not
prove UI behavior. The narrow 0.29.0 owner trial must confirm with fresh reads
that one UI Undo restores the exact three Column roots and all bound
descendants. Do not add a wrapper around an undocumented undo API or claim
grouped Undo before that trial passes.

#### Remaining native/API priorities 2, 4, and 5

##### Priority 2 — Slab and MultiSlab ownership

The pinned official
[`ModifySlab.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifySlab.py)
demonstrates an architectural property-editing route: it resolves a selected
adapter with `GetElement`, casts it to `SlabElement`, reads `Properties`, builds
new slab properties, assigns them to the element and calls `ModifyElements`.
It also gets and hides the selected adapter's parent while the edit interaction
is active. This is evidence for a Slab element property workflow. It does not
establish that a selected child adapter owns M4's project attributes, that a
`MultiSlab` owns the same fields, or which element is authoritative for the
reported Slab/MultiSlab lineage. No explicit MultiSlab property-owner contract
appears in the reviewed sources.
See the API references for [`SlabElement`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabElement/),
and [`SlabProperties`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/SlabProperties/).

Keep aggregate and unresolved child writes blocked. To implement a route,
establish the exact target and lineage from fresh model/view identity reads,
document which element owns each requested property for the specific family,
and bind its property snapshot and preservation fields. A narrow native trial
must then show the intended value change, fresh typed readback, preservation
of unrelated tiers/geometry and UI Undo. A property API call alone cannot close
the ownership question.

##### Priority 4 — native selection

The 0.28.0 research note records the distinction between
[`SelectElementsService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectElementsService/)
geometry queries, [`ElementsSelectService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsSelectService/)
document/IFC queries, [`PostElementSelection`](https://pythonparts.allplan.com/2025/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/PostElementSelection/)
for elements picked through a user interaction, and `HighlightService` for
visual highlighting. The pinned
[`GetObjectByAttributeValue.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ObjectAccessExamples/GetObjectByAttributeValue.py)
queries adapters and highlights them. The pinned
[`SelectObjectsByAttributeID.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/SelectObjectsByAttributeID.py)
uses an interactive user-pick path. These examples do not establish an API
that sets an arbitrary existing M4 query-result list as the native selection
and reads that exact set back.

Keep the existing highlight route described as highlighting. Before adding
native selection, document an exact set/replace operation, its clear behavior,
and a readback that distinguishes selected adapters from highlighted ones.
A narrow trial must verify the exact target count and identities, behavior
when replacing/clearing an existing selection, and that no model edit occurs.
The reviewed examples do not prove that no such API exists; they leave the
setter and readback contract unestablished.

##### Priority 5 — date and vector attributes

The 2026 [`ElementsAttributeService` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
uses a generic `object` value parameter, while the
[`AttributeDate` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDate/)
documents a date value for the `AllplanElement.SetAttributes` path. The
[`AttributeDoubleVec` API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
documents a vector attribute representation. Neither API signature by itself
establishes the accepted payload for M4's existing-adapter
`ChangeAttributes` route or an exact typed readback. The pinned generic
[`ChangeAttributes.py`](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/InteractorExamples/GeneralModification/ChangeAttributes.py)
example does not show date or vector values, and no date/vector end-to-end
setter plus readback example was found in the reviewed pinned tree.

Keep date/vector writes blocked until a family-specific contract specifies the
input encoding, runtime type binding, native setter payload and fresh typed
readback. Then verify unrelated-field preservation and UI Undo on a narrow
native trial. These source and API findings delimit reviewed evidence; they do
not claim that other supported call paths cannot exist.

#### Sources

- Official examples at immutable commit
  [`8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/tree/8e2c252477e20bc9afac8918f78a8eeabd473a81)
- [UndoRedoService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/UndoRedoService/)


### M4 editing API evidence for 0.28.0

Research date: 2026-10-23. This note records what the Allplan API material
and the official `NemetschekAllplan/PythonPartsExamples` repository document
for native selection, parent identity, and date/vector attributes. API
signatures and example code are evidence of a call path, not proof of its
runtime behavior, target ownership, readback, or safe Allplan acceptance.

#### Selecting existing query results

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

#### Model identity and parent edges

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

#### Date and vector values

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

#### Sources

- [2026 element-attributes manual](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
- [ElementsAttributeService API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
- [AttributeDoubleVec API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeDoubleVec/)
- [Official examples at immutable commit `8e2c252477e20bc9afac8918f78a8eeabd473a81`](https://github.com/NemetschekAllplan/PythonPartsExamples/tree/8e2c252477e20bc9afac8918f78a8eeabd473a81)


### M4 editing API evidence for 0.25.0

Research note, 2026-10-21. These are documented 2026 API surfaces, not native
Allplan acceptance. A method signature does not establish host integration,
transaction behavior, safety for a particular adapter, or successful readback.

#### Deleting an exact target

The 2026 [Base Elements API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/)
documents `DeleteElements(doc: DocumentAdapter, elements: BaseElementAdapterList)`.
An exact adapter exposes its owning document through
[`BaseElementAdapter.GetDocument()`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/).
This supports a candidate path for deleting already-resolved adapters in their
document. The reference does not document a return value, cascade/child rules,
atomicity, or Undo behavior. Keep deletion bound to an explicit exact target
and treat those semantics as open until verified.

#### Native selection remains interactive

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

#### Narrow native Wall material experiment

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

#### Date and vector payload boundaries

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
