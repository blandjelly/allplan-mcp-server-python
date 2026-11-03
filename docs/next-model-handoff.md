# Current M4 handoff

## Next task — native trial of 0.44.2: Beam Material diff, Slab UI material

Start condition: candidate **0.44.2** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2 and 6](development-plan.md#remaining-work-and-unresolved-errors)).

1. **Beam native Material (disposable, changed report).** Re-query
   `Beam_TypeUUID`; `model_edit` preview with
   `target={"kind":"native_material","tier_index":1}`, value `C30/37`,
   `native_types=["Beam_TypeUUID"]`; highlight, Apply with a new
   `execution_id`. If the outcome is again `unknown`, record the
   `component_tree_diff` of the reviewed view and check the UI. Only if the
   diff shows nothing but regenerated auxiliary children (root, lineage and
   other sections unchanged) and the UI shows `C30/37`, recover and submit the
   offered `reviewed_material_reconciliation`; otherwise leave it unknown.
   Then UI Undo and a fresh `material_comparison` on a **direct** Beam view.
2. **Slab (read-only, owner observation).** Record what the Allplan UI shows
   as the material of slab layer "Warstwa płyty" (child `8a693925…`, MultiSlab
   `bf097d95…`). Use the child's parent-edge view (`a0fcd7b3…`), not the
   query's direct view, for `material_comparison`. No Slab Apply.

Completion: the Beam diff recorded and the Beam outcome reviewed (reconciled
or left unknown, plus Undo); the UI Slab material recorded so the plan can
decide the tier-0 write candidate (item 2). Do not repeat the 0.40.0–0.44.1
probes or the Beam attribute write.

## Latest version

**0.44.2** (candidate, branch `develop/m4`): native-material preservation
drift with a changed `component_tree` now carries a bounded
`component_tree_diff` (root/flag changes, `lineage_changed`, per-type child
counts, up to four removed/added children and edges); non-Wall families report
`native_material_invariants_changed`. The Slab `parent_ref` probe names the
parent-edge child view when the requested view is not listed. No guard,
budget, journal or reconciliation rule changed; the diff never accepts drift.
Focused checks PASS (270 tests in the affected material/edit/probe modules,
plus 80 package/smoke/CI-policy tests for the version bump).
Full CI, ZIP verification and native trial pending.

**0.44.1** (source `8e06fa4`, PR #54) is the installed baseline; health:
Allplan 2026.1, `integrity=sha256-verified`. Owner trial 2026-11-03,
[raw evidence](test-results/evidence/0.44.1-2026-11-03/evidence-20261103.jsonl):

- **Slab tier 0 (read-only).** The first request used the query's direct
  child view `7f9df4e3…` and stopped with `probe_scope_unavailable` (the parent
  lists the child under `a0fcd7b3…`). With `a0fcd7b3…`: child and MultiSlab
  both `TierCount=1`, `VariableTier=1`, `GetSlabTierProperties(0).Material`
  `" "` (same as `SlabProperties.Material`), attribute 508 `TEST1`, zero
  setters. Tier 0 therefore does not expose a different material via the API;
  its members include `SetMaterial`/`SetThickness`, and `SlabProperties` has
  no `SetSlabTierProperties`.
- **Beam native Material.** Plan `4873ded4…`, execution
  `aa7189120e58435e80ca28dfc0996a31`: `""` → `C30/37`. After `ModifyElements`
  all three root representations read `C30/37` (`reconciliation_readback`),
  but the reviewed view's preservation changed only in `component_tree`
  (reason then named `wall_material_invariants_changed`) and the third view
  UUID was regenerated (`6035d406…` → `5aed7df4…`), so the outcome was
  `unknown`. The first recovery offered a reconciliation (not acknowledged).
  After UI Undo and a host restart, recovery read `""` on all views
  (original view `6035d406…` back) → `reconciled`/`old_value_observed`. This is
  no applied/preservation PASS; the 0.44.1 report did not say which children
  changed, hence 0.44.2.
- `material_comparison` on Beam view `362f80d3…` (the edit plan's view)
  stopped because only `6035d406…` is a direct view; the direct view read
  `""`. Use direct views for this probe.

**0.44.0** (`febdb72`, PR #53) trial
([raw evidence](test-results/evidence/0.44.0-2026-11-02/evidence-20261102.jsonl)):
Slab tiers are zero-based (`GetSlabTierProperties(1)` → `IndexError`); Beam
attribute 508 write PASS (execution `9eb643bf0b9547e5b537acfa3c91a006`,
`""` → `TEST-BEAM` on all three representations, UI and UI Undo
owner-observed, no post-Undo API read); trace archive automated.

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

- **Beam execution `aa7189120e58435e80ca28dfc0996a31`** (0.44.1) is
  `reconciled`/`old_value_observed` after `unknown` and UI Undo; keep its
  journal. Not an applied PASS.
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
