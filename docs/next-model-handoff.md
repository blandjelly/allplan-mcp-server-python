# Current M4 handoff

## Next task — verify candidate 0.42.1, then run one native trial

Complete required CI/package production and exact-ZIP verification for 0.42.1.
Then on a disposable fixture create a fresh preview (the prior plan expired),
review/highlight the exact target, and perform one trial with Apply, fresh
readback, preservation and Undo/restoration. See [plan items 1–3](office-editing-development-plan.pl.md#pozostałe-prace-i-nierozwiązane-błędy).

**Latest candidate 0.42.1:** on `codex/m4-fix-exact-slab-042`, based on
`develop/m4` `58512959` (PR #48 merged; installed source `3cd243f`). Native-
material-only previews now report `criteria.native_material_ownership` from
the selected native state instead of running the unrelated generic multi-view
component ownership comparison. Attribute/layer ownership guards and exact
target, material, preservation, setter, readback and recovery safeguards are
unchanged. **161 unique focused checks PASS** including version consistency:
154 non-HTTP checks and 7 HTTP checks. The initial HTTP attempt was blocked by
sandbox socket creation; the network-enabled rerun passed all 7. This is not
full CI.

The [exact-target contract](m4-editing-api-0.32.0.md#exact-child-native-material-target-0420)
limits the opt-in to one Slab child and its exact MultiSlab parent in one
foreground drawing, with no predicate, attributes or exclusions. It binds the
exact target and inventory through preview, revalidation, final setter and
readback/recovery; highlight targets the child, never its parent. Regenerated
or missing views stay unknown, without replacement-view fallback.

The supplied Allplan evidence contains only health, context and preview. The
installed 0.42.0 bridge reports source `3cd243f`, verified integrity, and
Allplan 2026.1 (executable 16.1617.8659.814). Its preview matched the exact
Slab child, observed current Material `" "` against requested `C35/45`, and
reported `usable_for_write=true`; `setter_calls_started=0`. The agent stopped
before highlight. The old `criteria.component_ownership` result was an
aggregate ancillary conflict. Supplied evidence has no per-view observations
to establish its cause; a distinct-view fixture reproduced the report, but
this does not establish native owner conflict or failed write. Raw evidence is
preserved [unchanged here](test-results/evidence/0.42.0-2026-10-27/allplan-042-native-test-evidence.json).
This does not establish native acceptance or exact ZIP verification.

Do not repeat the completed 0.41 getter or historical setters.

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
