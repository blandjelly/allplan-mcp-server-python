# Current M4 handoff

## Next task — native trial of candidate 0.51.1 (plan items 2a, 5 and 8)

Start after the owner has merged the 0.51.1 PR with green full CI and
installed it (health: bridge 0.51.1, the merged source commit,
`sha256-verified`). Drawing 101, Wall 300 with window `f4da72fe…` only,
plain-language requests, one Apply per step, UI check of both places
("Obmiar"/material in the element dialog and "Rodzaj rozliczenia"/"Materiał"
in the attributes palette), UI Undo counting the steps, then a fresh
`material_comparison` with `attribute_ids` [120] (508 is not stored there, so
`evidence_complete=false` is expected). Do not retry an `unknown` outcome;
recover read-only with the original execution ID and record
`preservation.identity_diff` and `preservation.regeneration_residual`.

Current state (fresh reads at the end of the 0.51.0 trial, 2026-11-07):
Wall 300 with window `f4da72fe…` (view `a76b11f4…`): Material `TEST1`, native
CalculationMode 0, attribute 120 `m3`, 508 not stored. Wall 240 `06d71e4d…`
and the Wall 200 with door `545bb0a2…` were UI-undone after PASS writes
(expected: Wall 240 `TEST`/508 `Silikat`, 0/`m`; Wall 200 `TEST1`, 0/`m3`).

1. **Read-only first:** a preview of the step-2 request; its
   `resource.native_property_state` must have no `partial_preservation` and
   `tier_hierarchy.shared_children` with the WindowTier (parent: Window).
