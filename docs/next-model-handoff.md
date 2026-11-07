# Current M4 handoff

## Next task — native trial of candidate 0.50.1 (plan items 2a and 5)

Start after the owner has merged the 0.50.1 PR with green full CI and
installed it (health: bridge 0.50.1, the merged source commit,
`sha256-verified`). Drawing 101, one Apply per step, UI check of both places
("Obmiar" in the element dialog and "Rodzaj rozliczenia" in the attributes
palette), then UI Undo **counting the steps needed until both places show the
old value**, then a fresh `material_comparison` with `attribute_ids [120]`.
Do not retry an `unknown` outcome; recover read-only with the original
execution ID and record `preservation.identity_diff`.

Current state (fresh reads after the 0.50.0 trial's UI Undos, 2026-11-07):
Column native 2 / attribute 120 `m` (view `cc752bda…`); Wall 240 native 0
`m3` but attribute 120 `m` (still diverged); Wall 200 with door native 0 /
`m3`; Beam 0 / `m3` (direct view `6035d406…`); MultiSlab attribute 120 `m3`
(tier `m2`).

1. **Wall 200 with door `545bb0a2…` → `m`**, plain request
   ("zmień calculation mode dla ściany 200 mm na m"). The plan must be
   `paired_property` with the native change and attribute 120 (`m3`→`m`).
   Expect native `applied` with
   `accepted_preservation_drift.accepted="identities_regenerated_evidence_otherwise_equal"`,
   `regenerated_identities` = 2 × AttributeContainer, Door, DoorSill and an
   empty `view_map`, then attribute 120 `applied`/`readback_matches` (its
   setter runs: the attribute did not follow the native write in 0.49.0 and
   0.50.0). Check the door in the UI. This is the first paired write with two
   setters, so the UI Undo step count is the key result. Any other
   regeneration stays `unknown` with `identity_diff`: record it, recover
   read-only, do not retry.
2. **Routing check, Column → `m3`**, plain request ("zmień calculation mode
   dla słupa na m3"). The agent must send `paired_property` (0.50.0 trial: it
   sent `native_calculation_mode`). Expect native `applied` (AttributeContainer
   + root view renamed) and attribute 120 `applied` with
   `paired_attribute_already_set_by_native_write`, `setter_calls_started=0`.
   A single-place preview now reports `paired_property_hint` when attribute
   120 differs.
3. Optional (item 2a): paired material on Wall 240 (native `TEST`, 508
   `Silikat`). The Material drift rule is unchanged (Beam only), so an
   `unknown` native outcome with `identity_diff` is a possible result; it is
   evidence for a Wall Material rule, not a failure to retry.

Closure: Wall with door `applied` native and attribute, UI values of both
places, the UI Undo step count and a restoration read of both; Column routed
as `paired_property`. Then plan item 3's explicit layer write or item 4. Do
not repeat: the 0.50.0 writes listed below, the 0.49.0 single-place writes,
the 0.48.0 reads, the MultiSlab attribute 508/120 writes, the exact
parent-edge tier 508 write (0.47.0), the Beam native Material write (PASS
0.46.0), the native Slab Material Apply (0.43.0) or the 0.40.0–0.45.0 probes.

## Candidate 0.50.1

Branch `claude/m4-0501-wall-door-regeneration` (PR to `develop/m4`, link in
the PR list; the owner checks the tested commit). Fixes the one failure of the
0.50.0 trial ([contract](m4-editing-api.md#paired-properties-and-identity-regeneration-0500)):

- **Wall with door:** the `CalculationMode` identity-regeneration rule for
  `Wall_TypeUUID` also lists `Door_TypeUUID` and `DoorSill_TypeUUID`. In the
  trial (`bd30912a…`) the setter regenerated exactly the Door, its DoorSill
  and two AttributeContainers (root and door tier); DoorTier and DoorReveal
  kept identity and geometry. The bound evidence with these four pairs renamed
  hashes to the logged post-setter evidence, so 0.50.1 reports that write
  `applied` and the paired attribute 120 setter then runs. Windows and other
  openings are not observed and stay `unknown`. A regression test replays the
  logged evidence ([fixture](../tests/data/wall_door_calculation_mode_0500.json)).
- **Routing:** the `model_edit` description states that naming the property
  ("calculation mode", "obmiar", "materiał") is a plain request, and a
  single-place `native_calculation_mode` preview reports
  `paired_property_hint` (attribute 120 differs; informational, no change)
  with the plain `paired_property` request.
- Focused checks (local, Linux): 382 tests in 21 affected/dependent modules
  PASS (paired property, CalculationMode, Wall material/HTTP, model edit,
  ownership, native families, executor, recovery, exact target, material
  comparison, probe, package, registration, host, MCP smoke), including 4 new
  Wall-with-door tests and 1 hint test. Full CI and native acceptance are not
  run yet.

## Installed version and last native evidence

**0.50.0** (source `bf9605c`, merged as PR #64 / `297e89f`) is installed;
health reports bridge 0.50.0, source
`bf9605ca5b497a3e949aa746e4309502ffb7548d`, `sha256-verified`, Allplan 2026.1
(executable 16.1617.8659.814). Full CI before the merge was the owner's gate.

**Native trial 2026-11-07 — `applied` with UI Undo on Column, Wall 240, Beam and MultiSlab; Wall with door `unknown`**
([raw evidence](test-results/evidence/0.50.0-2026-11-07/evidence-20261107.jsonl),
[agent log](test-results/evidence/0.50.0-2026-11-07/agent-log.md), table in
the [API note](m4-editing-api.md#native-observations-0500-trial-2026-11-07)).
One UI Undo after each write; the owner confirmed every logged value in the UI.

- Column `1214d281…` (native 2→0, sent as `native_calculation_mode`):
  `applied` with AttributeContainer + root view `cc752bda…`→`5b2d4fb8…`
  accepted; attribute 120 followed (`m3`). One UI Undo restored 2/`m` and the
  original view.
- Wall 240 `e4de1f73…` (paired → `m`; plan native only, attribute already
  `m`): `applied` with 2 × AttributeContainer + WallAxis accepted. One UI Undo
  restored native 0; attribute stays `m` (it was not changed). The first
  plain Wall 240 request was sent as `native_calculation_mode` → `no_op`
  despite the diverging attribute (routing finding, fixed by the hint).
- **Wall 200 with door `bd30912a…` (paired → `m`): `stopped`, native
  `unknown` (`native_property_invariants_changed`, `partial_preservation` and
  `preservation_diagnostic` with Door/DoorSill/2 × AttributeContainer renamed),
  attribute `skipped`.** Reconciliation readback 2, attribute 120 `m3`. After
  one UI Undo the read-only recovery returned `reconciled`/`old_value_observed`
  with the preflight evidence hash restored (`d969033f…`); no acknowledgement
  was needed. Fixed in 0.50.1.
- Beam `d129c7c1…` (paired → `m`): `completed`; native `applied`
  (AttributeContainer + WallAxis accepted), attribute
  `paired_attribute_already_set_by_native_write`, no attribute setter. One UI
  Undo restored 0/`m3`; the Beam's direct view is now `6035d406…`
  (`362f80d3…` gives `probe_scope_unavailable` in `material_comparison`).
- MultiSlab `1dac121c…` (attribute 120 → `m`, sent as a plain attribute
  write; equal to the paired attribute-only plan): `completed`, identities
  unchanged; one UI Undo restored `m3`; tier `m2` unchanged.
- **UI Undo:** one step restored every write with a single setter, including
  the native write whose attribute followed (Column, Beam). The count for a
  native write plus an attribute setter is not established (item 1 above).

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
