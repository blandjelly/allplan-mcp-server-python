# Allplan MCP — M4 development plan

## Current state and next task

M4 is partially accepted. The current version, delivery and the concrete next
task are in the [handoff](next-model-handoff.md). This plan keeps the
remaining work and its closure conditions, following the
[documentation policy](documentation-policy.md). Per-pair status is in the
[coverage matrix](m4-coverage-matrix.md); evidence of earlier trials is in
[validation status](validation-status.md). Do not repeat accepted scopes or
extend them to other families, types or versions without evidence.

## Product goal and boundaries

Owner decision (2026-11-02): the tool must edit **every attribute that the
Allplan 2026 API exposes** for Columns, Beams, Walls and Slabs. Editing their
**native properties** (beyond native Material) is the preferred extension
wherever the API allows a safe, verifiable write. The owner gives
instructions in Polish; the agent resolves exact fields, owners and value
types, shows the plan, revalidates it, performs a supported write and a fresh
readback. The material attribute and native Material have separate API
bindings; any coupling must be read in the actual project. The organizational
layer and surface have separate write targets.

Reads may cover explicitly named open drawings; Apply is limited to one
active drawing and 1–32 real changes. Multi-file and whole-project writes need
a separate design and acceptance.

Other owner decisions (2026-11-02):

- Priority: resolve the Slab native Material problem first (items 1–2).
- Delivery: the ZIP is the GitHub Actions `package` artifact;
  `evaluation-packages/` is a historical archive (up to 0.33.0).
- Beam: in the owner's Allplan 2026 only SkeletonBeam (structural framing
  beam) has been found; an ordinary `Beam_TypeUUID` fixture is not
  established (see item 6).
- Documentation is English only; CI runs product jobs only for code changes.

## Remaining work and unresolved errors

| Priority | What remains / condition for further work |
| --- | --- |
| 1 — recovery lock and delivery | 0.42.1 CI/ZIP confirmed by the owner; health binds the install to `eecdfeb`, integrity verified. CI run identity, ZIP hash and upgrade/restore are not independently verified. Slab execution `a8a31c72975541feb1c36a2e8cbb8f65` is unknown/recovery_required (the setter may have run). Wall `3f2a8c9d7b5e4a1c9f8e6d3c2b1a0e9f` was reconciled by reviewed reconciliation, preservation=false. Keep the older histories `87a…` and `4388…` described in the handoff. Never retry Apply or delete the journal. |
| 2 — native Material Slab/MultiSlab: post-setter inventory drift | Diagnosed in 0.43.0: the 0.42.1 conflict was raised at `fresh_resolve` **after** the setter; both pre-setter inventory checks passed. Post-setter observation now reports the inventory diff and keeps the outcome unknown; pre-setter guards are unchanged. Next: native trial of 0.43.0 (read-only recovery of `a8a31c…`, then one new Slab Apply). See the handoff. |
| 3 — Slab/MultiSlab attributes: reported value PASS, owner incomplete | The reported 0.39.0 Apply/readback PASS stands, but historic payloads and exact owner binding are missing. The 0.41.0 getter (ID 508 `TEST1` on child and parent) does not assign the historic write owner or prove coupling with native Material. Keep `target.property_owner="selected_element"`, lineage/children and the overlap guard. Do not repeat accepted writes to recreate evidence. |
| 4 — attribute types × families | Close owner-specific roundtrips for every family/type pair in the [matrix](m4-coverage-matrix.md). Column Enum `Status` ID 49 is BLOCKED (`<niezdefiniowany>`, no confirmed label). Wall CheckBox ID 1371 has no raw Apply; no SDK Boolean fixture. Date/vector/object values need exact setter payload and typed readback contracts; an SDK symbol or constructor is not enough ([type coverage](m4-attribute-type-coverage.md)). |
| 5 — native properties beyond Material (new) | Not started. First write an API note: which `WallTierProperties`, `ColumnProperties`, `BeamProperties`, `StructuralBeamProperties` and `SlabProperties` members (thickness, height/plane references, surface, priority, calculation mode, trade, hatch/filling) have documented setters, their owners and readback; then one property per family with preview, preservation and Undo evidence. The current preservation snapshot already reads many of these values. |
| 6 — Beam fixture | Ordinary `Beam_TypeUUID` stays `fixture_missing`. The owner must check whether the installed Allplan offers an architectural beam tool (see handoff); otherwise record the scope as SkeletonBeam only. The SkeletonBeam 1 target/parent-edge view discrepancy remains open. |
| 7 — layer and no-op: partially accepted | Keep W1 read/write, single Undo and the reported no-op in their scope. Remaining family/owner pairs and grouped Undo need evidence. No-op has no Apply path. |
| 8 — delete and selection: partially accepted / missing | Keep grouped Column delete/Undo and the Wall subtree observation. Other declared families/subtrees need evidence. Native selection remains unsupported pending an installed-SDK set/clear/readback contract ([selection API](m4-native-selection-api.md)); highlight does not close selection. |

### Evidence needed to close items 1–8

Items refer to one active drawing and the existing 1–32 change limit. Keep
reported PASS results; add only missing evidence or a changed flow; do not
repeat completed Apply calls just to recreate a log. From 0.43.0 the launcher
captures raw bridge requests/responses in the package `logs/evidence/`; attach
those files instead of chat summaries.

1. **Delivery and recovery:** for 0.42.1 (`eecdfeb`) the owner confirmed CI
   and ZIP; health binds the installed bridge to that source, integrity
   verified. The CI run ID, ZIP hash and upgrade/restore are not independently
   verified. The 31-record inspection is done: `87a…` stays stopped/reconciled
   without applied/preservation evidence; absence of `4388…` there does not
   establish its archive state. Do not repeat the inspection without a new
   reason. Closure needs delivery accounting and resolution of unknown
   outcomes, including Slab `a8a31c72975541feb1c36a2e8cbb8f65`.
