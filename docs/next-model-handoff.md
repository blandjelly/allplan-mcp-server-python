# Current M4 handoff

## Next task — native trial of candidate 0.51.0 (plan items 2a, 5 and 8)

Start after the owner has merged the 0.51.0 PR with green full CI and
installed it (health: bridge 0.51.0, the merged source commit,
`sha256-verified`). Drawing 101, plain-language requests, one Apply per step,
UI check of both places ("Obmiar"/material in the element dialog and "Rodzaj
rozliczenia"/"Materiał" in the attributes palette), then UI Undo **counting
the steps until every changed place shows the old value**, then a fresh
`material_comparison` with `attribute_ids` [120] or [508]. Do not retry an
`unknown` outcome; recover read-only with the original execution ID and
record `preservation.identity_diff`.

Current state (fresh reads at the end of the 0.50.1 trial, 2026-11-07):
Column `eb88c850…` native 2 / attr 120 `m` (view `cc752bda…`); Wall 240
`06d71e4d…` Material `TEST`, 508 `Silikat`, native 0 / attr 120 `m`; Wall 200
with door `545bb0a2…` Material `TEST1`, 508 not stored, native 0 / attr 120
`m3`; Wall 300 with window `f4da72fe…` new (values not read); Beam 0/`m3`,
MultiSlab attr 120 `m3` (unchanged since 0.50.0).

1. **One UI Undo for two setters — Wall 200 with door → `m`** ("zmień
   calculation mode dla ściany 200 mm na m"). Plan `paired_property` with
   native 0→2 and attribute 120 `m3`→`m`. Expect native `applied` (door
   renaming), attribute 120 `applied`/`readback_matches`, and
   `undo_group.status="created"`, `setters_in_step=2`. Key result: **one** UI
   Undo restores 0/`m3`. If two steps are still needed, keep the result's
   `undo_group` (incl. `in_undo_service_*`) for the next API route.
2. **Paired material, Wall 240 → `Cegła`** ("zmień materiał ściany 240 mm na
   Cegła"). Plan native `TEST`→`Cegła` + 508 `Silikat`→`Cegła` (not
   `native_material`). Expect native `applied` with
   `identities_regenerated_evidence_otherwise_equal` (2 × AttributeContainer
   + WallAxis expected), attribute 508 `applied`, both places in the UI, one
   UI Undo.
3. **Paired material, Wall 200 with door → `Cegła`**. Plan native only, with
   the Wall in `paired_property.attribute_follows_native` (508 not stored).
   Expect native `applied` with Door/DoorSill/2 × AttributeContainer renamed;
   both UI places show `Cegła`; one UI Undo.
4. **Wall 300 with window.** Read-only first: `model_query` lists the Window
   with `family=opening`, `opening_kind=window`. Then a paired calculation
   mode (or material) request on the window Wall. Expected (hypothesis):
   `applied` with Window, Sill, WindowOpeningSmartPart and AttributeContainers
   renamed; WindowTier/WindowReveal unchanged. Any other drift stays
   `unknown` with `identity_diff`: record it, recover read-only, do not retry.
5. Optional: `component_identity` on the window Wall's WallTier names
   `component_child_owner_mismatch`; deleting the window (disposable) with UI
   Undo only if the owner wants that destructive check (plan item 8).

Closure: one UI Undo for a paired write with two setters; Wall Material
`applied` on both Walls with UI check; the window Wall `applied`. Then plan
item 3's explicit layer write or item 4. Do not repeat: the 0.50.1 Column
routing check and its writes, the 0.50.0/0.49.0 writes, the 0.48.0 reads, the
MultiSlab attribute 508/120 writes, the exact parent-edge tier 508 write
(0.47.0), the Beam native Material write (PASS 0.46.0), the native Slab
Material Apply (0.43.0) or the 0.40.0–0.45.0 probes.

## Candidate 0.51.0

Branch `claude/m4-0510-undo-group-wall-window` (PR to `develop/m4`, link in
the PR list; the owner checks the tested commit). Fixes the 0.50.1 trial
findings ([contract](m4-editing-api.md#one-ui-undo-step-wall-material-and-openings-0510-contract)):

- **One UI Undo per Apply:** every setter of a typed plan with two or more
  changes runs inside one `NemAll_Python_IFW_Input.UndoRedoService(doc,
  True, True, True)` (official-example pattern), closed by one
  `CreateUndoStep()` after the last setter, also after a stop. The result and
  journal report `undo_group`; a failure there never changes an outcome.
- **Wall Material:** the identity-renaming rule is per family and applies to
  `Material` as well (the 0.50.1 Material writes changed exactly the sections
  of the accepted CalculationMode renamings); Material drift now reports
  `identity_diff`.
- **Paired material without stored 508:** paired requests read the attribute
  with presence proof; on a Wall a not-stored 508 follows the native material
  (owner observation), so only the native change is planned
  (`attribute_follows_native`). Other families stay blocked.
- **Routing:** `native_material` previews report `paired_property_hint` when
  508 differs; the description says a single-place choice does not carry over.
- **Wall with window / openings:** Window, Sill and WindowOpeningSmartPart may
  be renamed on a Wall (not observed natively); `Door_TypeUUID` and
  `Window_TypeUUID` are openings (`opening_kind`, `native_types`, delete of a
  Wall-owned door/window with its subtree); `component_identity` names the
  bounded cause of a failure.
- Local checks (Linux): all 876 tests in 68 modules PASS with the CI runner
  (`utils/run_tests_parallel.py`), including 8 undo-group, 9 wall/window and
  new query/delete/identity tests. Full CI and native acceptance are not run.

## Installed version and last native evidence

**0.50.1** (source `6b04d97`, merged as PR #65 / `a1b2e04`) is installed;
health reports bridge 0.50.1, source
`6b04d975e05212fefeff35de69f86db81dc51262`, `sha256-verified`, Allplan 2026.1
(executable 16.1617.8659.814). Full CI before the merge was the owner's gate.

**Native trial 2026-11-07 — door renaming and Column routing PASS; two UI Undo steps; Wall Material `unknown`**
([raw evidence](test-results/evidence/0.50.1-2026-11-07/evidence-20261107.jsonl),
[agent log](test-results/evidence/0.50.1-2026-11-07/agent-log.md), table in
the [API note](m4-editing-api.md#native-observations-0501-trial-2026-11-07)).
The owner confirmed every logged value in the UI.

- **Wall 200 with door `4043e559…` (paired → `m`): `completed`**; native
  `applied` with 2 × AttributeContainer, Door, DoorSill renamed; attribute 120
  setter `applied`. **Two UI Undo steps** (first the attribute: read 2/`m3`;
  then the native value: 0/`m3`). Fixed in 0.51.0 (one undo step).
- Column `341415e4…` (plain request routed as `paired_property` → `m3`):
  `completed`; native `applied` (AttributeContainer + root view
  `cc752bda…`→`86a9536a…`), attribute already set by the native write. One UI
  Undo (the UI offered no second) restored 2/`m` and view `cc752bda…`.
- Wall 200 paired material `Cegła`: preview blocked (`attribute:508`
  `old_value_unknown`: 508 not stored). Native only `37196703…`: `unknown`
  (`partial_preservation`, `preservation_diagnostic`), readback `Cegła`;
  the owner saw both UI places change. One UI Undo; recovery
  `reconciled`/`old_value_observed`.
- Wall 240 plain material sent as `native_material` (routing error)
  `9ed2e229…`: `unknown` (the sections of the accepted CalculationMode
  renaming), readback `Cegła`, 508 stayed `Silikat`. One UI Undo; recovery
  `reconciled`/`old_value_observed`.
- Wall 300 with window `f4da72fe…` inserted; read-only tree: Window →
  WindowTier → Sill, WindowReveal → WindowOpeningSmartPart → AttributeContainer,
  AttributeContainer; the WallTier also lists the WindowTier.
  `component_identity` failed on the WallTier, Sill and WindowReveal.

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
