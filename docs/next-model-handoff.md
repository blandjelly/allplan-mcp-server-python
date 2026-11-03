# Current M4 handoff

## Next task — native trial of 0.47.0: slab material on the MultiSlab shown in the UI

Start condition: candidate **0.47.0** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2–3](development-plan.md#remaining-work-and-unresolved-errors)).
Current stored state (0.46.0 read after UI Undo): MultiSlab
`bf097d95-8275-4229-ac74-27bbea26c211` (view `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`)
attribute 508 `TEST1`, shown in the UI; its tier `8a693925-ae20-4dda-91d1-3951af3c0a52`
(parent-edge view `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`) `TEST2`, not shown.

1. **Hint, read-only.** Preview
   `{"action":"preview","scope":{"drawing_files":[101],"include_passive":false,"visibility":"api_select_all"},"native_types":["Slab_TypeUUID"],"changes":[{"target":{"kind":"attribute","attribute_id":508,"property_owner":"selected_element"},"value_type":"text","value":"TEST3","mode":"replace"}]}`.
   Expected: no change, `blocked[0].reason="slab_tier_not_shown_in_ui_use_multislab"`,
   `blocked[0].ui_owner.model_uuid` = the MultiSlab above. Also run
   `material_comparison` on the tier view without `parent_ref`: the error now
   names `parent_ref`.
2. **Slab material in plain language (disposable).** Tell the agent only
   "zmień materiał stropu na TEST3". Expected: it previews
   `native_types=["MultiSlab_TypeUUID"]`, attribute 508, `property_owner="selected_element"`,
   one change on `bf097d95…`. Highlight, Apply with a new `execution_id`,
   record outcome and readback, the UI material (`TEST3`), then UI Undo and
   `material_comparison` with `parent_ref` (MultiSlab `TEST1`, tier `TEST2`).
   `unknown` → recover read-only and stop.
3. **Optional — tier storage route (0.46.0, still unobserved).** Restore the
   tier: preview with the step 1 scope, `native_types=["Slab_TypeUUID"]`,
   `exact_target={"drawing_file":101,"model_uuid":"8a693925-ae20-4dda-91d1-3951af3c0a52","view_uuid":"a0fcd7b3-85c8-4f83-99b7-59e8a3463c94","parent_ref":{"model_uuid":"bf097d95-8275-4229-ac74-27bbea26c211","view_uuid":"b4a59b5b-c0ae-4c1e-9d59-df5761390eb9"}}`
   and the step 1 change with value `TEST1`. Apply only with one change on
   `a0fcd7b3…`. Expected `applied` with
   every tier wrapper agreeing, UI unchanged (still the MultiSlab value);
   record `representation_consensus.exact_inventory`. No UI Undo needed (the
   restored value is the 0.44.2 baseline).

Completion: step 2 `applied` with UI and Undo closes the visible slab material
(items 2–3); step 3 settles whether the parent-edge tier write persists. Do not
repeat the Beam native Material write (PASS in 0.46.0), the native Slab
Material Apply, or the 0.40.0–0.45.0 probes.

## Latest version

**0.47.0** (candidate, branch `claude/m4-0470-multislab-ui-material`): a Slab
tier attribute write without `exact_target` is blocked as
`slab_tier_not_shown_in_ui_use_multislab`, and that row (also
`slab_has_parent_requires_explicit_property_owner`) names the MultiSlab to
preview in `blocked[].ui_owner` with a `next_preview` hint; nothing is
redirected. The tool description tells the agent that the slab material
shown in the UI is the MultiSlab's attribute 508. `material_comparison`
errors on a non-direct view name the `parent_ref` route
([contract](m4-editing-api.md#slab-tier-attribute-writes-and-the-ui-material-owner-04500460-observations-0470-contract),
[tool reference](tool-reference.md#exact_target--native-material-or-one-attribute-on-one-exact-slab-child)).
Focused checks PASS (250 tests in 15 affected ownership/material/identity/
model-edit/MCP/package modules, 4 new or extended). Full CI, ZIP verification
and native trial pending.

**0.46.0** (source `6437bf2`, PR #57) is the installed baseline. Owner trial
2026-11-03, [raw evidence](test-results/evidence/0.46.0-2026-11-03/evidence-20261103.jsonl),
[conversation log](test-results/evidence/0.46.0-2026-11-03/agent_text.md):

- **Beam native Material — PASS.** Execution `5a0bc36674f545d58e959124aab5ea29`:
  `""` → `C30/37`, `applied`/`readback_matches` on all root views, with
  `accepted_preservation_drift.accepted="auxiliary_children_regenerated"`
  (one-for-one AttributeContainer/WallAxis) on `362f80d3…`. The owner
  reports UI and UI Undo passed; a later preview shows old value `""`.
- **Slab — the UI shows the MultiSlab.** `material_comparison` (first call
  without `parent_ref` failed `probe_scope_unavailable`; the second with it
  succeeded) read 508 `TEST2` on the tier and `TEST1` on the MultiSlab; the
  owner sees one slab object showing `TEST1`. The exact-target tier preview
  was `no_op` (already `TEST2`), so the 0.46.0 tier route ran no setter. With
  the owner's approval the agent wrote the MultiSlab instead: execution
  `04569db1850748b2b029629c935dd36a`, `TEST1` → `TEST2`, `applied` on
  `b4a59b5b…`, UI `TEST2`, UI Undo, fresh read MultiSlab `TEST1`, tier `TEST2`.
  The tier value is most likely the 0.45.0 write, so the 0.45.0 `applied`
  results wrote tier storage that the UI does not display. This is the basis
  for 0.47.0.

**Earlier trials** (raw evidence retained unchanged):
[0.45.0](test-results/evidence/0.45.0-2026-11-03/evidence-20261103.jsonl)
(`207b299`, PR #56) — the Beam step wrote attribute 508 (`47fa1ac7…`, UI and
UI Undo) instead of native Material; two non-exact tier writes (`686a0ea5…`,
`010dc61b…`) reported `applied` on wrapper `7f9df4e3…` while the UI kept
`TEST1` (explained by the 0.46.0 read above).
[0.44.2](test-results/evidence/0.44.2-2026-11-03/evidence-20261103.jsonl)
(`4238a08`, PR #55) — Beam native Material `457f34db…` reached `C30/37` with a
one-for-one AttributeContainer/WallAxis regeneration, reviewed reconciliation,
UI Undo; Slab UI material `TEST1` is attribute 508, native Material `" "`.
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

- **0.46.0/0.45.0 executions.** Beam `5a0bc366…` (native Material) and
  MultiSlab `04569db1…` (508) are `completed` and UI-undone. Beam `47fa1ac7…`
  (0.45.0, attribute 508) is `completed` and UI-undone. Slab tier `686a0ea5…`
  and `010dc61b…` (0.45.0) are `completed`/`applied`; the tier still reads
  `TEST2`, which the UI does not show. They are not a UI material PASS, need
  no recovery (not `unknown`) and must not be replayed.
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
