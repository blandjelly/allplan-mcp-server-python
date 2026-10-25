# Validation status and necessary evidence

Current candidate and next action: [handoff](next-model-handoff.md).
Remaining development and unresolved errors:
[development plan](office-editing-development-plan.pl.md).
Current candidate 0.36.0 is on `fix/m4-material-lifetime-trace`, based on
`develop/m4` commit `9553c8d10d6cd8f0987b1310d0ee89d3b519dc49`. On Python
3.12.14, 160 distinct focused tests passed across `test_wall_material_edit`,
`test_native_material_columns`, `test_component_identity`,
`test_edit_ownership`, `test_model_edit`, `test_native_model_edit` and
`test_trace_cleanup`. Ten HTTP tests passed across
`test_wall_material_http`, `test_component_identity_http` and
`test_model_edit_recovery_http`. The borrowed-owner regression failed against
the actual 0.35.0 source and passed on this candidate. Full GitHub CI,
exact-ZIP verification and the bounded native preview are separate pending
gates as described in the [handoff](next-model-handoff.md) and testing policy.

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

- **0.35.0 native material preview crash:** Three previews on 25.10.2026
  crashed Allplan with `C0000005` reading address `690`. At 17:34:17.597,
  17:36:17.018 and 17:42:03.510 Europe/Warsaw, each M1 scan returned and
  `Native.material_observation` started without a corresponding return or
  failure. The first two requests targeted the original 240 mm Wall; the third
  targeted a 200 mm Wall. The request IDs were
  `aaa5eaeb-aae1-42b7-9cbe-4e2f27679653`,
  `cad8b848-9c8b-4f64-8d44-e3a38cc050a2` and
  `16b62bb6-3ceb-44f8-94f4-1faabfde6daf`. Preview did not reach Apply. The
  `model_edit` reads material before filtering by thickness, so the requested
  thicknesses do not identify which root was being read.
  Cause remains unknown. A mixed `native`/`props`/`tier` set in
  `wall_material.snapshot` is a candidate code issue, not a proven crash cause.
  The owner checked WER and CrashDumps and found no dump for 25.10. The
  available 29.09 PID 24704 and 08.10 PID 27988 dumps are historical
  `C0000374` heap corruption events and do not diagnose these `C0000005`s.
  Do not request another 0.35.0 crash or ask for those absent dumps. The
  owner-supplied raw archive `crash log 0.35.0.zip` remains in local/chat
  attachments. SHA-256:
  `4ac1f7382f23e12f41e2398e0db6d41e4c6c264c78a57517ac22927bfdb534ac`.
- **Completed Column Apply/readback from 0.35.0:** journal record
  `repairs/c2fd4904f22c4d58bba15b9014bf07eb.json`, plan
  `1a3cb68bc86c4076a84413c89f9ecca6`, model UUID
  `eb88c850-0cac-408a-8091-f118872d74c2`, file 101, `Column_TypeUUID`, records
  `native.material` from empty string to `Żelbet`, `completed` / `applied`,
  `readback_matches`, and readback `Żelbet`. This confirms that Apply and
  readback for this Column only. The supplied evidence does not include a
  no-op, drift, UI Undo or restoration result; do not repeat this write/readback
  trial.
- **0.36.0 next native check:** After required CI and exact-ZIP verification,
  owner runs only preview on the original 240 mm Wall. Preserve the first new
  durable trace or failure and stop; no Apply for blocked or unknown preview.
  This focused crash trial is not full native acceptance. Keep the 200 mm
  Wall/opening `component_child_owner_mismatch` unresolved and do not repeat it.
  Candidate work retains both existing native reads and their material
  comparison, keeps the first owners alive through the full read, and includes
  `tier` in `_detailed_snapshot` so the final snapshot uses coherent
  `native`/`props`/`tier`. It adds durable `model_edit.observe` trace for
  preview/revalidation/source observations, with the same root reference
  metadata on traced SDK reads, preserving existing guards.
  The uploaded `m4-native-probe.jsonl` measured 2,096,914 bytes; source
  `NativeProbeTrace.MAX_BYTES` is 8 MiB. Preserve trace and journal history.
  Do not add auto cleanup/delete; if storage blocks, retain its snapshot and
  follow existing reviewed snapshot and confirmation procedure.
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
