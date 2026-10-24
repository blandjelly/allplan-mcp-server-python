# Validation status and necessary evidence

Current candidate and next action: [handoff](next-model-handoff.md).
Remaining development and unresolved errors:
[development plan](office-editing-development-plan.pl.md).
Candidate 0.35.0 on `fix/m4-material-unblock` passed 153 distinct
affected/dependent tests and 4 MCP HTTP tests on Python 3.12. Version metadata
agrees on 0.35.0. Full GitHub CI, exact-ZIP verification and native acceptance
are separate pending gates owned as described in the testing policy.
The owner reports that 0.34.0's 240 mm Wall preview blocked at geometry and its
Column request returned `old_value_unknown` through the Wall-only path. No raw
responses were supplied, so these reports do not establish exact runtime
stages or native acceptance. The 0.34.0 package/CI references remain in the
prior handoff and repository history; the current trial is defined in the
[handoff](next-model-handoff.md).

## Accepted baseline and scoped M4 observations

M0–M3 are accepted only for the retained `MCP_QA_DEMO` fixture and recorded
one-/two-change scenarios in foreground drawing 101. They do not establish
arbitrary combinations, multi-file writes, cross-copy identity or general
office use. See the [fixture](fixture-guide.md) and
[M3 contract](m3-execution-contract.md).
Original baseline reports remain in
[Git history](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results).

The following prior outcomes are retained to avoid repeating completed work.
Except where explicitly supported by source evidence, owner reports lack an
exact installed manifest/build and do not establish exact-ZIP acceptance.

