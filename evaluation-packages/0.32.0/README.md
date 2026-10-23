# 0.32.0 candidate evaluation record

Status: **161 unique focused checks passed. The initial full CI run failed on
one exact diagnostic-shape assertion; corrected-source CI, package build, ZIP
verification, and native Allplan acceptance are pending.** Initial source commit
[`c7783cc05f00b032ead10f49e54092b9504a35c6`](https://github.com/blandjelly/allplan-mcp-server-python/commit/c7783cc05f00b032ead10f49e54092b9504a35c6)
is on `fix/m4-material-metadata-0.32.0`. [PR #30 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/30)
is open. Initial full CI [run 40032392662](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40032392662)
failed: the Ubuntu job ran 635 tests and failed one `test_model_delete`
assertion expecting the old exact diagnostic shape after bounded
`diagnostic.evidence` was added. The Windows job was canceled by fail-fast and
the package job was skipped. The test assertion and focused delete checks are
being updated; the corrected-source commit and CI rerun are pending.

- Version: `0.32.0`
- Focused verification: **161 unique checks passed** ([record](focused-verification.json)).
- Candidate source: [commit `c7783cc`](https://github.com/blandjelly/allplan-mcp-server-python/commit/c7783cc05f00b032ead10f49e54092b9504a35c6); [PR #30](https://github.com/blandjelly/allplan-mcp-server-python/pull/30).
- CI: the initial run failed as described above; corrected-source CI is pending.
- Package: build and exact ZIP verification are pending. The [verification script](verify_package.py) is present; no candidate archive or package-verification result is recorded yet.
- Native Allplan: pending. The planned scope is the original 240 mm Wall material path. The 0.31.0 240 mm preview was blocked by `wall_material_tier_hierarchy_unsupported`; the separate 200 mm opening case was blocked by `component_child_owner_mismatch` and remains unresolved. The 0.32.0 trial must preserve any bounded diagnostic evidence and does not repeat the 200 mm material preview or write.
- Acceptance: this candidate does not close M4 priorities 1–5. See the current [development plan](../../docs/office-editing-development-plan.pl.md) and [0.32.0 API note](../../docs/m4-editing-api-0.32.0.md).

## Candidate scope

The candidate allows direct tier `AttributeContainer_TypeUUID` leaves only
after checking each container's full container → tier → Wall lineage. It
captures stored values with bounded JSON representations and rechecks
container identities and values during preservation, revalidation, and
readback. This evidence preserves observed state; it does not establish
attribute ownership or add an attribute write path. Unsupported children,
nested containers, unsupported values, openings, and other Wall children
remain blocked. Fake-adapter focused tests do not prove that this change is the
cause of the prior native diagnostic. See the
[single-path native trial plan](../../docs/m4-single-drawing-0.32.0.pl.md).
