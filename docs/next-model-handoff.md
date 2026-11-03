# Current M4 handoff

## Next task — native properties API note (plan item 5), owner picks the order of items 4–8

The Slab material priority (plan items 2–3) is closed by the 0.47.0 trial
below. The remaining M4 work is in the
[plan](development-plan.md#remaining-work-and-unresolved-errors); the owner
decides which item goes first. Default proposal, because it needs no native
trial to start: **item 5, step 1** — write the API note for native properties
beyond Material. Scope: `WallTierProperties`, `ColumnProperties`,
`BeamProperties`, `StructuralBeamProperties`, `SlabProperties` members
(thickness, height/plane references, surface, priority, calculation mode,
trade, hatch/filling): which have documented setters, their owner (element,
tier, parent), the modify call that persists them and an independent readback.
Separate SDK documentation, hypothesis and native observation; extend
[editing API notes](m4-editing-api.md) rather than adding a file. Completion:
the note names one candidate property per family with a write/readback/Undo
plan and the preservation fields it must keep; no runtime code yet.

Do not repeat: the MultiSlab attribute 508 write (PASS 0.46.0 and 0.47.0),
the exact parent-edge tier write (0.47.0), the Beam native Material write
(PASS 0.46.0), the native Slab Material Apply (0.43.0) or the 0.40.0–0.45.0
probes.

## Latest version

**0.47.0** (source `ceec638`, merged as PR #58 / `0ad7a4c`) is installed;
health on 2026-11-03 reports bridge 0.47.0, source
`ceec638ea4d7d825e5036cb643a293021e61df2a`, integrity `sha256-verified`,
Allplan 2026.1. Behaviour: a Slab tier attribute write without
`exact_target` is blocked as `slab_tier_not_shown_in_ui_use_multislab` and
names the MultiSlab in `blocked[].ui_owner` with a `next_preview` hint; the
tool description tells the agent the UI slab material is the MultiSlab's
attribute 508; `material_comparison` on a non-direct view names `parent_ref`
([contract](m4-editing-api.md#slab-tier-attribute-writes-and-the-ui-material-owner-04500460-observations-0470-contract)).
Focused checks PASS (250 tests); full CI and ZIP were the owner's gates
before the merge (no CI run ID or ZIP hash recorded here).

**Native trial 2026-11-03 — PASS for steps 1–3**
([raw evidence](test-results/evidence/0.47.0-2026-11-03/evidence-20261103.jsonl), drawing 101):

1. **Hint (read-only) — PASS.** Tier preview (`Slab_TypeUUID`, 508 `TEST3`)
   returned no change, `blocked[0].reason="slab_tier_not_shown_in_ui_use_multislab"`
   and `ui_owner` = MultiSlab `bf097d95…`/`b4a59b5b…`. `material_comparison`
   on tier view `a0fcd7b3…` without `parent_ref` failed
   `probe_scope_unavailable` with a message naming `parent_ref`.
2. **Plain-language slab material — PASS.** The agent previewed
   `MultiSlab_TypeUUID`, 508, `selected_element`, one change on `bf097d95…`
   (old `TEST1`). Apply `3f9c2a7e1b4d4e8f9a6c0d5b2e1f7a84`: `completed`,
   `applied`/`readback_matches` `TEST3` on `b4a59b5b…`, consensus complete and
   agreed. Owner: UI showed the agent's value, UI Undo worked. Post-Undo reads:
   MultiSlab `TEST1`; `material_comparison` with `parent_ref`: tier `TEST2`,
   MultiSlab `TEST1`, native Material `" "` on both. The plain-language prompt
   and UI observations are owner-reported (no conversation log supplied).
3. **Exact parent-edge tier write — VALUE.** Exact-target preview, one change
   `TEST2` → `TEST1` on the tier `8a693925…`. Apply
   `9b2e4d71c6a84f3e8d05a7f1e3b96c20`: `completed`, `applied`/`readback_matches`
   `TEST1`; both tier wrappers `7f9df4e3…` and `a0fcd7b3…` read the same value
   (identical readback hash), reviewed view present, `exact_inventory.status="unchanged"`
   (no AttributeContainer regeneration). MultiSlab still `TEST1`; owner sees
   `TEST1` in the UI. Limits: the UI observation cannot discriminate because
   tier and MultiSlab now hold the same value (0.46.0 already showed the UI
   follows the MultiSlab); no UI Undo was run (the write restored the 0.44.2
   baseline); persistence after save/reopen is not observed.

Current stored state: MultiSlab 508 `TEST1`, tier 508 `TEST1`, native Material
`" "` on both.

**Earlier trials** (raw evidence retained unchanged):
[0.46.0](test-results/evidence/0.46.0-2026-11-03/evidence-20261103.jsonl)
(`6437bf2`, PR #57, [conversation](test-results/evidence/0.46.0-2026-11-03/agent_text.md)) —
Beam native Material PASS (`5a0bc366…`, `""` → `C30/37`, accepted
`auxiliary_children_regenerated`, UI and UI Undo); the UI slab material is
the MultiSlab's 508 (MultiSlab write `04569db1…` `TEST1` → `TEST2`, UI, UI Undo).
[0.45.0](test-results/evidence/0.45.0-2026-11-03/evidence-20261103.jsonl)
(`207b299`, PR #56) — Beam 508 write (`47fa1ac7…`, UI and UI Undo); two
non-exact tier writes (`686a0ea5…`, `010dc61b…`) reported `applied` on wrapper
`7f9df4e3…` only and wrote tier storage the UI does not show.
[0.44.2](test-results/evidence/0.44.2-2026-11-03/evidence-20261103.jsonl)
(`4238a08`, PR #55) — Beam native Material `457f34db…` reached `C30/37` with a
one-for-one AttributeContainer/WallAxis regeneration, reviewed reconciliation,
UI Undo; Slab UI material `TEST1` is attribute 508, native Material `" "`.
[0.44.1](test-results/evidence/0.44.1-2026-11-03/evidence-20261103.jsonl)
(`8e06fa4`, PR #54) — Slab tier 0 `Material` `" "`; first Beam native Material
write (undone, recovered `old_value_observed`); `material_comparison` on a Beam
needs a direct view (`6035d406…`, not `362f80d3…`).
[0.44.0](test-results/evidence/0.44.0-2026-11-02/evidence-20261102.jsonl)
(`febdb72`, PR #53) — Slab tiers are zero-based; Beam 508 write PASS
(`9eb643bf0b9547e5b537acfa3c91a006`, UI and UI Undo).
[0.43.1](test-results/evidence/0.43.1-2026-11-02/evidence-20261102.jsonl)
(`4a517bc`, PR #52) — Beam listing of 44 attributes, `consistent`.
[0.43.0](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)
(`1be4072`, PR #51) — Slab native Material Apply `9c6a0d32…` (`C35/45`): the
setter ran, readback stayed `" "`, UI Undo restored it; do not repeat.
[0.42.1](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
(`eecdfeb`, PR #49) — owner-confirmed CI/ZIP.

## Key errors and necessary earlier context

- **0.47.0 executions.** MultiSlab `3f9c2a7e…` (508 `TEST3`) is `completed`
  and UI-undone; tier `9b2e4d71…` (508 `TEST2` → `TEST1`) is `completed`, not
  undone (baseline restored). Neither needs recovery; do not replay.
- **0.46.0/0.45.0 executions.** Beam `5a0bc366…` (native Material) and
  MultiSlab `04569db1…` (508) are `completed` and UI-undone. Beam `47fa1ac7…`
  (0.45.0, attribute 508) is `completed` and UI-undone. Slab tier `686a0ea5…`
  and `010dc61b…` (0.45.0) are `completed`/`applied` on one wrapper only; the
  tier value they left (`TEST2`) was overwritten by `9b2e4d71…`. They are not
  a UI material PASS, need no recovery and must not be replayed.
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
