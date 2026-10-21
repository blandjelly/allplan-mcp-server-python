# Allplan MCP 0.25.0 — guarded deletion and native Wall material

Runtime source: `574ef06ca97fced289b414faa3ba91b78b5b91ef`, based on `develop/m4`.
[PR #23](https://github.com/blandjelly/allplan-mcp-server-python/pull/23).
Native Allplan acceptance of the new operations is pending.

[Windows ZIP](allplan-mcp-0.25.0-windows-evaluation.zip) ·
[Checksum](allplan-mcp-0.25.0-windows-evaluation.zip.sha256) ·
[Short Polish trial](../../docs/m4-single-drawing-0.25.0.pl.md).

[Final CI 39660850663](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39660850663)
passed **557 tests on each Windows/Ubuntu Python 3.12 job**, followed by one
package build. The original CI artifact digest was verified during transfer;
the ZIP, wheel and sdist have not been rebuilt or modified.

The exact ZIP passed checksum/payload verification, registration, frozen
dependency sync and import of both new edit schemas, upgrade from 0.24.0 and
restore. All **42 bridge hashes** matched. Active journal/trace/log markers
and execution/trace archive markers survived. These are portable package
checks with temporary installation directories, not an Allplan installation
or native model test.

[Source CI](source-ci.json) · [Exact ZIP verification](package-verification.json) ·
[Verification log](package-verification.log) · [Verifier](verify_package.py) ·
[Artifact hashes](artifact-hashes.json) · [Focused checks](focused-verification.json).

| Operation | Implemented candidate scope | Native acceptance |
| --- | --- | --- |
| `target.kind=delete` | Supported component roots and bounded full owned subtrees; a directly Wall-owned WindowDoor opening can be deleted independently while preserving its parent. Explicit exclusions protect descendants. Matching Slab and MultiSlab become one reviewed root deletion. | Pending; native cascade behavior is checked by fresh absence, never assumed. A Slab tier cannot be deleted separately. |
| `target.kind=native_material, tier_index=1` | Standalone single-tier Wall without openings, exact string, serialized Polyhedron3D tier geometry and explicit non-material drift evidence. | Pending; no catalog existence claim. Complex-property representations are bounded drift evidence, not exhaustive hidden SDK state. |
| `component_identity` | Pure identity scan no longer requires layer/display-name consensus. Exact model/view identity and hierarchy consensus remain required. | The cause of the owner's failed 0.24.0 probe remains unproven. |

Both write paths retain reviewed plan/hash, highlight, native writability,
one foreground drawing, write-ahead journal, fresh readback, unknown-result
blocking and setter-free replay/recovery. Deletion readback rejects missing
or conflicting drawing-file identities instead of inferring absence. Missing
SDK symbols remain `not_checked` and cannot authorize a write.

**166 unique focused affected/dependent cases passed across iteration runs:**
155 unit and 11 MCP HTTP cases. An additional native-fake scenario confirmed
that matching Slab/MultiSlab identities result in one root deletion. Full CI
replaced a full local suite run. The [initial CI](initial-ci-result.json)
found one capability-metadata regression; it built no package. The corrected
source passed 35 dependent tests and then the final CI above. An earlier
source run was cancelled before packaging when the deletion absence guard
was strengthened.

The owner's [0.24.0 log and scoped observations](../../docs/test-results/m4-owner-observation-0.24.0-2026-10-21.md)
are preserved. Previously accepted outcomes do not need repeating.
Priorities 1–5 remain partially open: native UI selection, date/vector/object
codecs, unresolved native Slab view evidence, family-specific native coverage
and remaining Undo observations are not supplied by portable tests. Multi-file
and whole-project execution remain separate future stages.

ZIP SHA-256: `6b585e3af7c2f3eb3487436ae9a98636967e1b7562da0200c03837333ec02291`.

The delivery commit contains documentation, evidence and original artifacts
only; the delivered package retains the clean runtime source identified above.
