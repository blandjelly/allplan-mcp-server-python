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

- Priority: resolve the Slab material problem first (items 1–2).
  Owner observations 2026-11-03: the Slab UI material is attribute 508 of
  the MultiSlab, the object the UI shows (0.46.0).
- Delivery: the ZIP is the GitHub Actions `package` artifact;
  `evaluation-packages/` is a historical archive (up to 0.33.0).
- Beam: an architectural beam (`Beam_TypeUUID`, "Podciąg") exists in the
  owner's project since 2026-11-02 (see item 6).
- Documentation is English only; CI runs product jobs only for code changes.

## Remaining work and unresolved errors

| Priority | What remains / condition for further work |
| --- | --- |
| 1 — delivery and older unknowns | 0.42.1 CI/ZIP confirmed by the owner; CI run identity, ZIP hash and upgrade/restore are not independently verified (0.43.0 health: `sha256-verified`). The Slab locks (`a8a31c…`, `9c6a0d…`) are reconciled by read-only recovery with the value unchanged; neither is an applied result. Wall `3f2a8c9d7b5e4a1c9f8e6d3c2b1a0e9f` was reconciled by reviewed reconciliation, preservation=false. Keep the older histories `87a…` and `4388…` described in the handoff. Never retry Apply or delete a journal. |
| 2 — Slab material: the UI shows the MultiSlab's attribute 508 | Owner observations: the slab UI material is attribute 508 (0.44.2), and it is the **MultiSlab's** value (0.46.0: tier `TEST2`, MultiSlab `TEST1`, UI `TEST1`; MultiSlab Apply `04569db1…` `TEST1`→`TEST2` `applied`, UI `TEST2`, UI Undo restored `TEST1`). The native Slab Material route is not pursued (0.43.0 setter left `" "`; guards kept). The 0.45.0 tier `applied` results most likely wrote tier storage the UI does not show. 0.47.0 blocks non-exact tier writes as `slab_tier_not_shown_in_ui_use_multislab` with a `ui_owner` hint and tells the agent to use the MultiSlab (CODE). Next: plain-language trial (handoff step 2). |
| 3 — Slab/MultiSlab attributes | MultiSlab attribute 508 write PASS (0.46.0, UI and Undo). The 0.39.0 reported tier/assembly PASS lacks payloads and owner binding and may have written invisible tier storage. The exact parent-edge tier route (0.46.0) ran no setter yet (preview `no_op`); optional handoff step 3 checks it. Keep `target.property_owner="selected_element"`, lineage/children and the overlap guard. |
| 4 — attribute types × families | Close owner-specific roundtrips for every family/type pair in the [matrix](m4-coverage-matrix.md). Column Enum `Status` ID 49 is BLOCKED (`<niezdefiniowany>`, no confirmed label). Wall CheckBox ID 1371 has no raw Apply; no SDK Boolean fixture. Date/vector/object values need exact setter payload and typed readback contracts; an SDK symbol or constructor is not enough ([type coverage](m4-attribute-type-coverage.md)). |
| 5 — native properties beyond Material (new) | Not started. First write an API note: which `WallTierProperties`, `ColumnProperties`, `BeamProperties`, `StructuralBeamProperties` and `SlabProperties` members (thickness, height/plane references, surface, priority, calculation mode, trade, hatch/filling) have documented setters, their owners and readback; then one property per family with preview, preservation and Undo evidence. The current preservation snapshot already reads many of these values. |
| 6 — Beam: closed for attribute 508 and native Material | Fixture "Podciąg, wieniec" ([fixture guide](fixture-guide.md)). Attribute 508 write PASS (0.44.0, 0.45.0). Native Material PASS (0.46.0 `5a0bc366…`: `applied` with accepted `auxiliary_children_regenerated`, owner-reported UI and Undo, post-Undo `""`). Other Beam types and native properties continue under items 4–5. |
| 7 — layer and no-op: partially accepted | Keep W1 read/write, single Undo and the reported no-op in their scope. Remaining family/owner pairs and grouped Undo need evidence. No-op has no Apply path. |
| 8 — delete and selection: partially accepted / missing | Keep grouped Column delete/Undo and the Wall subtree observation. Other declared families/subtrees need evidence. Native selection remains unsupported pending an installed-SDK set/clear/readback contract ([selection API](m4-native-selection-api.md)); highlight does not close selection. |

### Evidence needed to close items 1–8

Items refer to one active drawing and the existing 1–32 change limit. Keep
reported PASS results; add only missing evidence or a changed flow; do not
repeat completed Apply calls just to recreate a log. From 0.43.0 the launcher
captures raw bridge requests/responses in the package `logs/evidence/`; attach
those files instead of chat summaries.

1. **Delivery and recovery:** for 0.42.1 (`eecdfeb`) the owner confirmed CI
   and ZIP; the CI run ID, ZIP hash and upgrade/restore are not independently
   verified. The 31-record inspection is done: `87a…` stays stopped/reconciled
   without applied/preservation evidence; absence of `4388…` there does not
   establish its archive state. Do not repeat the inspection without a new
   reason. The Slab unknowns `a8a31c…` and `9c6a0d…` were reconciled by
   read-only recovery (value `" "`). Closure needs delivery accounting.
2. **Slab material:** the UI material is the MultiSlab's attribute 508
   (0.44.2, 0.46.0). Closure: one 0.47.0 plain-language request ("change the
   slab material") that the agent turns into a MultiSlab attribute 508 Apply
   ending `applied`, with the UI showing the value and UI Undo restoring it
   ([contract](m4-editing-api.md#slab-tier-attribute-writes-and-the-ui-material-owner-04500460-observations-0470-contract)).
   The native Slab Material route (0.41.0 getter, 0.42.x exact target, 0.43.0
   setter leaving `" "`) stays guarded and is not pursued
   ([evidence](test-results/evidence/0.43.0-2026-11-02/evidence-20261102.jsonl)).
3. **Slab/MultiSlab attributes:** MultiSlab 508 PASS (0.46.0). For tiers:
   the exact parent-edge route needs one native Apply (handoff step 3)
   showing that all tier wrappers agree; the reported 0.39.0 tier result has
   no payload or owner binding. Do not infer parent/child equivalence or relax
   the overlap guard.
4. **Attribute types × families:** one trial per open matrix cell with exact
   name↔ID binding, SDK type, Apply payload, typed readback and UI Undo. Dates
   need a documented or native-verified codec first.
5. **Native properties:** API note, then per-family single-property trials as
   described in item 5 of the table.
6. **Beam:** closed for attribute 508 and native Material (0.44.0–0.46.0
   evidence in the [handoff](next-model-handoff.md#latest-version)).
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
  Every larger scope has its own acceptance. The diagnostic trace archives
  full segments automatically (0.44.0, no deletion, 256 MiB budget); archive
  retention/export beyond that budget stays a manual owner decision.

The [documentation policy](documentation-policy.md) defines handoff and task
updates; the [testing policy](testing-policy.md) defines checks and builds.
The aggregate CI gate `ci-required` exists; the owner confirms whether it is
configured as a required check for `develop/m4` ([testing policy](testing-policy.md#required-github-check)).
The gate does not replace ZIP or Allplan acceptance. The
[tool reference](tool-reference.md), [API evidence](m4-attribute-api-evidence.md)
and [type matrix](m4-attribute-type-coverage.md) remain the API contract sources.