| Scope to preserve | Evidence and limit |
| --- | --- |
| Read/query/highlight | Scoped Column observation, Wall 240 mm/`Beton` read, and Wall `<240 mm` filter/highlight/clear were observed. Highlight does not establish native selection. [Original observations](https://github.com/blandjelly/allplan-mcp-server-python/tree/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results). |
| Earlier Slab/Column attributes | Owner log reports `Materiał=beton zbrojony` and `Element nośny=1` on two Slab representations with readback, and `Priorytet` on two results plus ordered `MCP_QA_MARK` on six Columns. It contains no request payload or attribute ID. Later read-only evidence shows ID 508 as a String with value `beton zbrojony` on Slabs; the official example calls 508 `Material`, but there is no live name/ID roundtrip in that evidence. None of this establishes native material or a Wall/Column material-attribute write. [Source log](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md), [read-only evidence](test-results/evidence/0.31.0-2026-10-24/slab-multislab-readonly-evidence.json), [API note](test-results/m4-agent-test-api-evidence.md). |
| Journal archival | 0.23.0 owner PASS: preview and confirmed archive of 614,396 trace bytes and 32 resolved records (739,786 bytes), preserving replay protection. Native restart/replay was not demonstrated by that report. Trial 1 in 0.30.0 was reported PASS without detailed raw evidence for its individual substeps. [Original archival observation](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-journal-cleanup-0.23.0-owner-pass-2026-10-21.md). |
| Identity, lookup and W1 | Owner reported identity reads, lowercase attribute-name resolution, W1 read/write with one UI Undo per changed element, and 0.30.0 identity/no-op trials PASS. Detailed raw logs for trials 1–3 are absent. Do not infer field ownership, all-family coverage or grouped W1 Undo. [0.27.0 source log](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md). |
| Typed deletion | Separate Wall subtree deletion and Beam W1 moves remain scoped observations. The repaired 0.29.0 three-Column delete trial was reported PASS: fresh scan found Columns/attribute containers absent; one UI Undo restored all three Columns. Tool metadata retained `undo: not_checked`, without automatic post-Undo readback, target UUIDs or exact ZIP manifest. This supersedes the earlier one-of-three Undo failure only for that Column operation. [0.29.0 source log](test-results/evidence/allplan-test-log-0.29.0-2026-10-23.md). |
| Scalar attributes | Four 0.30.0 pairs: Column text/integer/real and Wall text, each with typed readback and owner-confirmed UI Undo/restoration read. [Detailed log](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md), [persisted requests](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trial-apply-requests.jsonl). |
| Wall Enum | ID 120 `Rodzaj rozliczenia`: `m3` → `m2` → `m3`, Apply/readback and owner-confirmed UI Undo; four consistent representations. [Apply request](test-results/evidence/0.31.0-2026-10-24/enum-apply-evidence.json), [execution/readback](test-results/evidence/0.31.0-2026-10-24/enum-apply-execution-evidence.json), [Undo readback](test-results/evidence/0.31.0-2026-10-24/enum-undo-evidence.json). Metadata still says `allplan_acceptance=not_run`, `runtime_verified=false`; no exact installed ZIP attribution. |
| Wall CheckBox | ID 1371 has only [post-Undo readback](test-results/evidence/0.31.0-2026-10-24/boolean-checkbox-undo-evidence.json): value 0, SDK Integer 73. No raw Apply evidence; this is not an accepted complete Boolean cycle. |

Do not repeat these accepted scopes or generalize them to other family/type
pairs. Missing fixtures and blocked paths are separate from PASS.

## Evidence for unresolved cases

- **0.34.0 native material — owner report only:** Wall 240 mm preview was
  reportedly blocked at tier geometry; Column at X=0, Y=0 reportedly returned
  `old_value_unknown` because that candidate's adapter was Wall-only. No raw
  responses are available. Candidate 0.35.0 expands the native property route
  to standalone single-tier Walls and Columns while keeping the public
  `native_material` request. Do not treat the report or implementation as
  native acceptance; use the bounded Wall/Column trial in the
  [handoff](next-model-handoff.md).
- **Wall material — 0.33.0 native trial:** on drawing 101, the query found one
  original 240 mm `Ściana, prosta` (`Wall_TypeUUID`) with material observed as
  `Beton`. Query reported `scan_complete=true` but
  `requested_scope_complete=false`; model UUID was
  `06d71e4d-193b-483e-8a32-344ade3d612c`, and `usable_for_write=false`.
  Preview matched one element and blocked one property (`changes=0`):
  `wall.native_material` / `native_material_preservation_unavailable`, old
  value `Beton`, observation `not_checked` because
  `wall_material_tier_child_unsupported` at `material_tier_children`
  (`ValueError`). The diagnostic identifies owner `WallTier_TypeUUID`
  (`a7fae808-845c-4491-9f44-3757c493e673`, model
  `4db19151-9090-4b1c-bd50-b6fba6873aff`) and child `WallAxis_TypeUUID`
  (`b7b85ac6-3b03-4b81-a353-153216f8ae4d`, model
  `6446ff90-420c-4d1d-8d3f-cccb1987c768`), both in drawing 101. No exception
  message was supplied. `usable_for_write=false`, `setter_calls_started=0`,
  `apply_available=false` and `production_apply_available=false`; no write or
  native acceptance occurred. Query request ID was
  `f5fc110f-ad9f-481a-a5fd-70326103c27a`; preview request ID
  `c5e0d95e-f705-44d4-b903-f12b2f0732a2`, plan ID
  `7cb19ce69f1242229b441a289e71424c`, plan hash
  `adece99dd84670cf267ba10cc7328f0d2f22b3c77b6f6ff80d968c6f3be0a1d2`.
  See the [raw log](test-results/evidence/0.33.0-2026-10-24/wall-native-material-preview-log.md).
  This records the observed 0.33.0 blocker only; it does not establish its
  native preservation cause.
- **Wall material — prior 0.32.0 report:** on drawing 101, original 240 mm
  Wall (`Ściana, prosta`), material `Beton` → `Silikat`, was BLOCKED before
  writes. It reported `native_material_preservation_unavailable`, old value
  `Beton`, reason `wall_tier_child_unsupported`, stage
  `material_tier_children`, `ValueError`, with no diagnostic evidence. That
  exact reason was absent from the 0.33.0 source and retained 0.32.0 ZIP; both
  used `wall_material_tier_child_unsupported`. An installed/live host
  mismatch is possible, not proven. Supplied tier UUID
  `4db19151-9090-4b1c-bd50-b6fba6873aff` and container UUID
  `abecfaf0-ad01-45e1-91df-4b32ed9960ae` have unknown actual lineage. The
  0.33.0 trial independently observed the unsupported tier child described
  above; neither result alone establishes the preservation cause. At the time
  of this report, the next trial was candidate 0.34.0: verify its manifest/hash
  and Allplan build, reload
  PythonHost, then test the original 240 mm Wall and a disposable copied or
  independent Wall with opening/macro/nested metadata where fixtures permit.
  The public contract remains single-tier (`tier_index: 1`); multi-tier stays
  blocked. Include no-op and controlled drift/conflict previews. A qualifying
  preview on a disposable fixture may proceed to Apply, fresh readback, one UI
  Undo and restoration readback. The separate 200 mm Wall/opening model
  `545bb0a2-a054-4c91-ac6c-ec552d5b0c18` reported
  `component_child_owner_mismatch` at `child_parent_identity`; keep it
  unresolved and do not repeat its preview.
  The prior [0.31.0 conversation log](test-results/evidence/0.31.0-2026-10-24/allplan-conversation-log.md)
  records historical clues for the original Wall model/view
  `06d71e4d-193b-483e-8a32-344ade3d612c` /
  `2d33e5a6-b4e8-444b-94e8-d4d0ae75d622` and tier model/view
  `4db19151-9090-4b1c-bd50-b6fba6873aff` /
  `1bdccbc1-6931-46fd-9f1f-f7b8657ac284`; these are not identities freshly
  verified by the 0.32.0 report. The supplied container UUID
  `abecfaf0-ad01-45e1-91df-4b32ed9960ae` likewise has unverified lineage.
- **Slab/MultiSlab:** the [0.27.0 log](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md)
  retains the parent-lineage conflict; the
  [latest raw attribute probe](test-results/evidence/0.31.0-2026-10-24/slab-multislab-readonly-evidence.json)
  retains view differences, incomplete Slab evidence and unestablished field
  ownership. No new Slab/MultiSlab write was performed.
- **Multiview recovery:** the [owner follow-up](test-results/evidence/m4-agent-followup-blocker-2026-10-19.md)
  records unresolved execution `4388b04e39a14fac811db4f58723d01f`.
  Native resolution has not been recorded.
- **Broad property crash:** [original analysis and source evidence](https://github.com/blandjelly/allplan-mcp-server-python/blob/c42adf0377438dcb729df08b0527635301af2e50/docs/test-results/m4-native-crash-0.16.0.md).
  Allplan 2026-1-7 failed during `/model-properties`; no native stack
  established the reader/cause. Broad discovery remains suspended.

The [backlog](office-editing-development-plan.pl.md) specifies the remaining
contracts, fixture gaps and acceptance criteria. Preserve all target,
revalidation, journal, replay and unknown-result guards.

## Historical records

Superseded release narratives, interpreted observations and trial plans were
removed from the working documentation. Their original contents remain at the
[pinned pre-cleanup revision](https://github.com/blandjelly/allplan-mcp-server-python/tree/c42adf0377438dcb729df08b0527635301af2e50).
Raw evidence linked above remains unchanged. Evaluation ZIPs, machine-readable
CI/package records and build/verification logs remain preserved; no old package
was rebuilt or reverified. Versioned API research retains its original scope
and is not a source for current candidate or acceptance status.
