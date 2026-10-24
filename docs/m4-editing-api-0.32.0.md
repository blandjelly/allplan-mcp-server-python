# M4 native Wall material preservation

## Bounded auxiliary trees — candidate 0.34.0

The 0.33.0 owner trial on a 240 mm Wall was blocked before setters because a
`WallAxis_TypeUUID` below its tier was rejected by the child-type whitelist.
The [raw log](test-results/evidence/0.33.0-2026-10-24/wall-native-material-preview-log.md)
records `wall_material_tier_child_unsupported` at `material_tier_children`;
no exception message was supplied. This identifies a shape rejected by the
adapter, without proving that a subsequent native material write will work.

Candidate 0.34.0 removes material-specific child-type whitelisting, blanket
opening rejection, and the requirement that an AttributeContainer be a leaf.
A standalone Wall still requires exactly one direct `WallTier_TypeUUID`,
`tier_index: 1`, a valid serialized tier `Polyhedron3D`, readable material and
explicit tier/common/axis/plane/surface evidence. The existing represented
Wall alone goes through `SetMaterial`, `SetProperties` and `ModifyElements`;
no auxiliary child is submitted as a new edit target. Multi-tier Walls remain
unsupported. The SDK basis and limits of this route are in the
[existing API research](m4-editing-api-0.25.0.md).

## Evidence and limits

Root and tier auxiliary children may include axes, openings, macros, other
adapter types and nested metadata. Every descendant has a fresh identity,
complete parent lineage, direct-child inventory and parent-edge evidence.
Each inventory is enumerated again from live adapters and compared by drawing,
model and type. Native collection owners remain alive while their wrappers
are read. Structural parent comparisons permit alternate views of the same
model; observed view UUIDs remain bound in the complete snapshot. The selected
Wall target retains its exact view binding.

`root_attribute_containers` and `tier_attribute_containers` retain direct
metadata snapshots; `auxiliary_components.root` and `.tier` contain other
direct auxiliary nodes. Each node's `children` recursively stores its
descendants, including nested AttributeContainers. All stored container values
use `ReadAll` and the existing bounded value codec. Unsupported values,
malformed or duplicate IDs, missing lineage, duplicate/cyclic/cross-file
identities and changed enumerations still block or conflict. These values are
preservation evidence, without establishing attribute ownership or write codecs.

Each auxiliary node also records `geometry`. A successful bounded
`WriteToStream` produces an observed `stream_sha256`. A missing serializer,
unavailable geometry, failed serialization or an oversized stream records
`not_checked` with a bounded reason/error type, without native exception text.
This auxiliary geometry result alone does not block preview. Its status and
any digest remain part of revalidation and readback: losing coverage or
changing an observed digest conflicts. A consistently unavailable stream cannot
detect hidden geometry changes; this is reduced preservation coverage, not a
claim that every auxiliary property was preserved. Required tier-solid and
explicit Wall-property checks remain mandatory.

The shared limits are 256 auxiliary nodes and 1 MiB of auxiliary snapshot
JSON, including ownership and per-node framing. Existing per-owner limits of
64 direct AttributeContainers remain. Stored metadata keeps its 4096-row limit
per container and 256 KiB limits per container and across the tree. Serialized
geometry streams are limited to 524288 characters. The shared component reader
bounds lineage to 16 parent steps and direct children to 256; the existing
cooperative scan budget remains in force.

## Execution, recovery and native trial

The reviewed plan binds current material and the full bounded evidence.
Apply rechecks it immediately before the existing native setter route. Fresh
readback must match the requested material and all captured evidence. Drift
before modification prevents setters; drift or an incomplete required read
after modification follows the existing unknown-result flow. Replay and
recovery use the original execution ID without retrying setters. Exact target,
plan hashes, journal and final write guards remain in force.

Focused fake-adapter checks cover the reported 240 mm Wall axis, openings and
mixed nested trees, metadata and geometry coverage, pre-write conflicts,
post-write unknown/replay/recovery, malformed ownership and shared budgets.
These are automated checks, not native acceptance. The
[handoff](next-model-handoff.md) gives the bounded 0.34.0 edge-case trial and
[validation status](validation-status.md) preserves earlier evidence.

Use a separate disposable opening fixture; the original 200 mm Wall/opening
`component_child_owner_mismatch` remains unresolved. Relaxed child types do
not bypass that ownership check. Do not repeat accepted journal, scalar, Enum,
W1 or grouped Column delete trials. Broad property discovery remains suspended;
this change does not authorize new Slab/MultiSlab or auxiliary write paths.
