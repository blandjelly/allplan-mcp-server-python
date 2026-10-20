# Allplan MCP 0.24.0 — component identity and guarded slab owners

Candidate based on develop/m4. The final source CI and exact CI ZIP verification
will be recorded here after completion. No native 0.24.0 acceptance is claimed.

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
unchanged. Final source CI remains a separate required result.

[Short next trial](../../docs/m4-single-drawing-0.24.0.pl.md) ·
[Family/type matrix and API gaps](../../docs/m4-single-drawing-coverage-0.24.0.md) ·
[Development plan](../../docs/office-editing-development-plan.pl.md) ·
[0.23.0 owner PASS](../../docs/test-results/m4-journal-cleanup-0.23.0-owner-pass-2026-10-21.md).

Native selection, native material mutation, dates/vectors/opaque SDK codecs,
door/window discrimination, complete family acceptance, broader Undo,
multi-file execution and whole-project access remain open. Preserve original
journals, trace/logs, archives and unknown execution IDs during installation.
