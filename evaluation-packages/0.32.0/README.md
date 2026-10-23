# 0.32.0 candidate evaluation record

Candidate source [`75cd26e31ae1e3ee0d6ef86411b55490cd457302`](https://github.com/blandjelly/allplan-mcp-server-python/commit/75cd26e31ae1e3ee0d6ef86411b55490cd457302) is associated with [PR #30 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/30). It has **161 unique focused checks passed**, final full CI passed on Ubuntu and Windows (635 tests each) with the package job, and one fallback package built from a clean checkout of the exact source was verified. Native Allplan acceptance remains pending; M4 priorities 1–5 remain open beyond their previously accepted scopes.

- Focused checks: [record](focused-verification.json).
- Final CI: [run 40033163989](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40033163989), exact source `75cd26e`; 635/635 Ubuntu Python 3.12.15 and 635/635 Windows Python 3.12.10, package job passed ([source CI record](source-ci.json)). The earlier failed run is retained in that record.
- Package: one fallback build from a clean exact-source checkout (`source_modified=false`). The exact ZIP passed verification once: checksum, payload, registration, frozen sync/import, schemas, native source limits, upgrade/restore from 0.31.0, and journal/trace/bridge-log markers. It contains 210 payload files and verifies 43 bridge hashes. SHA-256: `99fe6909340d4d4e3174601cf23a4854dfece683a1b75b95e5fdebfcc0aaf8b5`.
- Artifacts: [verified evaluation ZIP](allplan-mcp-0.32.0-windows-evaluation.zip), [SHA-256 file](allplan-mcp-0.32.0-windows-evaluation.zip.sha256), [verification result](package-verification.json), [verification log](package-verification.log), [build log](build.log), and [artifact hashes](artifact-hashes.json). The [verification script](verify_package.py) records the procedure.
- Native Allplan: not run for 0.32.0. Any trial is limited to the original 240 mm Wall material path. The 0.31.0 preview was blocked by `wall_material_tier_hierarchy_unsupported`; the separate 200 mm opening case returned `component_child_owner_mismatch` and remains unresolved. Do not repeat the 200 mm material preview or write. See the [single-path trial plan](../../docs/m4-single-drawing-0.32.0.pl.md).
- Scope: M4 priorities 1–5 remain partial/open; see the [development plan](../../docs/office-editing-development-plan.pl.md) and [API note](../../docs/m4-editing-api-0.32.0.md).

## Candidate scope

The candidate permits direct tier `AttributeContainer_TypeUUID` leaves only
after verifying each container's container → tier → Wall lineage. It captures
stored values with bounded JSON representations and rechecks container
identities and values during preservation, revalidation, and readback. The
snapshot does not establish field ownership or add an attribute write path.
Unsupported children, nested containers, unsupported values, openings, and
other Wall children remain blocked. Focused fake-adapter tests do not prove
that the former blanket-child guard caused the prior native diagnostic.
