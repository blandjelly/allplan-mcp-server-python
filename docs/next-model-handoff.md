# Current M4 handoff

Current development branch: **`develop/m4`**. Start M4 topic branches there
and target pull requests to `develop/m4`. Main remains separate. Read
[AGENTS.md](../AGENTS.md) and the [testing policy](testing-policy.md) before
implementation. The policy is the source of truth for automated checks and
package builds.

## Retained candidate: 0.25.0

Candidate 0.25.0 extends `model_edit` with exact component deletion and an
experimental native-material setter for a standalone single-tier Wall.
Deletion binds the full owned subtree (maximum 256 including the target), calls
the native delete API on that target once, and requires a fresh complete scan
to confirm it and every descendant are absent; partial or unknown results are
recovered by the original execution ID without retrying. A
`WindowDoor_TypeUUID` opening is independently targetable only with exact
lineage `[opening, Wall root]` and no macro ancestors; its parent Wall must
remain. A Slab child stays blocked unless covered by a selected full
MultiSlab root.
The Wall route binds the material and preservation evidence for tier geometry,
hierarchy, tier/common values, axis and plane/surface representations. It
accepts only a bounded exact string at tier 1, without catalog lookup or an
existence claim. Neither operation has native Allplan acceptance yet.

The [0.25.0 trial](m4-single-drawing-0.25.0.pl.md) covers only typed deletion,
the experimental material path, and the unobserved W1 no-op/Undo scope. The
[API evidence note](m4-editing-api-0.25.0.md) records the documented SDK surfaces
and remaining date/vector blockers. Native selection remains unsupported;
date/vector/object attribute writes remain blocked. Final source
`574ef06ca97fced289b414faa3ba91b78b5b91ef` passed
[CI 39660850663](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39660850663):
557 tests on each Windows/Ubuntu Python 3.12 job, then one package build.
166 unique focused unit/HTTP checks passed across affected iteration runs.
The exact original CI ZIP passed payload/checksum, registration, frozen
sync/import, upgrade from 0.24.0 and restore; 42 bridge hashes and active/archive
journal/trace/log markers were preserved. An initial CI capability-metadata
failure was corrected before this final run; it produced no package.
[0.25.0 delivery and evidence](../evaluation-packages/0.25.0/README.md).
A read-only identity-scan adjustment
now limits `model_identity` fields to `file_state` and required type identity,
so differing `layer_id` or display names between wrappers no longer block a
structural identity result. That does not prove the cause of, or resolve, the
owner's 0.24.0 exact-view probe failure; a same-build native identity read is
still needed. This candidate does not close priorities 1–5 or the single-drawing
native acceptance gate.

The owner confirms that the [22 October conversation log](test-results/evidence/log_rozmowy-2026-10-22.md)
matches Allplan behavior. Preserve its [scoped 0.25.0 observation](test-results/m4-owner-observation-0.25.0-2026-10-22.md):
read-only `component_identity` PASS for one Wall and one MultiSlab query result;
one remaining Wall and its children were reported deleted after confirmation
and a fresh complete scan; one 200 mm Wall was moved from layer 3702 to W1
(65535) with readback. The log does not contain an exact installed manifest,
raw MCP responses, or Allplan build identifier, so do not bind these outcomes
to the exact 0.25.0 ZIP or claim full typed-delete acceptance. Door opening
deletion and deletion of its owning Wall were blocked; native material and
hatch 129 were blocked; moving all Walls to W1 was blocked by the 240 mm Wall's
`repair_conflict`. W1 no-op/Undo remains unobserved. These outcomes do not close
priorities 1–5 or the single-drawing acceptance gate.

## Retained candidate: 0.26.0 — CI and exact ZIP verification passed

