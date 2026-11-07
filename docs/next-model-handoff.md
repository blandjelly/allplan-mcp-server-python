# Current M4 handoff

## Next task — native trial of candidate 0.50.0 (plan items 2a and 5)

Start after the owner has merged the 0.50.0 PR with green full CI and
installed it (health: bridge 0.50.0, the merged source commit,
`sha256-verified`). Drawing 101, one Apply per step, UI check of both places
("Obmiar" in the element dialog and "Rodzaj rozliczenia" in the attributes
palette), then UI Undo **counting the steps needed until both places show the
old value**, then a fresh `material_comparison` with `attribute_ids [120]`
(Beam view `6035d406…`). Do not retry an `unknown` outcome; recover read-only
with the original execution ID and record `preservation.identity_diff`.

Use `{"target":{"kind":"paired_property","property":"calculation_mode"},"value":…}`
(plain request). Current state (fresh reads 2026-11-07): Wall 240 native 0
`m3` but attribute 120 `m` (diverged after the 0.49.0 Undo); Wall 200 native
0 / `m3`; Beam 0 / `m3`; MultiSlab attribute 120 `m3` (tier `m2`); Column
attribute 120 `m` (native not read after Undo, expected 2).

1. **Column → `m3`:** expect native `applied` with
   `accepted_preservation_drift.accepted="identities_regenerated_evidence_otherwise_equal"`
   (AttributeContainer + root view, `view_map`) and attribute 120 `applied`
   (`paired_attribute_already_set_by_native_write`, or written on
   `effective_target_view_uuid`).
2. **Wall 240 → `m3`:** the plan must contain only the attribute 120 change
   (native already `m3`); Apply repairs the divergence. Then **Wall 240 → `m`:**
   native + attribute; the Wall renaming rule is unverified (0.49.0 gave no
   per-section diff), so an `unknown` with `identity_diff` is a possible result.
3. **Wall 200 with door → `m`:** attribute 120 did not follow in 0.49.0, so
   expect an attribute setter after the native change; door unchanged.
4. **Beam → `m`**, then **MultiSlab → `m`** (attribute only,
   `plan.paired_property.attribute_only`, tier stays `m2`).
5. Optional (item 2a): paired material on Wall 240 (native `TEST`, 508
   `Silikat`), one value for both places.

Closure: per family `applied` native and attribute outcomes, UI values of both
places, the UI Undo step count and a restoration read of both. Then plan item
3's explicit layer write or item 4. Do not repeat: the 0.49.0 single-place
writes, the 0.48.0 reads, the MultiSlab attribute 508/120 writes, the exact
parent-edge tier 508 write (0.47.0), the Beam native Material write (PASS
0.46.0), the native Slab Material Apply (0.43.0) or the 0.40.0–0.45.0 probes.

## Candidate 0.50.0

Branch `claude/m4-0500-paired-properties` (PR to `develop/m4`, link in the PR
list; the owner checks the tested commit). Behaviour
([tool reference](tool-reference.md#paired_property--native-property-and-same-named-attribute-together-0500),
[contract](m4-editing-api.md#paired-properties-and-identity-regeneration-0500)):

- `paired_property` (owner decision 2026-11-07): native property + same-named
  attribute in one plan (`calculation_mode` = `CalculationMode` + 120,
  `material` = `Material` + 508); native first, attribute after an `applied`
  native change, no attribute setter when the native write already set it,
  regenerated reviewed view carried over; native half only on single-tier
  Wall, Column, Beam; attribute only (with `property_owner=selected_element`)
  elsewhere. Single-place kinds stay for explicit requests.
- `CalculationMode` post-setter drift that only renames the family's listed
  regenerated identities is accepted
  (`identities_regenerated_evidence_otherwise_equal`); other drift stays
  `unknown` with `preservation.identity_diff`. Material rule unchanged.
- Focused checks (local, Linux): 297 material/ownership/model-edit/executor/HTTP
  tests (including 13 new `test_paired_property` tests and one new MultiSlab
  paired test) and 123 MCP smoke, package, registration, host, delete and
  journal tests PASS. Full CI and native acceptance are not run yet.

## Installed version and last native evidence

**0.49.0** (source `c4be672`, merged as PR #63 / `869c322`) is installed; the
evidence's version response reports bridge 0.49.0, source
`c4be6723ed85587e38f4bca52064c1f0f251a16c`, integrity `sha256-verified`,
Allplan 2026.1. Full CI before the merge was the owner's gate.

**Native trial 2026-11-07 — native `CalculationMode` write VALUE, no `applied`
outcome** ([raw evidence](test-results/evidence/0.49.0-2026-11-07/evidence-20261107.jsonl),
[agent log](test-results/evidence/0.49.0-2026-11-07/agent-log.md), per-step
table in the [API note](m4-editing-api.md#native-observations-0490-trial-2026-11-07)):

- Native writes on Column (`7b2e4f91…`, 2→0), plain Wall 240 (`9e04b7d1…`,
  0→2), Beam (`5a7c3e9b…`, 0→2) and Wall 200 with door (`7d3f0c8a…`, 0→2)
  reached the new code (reconciliation readback, owner UI check) and UI Undo
  restored it, but all ended `unknown` through post-setter identity drift
  (AttributeContainer everywhere, Column root view `cc752bda…`→`8f88036e…`,
  Beam WallAxis, Wall sections without a diff). All four are `reconciled`
  and do not block writes. 0.50.0 accepts exactly that renaming.
- Attribute writes: Wall 240 attribute 120 `m3`→`m` (`c41d8e2a…`) and
  MultiSlab attribute 120 `m3`→`m` (`e27b9d4f…`, tier `m2` reported in
  `slab_tier_values`, unchanged) were `applied` and UI-undone.
- **Mirror verdict:** attribute 120 is not one storage with the native value.
  It followed the native write on Column, Beam and Wall 240, not on Wall 200;
  on Wall 240 the UI Undo restored the native code but left attribute 120 at
  `m`. Owner decision (2026-11-07): plain requests change both places
  (plan item 2a, candidate 0.50.0).
- Attribute 120 needs `value_type` `enum`/`auto`; `text` was rejected before
  any write (`attribute_type_unsupported`).

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
