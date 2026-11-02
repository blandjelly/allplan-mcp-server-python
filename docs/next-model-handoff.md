# Current M4 handoff

## Next task — native trial of 0.43.1: read Beam (Podciąg) attributes; study why Slab Material stays blank

Start condition: candidate **0.43.1** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2 and 6](development-plan.md#remaining-work-and-unresolved-errors)).

1. **Beam (read-only).** `allplan_health`, then re-query `Beam_TypeUUID` in
   drawing 101 (refs observed 2026-11-02: model
   `7cc9ac55-6111-4508-bae8-d33918dbe77e`, views `362f80d3-…` and `6035d406-…`;
   re-read them, UUIDs may change). Run `model_property_probe`
   `element_attributes` (no filter, then `name_contains="material"`) with
   either view. Expected: all root views are read and, if they agree, the
   listing carries `view_uuids` (2) and `adapter_attribute_consistency=
   "consistent"`; otherwise `conflicting_view_attributes` with per-view
   fingerprints. Optionally run `component_identity` on the same refs: it may
   still fail, but the message now names the cause (no direct adapter / view
   not among direct views / representations disagree). Zero setters.
2. **Slab (no new Apply).** The same `C35/45` payload must not be repeated.
   Next agent step is read-only API study: compare `SlabProperties.Material`
   on the child, the MultiSlab parent and tier properties
   (`GetSlabTierProperties`) and decide on a changed flow before any trial.
   Closure of plan item 2 needs a flow whose readback shows the new value.

Completion: Beam attribute listing recorded (or its remaining blocker), Slab
hypothesis and changed flow written in the plan. Do not repeat the 0.40.0,
0.41.0, 0.42.0 or 0.43.0 probes. If the Beam listing works, the next task is one
disposable Beam attribute write and then native Material on the Beam.

## Latest version

**0.43.1** (candidate, branch `claude/m4-0431-multiview-beam-probe`):
the `element_attributes` probe now accepts a root with several views
(Beam Podciąg has two): it requires every view to have live adapters, reads all
of them and reports values only if they agree (otherwise
`conflicting_view_attributes` with per-view fingerprints; a requested view
outside the root's views still blocks). Unresolved identity errors name their
cause. The exact-inventory diff gains descriptive `child_type_changes`.
Pre-setter guards, journals and write paths are untouched. Focused checks PASS
(attribute probe, component identity, property probe, exact material target and
HTTP, recovery HTTP, native model edit, material comparison, model properties);
full CI, ZIP verification and native trial are pending.

**0.43.0** (source `1be4072`, PR #51) is the installed baseline; health:
Allplan 2026.1, `integrity=sha256-verified`. Owner-run native trial,
[raw evidence](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)
(the owner reports the log agrees with the UI and that UI Undo worked):

- **Lock cleared.** Read-only recovery of `a8a31c…` is `reconciled`
  (`old_value_observed`, Material `" "`), `write_blocked=false`; this is not an
  applied result. `exact_inventory` was `changed`
  (`expected_summary_unavailable`: the 0.42.1 plan had no summary).
- **Diagnosis confirmed.** New Apply `9c6a0d326b61440f8f11311c1ec569b9` (plan
  `210a1b…`, requested `C35/45`) ends `unknown`,
  `exact_inventory_changed_after_setter`. The only difference is one
  `AttributeContainer_TypeUUID` child of the MultiSlab replaced by a new UUID
  (`b4e594f7…` → `60c64a1a…`); edges, parent and scalars are unchanged.
  Read-only recovery: `reconciled`, `old_value_observed`.
- **No effect on the observed Material.** Readback after the setter, recovery
  and the later previews all show `" "`, not `C35/45`; the setter and
  `ModifyElements` ran without error and regenerated the container, but the
  value did not change. After UI Undo the preview fingerprint equals the
  pre-Apply one (`796cd7…`, container `b4e594f7…` again), so Undo restored the
  inventory. Cause (wrong owner, tier-level storage or a no-op setter) is not
  established. The drift category cannot count as applied while the value is
  unchanged.
- **Beam fixture found.** The owner added an architectural beam
  "Podciąg, wieniec" (`Beam_TypeUUID`, layer 3755, 7540×240×400 mm, two root
  views). `model_query` finds it; `element_attributes` was refused with
  "ambiguous root adapter representations" because the probe required one
  view (fixed in 0.43.1); `component_identity` failed with "missing or
  conflicting" (cause unreported before 0.43.1; the direct scan may not list
  this root).

**0.42.1** (source `eecdfeb`, PR #49) was the earlier baseline: owner-confirmed
CI and ZIP, CI run identity, ZIP hash and upgrade/restore not independently
verified. [Raw 0.42.1 evidence](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
is retained unchanged.

## Key errors and necessary earlier context

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
