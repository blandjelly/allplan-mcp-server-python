# M4 native Wall material preservation — candidate 0.32.0

Candidate 0.32.0 extends the existing guarded native material path for a
single-tier Wall. It addresses an implementation gap in which every child
under the tier was rejected before its type and ownership were checked. The
new path admits only direct `AttributeContainer_TypeUUID` leaves whose full
lineage resolves as container → tier → Wall. This snapshot is preservation
evidence; it does not establish that a container attribute belongs to a
particular field or that the container can be edited through a setter.

**161 unique focused checks passed** ([record](../evaluation-packages/0.32.0/focused-verification.json)).
Source
[`c7783cc05f00b032ead10f49e54092b9504a35c6`](https://github.com/blandjelly/allplan-mcp-server-python/commit/c7783cc05f00b032ead10f49e54092b9504a35c6)
is on `fix/m4-material-metadata-0.32.0`; [PR #30](https://github.com/blandjelly/allplan-mcp-server-python/pull/30)
targets `develop/m4`. Initial full CI [run 40032392662](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40032392662)
failed one Ubuntu `test_model_delete` exact-shape assertion after
`diagnostic.evidence` was added. The Ubuntu job ran 635 tests; Windows was
canceled by fail-fast and the package job was skipped. The assertion and
focused delete checks are being updated; corrected-source CI is pending. The
package build/ZIP verification and native Allplan acceptance are also pending.
Focused fake-adapter tests reproduce the prior blanket-child
rejection and exercise the new bounded path. They do not prove that this was
the cause of the owner's native 0.31.0 diagnostic. The 200 mm
Wall-with-opening `component_child_owner_mismatch` remains unresolved and is
outside this change. See the [0.31.0 owner observation](test-results/m4-owner-observation-0.31.0-2026-10-24.md)
for the supplied native evidence.

## Accepted child shape and identity checks

The Wall remains the exact bound target. Its existing guards still require a
standalone Wall root, exactly one direct `WallTier_TypeUUID`, no opening or
other Wall children, valid geometry, one tier and a complete preservation
snapshot. The tier may now have direct metadata children, but every such child
must be an `AttributeContainer_TypeUUID` leaf. A non-container child, nested
container, missing or inconsistent lineage, duplicate identity, or changed
child set blocks the preview or conflicts during revalidation.

For each container, the adapter lineage must include the container, its tier,
and the Wall, with every parent edge checked by drawing, model UUID and type.
Observed view UUIDs are retained in the snapshot. The immediate tier-child
inventory is enumerated again from live adapters and compared structurally
with the earlier ownership observation; each repeated enumeration must resolve
to the same set of drawing/model/type identities. The actual adapter wrappers
from the fresh enumeration are used to read the container. This permits
alternate wrappers for the same model while preserving the exact observed
edges for later checks.

The limits are 64 direct containers, at most 4096 stored attribute rows per
container, 256 KiB of encoded rows per container, and 256 KiB for the aggregate
serialized container snapshot. Stored values are read through `ReadAll` and
must have a bounded JSON representation: a scalar, or a one-level sequence of
at most 64 scalar members. Unknown SDK objects, nested sequences, oversized
strings or values, non-finite numbers, malformed/duplicate IDs, and other
unsupported data block preservation instead of being omitted or coerced.
The complete sorted attribute snapshot is included in the Wall material
preservation state and checked again during revalidation and post-write
readback.

These container values are used only to detect whether a native material
operation preserves the observed state. They do not authorize writing
container attributes, infer field ownership, create codecs, or provide an
attribute definition/catalog. No new write path is added for Slab, MultiSlab,
openings, nested metadata, native selection, date/vector attributes, or other
Wall children.

## Existing write and recovery safeguards

Only the existing represented Wall object is submitted to the existing
`ModifyElements` route. The exact target binding, reviewed material value,
preview/revalidation checks, journaling and execution/recovery behavior remain
in force. There is no automatic retry or rollback after an uncertain native
outcome. A changed material is accepted only when fresh readback matches and
the preservation snapshot—including the container inventory and values—still
matches. A failed or changed preservation check prevents Apply or reports the
existing conflict/unknown state according to when it is detected.

The focused fake-adapter coverage includes a direct container leaf, a
same-model alternate tier wrapper, unsupported children and values, container
identity/value drift before modification, and post-modification metadata drift
with no repeated native call on recovery. This evidence validates the
implemented guard behavior in tests; it is not a native Allplan result.

## Bounded lineage diagnostics

When a component child fails parent verification,
`blocked[].observation.diagnostic` may contain an `evidence` object with the
exact observed `target`, `child`, and `observed_parent` identities. The parent
is `null` when the adapter reports no parent. For an unsupported material tier
lineage, the diagnostic may include `selected_wall`, `tier_lineage`,
`tier_child_count`, and a `tier_children_sample` limited to eight identities.
These bounded fields are included only when that specific evidence was read;
they contain no exception text or object representations.

The evidence can guide a read-only `component_identity` follow-up for the
unresolved 200 mm opening mismatch. It does not establish ownership or make the
material path eligible. Do not repeat its material preview or perform any
write; the planned 0.32.0 material trial remains limited to the original
240 mm Wall.

The native trial is limited to the original 240 mm Wall material path. It must
capture the initial reason, diagnostic stage, and any `diagnostic.evidence`,
and obtain fresh
`component_identity` for the Wall and exact tier whenever preview is blocked.
If the path qualifies, one reviewed Apply, fresh material/preservation
readback, and one owner UI Undo with fresh restoration readback are required.
Do not repeat the accepted Enum, journal, scalar, or grouped Column delete
trials. The Boolean/CheckBox record has only a documented post-Undo read and no
raw Apply evidence; do not repeat that read as if it were a complete accepted
trial. Do not retry the unresolved 200 mm opening case.

This candidate does not close M4 priorities 1–5. Remaining gaps include the
Slab/MultiSlab project-attribute owner and write contract, date/vector setter
payloads and readback, native UI selection set/clear/readback, broader
family/type coverage, and the unresolved opening-owner diagnostic. The
[coverage matrix](m4-single-drawing-coverage-0.24.0.md) and prior
[0.31.0 correction note](m4-editing-api-0.31.0.md) retain the earlier scope.