Source `48e64b1a06bef005c26a143860d9257038cccde3` on PR #24 targeting
`develop/m4`, merged as `40f71b737616b9dde4b3f6804b774c0e5f76ac40`, passed
[CI run 39822585188](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39822585188):
580 tests on each Windows/Ubuntu Python 3.12 job and the package job. The
original CI artifact (ID 12445232990, digest
`4e2617cf34cf2269663942ac193a526eac3e0fcb2743e0da78712333ec4bfbfd`) could not
be transferred because the execution proxy returned CONNECT 403. Per testing
policy, one local fallback build was produced from a clean detached worktree at
the exact source commit with `source_modified=false`. The delivered ZIP SHA-256
is `4c0dd3ed9c9c038320fe08032a26ef61d8be7a57ed4169d5cdd3bc5952b292a9`. The
exact ZIP passed checksum/payload, exact registration, frozen sync/import,
`drawing_identity` schema, upgrade from 0.25.0 and restore, 42 bridge hashes,
and preservation of active/archive journal, trace and log markers. The CI
artifact itself was not delivered; the locally built fallback is the verified
package. See [CI record](../evaluation-packages/0.26.0/source-ci.json),
[focused checks](../evaluation-packages/0.26.0/focused-verification.json),
[build provenance](../evaluation-packages/0.26.0/build.log) and
[artifact hashes](../evaluation-packages/0.26.0/artifact-hashes.json),
[exact ZIP verification](../evaluation-packages/0.26.0/package-verification.json)
and [verification log](../evaluation-packages/0.26.0/package-verification.log).

The [0.26.0 short trial](m4-single-drawing-0.26.0.pl.md) remains limited to
paged read-only `drawing_identity` for drawing 101, read-only layer-0
observation, missing W1 no-op/Undo, and one fresh read-only diagnostic preview
for an exact blocked target. Focused tests cover layer ID 0 in Wall layer
reading and reviewed W1 plan/Apply from the old value 0; this does not supply
native Undo or prove the historical `repair_conflict` cause. Material/delete
changes improve diagnostics only: native material remains blocked, and prior
0.25.0 deletion is
a limited PASS that must not be repeated. Priority 1's bounded journal-cleanup
PASS remains accepted; priority 2's identity inventory does not establish field
ownership; priority 3 lacks native Undo; priority 4 selection remains
unsupported and material remains blocked; priority 5 adds no date/vector codec.
At package delivery, no native 0.26.0 trial had been recorded. The later
[bounded owner observation](test-results/m4-owner-observation-0.26.0-2026-10-22.md)
adds partial native evidence; full native acceptance remains incomplete.
Priorities 1–5 and the single-drawing native acceptance gate remain open. See
the [coverage matrix](m4-single-drawing-coverage-0.24.0.md).

The [scoped 0.26.0 owner observation](test-results/m4-owner-observation-0.26.0-2026-10-22.md)
preserves the supplied [conversation log](test-results/evidence/log_rozmowy-0.26.0-2026-10-22.md).
It reports 26/26 enumerated drawing identities, with 7 `observed` and 19
`not_checked`; two readbacks on one Column after confirmed layer changes
3700 → W1 (65535) → 0; and one 200 mm Wall highlight submission. The log lacks
raw MCP responses, installed manifest, exact ZIP and Allplan build ID. The
highlight response requested visual observation; the log does not record its
result or a native selected-element count. Material was not changed. A prior
assistant reply attributed the blocked preview to a `Door_TypeUUID` child, but
the later response records empty `blocked` arrays and no diagnostic fields, so
that child is not established as the actual cause. No W1 no-op/Undo or delete
was performed. This does not close priorities 1–5 or full native 0.26.0
acceptance.

## Current delivery: 0.27.0 — CI and exact ZIP verification passed

