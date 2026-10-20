# Allplan MCP 0.24.0 — component identity and guarded slab owners

Runtime source: `8e7e16040a80236bac2eca3689a42a75b83659a1`, based on develop/m4.
[PR #22](https://github.com/blandjelly/allplan-mcp-server-python/pull/22).
No native 0.24.0 acceptance is claimed.

[Windows ZIP](allplan-mcp-0.24.0-windows-evaluation.zip) ·
[Checksum](allplan-mcp-0.24.0-windows-evaluation.zip.sha256) ·
[Short Polish trial](../../docs/m4-single-drawing-0.24.0.pl.md).

[Final CI 39509201386](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39509201386)
passed **529 tests on each Windows/Ubuntu Python 3.12 job**, followed by one
package build. The original artifact digest was verified during transfer;
there was no local rebuild. The exact CI ZIP passed payload/checksum,
registration, frozen sync/import and the delivered identity/query schemas,
upgrade from 0.23.0, and restore. All **40 bridge hashes** matched; active
journal/trace/log markers and execution/trace archive markers survived.

[Source CI](source-ci.json) · [Exact ZIP verification](package-verification.json) ·
[Verification log](package-verification.log) · [Verifier](verify_package.py) ·
[Artifact hashes](artifact-hashes.json).

The candidate adds `model_property_probe phase=component_identity`, explicit
drawing/model/view/type identity, bounded parent/child manifests and native
representation type. The optional `model_query` field `component_ownership`
does not change default reads or authorize edits.

Typed edits block Slab children and every MultiSlab aggregate pending an
explicit property-owner adapter. Standalone Slab edits bind and recheck
ownership at preflight, the final setter boundary, fresh readback and recovery.
Unknown results and exact-ID journal replay never retry a setter. This
intentionally restricts future slab writes without rewriting accepted owner
observations or deleting historical execution records.

[Focused verification](focused-verification.json): **201 affected/dependent
tests PASS**, including parent/child conflicts, equal-geometry independent
slabs, stale ownership, exact W1 targets/exclusions/readback/replay/no-op,
unsupported native selection/material and unsupported SDK codecs. These are
portable fake/HTTP contracts, not native acceptance.

The [initial CI](initial-ci-result.json) passed Ubuntu but hit two real-clock
read-budget errors and a workflow verification failure on Windows; it built
no package. Functional model-edit fixtures now inject a deterministic clock,
with an explicit expiry regression. [57 dependent tests passed](clock-focused-verification.json)
after that test-only fix; production time limits and durable trace writes are
unchanged. The successful final source CI above includes the explicit expiry
regression, for 24 added tests and 529 total tests per platform.

[Short next trial](../../docs/m4-single-drawing-0.24.0.pl.md) ·
[Family/type matrix and API gaps](../../docs/m4-single-drawing-coverage-0.24.0.md) ·
[Development plan](../../docs/office-editing-development-plan.pl.md) ·
[0.23.0 owner PASS](../../docs/test-results/m4-journal-cleanup-0.23.0-owner-pass-2026-10-21.md).

Native selection, native material mutation, dates/vectors/opaque SDK codecs,
native door/window-kind acceptance, complete family acceptance, broader Undo,
multi-file execution and whole-project access remain open. Preserve original
journals, trace/logs, archives and unknown execution IDs during installation.

ZIP SHA-256: `01378661f64db110beb2802a538e76a14e0e6b32a08d38c1f1e020b7e70ddf2f`.

The delivery commit adds documentation/evidence/artifacts only. The delivered
wheel, sdist and ZIP remain the unchanged clean CI source identified above.