2. **Paired calculation mode → `m`** ("zmień calculation mode dla ściany
   300 mm na m"): expect native 0→2 `applied` with
   `identities_regenerated_evidence_otherwise_equal` (Window, Sill,
   2 × AttributeContainer renamed, as observed in 0.51.0), attribute 120
   `m3`→`m` `applied`, `undo_group` `setters_in_step=2`; one UI Undo
   restores 0/`m3`.
3. **Paired material → `Cegła`**: native only (`attribute_follows_native`),
   expect `applied` with the same renaming; both UI places `Cegła`; one UI
   Undo.
4. If either stays `unknown`, the result names the residual paths; record
   them and recover read-only. Optional (plan item 8): `component_identity`
   on the window Wall's WallTier now reports `shared_children`; deleting the
   window only if the owner wants that destructive check.

Closure: the window Wall `applied` for both paired properties with UI check
and one UI Undo. Then plan item 3's explicit layer write or item 4. Do not
repeat: the 0.51.0 writes on the Wall 240 and the Wall with door (PASS), the
0.50.1/0.50.0/0.49.0 writes, the 0.48.0 reads, the MultiSlab attribute
508/120 writes, the exact parent-edge tier 508 write (0.47.0), the Beam native
Material write (PASS 0.46.0), the native Slab Material Apply (0.43.0) or the
0.40.0–0.45.0 probes.

## Candidate 0.51.1

Branch `claude/m4-0511-window-wall-evidence` (PR to `develop/m4`, link in
the PR list; the owner checks the tested commit). Fixes the 0.51.0 trial
finding ([contract](m4-editing-api.md#shared-opening-tier-and-regeneration-residual-0511-contract)):

- **Window Wall evidence:** the WallTier's WindowTier (parent: Window) is a
  bound `shared_children` edge instead of `component_child_owner_mismatch`,
  so the Wall snapshot is complete and order-independent rather than
  `partial_preservation` (reproduced with SDK doubles: regenerated parts
  enumerated after the WallTier changed the partial snapshot). Any other
  foreign parent still fails closed. `component_identity` uses the same rule.
- **`regeneration_residual`:** an unaccepted post-setter renaming lists up to
  8 evidence paths that still differ after renaming (review evidence only).
- Renaming rule, byte-equality, unknown outcomes, journals and recovery are
  unchanged.
- Focused local checks (Linux): 445 tests in 24 affected/dependent modules PASS
  (`unittest`). Full CI and native acceptance are not run.

## Installed version and last native evidence

**0.51.0** (source `f7ee761`, merged as PR #66 / `d46c5a2`) is installed;
health reports bridge 0.51.0, source
`f7ee761cf7902c719098523ed3e0afcd400cd276`, `sha256-verified`, Allplan 2026.1
(executable 16.1617.8659.814).

**Native trial 2026-11-07 — one UI Undo per Apply and Wall Material PASS; window Wall `unknown`**
([raw evidence](test-results/evidence/0.51.0-2026-11-07/evidence-20261107.jsonl),
table in the [API note](m4-editing-api.md#native-observations-0510-trial-2026-11-07)).
Owner results: tests 1–3 PASS, test 4 `unknown` with correct native values.

- Wall 200 with door paired calculation mode `m` (`6e6c83d2…`): `completed`,
  both setters in one `undo_group`; **one UI Undo** restored both places.
- Wall 240 paired material `Cegła` (`c6183d71…`): native + 508 `applied`
  (2 × AttributeContainer, WallAxis renamed); one UI Undo.
- Wall 200 with door paired material (`9109d250…`): native only (508 follows),
  `applied` (Door, DoorSill, 2 × AttributeContainer renamed); one UI Undo.
- Wall 300 with window: calculation mode (`a47dca16…`) and material
  (`5346fd71…`) reached the value (native 2 with attribute 120 still `m3`;
  `Cegła`) but stayed `unknown` on partial evidence with exactly Window, Sill
  and 2 × AttributeContainer renamed; the attribute 120 setter was skipped.
  Fixed in 0.51.1.

**0.50.1 trial (2026-11-07)** ([raw evidence](test-results/evidence/0.50.1-2026-11-07/evidence-20261107.jsonl),
[agent log](test-results/evidence/0.50.1-2026-11-07/agent-log.md),
[observations](m4-editing-api.md#native-observations-0501-trial-2026-11-07)):
door renaming and Column paired routing PASS; a paired write needed two UI
Undo steps and Wall Material stayed `unknown` (both fixed and PASS in 0.51.0).
The window Wall tree: Window → WindowTier → (Sill, WindowReveal →
WindowOpeningSmartPart → AttributeContainer, AttributeContainer); the WallTier
also lists the WindowTier.

**0.50.0 trial (2026-11-07)** ([raw evidence](test-results/evidence/0.50.0-2026-11-07/evidence-20261107.jsonl),
[observations](m4-editing-api.md#native-observations-0500-trial-2026-11-07)):
Column, plain Wall 240 and Beam `CalculationMode` writes `applied` with the
renaming rule and one UI Undo each; the Wall with door stopped `unknown`
(Door/DoorSill regeneration, fixed in 0.50.1 and PASS in its trial); the
Beam's direct view is `6035d406…` (`362f80d3…` gives `probe_scope_unavailable`
in `material_comparison`).

**0.49.0 trial (2026-11-07)** ([raw evidence](test-results/evidence/0.49.0-2026-11-07/evidence-20261107.jsonl),
[observations](m4-editing-api.md#native-observations-0490-trial-2026-11-07)):
native `CalculationMode` writes reached the value on Column, Wall 240, Beam
and Wall 200 but ended `unknown` through identity regeneration (all
reconciled); attribute 120 is **not** one storage with the native value
(followed on Column, Beam, Wall 240, not on the Wall with door; Undo on Wall
240 left it at `m`). Attribute 120 needs `value_type` `enum`/`auto`.

**0.48.0 read-only trial (2026-11-04)**
([raw evidence](test-results/evidence/0.48.0-2026-11-04/evidence-20261104.jsonl))
— still relevant:

- `Priority` agrees with the UI on Wall, Column, Beam and MultiSlab;
  `Thickness` is native millimetres, the UI shows metres.
- MultiSlab native `SlabProperties` (`m2`, Material `" "`) is not what the UI
  shows ("Cały obiekt": attribute 120 `m3`, 508 `TEST1`); the tier is shown in
  "Warstwa bieżąca" (508 `TEST2`, 120 `m2`). Plain slab requests target
  "Cały obiekt"; the layer only when named.
- **Trade (Wall, [raw evidence](test-results/evidence/0.48.0-2026-11-04/evidence-20261104-trade.jsonl)):**
  "Roboty murarskie" = native 12, cleared = 0 (initially −1); attribute 209 is
  not returned either way, so `Trade` has no attribute pair. A Trade write
  needs the project's code↔label list. Each UI edit replaced the Wall's
  AttributeContainer, so a new container UUID alone does not indicate an
  agent write.
- Wall has two UI materials: native tier Material `TEST` (element dialog) and
  attribute 508 `Silikat` (attributes palette).

Current stored state: MultiSlab 508 `TEST1`, tier 508 `TEST2`, native
Material `" "` on both; Wall 240 native `Trade` 0 ("Typ robót" empty).

**Earlier trials** (raw evidence retained unchanged):
[0.47.0](test-results/evidence/0.47.0-2026-11-03/evidence-20261103.jsonl)
(`ceec638`, PR #58) — non-exact tier writes blocked with `ui_owner`;
plain-language MultiSlab 508 Apply `3f9c2a7e…` (`TEST1` → `TEST3`, UI, UI
Undo); exact parent-edge tier write `9b2e4d71…` (`TEST2` → `TEST1`, both tier
wrappers agree, inventory unchanged, no UI Undo).
[0.46.0](test-results/evidence/0.46.0-2026-11-03/evidence-20261103.jsonl)
(`6437bf2`, PR #57, [conversation](test-results/evidence/0.46.0-2026-11-03/agent_text.md)) —
Beam native Material PASS (`5a0bc366…`, `""` → `C30/37`, accepted
`auxiliary_children_regenerated`, UI and UI Undo); the UI slab material is
the MultiSlab's 508 (MultiSlab write `04569db1…` `TEST1` → `TEST2`, UI, UI Undo).
[0.45.0](test-results/evidence/0.45.0-2026-11-03/evidence-20261103.jsonl)
(`207b299`, PR #56) — Beam 508 write (`47fa1ac7…`, UI and UI Undo); two
non-exact tier writes (`686a0ea5…`, `010dc61b…`) reported `applied` on wrapper
`7f9df4e3…` only and wrote tier storage (shown in the UI only in "Warstwa
bieżąca" mode, which was not checked then).
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

- **0.51.0 executions:** `6e6c83d25205408dbf610c4f41c54b3f`,
  `c6183d71b59f4af99b74c406f65e6467` and `9109d2501c264b4a8ad928d24c2d87dd`
  are `completed` and UI-undone. `a47dca1661274ac5a9f3390a816f3cd4` (window
  Wall calculation mode) is `reconciled`/`old_value_observed` after UI Undo
  (an Apply attempted before that recovery was rejected with
  `repair_recovery_required`, `4465eca9…`, no execution).
  `5346fd712e9f4923a432e697cf9cb93f` (window Wall material) is `reconciled`
  by acknowledged review (`reviewed_material_preservation_conflict`,
  `preservation_verified=false`, readback `Cegła`), then UI-undone. Neither is
  an applied PASS; nothing to replay.
- **0.50.1 executions:** `4043e5598cd444ab8c6c194baa1653f5` (Wall 200 paired
  calculation mode) and `341415e41d8f41e499b6cbd2b4397ccf` (Column) are
  `completed` and UI-undone (two steps and one step).
  `37196703c18e4cb2a7292b8fba30c953` (Wall 200 native Material) and
  `9ed2e229963f4611a206676c46c56a43` (Wall 240 native Material) are `stopped`:
  `unknown`, then read-only recovery after one UI Undo each returned
  `reconciled`/`old_value_observed`, `write_blocked=false` (one acknowledged
  recovery attempt was rejected with `repair_conflict` because the evidence
  had changed). Not applied PASS results; nothing to replay.
- **0.50.0 executions:** `1214d281a5a64144bc34506292ae7e72` (Column),
  `e4de1f7396cf43d79b404c55a94c93f0` (Wall 240),
  `d129c7c181f4407ab27fbf533dc7a954` (Beam) and
  `1dac121c0d2b4adfb086c86c2c33dfe4` (MultiSlab) are `completed` and UI-undone.
  `bd30912a43514f148735907c0b4dc258` (Wall 200 with door) is `stopped`: native
  `unknown`, attribute `skipped`; read-only recovery after the UI Undo
  returned `reconciled`/`old_value_observed`, `write_blocked=false`. It is not
  an applied PASS; nothing to replay.
- **0.49.0 executions** (all `stopped`, nothing to replay): native
  `7b2e4f91a0c34d58b6e1f3a9d2c75e10` (Column, reconciled with the owner's
  acknowledgement), `9e04b7d1c5a84f6e8b2d3c7f0a1e5d94` (Wall 240),
  `5a7c3e9b1d2f4806a9e4b8c0d3f21e76` (Beam; its first Apply was rejected with
  `repair_recovery_required` before any execution existed, and the ID was then
  used once for plan `8927d4b4…`), `7d3f0c8a2b6e4d19a5f1c9e0b4d72a38` (Wall
  200) are `reconciled` (`old_value_observed` after UI Undo), not applied
  PASS results; attribute executions `c41d8e2a…` and `e27b9d4f…` are
  `completed` and UI-undone.
- **0.47.0 executions.** MultiSlab `3f9c2a7e…` (508 `TEST3`) is `completed`
  and UI-undone; tier `9b2e4d71…` (508 `TEST2` → `TEST1`) is `completed`, not
  undone in that trial; 0.48.0 reads the tier as `TEST2` again (cause
  unknown; the owner is unsure about a manual change). Neither needs recovery; do not replay.
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
- `ci-required` is a required check on `develop/m4`; direct pushes are
  rejected, so changes go through PRs. Plan item 1 (delivery accounting) is
  closed by owner decision: full CI plus health integrity is the delivery
  evidence. The execution safeguards above stay in force.

Preserve exact target/owner binding, revalidation, journals, trace, replay
protection, write and Undo guards, and unknown outcomes.