Status updated 23 October 2026 (Europe/Warsaw). Final source
`e62a50c9c6c6b51978b6f1a55f9d9978eee5b1c3` on PR #25 targeting `develop/m4`,
merged as `23b8b2591d7be0721fe7a5651379408e7a2f5e76`,
passed [full CI run 39841530841](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39841530841):
593 tests on each Windows and Ubuntu Python 3.12 job, plus the package job.
The historical run remains dated 22 October. Exact ZIP verification passed
on its first run for the single fallback ZIP built from clean detached source
(`source_modified=false`). The original CI artifact was not delivered: its
reusable file reference could not be transferred to the executor. The verified
ZIP has SHA-256
`eab80cd2c907e7fd90ba733f4f8d1335f097986b938c74ccdda6bf3382cdaa30` and 183
payload files. Checksum/payload, registration, frozen sync/import,
`drawing_identity` schema, upgrade from 0.26.0, restore, 42 bridge hashes and
journal/trace/log plus archive markers passed. See [package verification](../evaluation-packages/0.27.0/package-verification.json),
[verification log](../evaluation-packages/0.27.0/package-verification.log),
[build provenance](../evaluation-packages/0.27.0/build.log) and the
[evaluation package record](../evaluation-packages/0.27.0/README.md).

This source follows the superseded initial CI attempt for
`bab1c02eb73cf4a0139116b2c6ab422a3ec23af3`, retained in
[initial-ci.json](../evaluation-packages/0.27.0/initial-ci.json): run
39840589327 failed because the package version constant was still 0.26.0. The
corrected final source passed the full matrix. The [focused checks](../evaluation-packages/0.27.0/focused-verification.json)
cover 143 unique affected/dependent tests across iterations; they are separate
from the full CI result. No native Allplan 0.27.0 trial has been run.

## 0.27.0 candidate scope

The current source changes target three guarded behaviors. `model_edit` uses
the shared bounded attribute-name resolver for every bind. The read-only
`attribute_name` probe keeps exact lookup first and calls the fallback only on
`ValueError`/`TypeError` lookup miss. It checks supplied, trimmed NFC,
first-character uppercase, all-uppercase and all-lowercase forms; it collects
successful IDs, verifies the actual name/ID roundtrip and accepts case-fold
equivalence only when all successful variants identify one project ID.
Ambiguous IDs fail closed. There is no fuzzy search or catalog enumeration;
this is intended to resolve lowercase `mcp_qa_mark` to the canonical project
name and ID.

Native Wall material preservation now fails closed unless the root has exactly
one `WallTier_TypeUUID` child with lineage `[tier, Wall root]`, no children,
and no other children. A `WindowDoor_TypeUUID` child reports
`wall_material_openings_unsupported`; every other child, including unknown
Door/Window/Macro adapters, reports `wall_material_child_type_unsupported`.
Bounded native read errors retain stable stage/error-type diagnostics. Preview
separates an observed old material string from preservation eligibility:
blocked plans can report the old value as `observed` alongside
`native_material_preservation_unavailable` and its observation diagnostic.
`criteria.operation_eligibility_failures` currently reports Wall
native-material preservation blockers. `criteria.required_field_failures`
contains only unreadable required destination fields; predicate failures stay
in `report.criterion_failures`, and the destination-field list may be empty
for a blocked material operation. A post-write observation still
requires preservation evidence; reading the material alone cannot authorize
or validate a write. These changes do not add a material setter case, weaken
guards, or provide native acceptance.

Full CI and exact ZIP verification passed. There is no new native observation
for 0.27.0. The [short trial](m4-single-drawing-0.27.0.pl.md)
covers only the name-variant resolution, material diagnostics and remaining
unobserved native scope; it must not repeat accepted writes or deletion.

### Priority checklist (1–5)

1. **Journal cleanup — bounded 0.23.0 PASS accepted.** The archival preview and
   confirmations remain accepted and must not be repeated. Snapshot/replay
   after native restart is still not visible in owner evidence. Next evidence:
   only a previously unobserved restart/replay scope if specifically planned;
   preserve unresolved/corrupt/oversized records.
2. **Slab/MultiSlab identity — inventory exists, field ownership unresolved.**
   0.26.0 pages drawing identity and preserves model/view UUIDs and lineage;
   it does not reconcile the original Slab view probe with the MultiSlab child
   or establish property ownership. 0.27.0 changes do not address this. Next
   evidence: read-only identity probes of the exact unresolved adapters in one
   native build, recording model/view UUID, parent/child and represented type.
