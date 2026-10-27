# Current M4 handoff

## Next task — exact-target native Material for a Slab child

Continue from the M4 source merged into **develop/m4**: candidate 0.41.0 source
`f775168aaf8fdb043c269ff09d6ffda9fcea17c9`, merged PR #47, merge commit
`dd741fa`. The next development task is the
[proposed exact-child edit contract](m4-editing-api-0.32.0.md#exact-child-edit-targeting--proposed-contract-not-an-available-api),
which is not implemented. Bind explicit child/parent model/view identities
through preview, revalidation and Apply, with bounded enumeration, fresh
property-owner checks, retained native containers and read-only unknown recovery.
Do not broaden predicate results or treat the diagnostic resolver as write
authorization. Cover stale/missing/conflicting identities, view/parent drift,
overlap, no-op and replay before the required CI/ZIP candidate and a justified
isolated native trial with readback, preservation and Undo.

The getter PASS does not prove that the semantic edit scan loses this Slab or
explain its earlier failed write. The native Material path already supports
selected Slab properties with a direct MultiSlab parent; changing its setter
or weakening `slab_write_blocker` is not justified. Do not repeat historical
setters or the completed getter trials. See [plan items 1–3](office-editing-development-plan.pl.md#pozostałe-prace-i-nierozwiązane-błędy).

## Latest source and verification

Candidate **0.41.0**, source `f775168aaf8fdb043c269ff09d6ffda9fcea17c9`, is
merged to `develop/m4` as PR #47 / `dd741fa`. The 82 focused checks and 8
MCP/HTTP checks are earlier focused results, separate from CI. GitHub Actions
run [40550057327](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40550057327)
completed successfully for configuration, Ubuntu and Windows Python 3.12
portable jobs, package production and `ci-required`. The earlier run
40549970082 failed and is not validation. The supplied report records the
owner's CI/ZIP confirmation; exact installed ZIP identity and upgrade/restore
were not independently verified. This evidence/documentation change keeps
runtime and version unchanged and produces no new package.

Installed bridge health reported 0.41.0, source commit `f775168aaf8fdb043c269ff09d6ffda9fcea17c9`,
and `installed_bridge_integrity=verified` with no mismatches.

**Read-only Allplan probe, 2026-10-27:** the exact Slab child and its separately
read immediate MultiSlab parent both returned native Material exactly `" "`
and attribute 508 `TEST1` in `ReadAll` and `ReadAllAndComputable`. The child and
parent refs/views were retained separately; the other-view UUID `37a3c6a2-d40a-4005-a830-3d212c9bd165`
remains a distinct representation observation. `target_in_direct_scan=false`
applies only to this exact child/view probe and does not diagnose `SelectAll` or
`model_edit` coverage. The read was complete for its requested scope, but
`usable_for_write=false`, `setter_calls_started=0`; it establishes no writable
owner, shared storage, persistence or child/parent equivalence. Preserve the
four raw evidence files in [the 0.41.0 evidence directory](test-results/evidence/0.41.0-2026-10-27/).
The earlier SkeletonBeam 1 target/parent-edge view discrepancy remains open;
do not generalize the Slab result to that beam or to ordinary Beam, whose
fixture is not established.

The earlier report of 0.39.0 intended-value PASS for native Material on Wall,
Wall with opening and Column, and for attribute writes on two SkeletonBeams and
the Slab/MultiSlab assembly remains limited to those reported results. It does
not establish preservation, Undo, exact package attribution or owner binding
for the historic Slab attribute writes. Do not repeat accepted writes just to
recreate evidence.

## Recovery and other boundaries

Retain unresolved execution history: `87a45065d5e14e3a9ac8c54756e273a0` was
reported `stopped`, `reconciled: 1`, integrity verified,
`requires_recovery=false`; this does not prove applied success or preservation.
`4388b04e39a14fac811db4f58723d01f` was absent from the inspected 31 records,
which does not establish its archive state. Do not delete journal records or
repeat the inspection without new evidence. Unknown outcomes stay unknown;
recovery is read-only and uses the original execution ID.

Scalability remains bounded by the 200-result page, 10,000 adapter, time,
memory and journal limits. More than 32 changes requires a reviewed durable
manifest and sequential batches in one drawing; larger writes depend on
operation-specific native acceptance. See [implementation plan S0–S5](implementation-plan.md#analiza-skalowania-developm4-i-ergonomii-mcp).

Native selection remains unsupported pending an installed-SDK contract for
replace, clear and independent readback. See [selection API analysis](m4-native-selection-api.md).
Preserve exact target/owner binding, revalidation, journals, trace, replay
protection, write and Undo guards, and unknown outcomes. Do not repeat broad
property discovery or earlier crashes with unproven causes. Required-check
configuration for `develop/m4` still needs owner confirmation.
