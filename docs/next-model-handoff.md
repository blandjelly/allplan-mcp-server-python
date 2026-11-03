# Current M4 handoff

## Next task — native trial of 0.45.0: Beam Material `applied`, Slab attribute 508

Start condition: candidate **0.45.0** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2, 3 and 6](development-plan.md#remaining-work-and-unresolved-errors)).

1. **Beam native Material (disposable).** Re-query `Beam_TypeUUID`;
   `model_edit` preview with `target={"kind":"native_material","tier_index":1}`,
   value `C30/37`, `native_types=["Beam_TypeUUID"]`; highlight, Apply with a
   new `execution_id`. Expected: outcome `applied` and, on the reviewed view,
   `accepted_preservation_drift.accepted="auxiliary_children_regenerated"`.
   Record the UI material, then UI Undo and a fresh preview (no Apply) showing
   old value `""` and the original children. If the outcome is `unknown`,
   recover read-only and stop; do not acknowledge a reconciliation.
2. **Slab attribute 508 (disposable).** The owner observed that the UI material
   of slab layer "Warstwa płyty" is attribute 508 (`TEST1`). Preview with
   `native_types=["Slab_TypeUUID"]`, `attribute_ids=[508]`,
   `attribute_read_mode="stored"` and change
   `{"target":{"kind":"attribute","attribute_id":508,"name":"Materiał","property_owner":"selected_element"},"value_type":"text","value":"TEST2","mode":"replace"}`.
   Apply only if the plan has exactly one change on child `8a693925…`;
   otherwise record the plan and stop. After Apply record the UI material of
   the slab layer, then `material_comparison` on the child's parent-edge view
   `a0fcd7b3…` with `include_parent=true` (child and MultiSlab 508), UI Undo
   and the same read again.

Completion: Beam `applied` with UI and Undo (closes item 6 native Material at
VALUE/PASS level); the Slab attribute 508 child write with UI and Undo, or the
recorded plan that prevented it (item 3). Do not repeat the 0.40.0–0.44.2
probes, the native Slab Material Apply or the Beam attribute write.

## Latest version

**0.45.0** (candidate, branch `claude/m4-0450-beam-regenerated-children`):
after a setter, the fresh readback/recovery of a `Beam_TypeUUID` native
Material accepts one drift only: `ModifyElements` replacing its
`AttributeContainer_TypeUUID`/`WallAxis_TypeUUID` children one-for-one under
the unchanged root, with every other section, root, lineage, flags and other
edges identical and all views agreeing. The reviewed representation reports
`accepted_preservation_drift`; the outcome can be `applied`. Preview,
revalidation and the final setter boundary stay byte-exact; other families,
other child types, count changes and pre-setter drift keep `unknown` /
`repair_conflict` ([tool reference](tool-reference.md#native_material--experimental-architectural-material)).
Focused checks PASS (257 tests in the affected material/edit/recovery modules,
plus 80 package/MCP smoke/CI-policy tests for the version bump).
Full CI, ZIP verification and native trial pending.

**0.44.2** (source `4238a08`, PR #55) is the installed baseline. Owner trial
2026-11-03, [raw evidence](test-results/evidence/0.44.2-2026-11-03/evidence-20261103.jsonl):

- **Beam native Material.** Plan `a5f6c4d7…`, execution
  `457f34dbed6d45109ffb397c5d40321c`: `""` → `C30/37`, outcome `unknown`
  (`native_material_invariants_changed`, only `component_tree` changed). The
  `component_tree_diff`: no root/flag/lineage change; AttributeContainer
  `b9f1cb84…` → `5d92036f…` and WallAxis `c40c8930…` → `4840a7fa…` (same view
  `b10f6f8a…`), both still edged to the root view `362f80d3…`. All views read
  `C30/37`; the third root view again regenerated (`6035d406…` → `7fb811fa…`).
  The owner saw `C30/37` in the UI and acknowledged the offered reconciliation
  → `reconciled`/`reviewed_material_preservation_conflict`,
  `preservation_verified=false`. UI Undo: the owner saw the material empty; a
  fresh preview read `""` with the original children. This is a VALUE result,
  not an applied/preservation PASS; it is the basis for 0.45.0.
- **Slab (read-only).** UI material of the slab layer: **`TEST1`** (owner).
  `material_comparison` on view `a0fcd7b3…` with the parent: native Material
  and tier 0 `" "`, attribute 508 `TEST1`, zero setters. The UI material is
  attribute 508; the native tier-0 write candidate is dropped.

**Earlier trials** (raw evidence retained unchanged):
[0.44.1](test-results/evidence/0.44.1-2026-11-03/evidence-20261103.jsonl)
(`8e06fa4`, PR #54) — Slab tier 0 `Material` `" "` on child and MultiSlab
(request the parent-edge child view `a0fcd7b3…`, not the query's `7f9df4e3…`);
the first Beam native Material write (same drift, undone, recovered
`old_value_observed`); `material_comparison` on a Beam needs a direct view
(`6035d406…`, not `362f80d3…`).
[0.44.0](test-results/evidence/0.44.0-2026-11-02/evidence-20261102.jsonl)
(`febdb72`, PR #53) — Slab tiers are zero-based; Beam attribute 508 write PASS
(`9eb643bf0b9547e5b537acfa3c91a006`, `""` → `TEST-BEAM`, UI and UI Undo).
[0.43.1](test-results/evidence/0.43.1-2026-11-02/evidence-20261102.jsonl)
(`4a517bc`, PR #52) — Beam listing of 44 attributes, `consistent`.
[0.43.0](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)
(`1be4072`, PR #51) — Slab native Material Apply `9c6a0d32…` (`C35/45`): the
setter ran, readback stayed `" "`, MultiSlab `AttributeContainer` regenerated,
UI Undo restored it; do not repeat that payload.
[0.42.1](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
(`eecdfeb`, PR #49) — owner-confirmed CI/ZIP.

## Key errors and necessary earlier context

- **Beam executions.** `457f34dbed6d45109ffb397c5d40321c` (0.44.2) is
  `reconciled`/`reviewed_material_preservation_conflict`,
  `preservation_verified=false`, then UI-undone; `aa7189120e58435e80ca28dfc0996a31`
  (0.44.1) is `reconciled`/`old_value_observed`. Keep both journals; neither is
  an applied PASS. Beam target: drawing 101, model
  `7cc9ac55-6111-4508-bae8-d33918dbe77e`, reviewed view `362f80d3…`.
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