3. **Single drawing layer — layer 0 fixed in runtime, native Undo missing.**
   0.26.0 log records a Column readback at ID 0 after a confirmed write, but no
   no-op or Undo; this does not substitute for the separate missing W1
   no-op/Undo trial. Next evidence: use only the explicitly designated,
   separate test targets from the trial, recording zero setters for no-op and
   one UI Undo plus fresh readback. Do not repeat prior writes/readbacks.
4. **Selection, delete and native material — separate statuses.** Selection
   remains unsupported. One 0.25.0 subtree deletion PASS is accepted and must
   not be repeated; broader typed-delete/Undo evidence remains absent. 0.27.0
   tightens native-material eligibility and diagnostics, but does not enable
   writes. Next evidence: one read-only preview per exact new observation,
   capturing complete raw response fields for operation eligibility; any
   future material write requires a narrow native trial and fresh
   preservation-bound readback under the existing plan acknowledgement. Do not
   repeat the 0.26.0 material observation or accepted deletion.
5. **Families and value codecs — native coverage partial.** Scalar/Enum routes
   remain bounded to their existing adapters; date/vector/object values remain
   blocked. 0.27.0 name variants address lookup only and create no codecs.
   Next evidence: a per-family native matrix for the exact adapter, field
   owner, value roundtrip and Undo, plus a separate exact setter/readback
   design before any date/vector implementation. Do not infer support from
   SDK symbols or repeat previously accepted attribute writes.

## Retained 0.24.0 evidence

0.24.0 adds the read-only `model_property_probe phase=component_identity`
for one exact drawing/model/view adapter: bounded parents, direct children,
and represented native Python type. `model_query fields=[component_ownership]`
is an opt-in structural read. Neither route derives identity from bounds or
establishes native property ownership.

Typed edits now bind slab ownership evidence. A Slab with a parent and every
MultiSlab aggregate are blocked pending an explicit property-owner adapter.
A standalone Slab rechecks its bound hierarchy at preflight, setter boundary,
fresh readback and recovery; drift leaves a conflict/unknown outcome without
retrying a setter. Exact-ID historical replay remains setter-free. Existing
accepted Slab attribute outcomes are preserved as historical observations.

201 focused affected/dependent tests passed for identity/probe/HTTP boundaries,
slab owner conflicts and
W1 targets/exclusions/fresh readback/replay/no-op across supported adapters.
Native selection returns explicit unsupported with no highlight fallback;
the 0.24.0 native-material write path and date/vector/object codecs were not
available in that release.
[Coverage and API evidence](m4-single-drawing-coverage-0.24.0.md) and the
[short next trial](m4-single-drawing-0.24.0.pl.md) separate those gaps.

Final source `8e7e16040a80236bac2eca3689a42a75b83659a1` passed
[CI 39509201386](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39509201386):
529 tests per Windows/Ubuntu Python 3.12 job, followed by one build. The exact
original CI ZIP passed payload/checksum, registration, frozen sync/import,
upgrade from 0.23.0 and restore; all 40 bridge hashes and active/archive history
markers were preserved. [0.24.0 delivery and evidence](../evaluation-packages/0.24.0/README.md).

The initial CI passed Ubuntu but failed three Windows workflow checks, including
two read-budget expirations. Functional model-edit tests now use an injected
clock; a new explicit expiry test still checks the production limit. 57
dependent tests passed after that test-only fix; 202 unique focused tests
were covered across both passes. Production budgets and durable trace writes
are unchanged. No native 0.24.0 observation is available in this environment.

## Retained 0.23.0 and prior owner evidence

The owner confirms the latest reported Allplan results: two queried Slab
attributes, `Priorytet` on two results, and ordered `MCP_QA_MARK` values on six
Columns. The [scoped observation](test-results/m4-agent-observation-2026-10-20.md)
retains the supplied log. Earlier replies and the exact installed manifest are
absent, so do not claim an exact artifact/build for those operations. Slab and
MultiSlab equal bounds do not establish common ownership or two distinct
physical targets. Resolve model/view identity and ownership before another
write to those results.

