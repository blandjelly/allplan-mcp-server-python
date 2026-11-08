# Current M4 handoff

## Next task — native trial of candidate 0.51.2 (plan items 2a, 4 and 7)

Start after the owner has merged the 0.51.2 PR with green full CI and
installed it (health: bridge 0.51.2, the merged source commit,
`sha256-verified`). Drawing 101, one Apply per step, plain-language
requests, UI check of both places and one UI Undo per Apply, then a fresh
read. Do not retry an `unknown` outcome; recover read-only with the original
execution ID and record `preservation.identity_diff`,
`preservation.regeneration_residual` and, when accepted,
`accepted_preservation_drift.reserialized_geometry`.

Current state (fresh reads at the end of the 0.51.1 trial, 2026-11-08, all
writes UI-undone): Wall 300 with window `f4da72fe…` Material `TEST1`, native
CalculationMode 0, attribute 120 `m3`, 508 not stored, window `268dec66…`
restored with its original identities; Wall 240 `06d71e4d…` 1371 = 0,
1442 = 1, 230 = 1; Wall 200 with door `545bb0a2…` layer 65535; Column
`eb88c850…` `TEST1`/508 `TEST1`, view `cc752bda…`; Beam `7cc9ac55…` 0/`m3`;
MultiSlab `bf097d95…` 110 = 200, 981 `<niezdefiniowany>`, 508 `TEST1`;
slab tier `8a693925…` 508 `TEST2`.

