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

## Current candidate: 0.26.0 — in progress

Candidate 0.26.0 documentation and implementation work is in progress on
`develop/m4`; do not report CI or package acceptance until the candidate's
final CI artifact and checks are recorded. The owner trial for it is limited to
the [0.26.0 short trial](m4-single-drawing-0.26.0.pl.md): paged read-only
`drawing_identity` for drawing 101, a read-only current-layer-0 check if
available, missing W1 no-op/Undo, and changed deletion/material diagnostics
only when they provide new evidence. Do not repeat the scoped 0.25.0 deletion,
identity reads, or 200 mm Wall W1 readback. The concise per-priority boundaries
are in the [coverage matrix](m4-single-drawing-coverage-0.24.0.md).

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