The owner also encountered a full journal and cleared it manually. The supplied
log omits the error and the measured state; do not infer whether the cause was
the 1 MiB active diagnostic trace, 128 active execution records, or the 1 MiB
per-record limit. Candidate 0.23.0 adds preview and confirmed archival for the
trace or resolved execution records. Unknown/running, corrupt, and oversized
records remain protected and blocking. Cleanup does not access the model or
retry a setter. The owner reports **PASS** for the 0.23.0 preview and confirmed
archival of both scopes: 614,396 trace bytes and 32 resolved execution records
totaling 739,786 bytes. The screenshot reports preserved IDs/replay protection,
no deletion and no model change. Exact installed manifest/build, native replay,
restart and stale-snapshot observations were not supplied. Preserve the
[bounded PASS](test-results/m4-journal-cleanup-0.23.0-owner-pass-2026-10-21.md);
do not repeat this accepted maintenance trial.

Source `8c71de958c47ab4cb418a62fbd2d55ce76cbc4db` passed CI 39336895867:
505 tests per Windows/Ubuntu Python 3.12 job, then one package job. The original
CI ZIP was verified and passed checksum/payload, registration, frozen sync and
import, upgrade from 0.22.1, and restore. The exact package check confirmed 38
bridge hashes and preserved journal, trace/log, and archive markers. Focused
checks cover 140 affected/dependent cases, including maintenance tests through
native fakes and MCP HTTP. The delivery commit adds docs/artifacts only.
[0.23.0 package evidence](../evaluation-packages/0.23.0/README.md).

## Next work

1. Preserve the 0.24.0 failed exact-view Slab probe and MultiSlab child UUID
   mismatch in the [0.24.0 owner record](test-results/m4-owner-observation-0.24.0-2026-10-21.md).
   The 22 October log adds one read-only identity PASS each for a Wall root and
   a MultiSlab query result. This does not establish the original Slab result's
   identity, reconcile its view UUID with the MultiSlab child, or establish
   property ownership. Continue read-only identity work on the exact unresolved
   targets before planning writes; preserve journal state and archives.
2. Complete only the unobserved W1 no-op/Undo scope on the explicit, separate
   test targets defined in the trial. The 0.25.0 log adds a 200 mm Wall W1
   readback (3702 → 65535), but no no-op or Undo; do not repeat that readback or
   treat a Wall test as the missing Column no-op/Undo result.
3. The owner performed a 0.25.0 native trial. Preserve its limited outcomes in
   the [owner observation](test-results/m4-owner-observation-0.25.0-2026-10-22.md):
   one remaining Wall subtree was reported removed after confirmation and a
   fresh complete scan, while opening deletion and deleting its owning Wall
   were blocked. Native material/hatch changes and bulk move to W1 were blocked.
   Exact package/build attribution and raw MCP evidence are absent; do not claim
   exact typed-delete acceptance, native material acceptance, no-op/Undo, or
   full 0.25.0 acceptance. Do not repeat the accepted single-Wall deletion or
   200 mm Wall W1 readback. Native selection remains unsupported.
4. Continue the [development plan](office-editing-development-plan.pl.md) for
   unresolved Slab/MultiSlab identity, selection, unaccepted families/types,
   then multi-file and whole-project work. Priorities 1–5 are not closed by
   candidate implementation or SDK documentation. Do not repeat accepted
   Column/Slab attribute outcomes or historical query/readback observations.
   The [bounded 0.24.0 observation](test-results/m4-owner-observation-0.24.0-2026-10-21.md)
   and [bounded 0.25.0 observation](test-results/m4-owner-observation-0.25.0-2026-10-22.md)
   record their separate conversation-log scopes. Priorities 1–5 remain open
   where acceptance criteria are unmet.

M4 remains partially accepted. The latest results do not establish native
selection, native material updates, all six families, multi-file execution, or
whole-project access. Preserve target binding, write revalidation, journaling,
unknown-result blocking, replay and Undo safeguards.

For earlier bounded native outcomes and historical evidence, use
[validation status](validation-status.md) and the retained owner observations in
`test-results/`. Do not use superseded owner-test instructions or commands.
