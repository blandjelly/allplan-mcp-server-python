# 0.31.0 candidate evaluation record

Status: **87 unique focused checks, full two-platform CI, and exact fallback
ZIP verification passed. Native Allplan trial is pending.** Source commit
[`0f99863b7c11143d9f14ca12a1027aad5b009195`](https://github.com/blandjelly/allplan-mcp-server-python/commit/0f99863b7c11143d9f14ca12a1027aad5b009195)
is on `fix/m4-material-owner-0.31.0`.
[PR #29 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/29)
is ready and ran the standard two-platform CI matrix.

- Version: `0.31.0`
- Focused verification: **87 unique checks passed** ([record](focused-verification.json)). This is 86 affected/dependent checks across `wall_material_edit`, `wall_material_http`, `model_edit`, `native_model_edit` and `edit_ownership`, plus one package version/lock check. A 25-test rerun overlapped the broader command and was not counted twice.
- Regression coverage: same-model alternate parent view is accepted while the observed edge stays bound and fresh material readback succeeds; parent-view drift conflicts before modification; a different parent model, type or drawing remains blocked.
- Full CI: 625 tests passed on Ubuntu Python 3.12.15 and 625 on Windows Python 3.12.10 in [run 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481); the package job passed.
- Original CI artifact ID 12527730616 could not be retrieved: the connector returned only a File Service ID and the normal-proxy download was forbidden.
- Verified fallback package: built once from clean detached source at the exact tested commit (`source_modified=false`). The [Windows evaluation ZIP](allplan-mcp-0.31.0-windows-evaluation.zip) passed exact verification: 201 payload files, 43 bridge hashes, SHA-256 `4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`. See the [checksum](allplan-mcp-0.31.0-windows-evaluation.zip.sha256), [verification result](package-verification.json), [verification log](package-verification.log), [source CI record](source-ci.json), [build log](build.log) and [artifact hashes](artifact-hashes.json).
- Native Allplan: pending; the 0.30.0 blocked material attempts are recorded in the [owner observation](../../docs/test-results/m4-owner-observation-0.30.0-2026-10-23.md) and are not 0.31.0 acceptance.

## Candidate scope

The candidate corrects Wall material preservation snapshot matching for a tier
whose observed parent is another view wrapper of the same native Wall. It uses
`same_model_identity` (drawing, model UUID and type), records the actual tier
wrapper in `tier_hierarchy`, and keeps the selected target bound to its exact
view UUID. The guards remain: standalone Wall root, exactly one direct
`WallTier_TypeUUID`, no tier children, no opening or other Wall children,
valid tier geometry and a complete existing preservation snapshot.

This fixes a same-model wrapper defect reproduced by focused tests. The exact
branch that caused the first 0.30.0 native diagnostic is not proven without
raw lineage/children evidence. The second 0.30.0 Wall-with-opening result
`component_child_owner_mismatch` is unresolved and is not addressed here. The
complex property representations remain bounded drift evidence, not
exhaustive preservation of hidden SDK state. See the
[0.31.0 API note](../../docs/m4-editing-api-0.31.0.md)
and [narrow native trial plan](../../docs/m4-single-drawing-0.31.0.pl.md).

## Remaining acceptance limits

This candidate does not close priorities 1–5. The owner-reported 0.30.0 PASS
for trials 1–3 and 5 remains limited to those reported stages. Trial 5 confirms
four scalar pairs only: Column text, integer and real; Wall text. Trial 4's two
Wall material previews were blocked before Apply with zero changes/setters.
Native material acceptance requires the planned 0.31.0 trial, including fresh
material and preservation readback plus Undo restoration.

Slab/MultiSlab field ownership remains unresolved. The documented
`ModifySlab.py` workflow edits `SlabElement.Properties`, but does not prove M4
project-attribute ownership or an adapter `ChangeAttributes` contract. Native
selection still lacks an arbitrary replace/clear/readback setter. Documented
`AttributeDate` and `AttributeDoubleVec` constructors do not establish the
existing adapter route's typed payload and readback. Do not guess payloads or
lift the current fail-closed guards without a specific verified contract.

The retained 0.30.0 package-verification record's
`native_Allplan: not_run` is historical to that package check and remains
unchanged.
