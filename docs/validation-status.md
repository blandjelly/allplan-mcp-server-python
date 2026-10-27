# Validation status and necessary evidence

Current version and next action: [handoff](next-model-handoff.md).
Remaining development and unresolved errors:
[development plan](office-editing-development-plan.pl.md).
Version **0.41.0** is merged into develop/m4 through
[PR #47](https://github.com/blandjelly/allplan-mcp-server-python/pull/47).
The exact-parent Slab child getter route passed the bounded native trial below;
this does not establish native material writes or persistence. Historical focused
checks and full CI are separate from that native result. Exact delivered
ZIP/upgrade/restore verification remains incomplete. Current API and recovery contracts are in
[API evidence](m4-editing-api-0.32.0.md).

## Delivery and CI evidence

The 0.41.0 source `f775168aaf8fdb043c269ff09d6ffda9fcea17c9` passed
[run 40550057327](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40550057327):
configuration, full Windows/Ubuntu Python 3.12 test jobs, package production and
`ci-required` all completed successfully, including their test/build steps.
The earlier failed run `40549970082` is not the accepted CI evidence. The
[health response](test-results/evidence/0.41.0-2026-10-27/01-health-context.json)
binds the installed bridge to that source and reports verified file integrity
with no mismatches. The [supplied report](test-results/evidence/0.41.0-2026-10-27/raport.md)
records the owner's CI/ZIP confirmation and a local sidecar SHA-256; it also
states that independent verification of the exact installed ZIP was not obtained.
Keep exact-ZIP, upgrade and restore gates unverified. The prior candidate's
**82 focused unit + 8 MCP/HTTP checks PASS** remain historical focused results,
not a new local run. No replacement package or new build was produced here.

The final 0.40.0 PR head `fca3da9820e684a41cd1c1e4300734a57e7bdbbb`
passed [Windows/Ubuntu Python 3.12, package and ci-required](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40499946308).
Each selected job and its test/build step completed successfully; the earlier
cancelled run is not the validation. The supplied
[health response](test-results/evidence/0.40.0-2026-10-27/01-health-context.json)
reports that exact bridge source commit and installed file integrity verified
with no mismatches, binding the native getter observations to that bridge
source. It does not identify the delivered ZIP/hash or verify upgrade/restore.
No artifact was downloaded or rebuilt here. This baseline does not validate
the changed 0.41.0 source.

Historical GitHub checks for the final 0.39.0 PR head
`959280e807099a04cf63f5e47d85b7e4ecd05c55` confirm successful
[Windows/Ubuntu Python 3.12 jobs, package production and ci-required](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40383968336).
Only four documentation files differ from runtime/test source `811a1bde`.
The earlier draft run skipped product jobs; it is not the final validation.
This establishes baseline CI and package production, but no exact-ZIP
installation/upgrade/restore or attribution of the owner's installed package.
It does not validate later candidates. Branch-protection inspection returned
`403 Resource not accessible by integration`; whether `ci-required` is
configured as required on `develop/m4` remains unconfirmed.

## Latest owner observations

**2026-10-27, 0.41.0 exact Slab child and separate immediate-parent read: PASS
for this getter scope only.** All four supplied files are preserved unchanged
in [the evidence directory](test-results/evidence/0.41.0-2026-10-27/).
Health reports Allplan 2026.1, bridge/MCP 0.41.0, embedded CPython 3.13.13,
external Python 3.14.8 and installed bridge integrity verified. Hotfix remains
`not_checked`, runtime compatibility `runtime_verified=false`. The project was
`Kopia MCP_QA_DEMO`, foreground drawing 101; durable project identity remains
unverified.

The [single request/response](test-results/evidence/0.41.0-2026-10-27/02-slab-child.json)
retains child model `8a693925-ae20-4dda-91d1-3951af3c0a52`, view
`a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, `Slab_TypeUUID`, and explicit parent
model `bf097d95-8275-4229-ac74-27bbea26c211`, view
`b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`, `MultiSlab_TypeUUID`.
`identity_resolution.method=exact_parent_children` and the observed child-parent
edge identify the same immediate parent that was separately read. Both native
representations are `SlabElement`; both `SlabElement.Properties.Material`
values are exactly `" "` (one space), while attribute 508 is `"TEST1"` in both
`ReadAll` and `ReadAllAndComputable`. Metadata binds 508 ↔ `Materiał`, SDK
`String`, with a live name/ID roundtrip. This closes the previous exact child
read blocker for this request; it does not diagnose its earlier native cause.

One target representation and one enumeration-parent representation were read,
with consensus and complete evidence; two child visits completed the parent
inventory. `target_in_direct_scan=false` refers to the requested exact view;
`other_view_uuids` contains `37a3c6a2-d40a-4005-a830-3d212c9bd165`. This neither
proves that the Slab model is absent from SelectAllElements nor establishes
view equivalence or a failure of the separate semantic edit scan. The direct
scan reports 26 identities, zero identity/file conflicts and complete
scan/requested-scope/returned-field coverage. Whole-project, unloaded files,
screen/occlusion and geometry-unit/offset coverage remain outside the result.

The [trace](test-results/evidence/0.41.0-2026-10-27/03-trace.jsonl) contains
365 ordered records for probe `d7b68f7e6ce645b68a022f76c762d318`: 182 matched
started/returned pairs and one final completed record, with no failed or
unmatched calls and no material/attribute/model setter calls. The response
reports `read_only=true`, `model_data_changed=false`, `usable_for_write=false`
and `setter_calls_started=0`. Native selection was not requested. Writable
owner, shared storage, persistence and physical/view equivalence remain
unestablished. Do not repeat this child probe, the completed 0.40.0 probes,
or historical setters to recreate evidence.

**2026-10-27, 0.40.0 getter-only material comparison:** the supplied raw
responses are preserved unchanged in [the evidence directory](test-results/evidence/0.40.0-2026-10-27/);
[owner report](test-results/evidence/0.40.0-2026-10-27/raport.md) summarizes
them. Allplan 2026.1, bridge 0.40.0, source `fca3da98`, installed bridge SHA-256 verified with no
mismatches; runtime compatibility remains `runtime_verified=false`, and the
hotfix was not checked. Project `Kopia MCP_QA_DEMO`, drawing 101 foreground.
Each successful probe reports complete scan/requested scope/returned fields for
that drawing, but not whole-project or unloaded-file coverage, screen visibility,
native component counts, geometry units/offset, write eligibility or durable
identity. The trace path is reported, but its file was not available for
independent call-level audit. No Apply, setter, Undo, deletion, layer change or
journal maintenance occurred.

All three successful probes resolved attribute 508 as `Materiał`, SDK `String`,
with a live name↔ID roundtrip. `ReadAll` and `ReadAllAndComputable` both returned
`TEST1`; the native getter returned exactly one space (`" "`). Thus native
Material and attribute 508 are distinct observed fields with different values
on these wrappers. This does not establish owner equivalence, shared storage,
write ownership or persistence. All successful results say
`usable_for_write=false`; property/writable owner and physical equivalence are
not established.

| Target | Wrapper and observed identity | Native Material | Attribute 508 | Limits |
| --- | --- | --- | --- | --- |
| SkeletonBeam 1 | `StructuralBeamElement`; model `2dfa6117-d481-4588-8647-d24049d61d29`, target view `d9f3d9b1-a005-4789-b929-c39b291d1cd0`; root lineage complete. Children include AttributeContainer `9a86b9d7-d1fa-4cb1-b06f-5ab043cb6004` and SkeletonAxis `1ae5ed7b-6eb2-46c7-a336-0bef55d0d78a` / view `1b43e246-c34a-4037-a68e-11ec73de9a59`. | `" "`, `StructuralBeamElement.StructuralBeamProperties.Material`, owner_ref is target. | `TEST1` in both read modes. | Parent edges carry view `efb18c61-fab3-42f4-b79b-9f41d05da940`, different from target view; equivalence unresolved. Probe `3d2ae565171c4ba7a2e357058119cca3`. |
| SkeletonBeam 2 | `StructuralBeamElement`; model `8f13565b-abfc-4ce2-8b1d-7d133fe1a10d`, view `5f6e4603-6282-4ae0-9d02-ad089e73b859`; root lineage complete. Children include AttributeContainer `2f91fb33-5e4d-481f-a775-2522adfbce42` and SkeletonAxis `26007d81-ecfc-4702-b8aa-1d1fb3aec2a7` / view `d6e727cd-31a6-44e4-92c6-a2346758be8b`. | `" "`, `StructuralBeamElement.StructuralBeamProperties.Material`, owner_ref is target. | `TEST1` in both read modes. | Property/writable owner unknown. Probe `a822050593f445f0bb3c3095d69826db`. |
| MultiSlab | `SlabElement`; model `bf097d95-8275-4229-ac74-27bbea26c211`, view `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`; root lineage complete. Children include Slab `8a693925-ae20-4dda-91d1-3951af3c0a52` / view `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94` and AttributeContainer `f0b54fce-8fdb-4f4e-86b2-9a59d6d499d7`. | `" "`, `SlabElement.Properties.Material`, owner_ref is the MultiSlab wrapper only. | `TEST1` in both read modes. | Child value was not read; parent observation does not establish child value or owner. Probe `c105c234f79f4378bf2491f22ec4f638`. |
| Slab child | Exact request used model `8a693925-ae20-4dda-91d1-3951af3c0a52`, view `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, `include_parent=true`, attribute `[508]`. | Not read. | Not read. | Blocked with `probe_scope_unavailable`; no child wrapper or separate parent read completed. This does not show that SelectAll omits Slab; native cause is unknown. Request `e8e7078e-2723-4ff9-91f6-40cd83811409`. |

The journal inspection was complete and read-only: 31 of 512 records, 481
remaining slots, no `new_execution_blockers`, and no records with
`requires_recovery=true`. Execution `87a45065d5e14e3a9ac8c54756e273a0` remains
`stopped`, integrity `verified`, one change `reconciled`, and
`requires_recovery=false`. This later observation updates its previously reported
`stopped/unknown` state; preserve that historical result and do not infer
ordinary applied success or preservation. Execution
`4388b04e39a14fac811db4f58723d01f` is absent from these 31 results; this does
not establish whether an archived record exists or connect any earlier Slab
write to that execution. Do not associate historical Slab writes with an
execution absent exact evidence. The probe logs and journal do not identify
execution IDs for earlier Slab setter attempts.

These are read observations only. They do not change the earlier intended-value
PASS reports for attribute writes on two SkeletonBeams and the MultiSlab/Slab
representations of one assembly, nor establish their owner bindings, undo, or
preservation. The [0.40.0 evidence](test-results/evidence/0.40.0-2026-10-27/)
contains the seven supplied files byte-for-byte. The [0.39.0 comparison log](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md)
remains the record of the earlier query, not this material-comparison result.

**2026-10-26, version 0.39.0 (owner attribution):** the owner reports PASS for
native material on the Wall, Wall with door/window and Column, and failure
for Beam and Slab native material. The [full attached conversation log](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md)
is published unchanged in this public repository with the owner's explicit
consent. This section records summarized test findings. The log is a
chronological summary of user/assistant
messages and tool names, not raw MCP requests/responses or execution journals.
Its historical commands and permissions are evidence, not new instructions.

| Tested scope | Result and evidence limit |
| --- | --- |
| Wall without openings; Wall with door/window | **Owner PASS for intended native value.** Log entries 6–8 report the requested native value, recovery/reconciliation without setter replay, and unverified preservation. The opening configuration is supplied by the owner's report; the log has no opening UUID or separate door/window inventory. |
| Column | **Owner PASS for intended native value.** Entry 9 reports the requested value in recovery and journal reconciliation. Hierarchy drift leaves preservation unverified. |
| Beam / SkeletonBeam native material | **Owner reports not working; discovery BLOCKED/incomplete.** Entries 10–11 return zero for `Beam_TypeUUID` and `SkeletonBeam_TypeUUID`, with two representation conflicts. Later entry 13 finds two SkeletonBeams through the attribute route. No native Beam setter/readback success is evidenced; zero matches do not prove absence or API non-support. |
| Slab native material | **FAIL for requested value.** Entry 12 reports two attempts with blank native readback, component drift and reconciliation without setter replay. Exact owner, execution IDs and setter counts cannot be established from this summary. Cause remains open. |
| Material attribute on two SkeletonBeams | **Reported attribute Apply/readback PASS** in entry 13. No ordinary Beam was found. Exact name/ID/type binding and per-target payload are absent; standard ID 508 is documented separately, not proven by this log. |
| Material attribute on MultiSlab and its Slab | **Reported attribute Apply/readback PASS** for both representations of one assembly; this is not two independent slabs. No raw payload identifies owner bindings, grouping, overlap handling or per-call order. Do not infer that a parent/child plan is eligible or weaken the overlap guard. |

Entry 1 reports an initially unreachable Allplan; entry 2 reports a healthy
Allplan **2026.1** and verified bridge integrity, with runtime compatibility
not yet verified. Exact hotfix, installed manifest/package hash, full CI,
upgrade/restore and UI Undo/restoration are absent. The log reports initial
journal blocks, later reconciliation and subsequent writes, but no execution
IDs or complete journal inventory. It cannot resolve every historical unknown.
Computer Use is reported only for UI inspection; the material writes are
attributed to MCP. The owner's intended-value PASS remains recorded even
where automatic preservation verification did not pass.

The older 0.38.0 Column journal block and pre-setter Beam `AttributeError`
are historical observations in the
[previous log](test-results/evidence/0.38.0-2026-10-26/allplan-conversation-log.md).
Do not present that Column block as the still-confirmed current blocker:
0.39.0 reports reconciliation. Preserve unresolved historical IDs below
until an ID-bound journal record establishes their outcome.

The SDK exposes native Material and generic element-attribute APIs separately.
A matching displayed value does not prove independent storage or equivalent
setters. The 0.40.0 results supply paired getter observations on both retained
SkeletonBeams and MultiSlab; 0.41.0 additionally reads the exact Slab child and
its separate immediate parent. Historical write-owner bindings and native
material persistence remain unresolved. See the
[API comparison](m4-editing-api-0.32.0.md#native-material-material-attribute-and-surface).

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

### Declared family and owner evidence for layer and delete

Property metadata discovery declares six families (`Column`, `Wall`, `Beam`,
`SkeletonBeam`, `Slab`, `MultiSlab`); model-edit plans declare those six plus
`WindowDoor`. Deletion allows top-level roots from that edit list and also a
`WindowDoor` directly owned by a Wall. Generic layer mutation is exposed for
declared edit types, while Wall has a separate tier-aware `set_wall_layer`
route. Slab/MultiSlab layer writes remain subject to explicit ownership
checks. These code declarations describe available routes and guards, not
native acceptance. The retained evidence is scoped as follows.

| Operation / declared owner | Retained native evidence | Missing evidence or scope limit |
| --- | --- | --- |
| Layer, Column | 0.30.0 no-op is specifically reported for Column/W1. | Exact refs and raw preview/revalidation showing zero setters and no Apply are absent. No changed Column layer write/Undo trial is identified. |
| Layer, Wall | A 20 cm Wall was reported moved to `Ogólne03` (ID 3702) in 0.27.0; no raw request or restoration result is retained. W1 generic read/write report does not identify this Wall. | Exact identity, fresh owner-bound readback/Undo and restoration are absent; no proof for tier-aware `set_wall_layer` route. |
| Layer, “Beam” report (type unknown) | 0.27.0 reports two elements described generically as “belki” moved to W1 with readback; their adapter type is not recorded. | Do not attribute this to `Beam_TypeUUID` without exact type evidence. Exact refs, owner, Undo and restoration are absent. |
| Layer, SkeletonBeam | No SkeletonBeam-specific W1/layer trial is identified. | Pair-specific trial, readback, Undo and restoration are missing; the generic “belki” report does not prove this family. |
| Layer, Slab | No Slab-specific layer trial is identified. | For a standalone root, fixture availability is not established and pair-specific trial/Undo are missing. A parented Slab child is blocked by the current owner contract for layer writes. |
| Layer, MultiSlab | No MultiSlab-specific layer trial is identified. | Aggregate layer writes are blocked by the current owner contract; no trial or group behavior is established. |
| Layer, WindowDoor | The generic edit family list declares `WindowDoor_TypeUUID`; no opening-specific layer trial is identified. | Fixture availability, exact target, readback and Undo/restoration are not established. |
| Layer, family not identified | Owner reports W1 reads/writes and one UI Undo per changed element. No raw requests, exact targets or family bindings are retained. | Keep separate from every family-specific row; do not treat it as family-specific PASS. Pair-level payload and restoration reads are missing. |
| Delete, Column root | Three W1 Columns were deleted with fresh absence readback; owner reported one UI Undo restored all three. This is the accepted grouped Column scope. | Exact refs and fresh post-Undo restoration read are absent; do not extend to another family/subtree. |
| Delete, Wall root/subtree | 0.27.0 reports deletion of one 240 mm Wall and a fresh native read confirming the Wall and five descendants absent. | Undo/restoration, exact dependency inventory and neighbor preservation were not reported. This does not establish a trial of `WindowDoor` alone. |
| Delete, Beam root | No Beam-root delete trial is identified. The generic “belki” W1 report does not establish a native Beam adapter or a disposable delete target. | Fixture availability is not established; exact refs, absence readback, neighbor preservation and Undo/restoration are missing. |
| Delete, SkeletonBeam root | Two SkeletonBeams were present in the 2026-10-27 comparison, but no delete trial is identified. | A disposable test fixture is not established; exact refs, absence readback, neighbor preservation and Undo/restoration are missing. |
| Delete, Slab root | No Slab-root delete trial is identified; the observed Slab was a MultiSlab child. | Standalone Slab fixture availability is not established by the bounded comparison; no root deletion, absence readback or Undo/restoration evidence. |
| Delete, parented Slab child | This combination is blocked by the owner contract: deletion permits a top-level component root or a directly Wall-owned `WindowDoor`, not a child Slab. | Do not classify the absent child trial as a missing fixture or request an owner trial for this forbidden target shape. |
| Delete, MultiSlab root | A MultiSlab was present in the 2026-10-27 comparison, but no delete trial is identified. | A disposable test fixture is not established; no subtree absence, neighbor-preservation or Undo/restoration evidence. |
| Delete, WindowDoor root/opening | Code permits a top-level `WindowDoor` root or a directly Wall-owned opening with complete subtree evidence; no separate opening deletion result is identified. | Fixture availability is not established; no exact opening refs, absence readback or Undo/restoration evidence. |

Evidence sources: [0.27.0 observations](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md), [0.29.0 Column deletion](test-results/evidence/allplan-test-log-0.29.0-2026-10-23.md), and [0.30.0 typed trials](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md). The current declaration is in [ModelEditPreview](../src/allplan_mcp/model_edit_models.py) and [model_delete](../python_host/PythonPartsScripts/PythonHost/model_delete.py).

The evidence and closure criteria for the missing pairs remain in [development
plan priorities 4–5](office-editing-development-plan.pl.md#dowody-potrzebne-do-zamknięcia-punktów-15).

## Evidence for unresolved cases

- **0.37.0 native Wall material and journal recovery (2026-10-26):** the
  supplied conversation log reports a 240 mm Wall in drawing 101 with material
  `Beton`; Apply to `Beton1` stopped as `unknown` because the control read was
  unavailable. Recovery under the same execution also could not read it, while
  an independent `wall_sample` returned `Beton1` and the owner confirmed the UI
  value. The owner reports PASS for the intended value on the 240 mm Wall
  without openings. This
  supports that the requested material was observed after the write, but does
  not reconcile the execution journal. The later 200 mm Wall request, which
  the owner identifies as the Wall with a door/opening, remained blocked by
  `scan_limit_exceeded`, including after diagnostic trace archival and
  PythonHost restart; the log does not include a separate component identity
  and no setter was issued. A subsequent
  Column Apply was blocked by the retained recovery guard. Recovery of
  `87a45065d5e14e3a9ac8c54756e273a0` remained `stopped/unknown` with
  `representation_read_unavailable`; no setter was retried. Preserve this
  journal record and lock; trace archival did not archive or resolve it. The
  log records no 0.37.0 native material trial for Column, Beam or Slab. The
  owner's conversation log is [preserved byte-for-byte](test-results/evidence/0.37.0-2026-10-26/allplan-conversation-log.md),
  SHA-256 `2070900576de55caed20a2b37fc5f081eb584b75d10983b64e9cb71e31dfec49`.

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
- **0.36.0 material observation (2026-10-26):** The owner reported no PythonHost
  interruption or Allplan crash. The user reported project attribute `Materiał`
  Apply/readback success for Wall, Column and Beam, and failure for Slab. The
  same user says native Beam material succeeded, but the supplied conversation
  log records native `Column` Apply/readback as completed, `native_material_type_unsupported`
  for SkeletonBeam and MultiSlab, and a Wall preview timeout at 5 seconds. The
  Beam native result is contradictory and unresolved; do not claim Beam native
  PASS. Do not repeat the completed native Column Apply/readback. The raw log
  is [preserved unchanged](test-results/evidence/conversation-log-0.36.0-2026-10-26.md),
  SHA-256 `6146fa08928b650f74d0f08fdadc00b6e8bf0b514c92484714a18d08c3aa9910`.
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
- **Slab/MultiSlab, historical context:** the 0.36.0 user report says the project `Materiał`
  attribute write did not work for Slab. Candidate 0.37.0 adds explicit
  `target.property_owner="selected_element"`, exact ref binding, complete
  lineage/children checks and parent/child overlap blocking. This is not native
  Allplan acceptance; ownerless old requests remain blocked for a child or
  aggregate, and no automatic redirect is allowed. The
  [0.27.0 log](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md)
  retains the earlier parent-lineage conflict; the
  [latest raw attribute probe](test-results/evidence/0.31.0-2026-10-24/slab-multislab-readonly-evidence.json)
  retains view differences, incomplete Slab evidence and unestablished field
  ownership. The 0.36.0 native log reports MultiSlab as unsupported. Candidate
  0.37.0 accepts only runtime `SlabElement` and root `SlabProperties.Material`;
  it does not redirect or substitute a tier owner. The latest 0.39.0 report
  above now records attribute success on both representations and failed
  native material persistence; ownership and complete native acceptance remain open.
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

