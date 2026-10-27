# Current M4 handoff

## Next task — diagnose exact Slab inventory conflict; retain recovery lock

Analyze the exact-target inventory comparison on the fresh execution resolver
against the retained 0.42.1 evidence before another native write. Determine
which inventory/parent-edge evidence differs; the error alone does not prove
actual model drift. Preserve exact view/owner binding, budgets, journals and
unknown outcomes. Execution `a8a31c72975541feb1c36a2e8cbb8f65` remains unknown
and blocks writes; recovery must stay read-only under that ID. Do not retry
Apply, delete its journal or acknowledge a reconciliation without reviewed
supporting evidence. Closure requires a diagnosed cause and focused regression
coverage; a further native trial is justified only by a changed flow and after
resolving the existing outcome. See [plan items 1–2](office-editing-development-plan.pl.md#pozostałe-prace-i-nierozwiązane-błędy).

## Latest version and native evidence

**0.42.1**, source `eecdfeb818407962cf4e853a912cf3c652da8345`, is merged
as [PR #49](https://github.com/blandjelly/allplan-mcp-server-python/pull/49)
into `develop/m4` (`29c7f487`). The owner confirmed CI and ZIP passed in this
chat; these are owner-reported results, without a CI run/ZIP identity in the
new JSON or independent upgrade/restore verification. Earlier **161 focused
checks PASS** remain separate from CI and native acceptance. This update
changes documentation/evidence only, with no new package or runtime tests.

[Raw 0.42.1 evidence](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
is retained unchanged (steps 0–14). Health binds the installed bridge to the
source above, integrity verified with no mismatches, on Allplan 2026.1.
In drawing 101 the exact Slab child/parent preview observes Material `" "`
against requested `C35/45`, one eligible change, and observed
`native_material_ownership` (`SlabElement`, `slab_properties`). Both highlights
submit one child model identity/adapter; UI visibility remains unverified.
The [exact-target contract](m4-editing-api-0.32.0.md#exact-child-native-material-target-0420)
and its exact view/inventory safeguards remain in force.

The first Apply (`33abafa85e3549e68c885bade046d336`) is rejected with
`repair_recovery_required`. Inspection finds an older Wall execution
`3f2a8c9d7b5e4a1c9f8e6d3c2b1a0e9f`; its read-only recovery observes Material
`TEST` with preservation drift. A subsequent acknowledged reconciliation
records `reviewed_material_preservation_conflict`, `preservation_verified=false`,
`stopped/reconciled`, and clears that blocker. This is no applied/preservation
PASS for the Wall. The log also retains an automatic-review rejection of an
initial recovery request; the later recovery results are recorded separately.

After fresh preview/highlight, Apply `a8a31c72975541feb1c36a2e8cbb8f65`
returns `stopped`, outcome `unknown`, `repair_conflict` at `fresh_resolve`:
**"Exact child inventory or parent edge changed."** Target preflight had
agreed material reads on both live views and the reviewed view present;
that does not establish that the later exact inventory matches. Read-only
recovery repeats the conflict at `recovery_resolve`, with
`write_blocked=true`, `recovery_required`. No successful Slab write/readback,
preservation, UI acceptance or Undo/restoration is established. Do not infer
setter success or absence from this unknown outcome. No further retry is due.

The earlier [0.42.0 preview-only evidence](test-results/evidence/0.42.0-2026-10-27/allplan-042-native-test-evidence.json)
and the completed 0.41 getter remain valid in their original scopes; do not
repeat their historical setters/getters to recreate evidence.

## Previous candidate and native evidence

Candidate **0.41.0**, source `f775168aaf8fdb043c269ff09d6ffda9fcea17c9`, is
merged to `develop/m4` as PR #47 / `dd741fa`. The 82 focused checks and 8
MCP/HTTP checks are earlier focused results, separate from CI. GitHub Actions
run [40550057327](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40550057327)
completed successfully for configuration, Ubuntu and Windows Python 3.12
portable jobs, package production and `ci-required`. The earlier run
40549970082 failed and is not validation. The supplied report records the
owner's CI/ZIP confirmation; exact installed ZIP identity and upgrade/restore
were not independently verified. The later documentation-only update was
commit `a26` and did not change runtime or create a package.

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

The exact-target contract does not change native setter semantics or establish
Allplan write acceptance. Preserve the 0.41.0 result below as getter-only
evidence; it does not prove that the semantic edit scan loses this Slab or
explain the earlier failed write.

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
