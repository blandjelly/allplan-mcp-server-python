# Current M4 handoff

## Next task — native trial of 0.44.1: Slab tier 0 Material, Beam native Material

Start condition: candidate **0.44.1** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2 and 6](development-plan.md#remaining-work-and-unresolved-errors)).

1. **Slab (read-only, zero setters).** Repeat the `material_comparison` with
   `attribute_ids=[508]`, `parent_ref` and `include_parent=true` (child
   `8a693925…`/`a0fcd7b3…`, MultiSlab `bf097d95…`/`b4a59b5b…`; re-query UUIDs).
   Record `slab_tiers.tiers[0]` (`Material`, members) and `variable_tier` on
   child and parent. If tier 0 holds the UI-visible material, the next code
   change is a tier-0 owner write (`SlabTierProperties` setter); otherwise
   the member lists decide the next candidate. No Slab Apply.
2. **Beam native Material (disposable).** Re-query `Beam_TypeUUID`; `model_edit`
   preview with `target={"kind":"native_material","tier_index":1}`, value
   `C30/37`, `native_types=["Beam_TypeUUID"]`; highlight, Apply with a new
   `execution_id`, fresh readback, UI check, then UI Undo and a restoration
   preview (or `material_comparison` on the Beam). Stop at any blocker.

Completion: tier 0 observation and a decided Slab flow in the plan; Beam
native Material cycle recorded (or its blocker). Do not repeat the
0.40.0–0.44.0 probes or the Beam attribute write.

## Latest version

**0.44.1** (candidate, branch `claude/m4-0441-slab-tier0-ci-speed`):
`slab_tiers` reads tiers zero-based (tier 0 always, others within
`TierCount`) and adds `variable_tier`. CI runs the same test modules through
[run_tests_parallel.py](../utils/run_tests_parallel.py) with a uv cache
([testing policy](testing-policy.md#candidate-and-ci-selection)); this is a CI
change, so the full matrix applies. Focused checks PASS; a local parallel run
of all 805 tests PASS (245 s sequential vs 70 s, Linux). Full CI, ZIP
verification and native trial pending.

**0.44.0** (source `febdb72`, PR #53) is the installed baseline; health:
Allplan 2026.1, `integrity=sha256-verified`. Owner trial,
[raw evidence](test-results/evidence/0.44.0-2026-11-02/evidence-20261102.jsonl)
(owner: UI identical to the log, Undo worked):

- **Trace.** `inspect_journal`: active 0.5 MB, archive seven segments
  (43.6 MB, complete); no rotation was due.
- **Slab tiers.** On the Slab child (both views), the MultiSlab and the parent
  read: native Material `" "`, `tier_api=present`, `TierCount=1`,
  `GetSlabTierProperties(1)` → `IndexError`, i.e. tiers are zero-based and
  tier 0 was not read. Both SkeletonBeams: `StructuralBeamProperties.Material`
  `" "`; Beam: `BeamElement.Properties.Material` `""`.
- **Beam attribute write PASS.** Plan `9ea3c5f0…`, execution
  `9eb643bf0b9547e5b537acfa3c91a006`: attribute 508 `""` → `TEST-BEAM`,
  `completed`/`applied`, `readback_matches`; all three root representations
  (views `362f80d3` ×2, `6035d406`) agreed before and after. UI showed the
  value; UI Undo worked (owner-observed). The later `inspect` sample did not
  include the Beam, so there is no post-Undo API read.

**0.43.1** (`4a517bc`, PR #52) read-only trial
([raw evidence](test-results/evidence/0.43.1-2026-11-02/evidence-20261102.jsonl)):
Beam listing of 44 attributes on both views, `consistent`; the trace filled
and was archived by confirmed cleanup (automated from 0.44.0).

**0.43.0** (source `1be4072`, PR #51) trial
([raw evidence](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)):
Slab Apply `9c6a0d326b61440f8f11311c1ec569b9` (`C35/45`) ran the
`SlabProperties.Material` setter and `ModifyElements` without error, but every
readback stayed `" "`; the only inventory change was the MultiSlab
`AttributeContainer` regenerated (`b4e594f7…` → `60c64a1a…`), and UI Undo
restored it. Cause (wrong owner, tier storage or no-op setter) is open; do not
repeat that payload. **0.42.1** (`eecdfeb`, PR #49): owner-confirmed CI/ZIP;
[raw evidence](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
retained unchanged.

## Key errors and necessary earlier context

- **Slab executions.** `a8a31c72975541feb1c36a2e8cbb8f65` (0.42.1) is
  `reconciled` by read-only recovery on 0.43.0 (value `" "`); `9c6a0d32…`
  (0.43.0) is `reconciled`/`old_value_observed` after `unknown`. Target: drawing
  101, child model `8a693925-ae20-4dda-91d1-3951af3c0a52`, view
  `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, parent MultiSlab
  `bf097d95-8275-4229-ac74-27bbea26c211` / `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`
  (`native_material_ownership`: `SlabElement`, `slab_properties`). Neither
  execution is an applied/preservation PASS; keep their journals.
- **Wall `3f2a8c9d7b5e4a1c9f8e6d3c2b1a0e9f`** was cleared by reviewed
  reconciliation (`reviewed_material_preservation_conflict`,
  `preservation_verified=false`): not an applied/preservation PASS.
- **Older histories:** `87a45065d5e14e3a9ac8c54756e273a0` is `stopped`,
  `reconciled: 1`, `requires_recovery=false` (no proof of applied success or
  preservation). `4388b04e39a14fac811db4f58723d01f` was absent from the 31
  inspected records, which does not establish its archive state. Do not delete
  journal records or repeat the inspection without new evidence.
- **Getter evidence (0.40.0/0.41.0)** remains read-only: native Material
  `" "` and attribute 508 `TEST1` on the Slab child, its parent and both
  SkeletonBeams; no writable owner or child/parent equivalence. The
  SkeletonBeam 1 target/parent-edge view discrepancy remains open.
- **0.39.0 reports** of native-value PASS on Wall, Wall with opening and Column
  and of attribute writes on two SkeletonBeams and the Slab/MultiSlab assembly
  stay limited to those reports ([coverage matrix](m4-coverage-matrix.md)).
- Scalability is bounded by the 200-result page, 10,000 adapters, time,
  memory and journal limits; more than 32 changes needs a durable manifest
  ([S0–S5](implementation-plan.md#scaling-analysis-of-developm4-and-mcp-ergonomics)).
- Native selection stays unsupported ([selection API](m4-native-selection-api.md)).
- The owner confirms whether `ci-required` is configured as a required check;
  direct pushes to `develop/m4` are rejected by repository rules, so changes go
  through PRs.

Preserve exact target/owner binding, revalidation, journals, trace, replay
protection, write and Undo guards, and unknown outcomes.
