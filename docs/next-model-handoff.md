# Current M4 handoff

## Next task — native trial of 0.46.0: Beam native Material, Slab tier attribute 508

Start condition: candidate **0.46.0** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2, 3 and 6](development-plan.md#remaining-work-and-unresolved-errors)).
Give the agent the exact requests below; in 0.45.0 the agent replaced step 1
with an attribute 508 write, so the native Material step was never run.

1. **Beam native Material (disposable).** Preview exactly
   `{"action":"preview","native_types":["Beam_TypeUUID"],"changes":[{"target":{"kind":"native_material","tier_index":1},"value":"C30/37"}]}`
   (not `kind:"attribute"`). Current state: attribute 508 `""` after the 0.45.0
   Undo; native Material is expected `""`. Highlight, Apply with a new
   `execution_id`. Expected: `applied` and, on view `362f80d3…`,
   `accepted_preservation_drift.accepted="auxiliary_children_regenerated"`.
   Record the UI material, then UI Undo and a fresh preview (no Apply) showing
   old value `""`. If the outcome is `unknown`, recover read-only and stop; do
   not acknowledge a reconciliation.
2. **Slab tier attribute 508 (disposable).** First read-only:
   `material_comparison` on child view `a0fcd7b3…` with `include_parent=true`,
   and record the UI material of slab layer "Warstwa płyty". The 0.45.0 Applies
   left the stored state unclear (see below); if the views disagree, stop and
   report. Then preview with
   `scope={"drawing_files":[101],"include_passive":false,"visibility":"api_select_all"}`,
   `native_types=["Slab_TypeUUID"]`, `exact_target={"drawing_file":101,"model_uuid":"8a693925-ae20-4dda-91d1-3951af3c0a52","view_uuid":"a0fcd7b3-85c8-4f83-99b7-59e8a3463c94","parent_ref":{"model_uuid":"bf097d95-8275-4229-ac74-27bbea26c211","view_uuid":"b4a59b5b-c0ae-4c1e-9d59-df5761390eb9"}}`
   and `changes=[{"target":{"kind":"attribute","attribute_id":508,"property_owner":"selected_element"},"value_type":"text","value":"TEST2","mode":"replace"}]`.
   Apply only if the plan has one change with `target_view_uuid` `a0fcd7b3…`.
   Record the outcome, `representation_consensus` (both views,
   `exact_inventory`), the UI material, the same `material_comparison`, then UI
   Undo and the read again. `unknown` → recover read-only and stop.

Completion: Beam `applied` with UI and Undo (item 6); Slab tier `applied` with
both views and the UI showing `TEST2`, then Undo (items 2–3), or the recorded
outcome that shows the parent-edge write also does not persist. Do not repeat
the 0.40.0–0.45.0 probes, the native Slab Material Apply, the Beam attribute
write or the non-exact Slab attribute write.

## Latest version

**0.46.0** (candidate, branch `claude/m4-0460-slab-tier-exact-attribute`): a `selected_element`
attribute write on a Slab tier inside a MultiSlab now requires `exact_target`
on its parent-edge view; otherwise it is blocked
(`slab_tier_requires_exact_parent_edge_target`). With it, `ChangeAttributes`
runs on the parent-edge wrapper, preflight and readback require agreement on
every wrapper of the tier, and a post-setter one-for-one AttributeContainer
replacement is the only accepted inventory drift
([contract](m4-editing-api.md#slab-tier-attribute-writes-and-the-parent-edge-view-0450-observation-0460-contract),
[tool reference](tool-reference.md#exact_target--native-material-or-one-attribute-on-one-exact-slab-child)).
The tool description now says not to substitute attribute `Materiał` for
`native_material`. Focused checks PASS (402 tests in 21 affected
model-edit/material/recovery/MCP/package modules, including 6 new tier
tests); full CI, ZIP verification and native trial pending. The 0.45.0 Beam regeneration
acceptance is unchanged and still not native-observed.

**0.45.0** (source `207b299`, PR #56) is the installed baseline. Owner trial
2026-11-03, [raw evidence](test-results/evidence/0.45.0-2026-11-03/evidence-20261103.jsonl):

- **Beam — attribute 508, not native Material.** The agent previewed
  `target.kind="attribute"`, ID 508 instead of step 1. Execution
  `47fa1ac745c848609da338b7da83fcb2`: `""` → `C30/37`, `applied` on all three
  root views; the owner saw `C30/37` in the UI, UI Undo worked, and a later read
  on view `6035d406…` returned `""` with the original children. Hence no
  `accepted_preservation_drift`: that is native-Material-only. The 0.45.0
  native Material acceptance remains untested.
- **Slab tier — false `applied`.** Executions
  `686a0ea5f98c47ad993fb570c389fbd8` and `010dc61bba7d4542ba8933d63bc4e7c5`
  (attribute 508 `TEST1` → `TEST2`, non-exact preview) each reported `applied`
  from one wrapper `7f9df4e3…` (`IsInMacro=true`); the UI material stayed
  unchanged after both, and a read between them returned `TEST1`. The
  parent-edge view `a0fcd7b3…` was never part of the consensus. No read follows
  the second Apply, and Undo of the Slab writes is not recorded, so the current
  stored value is unverified. This is the basis for 0.46.0.

**0.44.2** (source `4238a08`, PR #55): Beam native Material execution
`457f34dbed6d45109ffb397c5d40321c` read `C30/37` on every view with only a
one-for-one AttributeContainer/WallAxis regeneration, reconciled after review
(`preservation_verified=false`), UI Undo restored `""`; basis for 0.45.0. Slab
read-only: UI material `TEST1` is attribute 508; native Material and tier 0
read `" "` ([raw evidence](test-results/evidence/0.44.2-2026-11-03/evidence-20261103.jsonl)).

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

- **0.45.0 executions.** Beam `47fa1ac7…` (attribute 508) is `completed`
  and UI-undone. Slab `686a0ea5…` and `010dc61b…` are journaled `completed`/
  `applied` although the UI did not change: do not treat them as attribute 508
  PASS and do not replay them; they need no recovery (not `unknown`).
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
