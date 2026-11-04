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

- Priority: resolve the Slab material problem first (items 1–2). Closed
  2026-11-03: the Slab UI material is the MultiSlab's attribute 508 (0.46.0),
  and the 0.47.0 plain-language trial changed and undid it (item 2).
- Delivery: the ZIP is the GitHub Actions `package` artifact;
  `evaluation-packages/` is a historical archive (up to 0.33.0).
- Beam: an architectural beam (`Beam_TypeUUID`, "Podciąg") exists in the
  owner's project since 2026-11-02 (see item 6).
- Documentation is English only; CI runs product jobs only for code changes.

Owner decisions (2026-11-04): a plain "material" request on a Wall changes
both the native tier Material (element dialog) and attribute 508 (attributes
palette); a request naming one place changes only that one. The slab
properties palette shows the MultiSlab in "Cały obiekt" and the tier in
"Warstwa bieżąca" mode; both are UI owners (item 3). Plain slab requests
target "Cały obiekt" (the palette's first view; the layer has other
settings); the layer is changed only when the request names it.

## Remaining work and unresolved errors

| Priority | What remains / condition for further work |
| --- | --- |
| 1 — delivery and older unknowns: closed (owner decision 2026-11-03) | Delivery evidence is full CI (`ci-required`, confirmed as a required check on `develop/m4`) plus installed-bridge health (version, source commit, `sha256-verified`) in each native trial. No retroactive CI run IDs or ZIP hashes. The older executions need no further work; their journal safeguards stay in the [handoff](next-model-handoff.md#key-errors-and-necessary-earlier-context). One upgrade/restore check on the final M4 version is optional (see closure criteria). |
| 2 — Slab material: closed | The slab UI material is the MultiSlab's attribute 508. 0.47.0 trial (2026-11-03): the tier hint blocks non-exact tier writes with `ui_owner`; a plain-language request became a MultiSlab 508 Apply (`3f9c2a7e…`, `applied`, UI, UI Undo, post-Undo read `TEST1`). The native Slab Material route is not pursued (0.43.0 setter left `" "`; guards kept). |
| 3 — Slab/MultiSlab attributes: closed for attribute 508 | MultiSlab 508 PASS (0.46.0, 0.47.0). The exact parent-edge tier route wrote tier storage (0.47.0 `9b2e4d71…`, `TEST2`→`TEST1`, both tier wrappers agree, inventory unchanged; no UI Undo). The owner showed on 2026-11-04 that the tier **is** visible in the UI palette's "Warstwa bieżąca" mode (508 `TEST2`, 120 `m2`); "Cały obiekt" shows the MultiSlab. Candidate 0.49.0 (code, native trial pending): MultiSlab stays the default (owner decision), the block is renamed `slab_tier_requires_exact_layer_target` with corrected guidance, and MultiSlab attribute previews report the tiers' differing values (`slab_tier_values`). Remaining: native check of that report, and one UI-checked tier write with UI Undo in "Warstwa bieżąca" for an explicit layer request (exact route). Other attribute types on Slab/MultiSlab continue under item 4. Keep `target.property_owner="selected_element"`, lineage/children and the overlap guard. |
| 2a — Wall material: both places (owner decision 2026-11-04) | A plain "material" request on a single-tier Wall must change native tier Material and attribute 508 together; naming one place changes only that one. Needs a design: one plan with two changes on the same Wall (native + attribute), one Apply, readback of both, preservation that excludes exactly these two fields, and a check of how many UI Undo steps restore both. Existing routes: Wall native Material VALUE (0.37.0/0.39.0, preservation unverified), Wall attribute 508 write. Not started. |
| 4 — attribute types × families | Close owner-specific roundtrips for every family/type pair in the [matrix](m4-coverage-matrix.md). Column Enum `Status` ID 49 is BLOCKED (`<niezdefiniowany>`, no confirmed label). Wall CheckBox ID 1371 has no raw Apply; no SDK Boolean fixture. Date/vector/object values need exact setter payload and typed readback contracts; an SDK symbol or constructor is not enough ([type coverage](m4-attribute-type-coverage.md)). |
| 5 — native properties beyond Material | API note ([note](m4-editing-api.md#native-properties-beyond-material--api-note-plan-item-5)); first candidate `CalculationMode`, `Thickness` second. **Step 1 done** (0.48.0 read-only trial 2026-11-04, [handoff](next-model-handoff.md#installed-version-and-last-native-evidence)): native `CalculationMode` = attribute 120 = UI on Wall, Column (`m`) and Beam (consistent, storage coupling unproven); on the MultiSlab native `m2` ≠ attribute 120/UI `m3` (native Slab route is not the UI owner, as for material); `Priority` = UI on all four; `Trade` not determinable (all unset, −1/0). **Step 2 implemented in candidate 0.49.0** ([contract](m4-editing-api.md#calculationmode-write-contract-0490)): `native_calculation_mode` for Column, single-tier Wall and Beam, preservation without `CalculationMode`/attribute 120, native readback plus separate attribute-120 `mirror_crosscheck`; slabs blocked toward the MultiSlab attribute 120 route. **Next:** native trial (Column first), one write + UI + UI Undo per family, mirror verdict recorded ([handoff](next-model-handoff.md#next-task--native-trial-of-candidate-0490-plan-items-3-and-5)). Owner answers 2026-11-04: the Slab child is the "Warstwa bieżąca" palette mode; the tier change `TEST1` → `TEST2` after 0.47.0 is unexplained. **Trade (Wall, 2026-11-04):** "Roboty murarskie" = native 12, cleared = 0 (initially −1); attribute 209 not returned either way, so no attribute mirror — native `Trade` only. A Trade write needs the full code↔label list first. |
| 6 — Beam: closed for attribute 508 and native Material | Fixture "Podciąg, wieniec" ([fixture guide](fixture-guide.md)). Attribute 508 write PASS (0.44.0, 0.45.0). Native Material PASS (0.46.0 `5a0bc366…`: `applied` with accepted `auxiliary_children_regenerated`, owner-reported UI and Undo, post-Undo `""`). Other Beam types and native properties continue under items 4–5. |
| 7 — layer and no-op: partially accepted | Keep W1 read/write, single Undo and the reported no-op in their scope. Remaining family/owner pairs and grouped Undo need evidence. No-op has no Apply path. |
| 8 — delete and selection: partially accepted / missing | Keep grouped Column delete/Undo and the Wall subtree observation. Other declared families/subtrees need evidence. Native selection remains unsupported pending an installed-SDK set/clear/readback contract ([selection API](m4-native-selection-api.md)); highlight does not close selection. |

### Evidence needed to close items 1–8

Items refer to one active drawing and the existing 1–32 change limit. Keep
reported PASS results; add only missing evidence or a changed flow; do not
repeat completed Apply calls just to recreate a log. From 0.43.0 the launcher
captures raw bridge requests/responses in the package `logs/evidence/`; attach
those files instead of chat summaries.

1. **Delivery and recovery:** closed by owner decision (2026-11-03); see the
   table. Keep the journal safeguards; do not repeat the 31-record inspection.
2. **Slab material:** closed by the 0.47.0 plain-language trial
   ([evidence](test-results/evidence/0.47.0-2026-11-03/evidence-20261103.jsonl),
   [contract](m4-editing-api.md#slab-tier-attribute-writes-and-the-ui-material-owner-04500460-observations-0470-contract)).
   The native Slab Material route stays guarded and is not pursued.
3. **Slab/MultiSlab attributes:** closed for attribute 508 (MultiSlab PASS;
   exact tier route VALUE with all wrappers agreeing). Persistence of the tier
   value after save/reopen is not observed. Do not infer parent/child
   equivalence or relax the overlap guard.
4. **Attribute types × families:** one trial per open matrix cell with exact
   name↔ID binding, SDK type, Apply payload, typed readback and UI Undo. Dates
   need a documented or native-verified codec first.
5. **Native properties:** step 1 (read-only precheck) closed by the 0.48.0
   trial ([evidence](test-results/evidence/0.48.0-2026-11-04/evidence-20261104.jsonl)).
   Step 2 (code in 0.49.0, native trial pending): one `CalculationMode` write
   per family (Column, Wall, Beam) with typed readback, attribute-120
   cross-check verdict, UI and UI Undo; Slab through the MultiSlab attribute 120. `Trade`: native only (no 209 mirror on the Wall); needs the label list.
6. **Beam:** closed for attribute 508 and native Material (0.44.0–0.46.0
   evidence in the [handoff](next-model-handoff.md#installed-version-and-last-native-evidence)).
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
- Optional (owner decision 2026-11-03): one package upgrade and restore check
  on the final M4 version; if skipped, M4 closes noting that this scenario was
  not verified natively.

The [documentation policy](documentation-policy.md) defines handoff and task
updates; the [testing policy](testing-policy.md) defines checks and builds.
The aggregate CI gate `ci-required` is configured as a required check for
`develop/m4` (confirmed 2026-11-03 by a rejected direct push;
[testing policy](testing-policy.md#required-github-check)).
The gate does not replace ZIP or Allplan acceptance. The
[tool reference](tool-reference.md), [API evidence](m4-attribute-api-evidence.md)
and [type matrix](m4-attribute-type-coverage.md) remain the API contract sources.
