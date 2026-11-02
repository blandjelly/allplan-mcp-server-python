# Current M4 handoff

## Next task — native trial of 0.44.0: Slab tier read, first Beam attribute write

Start condition: candidate **0.44.0** passed full CI and the owner installed its
`package` artifact. Launch with **Launch Allplan MCP.cmd** and keep
`logs/evidence/evidence-YYYYMMDD.jsonl` as the evidence
([plan items 2 and 6](development-plan.md#remaining-work-and-unresolved-errors)).

1. **Health and trace.** `allplan_health`, then `fix_model_issues`
   `inspect_journal`: `native_trace.auto_rotation` should report
   `available=true` and `archive_bytes` ≈ 43 MB (seven segments). Do not force
   a rotation; record one if it happens (`NativeProbeTrace.auto_rotate`).
2. **Slab (read-only, zero setters).** Re-run the `material_comparison` from
   the [tool reference](tool-reference.md#model_property_probe--isolated-read-phases)
   (child `8a693925…`/`a0fcd7b3…`, `parent_ref` MultiSlab, `include_parent`).
   Record `native_material.slab_tiers` on child and parent: the
   `SlabProperties` member names, `tier_api`, `tier_count` and tier
   `Material`. If a tier holds the visible material (or `C35/45` appears
   there), the changed flow is a tier-owner write; if no tier API exists, the
   member list decides the next candidate. No Slab Apply in this trial.
3. **Beam (one disposable attribute write).** Re-query `Beam_TypeUUID`
   (UUIDs may change). `model_edit` preview of one text attribute on the
   Beam root — attribute `Materiał` 508 (`""`) → `TEST-BEAM` — then highlight,
   Apply with a new `execution_id`, fresh readback, UI check and UI Undo with a
   restoration preview. Stop at any preview blocker and record it (expected
   risk: the target/parent-edge view discrepancy described below).

Completion: Slab tier observation and a decided changed flow in the plan;
Beam attribute cycle recorded (or its blocker). Next after a Beam PASS:
native Material on the Beam. Do not repeat the 0.40.0–0.43.1 probes.

## Latest version

**0.44.0** (candidate, branch `claude/m4-0440-trace-rotation`):

- **Automatic trace archival.** A full 8 MiB `m4-native-probe.jsonl` segment
  is moved verbatim to `m4-native-probe-archive/<sha256>.jsonl` before the
  next native call, under the trace lock; nothing is deleted. It stops (and
  the previous `probe_trace_unavailable` block + confirmed cleanup applies)
  once the archive would exceed 256 MiB, its listing is incomplete, or on
  collision/rename failure ([tool reference](tool-reference.md#confirmed-journal-maintenance--m4-0230)).
  Execution records keep confirmation-only archival.
- **Slab tier study.** `material_comparison` reports `slab_tiers` for each
  `SlabElement` owner (read-only, traced).

Focused checks PASS (274 + 63: trace cleanup, property probe, journal
cleanup/inspection and HTTP, material comparison and HTTP, component identity,
element attributes, exact material target and HTTP, Wall probe/filter/material,
Column layer, native model edit, package, MCP smoke, registration). Full CI,
ZIP verification and native trial are pending.

**0.43.1** (source `4a517bc`, PR #52) is the installed baseline; health:
Allplan 2026.1, `integrity=sha256-verified`. Owner-run read-only trial,
[raw evidence](test-results/evidence/0.43.1-2026-11-02/evidence-20261102.jsonl)
(owner: log agrees with the UI); zero setters:

- **Beam read PASS (read-only).** Beam "Podciąg" model
  `7cc9ac55-6111-4508-bae8-d33918dbe77e`, views `362f80d3-…`/`6035d406-…`:
  `element_attributes` returned 44 attributes from three adapters on both
  views, `consistent`; `Materiał` 508 = `""`, layer 3755, length 7.54,
  `IfcBeam`. `component_identity` (view `6035d406`) now observes
  `BeamElement` with children `WallAxis` and `AttributeContainer`, but their
  parent edges point to the other root view `362f80d3` and
  `other_view_uuids=[]` — the same target/parent-edge view pattern as
  SkeletonBeam 1. Both SkeletonBeams also read (ID 508 present).
- **Slab unchanged.** `material_comparison` child/parent: native Material
  `" "` on both, ID 508 `TEST1`; MultiSlab child container is `b4e594f7…`
  again (the Undo-restored inventory).
- **Trace full.** Three element-attribute pages and a filter read failed with
  `probe_trace_unavailable` (8 MiB, six archives ≈ 35 MB); the owner ran the
  confirmed cleanup (archive `b23a9a2e…`) and the reads succeeded. 0.44.0
  automates this rotation.

**0.43.0** (source `1be4072`, PR #51) trial
([raw evidence](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)):
Slab Apply `9c6a0d326b61440f8f11311c1ec569b9` (`C35/45`) ran the
`SlabProperties.Material` setter and `ModifyElements` without error, but every
readback stayed `" "`; the only inventory change was the MultiSlab
`AttributeContainer` regenerated (`b4e594f7…` → `60c64a1a…`), and UI Undo
restored it. Cause (wrong owner, tier storage or no-op setter) is open; do not
repeat that payload. **0.42.1** (`eecdfeb`, PR #49): owner-confirmed CI/ZIP;
[raw evidence](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
retained unchanged.

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
