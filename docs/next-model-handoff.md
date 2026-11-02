# Current M4 handoff

## Next task — native trial of 0.43.0: resolve the Slab lock, then one reviewed Slab write

Goal: close plan items 1–2 for the exact Slab child
([plan](development-plan.md#remaining-work-and-unresolved-errors)).
Start condition: candidate **0.43.0** passed full CI (six jobs: it changes
`windows/` and the package builder), and the owner installed its ZIP from the
GitHub Actions `package` artifact. Launch with **Launch Allplan MCP.cmd**: from
0.43.0 it captures raw bridge requests/responses in the package
`logs/evidence/evidence-YYYYMMDD.jsonl`; keep those files as the trial evidence.

1. `allplan_health`, `get_model_context` in `Kopia MCP_QA_DEMO`, drawing 101.
2. Read-only `model_edit` `action=recover` for execution
   `a8a31c72975541feb1c36a2e8cbb8f65` (no acknowledgement). Expected: the
   observation carries `representation_consensus.exact_inventory` (status
   `changed`, diff `expected_summary_unavailable` because the 0.42.1 plan has no
   stored summary, plus the current bounded inventory) and the observed native
   Material; the outcome becomes `reconciled` if the value is read. If a
   reconciliation proposal appears, show it to the owner before any
   acknowledgement. Never retry Apply.
3. Only after the lock is cleared: one new preview → highlight → Apply on the
   same child with an owner-chosen value different from the current one.
   Expected with the current diagnosis: outcome `unknown`,
   `exact_inventory_changed_after_setter`, readback with the new value and a
   **complete diff** (children/edges added/removed, scalar changes). Then
   read-only recovery (expected `reconciled`), UI check of the value, one UI
   Undo and a fresh read of the restored value.

Completion: lock `a8a31c…` resolved, the post-setter diff recorded, the
coverage-matrix cell for Slab native Material updated. Then decide (owner
review of the diff) whether the observed drift category may count as applied
in a later version. Do not change pre-setter guards. Do not repeat the 0.40.0,
0.41.0 or 0.42.0 probes.

Owner check in parallel (plan item 6): whether the installed Allplan offers an
architectural beam (`Beam_TypeUUID`). In the Polish UI it is usually the
**Podciąg / nadciąg** tool in the Architecture role (task area for walls,
openings and components); the Actionbar search for "Podciąg" finds it. The
SkeletonBeam found so far comes from the structural framing tools. If no
architectural beam exists, the Beam scope is SkeletonBeam only.

## Latest version

**0.43.0** (candidate, branch `claude/m4-claude-code-setup`,
[PR #51](https://github.com/blandjelly/allplan-mcp-server-python/pull/51), draft):

- **Slab diagnosis.** In 0.42.1 `fresh_resolve` runs after `SetMaterial` +
  `ModifyElements`; both pre-setter inventory checks had passed with the
  reviewed fingerprint, so the exact MultiSlab inventory changed across the
  native submission. Post-setter observation (fresh readback and recovery) now
  re-verifies the target view, child type and parent edge, and reports a
  changed fingerprint with a bounded diff instead of raising; Apply keeps the
  outcome unknown. New plans bind an `inventory_summary`; 0.42.x journal
  bindings stay valid. Pre-setter guards and the final mutation boundary are
  unchanged ([contract](m4-editing-api.md#exact-child-native-material-target-0420)).
- Opt-in raw evidence capture (`ALLPLAN_MCP_EVIDENCE_DIR`), client-neutral MCP
  server instructions, **Connect Claude Code.cmd** (uses the `claude` CLI,
  never overwrites another server), Setup.cmd without a stale version.
- Focused checks PASS (exact material, native material families/columns,
  model edit, material comparison, ownership, identity, recovery, wall
  material, delete, column layer, client, package, MCP smoke, CI policy).
  Full CI, ZIP verification and native trial are pending.

**0.42.1** (source `eecdfeb`, PR #49, merged `29c7f487`) is the installed
baseline: owner-confirmed CI and ZIP; health binds the bridge to that source,
integrity verified, Allplan 2026.1. CI run identity, ZIP hash and
upgrade/restore were not independently verified.
[Raw 0.42.1 evidence](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
(steps 0–14) is retained unchanged.

## Key errors and necessary earlier context

- **Slab `a8a31c72975541feb1c36a2e8cbb8f65` — unknown, write lock.** Preview
  (drawing 101, child model `8a693925-ae20-4dda-91d1-3951af3c0a52`, view
  `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, parent MultiSlab
  `bf097d95-8275-4229-ac74-27bbea26c211` / `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`)
  observed Material `" "` against requested `C35/45` with
  `native_material_ownership` (`SlabElement`, `slab_properties`). Apply stopped
  `unknown`, `repair_conflict` at `fresh_resolve`; recovery repeated it at
  `recovery_resolve`. The write-ahead marker was saved before the setter, so
  **the setter may have run**; the current value is unknown. Do not infer
  setter success or absence; recover read-only with this ID.
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