1. **Window Wall, paired calculation mode → `m`** ("zmień calculation mode
   dla ściany 300 mm na m", exclude the Walls 240 and 200): expect native
   0→2 `applied` with `identities_regenerated_evidence_otherwise_equal`
   (Window, Sill, WallAxis, 3 × AttributeContainer renamed) and
   `reserialized_geometry` naming WindowTier and WindowReveal, attribute 120
   `m3`→`m` `applied`, `undo_group` `created`, `setters_in_step=2`; highlight
   `counts.matched=1`. UI: "Obmiar" and "Rodzaj rozliczenia" = `m`; one UI
   Undo restores 0/`m3`.
2. **Window Wall, paired material → `Cegła`**: native only
   (`attribute_follows_native`), expect `applied` with the same renaming and
   `reserialized_geometry`; both UI places `Cegła`; one UI Undo; read `TEST1`.
3. If 1 or 2 stays `unknown`: the residual now lists `stream_sha256`,
   `shape_sha256`, `structure_sha256` and `numbers` separately. Record which
   differ (equal structure + different shape = numbers changed beyond 1e-4;
   different structure = a different serialization) and recover read-only.
4. **Read-only checks of the 0.51.2 fixes:** a preview of "zmień TYLKO
   atrybut Rodzaj rozliczenia podciągu na m" must be blocked
   (`attribute_write_also_changes_native_property`, `paired_route`); a
   preview of attribute 1442 = 2 on the Wall 240 must fail with
   `attribute_value_out_of_range`; `model_property_probe` `layer_name` with
   `layer_id` 3700 must return `SZ_OGÓ01` and a `confirmed_target`.
5. Optional (plan item 4, owner labels from 2026-11-08): Column attribute 49
   `Status` to a confirmed label (for example `Nowo projektowane`) with the
   enum round trip, UI and one UI Undo; Beam Integer/Real from the B2
   discovery list.

Closure: the window Wall `applied` for both paired properties with UI check
and one UI Undo (plan item 2a). Do not repeat: the 0.51.1 PASS writes (slab
tier `1a019448…`, Wall 1442/230/1371, MultiSlab 110/981, Column paired
material `7c1e4a92…`, Wall 200 layer `b3e8d1f4…`, window delete
`d5a79c20…`, Beam 120 `8cc1e687…`), the 0.51.0 writes on the Wall 240 and
the Wall with door, the 0.50.1/0.50.0/0.49.0 writes, the 0.48.0 reads, the
MultiSlab attribute 508/120 writes, the Beam native Material write (PASS
0.46.0), the native Slab Material Apply (0.43.0) or the 0.40.0–0.45.0 probes.

## Candidate 0.51.2

Branch `claude/m4-0512-window-geometry-trial-fixes` (PR to `develop/m4`,
link in the PR list; the owner checks the tested commit). Fixes the 0.51.1
trial findings ([contract](m4-editing-api.md#opening-geometry-tolerance-and-trial-fixes-0512-contract)):

- **Window geometry re-serialization:** geometry evidence adds
  `shape_sha256` (numbers rounded to 4 decimals), `structure_sha256`
  (numbers replaced) and `numbers`. On a Wall, the WindowTier and
  WindowReveal below a renamed Window may differ in the exact stream hash
  when shape, structure and count are equal; every other byte must still be
  equal after renaming. The residual picks the pairing with the fewest
  differing paths.
- **Beam attribute 120 alone** is blocked
  (`attribute_write_also_changes_native_property`) with a `paired_route`.
- **CheckBox Integer** attributes accept only 0/1 (`attribute_value_out_of_range`).
- **Plan highlight counts** report the reviewed targets as `matched`
  (`scope_elements` = scanned peers, `count_kind=reviewed_plan_targets`).
- **Layer probe:** `layer_name` accepts `layer_id`; `layer_catalog`
  `candidate_ids` of another name fail with `layer_candidate_mismatch`
  instead of `host_error`.
- **`undo_group`** is reported on every typed Apply (`not_requested` with
  `single_change_plan` or `single_native_delete_call`).
- Unchanged: renaming types, journals, recovery, unknown outcomes, write
  guards and the plan TTL.
- Focused local checks (Linux): 517 tests in 30 affected/dependent modules
  PASS, plus `test_package`/`test_ci_policy` (32) and the version check
  (`pyproject`, `uv.lock`, `__version__` = 0.51.2). Full CI and native
  acceptance are not run.

## Installed version and last native evidence

**0.51.1** (source `0fdc2a8`, merged as PR #67 / `c3fc7b9`) is installed;
health reports bridge 0.51.1, source
`0fdc2a8e9c4294c6efb867add3f8f07e8493913c`, `sha256-verified`, Allplan
2026.1.

**Native trial 2026-11-08 — window Wall `unknown`; attribute types, slab
tier, Column Material, Wall layer and window delete PASS**
([raw evidence](test-results/evidence/0.51.1-2026-11-08/evidence-20261108.jsonl),
[test card with the owner's results](test-results/evidence/0.51.1-2026-11-08/test-card.md),
table in the [API note](m4-editing-api.md#native-observations-0511-trial-2026-11-08),
per-pair status in the [coverage matrix](m4-coverage-matrix.md)).

- **Window Wall (blocking, item 2a):** A1 preview had complete evidence
  (`shared_children` WindowTier, no `partial_preservation`). Three Applies
  reached the native value and stayed `unknown`: paired calculation mode
  `5008fcbe…` (plan `7a76ed98…`, the A1 plan; not in the card table) and
  `c1395fe6…`, paired material `3c5df3d9…`. Renamed: Window, Sill,
  WallAxis, 3 × AttributeContainer. The only residual besides pairing noise:
  the exact geometry stream hashes of WindowTier `360e85e2…` and
  WindowReveal `8ad3fe60…` (identities kept), identical before/after hashes
  in all three writes; UI Undo restored them. Attribute 120 was skipped; in
  A3 the owner saw `Cegła` in both places. All three reconciled. Fixed in
  0.51.2 (tolerance evidence, not yet observed).
- **PASS (one Apply, UI, one UI Undo, read after Undo):** slab tier 508
  `TEST2`→`TEST4` (exact route, `1a019448…`, all wrappers agree, inventory
  unchanged; the owner's UI check did not separate the two palette modes);
  Wall 240 Integer 1442 (CheckBox control) 1→0 (`9bf9d05d…`) and 1→2
  (`360930f8…`); Wall 240 Real 230 1→2 (`3be71e58…`); Wall 240 CheckBox 1371
  0→1 (`56739a30…`); MultiSlab Integer 110 200→201 (`1ca552c6…`, tier and
  native Priority unchanged) and Real 981 `<niezdefiniowany>`→0.25
  (`0a7fc6d5…`); Column paired material `TEST1`→`C35/45` (`7c1e4a92…`,
  native `applied` with AttributeContainer + root view renamed, 508 followed
  without a setter); Wall 200 layer 65535→3701 `SZ_OGÓ02` (`b3e8d1f4…`,
  root + tier); window delete with its 7-adapter subtree (`d5a79c20…`, Wall
  and neighbours kept, one UI Undo restored the window with its original
  identities).
- **Findings fixed in 0.51.2:** Beam attribute 120 alone (`8cc1e687…`)
  also changed native CalculationMode 0→2 (one UI Undo restored both); a
  CheckBox Integer took 2; highlight `counts.matched` counted all peers of
  the type; `layer_catalog` with `candidate_ids` gave `host_error`
  (`110b1ced-501d-49cb-9b53-a52843a4a301`); no read of a layer's name by ID;
  `undo_group` missing on single-setter Applies.
- **Not a product fault:** Wall Real 220 "Długość" did not change
  (`052283c9…`, `failed`/`readback_unchanged`, nothing written; likely
  geometry-derived). The agent's note that the plan TTL expired before the
  B3 Apply is not supported: preview 13:11:11, Apply 13:11:37 UTC.
- **Owner answers (card section C):** Trade list: 78 labels in alphabetical
  order without codes (screenshots `C1-*.png`; "Roboty murarskie" = 12 is
  not its list position), so codes need per-label readback. Column `Status`
  (ID 49) labels: Inny, Nieokreślony, Nieznany, Nowo projektowane,
  Rozbiórka, Tymczasowy, Wybudowane (`C2.png`). No Date attribute in the
  project. Selection experiment and the upgrade/restore check after the
  earlier stages. Destructive tests (and disposable elements) allowed. The
  tier `TEST1`→`TEST2` change after 0.47.0: unknown. Geometric native
  properties (thickness, length, height) are not pursued; the owner names
  Priority (the trial wrote attribute 110, which is not coupled to native
  Priority).
- Open observations: `host_session_id` changed between steps (the host
  restarted; no host log); `size_x_mm`/`size_y_mm` of the Wall 240 read
  `not_checked` (`ValueError`) once; the owner saw the deleted window vanish
  from the UI when stopping the host, although the Apply had already
  reported an empty subtree.

**0.51.0 trial (2026-11-07)** ([raw evidence](test-results/evidence/0.51.0-2026-11-07/evidence-20261107.jsonl),
[observations](m4-editing-api.md#native-observations-0510-trial-2026-11-07)):
one UI Undo per Apply (Wall with door paired calculation mode, Wall 240 and
Wall with door paired material) PASS; the window Wall stayed `unknown` on
partial evidence (fixed in 0.51.1).

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

- **0.51.1 executions (2026-11-08):** window Wall
  `5008fcbefbde45cfaf0d258e9ea87db9` and `c1395fe64f0743fab54e8bbd6d9da3cc`
  (calculation mode) and `3c5df3d971a6427da2748854e2b75114` (material) are
  `stopped`, read-only recovery after one UI Undo each:
  `reconciled`/`old_value_observed`, `write_blocked=false`; not applied PASS
  results, nothing to replay. `052283c9fbb047e8ac50c697c3eb3a5d` (Wall 240
  attribute 220) is `stopped`/`failed` (`readback_unchanged`, nothing
  written). `1a0194481b164593a6ed23231cbbb416`,
  `9bf9d05d03a643699d6c0dcc6e75aa3a`, `360930f8b4ff44098791e287d892060c`,
  `3be71e58cb87469c80d60f706fafdc45`, `8cc1e6871aae449dae601a27abab5c2b`,
  `1ca552c6efa8482a8d316217ca561e1a`, `0a7fc6d5fbdd4c54a2639cf93f0b416f`,
  `56739a3058334c6182269a2fafa95aef`, `7c1e4a92b5d84f60a3e91d2c8b0f5a47`,
  `b3e8d1f46a2c4975918c0d7e5f2a6b13` and `d5a79c20e1b64f38a7c4829b0e6f1d35`
  are `completed` and UI-undone (the journal does not know the Undo; do not
  replay or recover them).
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
