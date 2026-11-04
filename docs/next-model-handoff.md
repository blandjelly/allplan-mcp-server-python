# Current M4 handoff

## Next task — answer the owner questions, then design the `CalculationMode` write (plan item 5, step 2)

Step 1 of item 5 (read-only precheck) is done; results and their meaning are
below and in the [API note](m4-editing-api.md#native-observations-0480-read-only-precheck-2026-11-04).
Before code, settle the open owner questions recorded in
[plan item 5](development-plan.md#remaining-work-and-unresolved-errors): where
the UI shows the Slab child values (`TEST2`, `m2`), whether the tier 508 change
`TEST1` → `TEST2` after the 0.47.0 trial was the owner's own edit, and which of
the two Wall materials the owner means by "material".

**Then (0.49.0, code + focused tests, no native trial yet):** a native
`CalculationMode` write for **Column, single-tier Wall and Beam** following
the API note's step 2 route. Preview: exact owner binding, old code 0–4,
different new code. Readback: native `CalculationMode` = new code **and**
attribute 120 must read the matching label; report the attribute separately so
a diverging 120 is visible (it decides the mirror), never auto-accepted.
Preservation excludes only the target field and attribute 120. **Slab:** no
native `SlabProperties.CalculationMode` write — on the MultiSlab it reads `m2`
while the UI and its attribute 120 show `m3`; the UI "Rodzaj rozliczenia" of a
slab goes through the existing attribute route on the MultiSlab (attribute
120), as for material 508. Native trial afterwards: first the Column (its
non-default `m` makes the strongest check), one write + UI + UI Undo.

Do not repeat: the 0.48.0 precheck reads, the MultiSlab attribute 508 write
(PASS 0.46.0 and 0.47.0), the exact parent-edge tier write (0.47.0), the Beam
native Material write (PASS 0.46.0), the native Slab Material Apply (0.43.0)
or the 0.40.0–0.45.0 probes. For the Beam, `material_comparison` needs direct
view `6035d406…`; `362f80d3…` fails `probe_scope_unavailable` (again in 0.48.0).

## Latest version

**0.48.0** (source `5faa86d`, merged as PR #61 / `aec0e24`) is installed;
the evidence's version response reports bridge 0.48.0, source
`5faa86d2b027deea546f14860edcf5d03c464e43`, integrity `sha256-verified`,
Allplan 2026.1. Behaviour: getter-only `native_properties`
(`CalculationMode` with SDK label, `Priority`, `Trade`, tier `Thickness`) in
`material_comparison`, also for single-tier Wall and Column
([tool reference](tool-reference.md)). No setter or write path changed.
Full CI before the merge was the owner's gate.

**Native read-only trial 2026-11-04 — PASS for plan item 5 step 1**
([raw evidence](test-results/evidence/0.48.0-2026-11-04/evidence-20261104.jsonl),
drawing 101, `setter_calls_started=0`, `model_data_changed=false` everywhere,
all attribute values equal in `ReadAll` and `ReadAllAndComputable`). UI values
are owner-reported with screenshots in this chat (not stored as files).

| Element (model / view) | Native `CalculationMode` | Attr 120 | UI "Obmiar"/"Rodzaj rozliczenia" | Native `Priority` / UI | Native `Trade` / attr 209 / UI "Typ robót" | Material: native / attr 508 / UI | Thickness native / UI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wall `06d71e4d…`/`2d33e5a6…` (tier 1) | 0 `m3` | `m3` | `m3` | 300 / 300 | −1 / not returned / empty | `TEST` / `Silikat` / dialog `TEST`, attributes `Silikat` | 240.0 / 0.2400 |
| Column `eb88c850…`/`cc752bda…` | 2 `m` | `m` | `m` | 100 / 100 | −1 / `<niezdefiniowany>` / empty | `TEST1` / `TEST1` / `TEST1` | — |
| Beam `7cc9ac55…`/`6035d406…` | 0 `m3` | `m3` | `m3` | 100 / 100 | −1 / `<niezdefiniowany>` / empty | `""` / `""` / empty | — |
| MultiSlab `bf097d95…`/`b4a59b5b…` | 1 `m2` (tier 0 also `m2`) | `m3` | `m3` | 200 / 200 | 0 / not returned / empty | `" "` / `TEST1` / palette `TEST1` | tier 0: 200.0 / 0.2000 |
| Slab child `8a693925…`/`a0fcd7b3…` (with `parent_ref`) | 1 `m2` (tier 0 also `m2`) | `m2` | `m2` (owner, location to confirm) | 200 | 0 / `""` / empty | `" "` / `TEST2` / `TEST2` (owner) | tier 0: 200.0 |

What this means:

- **Mirror hypothesis per family.** Wall, Column, Beam: *consistent* — native
  code, attribute 120 and UI agree (the Column's non-default `m` is the
  strongest case). Shared storage is still unproven; the write in step 2
  decides it. MultiSlab: *refuted for the native route* — the
  `SlabProperties` read on the MultiSlab wrapper matches the tier values
  (`m2`, Material `" "`, Trade 0), while the UI shows attribute 120 `m3`;
  this matches the 0.43.0/0.46.0 material finding. Slab child: consistent
  (`m2` everywhere), but the child is not the UI owner of the slab.
- **Priority** agrees with the UI on all four families; a later Priority
  write has a direct UI check. **Thickness** is native millimetres, the UI
  shows metres.
- **Trade is not determinable:** every element is unset (UI empty). −1 and 0
  both appear as "unset"; attribute 209 returns nothing, `<niezdefiniowany>`
  or `""`. The owner did not find "−1" in the UI because it is the internal
  "no trade" index. Mapping codes to labels needs an element with a chosen
  "Typ robót" value.
- **Wall has two UI materials:** native tier Material `TEST` in the element
  dialog ("Materiał/Ilości") and attribute 508 `Silikat` in the attributes
  palette. A plain-language "material" request on a Wall is ambiguous.
- `evidence_complete=false` for Wall, MultiSlab and Slab child (Column and
  Beam `true`); per the tool reference it does not depend on the native
  property values.

Current stored state: MultiSlab 508 `TEST1`, tier 508 `TEST2` (was `TEST1`
after the 0.47.0 trial; cause to be confirmed by the owner), native Material
`" "` on both.

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
  undone in that trial; 0.48.0 reads the tier as `TEST2` again (owner to
  confirm the cause). Neither needs recovery; do not replay.
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