2. **Native Material Slab:** 0.41.0 getter-only PASS (exact child and its
   immediate parent: native Material `" "`, ID 508 `TEST1`, zero setters).
   0.42.0 added the opt-in `exact_target` for one Slab child under an exact
   MultiSlab parent ([contract](m4-editing-api.md#exact-child-native-material-target-0420)).
   The 0.42.1 trial confirmed the `native_material_ownership` report and two
   highlight submissions; Apply `a8a31c…` stopped unknown at `fresh_resolve`
   ("Exact child inventory or parent edge changed"), recovery repeated it.
   Diagnosis (0.43.0): `fresh_resolve` runs after `SetMaterial` +
   `ModifyElements`; the pre-setter resolve and the final mutation boundary
   both passed with the reviewed fingerprint, so the inventory changed across
   the native submission. The readback path already tolerated regenerated
   views, but `locate()` still required the pre-setter fingerprint. 0.43.0
   reports a bounded diff (`exact_inventory`) after the setter while the
   target view, child type and parent edge stay strict; Apply keeps the
   outcome unknown (`exact_inventory_changed_after_setter`), read-only
   recovery can reconcile from the observed value.
   Closure: recovery of `a8a31c…` with an observed value; one new Apply whose
   diff is reviewed; fresh readback/UI, preservation and Undo/restoration.
   If the diff shows only expected regeneration, decide (owner review) whether
   that category may be accepted as applied in a later version.
3. **Slab/MultiSlab attributes:** keep the reported 0.39.0 value PASS. Missing:
   exact historic payloads, owner bindings, grouping order and
   Undo/restoration. Do not infer parent/child equivalence or relax the
   overlap guard. Closure needs exact existing payloads or a separately
   justified changed flow.
4. **Attribute types × families:** one trial per open matrix cell with exact
   name↔ID binding, SDK type, Apply payload, typed readback and UI Undo. Dates
   need a documented or native-verified codec first.
5. **Native properties:** API note, then per-family single-property trials as
   described in item 5 of the table.
6. **Beam:** owner UI check; if an architectural beam exists, create a
   disposable fixture and add it to the [fixture guide](fixture-guide.md).
7. **Layer and no-op:** the matrix of existing reads and gaps is in
   [validation status](validation-status.md#declared-family-and-owner-evidence-for-layer-and-delete).
   For missing pairs: exact targets, old/new layer, preview/revalidation,
   fresh readback/UI and Undo with restoration read; for groups, one grouped
   Undo. Closure: documented coverage of the declared matrix, no-op with zero
   setters and no Apply, working highlight/clear, retained conflicts after
   scope/value change and replay.
8. **Delete and selection:** for missing declared families/subtrees:
   disposable fixture, exact refs and dependencies, preview, deletion with
   readback of the absent subtree, neighbour preservation and Undo with
   restoration read. Selection needs a documented native set/clear/readback
   contract, implementation and a trial comparing the exact set in API/UI,
   also after clear; leaving it unsupported requires an explicit scope
   decision. Next selection step: establish replace/clear/independent readback
   in the installed SDK and run the
   [narrow experiment](m4-native-selection-api.md#7-minimal-experiment-and-deciding-questions).

Historic unresolved execution IDs and the broad property discovery stay
recorded in [validation status](validation-status.md#evidence-for-unresolved-cases);
do not delete their journal or resume the broad probe. Mark a missing fixture
`fixture_missing` and an unresolved contract BLOCKED.

## Scaling and further extensions

1. Scaling and MCP ergonomics: [analysis and stages S0–S5](implementation-plan.md#scaling-analysis-of-developm4-and-mcp-ergonomics)
   separate larger reads, more than 32 changes in one drawing, and later
   multi-file work. 200 is a page limit, not a selection limit; the real
   barriers are full rescans, 10,000 adapters, time, memory and the journal.
   Measurements, ergonomics and reads can progress earlier; larger writes
   depend on acceptance of the specific operation. Closure: complete results,
   fewer scans/roundtrips confirmed by measurement, a durable manifest/batches
   and restart without repeated setters. Do not claim shared Undo or
   atomicity without evidence.
2. Plan the whole project separately: enumeration of unloaded files,
   activation, context restoration and incompleteness reporting. Missing
   access must never mean zero results.

## Closure criteria

- Every newly accepted flow has an exact scope, a binding to the installation
  and Allplan build, and fresh readback/UI/Undo appropriate to the operation.
  Keep the limits of earlier evidence; do not repeat their trials.
- A query explicitly reports completeness, owners, representations,
  openings/parents and, separately, selection and highlight.
- Preview, revalidation, Apply, replay and recovery keep plan boundaries,
  account for conflicts and never repeat setters after an unknown outcome.
- The journal keeps unresolved writes across limits, archival and restart.
  Every larger scope has its own acceptance.

The [documentation policy](documentation-policy.md) defines handoff and task
updates; the [testing policy](testing-policy.md) defines checks and builds.
The aggregate CI gate `ci-required` exists; the owner confirms whether it is
configured as a required check for `develop/m4` ([testing policy](testing-policy.md#required-github-check)).
The gate does not replace ZIP or Allplan acceptance. The
[tool reference](tool-reference.md), [API evidence](m4-attribute-api-evidence.md)
and [type matrix](m4-attribute-type-coverage.md) remain the API contract sources.
