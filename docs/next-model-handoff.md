# Current M4 handoff

Current development branch: **`develop/m4`**. Start M4 topic branches there
and target pull requests to `develop/m4`. Main remains separate. Read
[AGENTS.md](../AGENTS.md) and the [testing policy](testing-policy.md) before
implementation. The policy is the source of truth for automated checks and
package builds.

## Current candidate: 0.25.0

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
date/vector/object attribute writes remain blocked. Candidate CI and package
evidence are pending. The candidate contracts remain regression-testable, but
no passing candidate CI is claimed here. A read-only identity-scan adjustment
now limits `model_identity` fields to `file_state` and required type identity,
so differing `layer_id` or display names between wrappers no longer block a
structural identity result. That does not prove the cause of, or resolve, the
owner's 0.24.0 exact-view probe failure; a same-build native identity read is
still needed. This candidate does not close priorities 1–5 or the single-drawing
native acceptance gate.

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

1. The 0.24.0 owner log reports a failed exact-view identity probe for the
   Slab result and a child view UUID mismatch under MultiSlab. Preserve this
   bounded observation in the [owner record](test-results/m4-owner-observation-0.24.0-2026-10-21.md);
   resolve Slab/MultiSlab target identity read-only before planning another
   write. Preserve original journal state and archives.
2. Complete only the unobserved W1 no-op/Undo scope. The 0.24.0 log reports a
   W1 readback of layer ID 65535; it does not report no-op or Undo. Do not
   repeat the readback or accepted attribute outcomes.
3. Run only the [0.25.0 trial](m4-single-drawing-0.25.0.pl.md): exact typed
   deletion, the experimental one-tier Wall material route, and the unobserved
   W1 no-op/Undo scope. The earlier conversation log records deletion through
   UI only and W1 readback only; do not repeat that deletion, accepted
   readbacks, or attribute outcomes. Native selection remains unsupported.
   Preserve each native result as its own scoped observation after the owner
   supplies the exact package/build and results.
4. Continue the [development plan](office-editing-development-plan.pl.md) for
   unresolved Slab/MultiSlab identity, selection, unaccepted families/types,
   then multi-file and whole-project work. Priorities 1–5 are not closed by
   candidate implementation or SDK documentation. Do not repeat accepted
   Column/Slab attribute outcomes or historical query/readback observations.
   The [bounded owner observation](test-results/m4-owner-observation-0.24.0-2026-10-21.md)
   records the exact scope of the 0.24.0 conversation log.

M4 remains partially accepted. The latest results do not establish native
selection, native material updates, all six families, multi-file execution, or
whole-project access. Preserve target binding, write revalidation, journaling,
unknown-result blocking, replay and Undo safeguards.

For earlier bounded native outcomes and historical evidence, use
[validation status](validation-status.md) and the retained owner observations in
`test-results/`. Do not use superseded owner-test instructions or commands.
