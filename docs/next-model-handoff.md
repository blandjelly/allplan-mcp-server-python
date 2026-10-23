# Current M4 handoff

Current development branch: **`develop/m4`**. Start M4 topic branches there
and target pull requests to `develop/m4`. Main remains separate. Read
[AGENTS.md](../AGENTS.md) and the [testing policy](testing-policy.md) before
implementation. The policy is the source of truth for automated checks and
package builds.

## Latest completed candidate: 0.30.0 — full CI and exact ZIP verification passed

Source commit
[`9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6`](https://github.com/blandjelly/allplan-mcp-server-python/commit/9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6)
is on `feat/m4-combined-evidence-0.30.0`; [PR #28](https://github.com/blandjelly/allplan-mcp-server-python/pull/28)
targets `develop/m4`. **142 unique focused checks passed** ([record](../evaluation-packages/0.30.0/focused-verification.json)). Full
[CI run 39993048110](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39993048110)
passed 622 tests on Windows and 622 on Ubuntu, Python 3.12, plus the package
job. The original CI artifact was not delivered: the single normal-proxy
transfer failed with `URLError` before an HTTP response. One fallback build was
produced from a clean detached worktree at the exact source
(`source_modified=false`). Its exact ZIP passed verification on the first
attempt: 196 payload files and 43 bridge hashes; checksum/payload, registration,
frozen sync/import, both property-probe schemas, safety limits, upgrade/restore
to 0.29.0 and journal/trace/log marker preservation passed. SHA-256:
`78b7b24c98749ebbd28814f84d70a2fc9cbeab80b477b9fd1585e5c10e63af8e`. The
owner has since run the planned 0.30.0 Allplan trials; scoped outcomes follow
below. See the [0.30.0 candidate record](../evaluation-packages/0.30.0/README.md),
[verified ZIP](../evaluation-packages/0.30.0/allplan-mcp-0.30.0-windows-evaluation.zip),
[ZIP checksum](../evaluation-packages/0.30.0/allplan-mcp-0.30.0-windows-evaluation.zip.sha256),
[verification result](../evaluation-packages/0.30.0/package-verification.json),
[verification log](../evaluation-packages/0.30.0/package-verification.log),
[artifact hashes](../evaluation-packages/0.30.0/artifact-hashes.json),
[CI provenance](../evaluation-packages/0.30.0/source-ci.json) and
[fallback build log](../evaluation-packages/0.30.0/build.log).

This is a deliberately partial candidate for one combined session across
priorities 1–5. The session plan is not evidence of completed acceptance.

The current implementation adds read-only
`model_property_probe phase=attribute_evidence` for one exact foreground
drawing/model/view, 1–16 distinct observed attribute IDs and up to 16 exact
view wrappers, optionally including the immediate parent. It separates
ancestry, children, `ReadAll`, `ReadAllAndComputable`, native representation
and runtime type evidence. `evidence_complete` requires consensus and all
requested observations; partial evidence retains available data with
`state=not_checked`. Actual SDK member binding is labeled matched, ambiguous,
or unresolved. The probe does not establish field owner or setter payload.
Complete no-op previews/revalidations report fresh `no_op_evidence` and
`setter_calls_started=0`; no-op plans have no Apply route.

Owner-reported 0.30.0 trial status is PASS for trials 1, 2, 3 and 5, and
FAIL for trial 4's native-material write path. Both Wall previews were
blocked before Apply: the first requested `Żelbet` and reported
`native_material_preservation_unavailable` → `wall_material_tier_hierarchy_unsupported`; the
second, a Wall with opening model UUID
`545bb0a2-a054-4c91-ac6c-ec552d5b0c18`, reported
`component_child_owner_mismatch`. Both reported zero changes, zero setters,
no Apply and unchanged material. The detailed supplied log covers trial 5 only:
four scalar writes (text, integer and real on a Column;
text on a Wall) each passed fresh typed readback and one owner-confirmed UI
Undo/restoration read. Enum, Boolean, Beam, standalone Slab and opening cases
were not written because the value, fixture or read path was unavailable.
Trials 1–3 have no detailed raw log in the supplied evidence. Trial 4 has the
owner's blocker symptoms recorded below, but no raw MCP responses. Reported
statuses are retained without expanding their acceptance scope. See the
[scoped 0.30.0 owner observation](test-results/m4-owner-observation-0.30.0-2026-10-23.md),
[trial 5 log](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md)
and [persisted Apply requests](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trial-apply-requests.jsonl).
Slab/MultiSlab field ownership, date/vector setter payloads and native
selection set/clear/readback remain unresolved and blocked. The
[single-session 0.30.0 trial plan](m4-single-drawing-0.30.0.pl.md) records the
intended scope across all five priorities; the new material FAIL and the
limited scalar PASS do not close priorities 1–5. See the
[0.30.0 API evidence note](m4-editing-api-0.30.0.md).

## Candidate under evaluation: 0.31.0 — Wall material parent identity

Source commit
[`0f99863b7c11143d9f14ca12a1027aad5b009195`](https://github.com/blandjelly/allplan-mcp-server-python/commit/0f99863b7c11143d9f14ca12a1027aad5b009195)
is on `fix/m4-material-owner-0.31.0`; [PR #29](https://github.com/blandjelly/allplan-mcp-server-python/pull/29)
targets `develop/m4`. This candidate changes the guarded Wall material preservation
snapshot: it compares the tier's parent edge using `same_model_identity`
(drawing, model UUID and type) and records the actual tier wrapper in
`tier_hierarchy`. The selected target remains bound to its exact view UUID.
Standalone-root, supported hierarchy/type, no-opening, valid geometry and
single-tier guards remain in force.

Focused tests reproduce and fix the same-model parent-wrapper defect associated
with the first 0.30.0 diagnostic. The exact cause of that Allplan result is not
proven without raw lineage/children evidence; native retest is pending. The
second Wall-with-opening result `component_child_owner_mismatch` is unresolved
and not covered by this fix. **87 unique focused checks passed**: 86 affected/dependent
checks across `wall_material_edit`, `wall_material_http`, `model_edit`,
`native_model_edit` and `edit_ownership`, plus one package version/lock check.
The 25 overlapping checks were not counted twice. See the [focused record](../evaluation-packages/0.31.0/focused-verification.json).
Run 40012042481 passed 625 Ubuntu Python 3.12.15 tests, 625 Windows Python
3.12.10 tests, and the package job. The original CI artifact 12527730616 could
not be retrieved, so one fallback ZIP was built from the clean detached exact
source (`source_modified=false`). It passed exact verification: 201 payload
files, 43 bridge hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`. See the
[verification record](../evaluation-packages/0.31.0/package-verification.json),
[log](../evaluation-packages/0.31.0/package-verification.log) and
[verified ZIP](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip),
[checksum](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip.sha256),
[build log](../evaluation-packages/0.31.0/build.log) and
[CI provenance](../evaluation-packages/0.31.0/source-ci.json).
Native trial remains pending. See the [0.31.0 API note](m4-editing-api-0.31.0.md)
and the [one-path native trial plan](m4-single-drawing-0.31.0.pl.md). Do not repeat the accepted
0.30.0 trials 1–3/5 or the 0.29.0 grouped Column delete/Undo.

## Retained candidate: 0.29.0 — CI and exact fallback ZIP verification passed

Source `df050afc71b9e0c2303594d6acbd3da463df3e89` is on
`fix/m4-batch-undo-0.29.0`; [PR #27](https://github.com/blandjelly/allplan-mcp-server-python/pull/27)
targets `develop/m4`. Full CI run
[39971389774](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39971389774)
passed 607 tests on each Windows and Ubuntu Python 3.12 job plus the package
job. The configuration-only run 39971367200 also passed. The candidate passed
99 unique affected/dependent focused checks.

CI artifact 12510270932 (digest
`3d509667620fb3a23fc7a1daf0c9303f68e2ede98cccac1c4ee08d7b00e615da`) could not
be transferred: the connector supplied a file-service reference and the one
normal-proxy transfer failed with `URLError` before an HTTP response. Per policy,
one fallback build was made from a clean detached checkout at the exact source
(`source_modified=false`). The 191-payload-file ZIP passed exact verification
once; SHA-256:
`0e4211b7a28f69a0b0400c13e2a90efeca9c230d34e42599adc6e8a2932d5aa5`.
Checksum/payload, registration, frozen sync/import, `drawing_identity` schema,
source safety limits, upgrade from and restore to 0.28.0, 42 bridge hashes, and
active/archive journal, trace and log markers passed. See the
[0.29.0 evaluation record](../evaluation-packages/0.29.0/README.md),
[CI record](../evaluation-packages/0.29.0/source-ci.json),
[package verification](../evaluation-packages/0.29.0/package-verification.json),
[build provenance](../evaluation-packages/0.29.0/build.log), and
[API evidence](m4-editing-api-0.29.0.md).

The candidate expands one reviewed delete template over the complete exact
target set, journals unknown outcomes for all targets before the native call,
and makes one `DeleteElements` call with the complete bound adapter list. Fresh
readback records per-target and descendant results; unknown/partial outcomes
recover under the same execution ID without repeating deletion.

The owner reports **PASS for all steps** of the 0.29.0 native trial: three
`Column_TypeUUID` elements on W1 in active drawing 101 were deleted, a fresh
scan reported all three Columns and their attribute containers absent, and one
UI Undo restored all three Columns. This meets the grouped-Undo repair goal for
the tested Column operation. The 0.28.0 result remains historical: one Undo
restored only one of three Columns. The 0.29.0 log lacks raw MCP responses,
target UUIDs and the installed ZIP manifest; the owner observed Undo while the
tool reported `undo: not_checked` and did not perform automatic post-Undo
readback. See the [scoped owner observation](test-results/m4-owner-observation-0.29.0-2026-10-23.md)
and [attached test log](test-results/evidence/allplan-test-log-0.29.0-2026-10-23.md).
Priorities 1–5 remain partially open beyond this completed Column grouped
delete/Undo scope. Next work should address priorities 1–5 together; the scope
of a new candidate is not yet set. See the
[coverage matrix](m4-single-drawing-coverage-0.24.0.md).

## Retained candidate: 0.28.0 — CI and exact ZIP verification passed

Source `b59ef15d9bfd4dfb42476b240e31b5b300268d2d` is on
`fix/m4-owner-views-0.28.0`; [PR #26](https://github.com/blandjelly/allplan-mcp-server-python/pull/26)
targets `develop/m4`. Full CI run
[39871551499](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39871551499)
passed 601 tests on both Windows and Ubuntu Python 3.12 jobs and the package
job. Focused verification passed 170 unique affected/dependent checks.

CI artifact 12466447229 (digest
`52f5a8533673c7347de2a9fe6d3e12f49a24ecc460585cf4acd8687f25922649`) was not
available to the executor: the connector supplied a file-service reference and
the one normal-proxy transfer failed with `URLError` before an HTTP status.
Per policy, one fallback build was made from a clean worktree at the exact
source (`source_modified=false`). The 186-payload-file ZIP passed exact
verification on its first attempt. SHA-256:
`74099ec341cdf8b2bc87def42487fafbbbcdb963ec6f4b8859a412f7b6d064ed`.
Checksum/payload, registration, frozen sync/import, `drawing_identity` schema,
source safety limits, upgrade from and restore to 0.27.0, 42 bridge hashes,
and active/archive journal, trace and log markers passed. See the
[0.28.0 evaluation record](../evaluation-packages/0.28.0/README.md),
[verification result](../evaluation-packages/0.28.0/package-verification.json),
[build provenance](../evaluation-packages/0.28.0/build.log),
[artifact hashes](../evaluation-packages/0.28.0/artifact-hashes.json), and
[API evidence](m4-editing-api-0.28.0.md).

The candidate matches component parent edges by drawing, model UUID and type
across alternate view wrappers, retains actual parent view UUIDs in bound
`child_parent_edges` / `descendant_parent_edges`, and keeps the selected
target's exact view UUID bound. It raises journal capacity to 512 active
records, retains the 1 MiB per-record cap, sets active trace to 8 MiB and trace
inspection to 32 MiB, and bounds archive inventory at 1 GiB / 1024 files.
Slab/MultiSlab write guards remain unchanged. The owner later reported PASS for
0.28.0 trial points 1, 2, 3 and 5, and FAIL for point 4: one UI Undo restored
only one of the three deleted Columns, with no further Undo available. The
conversation log lacks target UUIDs, raw MCP responses, exact package manifest
and Allplan build ID, so these are scoped owner observations, not exact-artifact
acceptance. The [observation](test-results/m4-owner-observation-0.28.0-2026-10-23.md)
and [verbatim log](test-results/evidence/allplan-chat-log-0.28.0-2026-10-23.md)
record the limits. Priorities 1–3 and 5 remain partially open; priority 4's
group-Undo expectation failed and native Column acceptance remains incomplete.
The next candidate trial is scoped to one plural native delete call and one UI
Undo for the exact three-Column group:
[0.29.0 short trial](m4-single-drawing-0.29.0.pl.md). See also the
[0.28.0 trial record](m4-single-drawing-0.28.0.pl.md) and
[coverage matrix](m4-single-drawing-coverage-0.24.0.md).

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

## Retained delivery: 0.27.0 — CI and exact ZIP verification passed

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
from the full CI result. The owner later reported limited PASS for the trial's
lowercase attribute-name resolver and native-material diagnostics, plus W1
read/write and one UI Undo step per changed element. The report has no raw MCP
responses, exact target identifiers, installed manifest or Allplan build ID;
there is no explicit W1 no-op/zero-setter observation. The supplied chat log
also reports one Wall subtree deletion and two Beam moves to W1, while deletion
of three W1 Columns was blocked by `component_child_owner_mismatch`. See the
[scoped owner observation](test-results/m4-owner-observation-0.27.0-2026-10-23.md)
and its [verbatim chat log](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md).
Slab/MultiSlab lineage remains unresolved. No outcome is bound to an exact ZIP
or Allplan build.

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

Full CI and exact ZIP verification passed. The scoped 0.27.0 observations are
summarized above; they do not accept the full native workflow. Do not repeat
the accepted lowercase lookup, material diagnostic, Wall subtree deletion or
Beam W1 writes.

### Priority checklist (1–5)

1. **Implemented and accepted:** bounded journal preview and confirmed archival
   scope from 0.23.0. Candidate 0.28.0 expands capacity to 512 active records,
   1 MiB per record, 8 MiB active trace, 32 MiB trace-inspection limit, and
   archive inventory of 1 GiB / 1024 files. Focused checks, full CI, and exact
   ZIP verification passed. The owner reports PASS for trial 1 in the 0.30.0
   session, planned for inspect/archive/restart/replay through a resolved
   execution ID without a new setter; detailed raw evidence for this stage was
   not supplied, so do not infer individual substep acceptance. Protect
   unresolved, corrupt and unverifiable records.
2. **Implemented:** identity inventory, fail-closed Slab write guards and the
   0.30.0 requested-ID `attribute_evidence` read. The owner reports PASS for
   trial 2's identity/evidence stage, but the supplied detailed log does not
   cover it. The 0.27.0 read-only report retains a Slab/MultiSlab parent-lineage
   conflict; identity and attribute observations do not establish field
   ownership. Keep unresolved writes blocked.
3. **Implemented:** layer 0 handling and reviewed W1 plan/Apply. **Limited
   native report:** W1 read/write and one UI Undo per changed element. The owner
   reports PASS for trial 3's W1 no-op stage; detailed raw evidence was not
   supplied. Treat the zero-setter result as owner-reported at trial level and
   do not repeat accepted writes, readbacks or Undo. No-op must not be applied.
4. **Implemented in the 0.28.0/0.29.0 candidates:** typed subtree delete binds
   parent edges by drawing/model/type identity; 0.29.0 sends the reviewed
   Column group in one plural delete call. Focused checks, full CI, and exact
   ZIP verification passed for the candidate. The owner reports PASS for all
   steps of the 0.29.0 Column trial: one UI Undo restored all three deleted
   Columns after the fresh absence scan. This meets the grouped-Undo repair
   goal for that tested operation. See the
   [0.29.0 observation](test-results/m4-owner-observation-0.29.0-2026-10-23.md).
   The 0.28.0 one-of-three Undo remains historical. Trial 4's 0.30.0 native material stage failed before Apply. The first
   preview reported `native_material_preservation_unavailable` then
   `wall_material_tier_hierarchy_unsupported`; the second Wall with an opening
   reported `component_child_owner_mismatch`. Both had zero changes, zero
   setters and no Apply. The 0.31.0 material snapshot now compares the tier
   parent by same-model identity and records the actual wrapper. Its three
   parent-wrapper regressions passed as part of the 86 affected/dependent
   focused checks: alternate same-model parent acceptance with bound edge and
   readback, parent-view drift conflict, and blocking different parent model,
   type or drawing. The version check, full CI and exact fallback ZIP
   verification passed for 0.31.0; its native material trial remains pending.
   Slab/MultiSlab write blockers stay in force.
   Native selection set/clear/readback remains unsupported.
5. **Implemented:** bounded scalar/Enum contracts, family/value inventory,
   attribute-name resolver and the 0.30.0 requested-ID evidence phase.
   **Limited native PASS:** trial 5's detailed log confirms Column text,
   integer and real writes and one Wall text write, each with fresh typed
   readback and one owner-confirmed UI Undo/restoration read. Enum was not
   written because its observed value was undefined; Boolean and standalone
   Slab fixtures were missing; Beam and opening reads were blocked. **Remaining:**
   full family/type coverage, owner-specific roundtrips, and date/vector/object
   codecs. Do not infer support from SDK symbols or repeat accepted attribute
   writes.

### Acceptance coverage after the 0.30.0 session

| Priority | Achieved in the reported session | Still required for full acceptance |
| --- | --- | --- |
| 1 — journal | Trial 1 reported PASS; earlier preview/archive scope and bounded limits remain accepted. | The trial's raw evidence was not supplied, so restart/replay substeps are not independently documented. Preserve unknown and unverifiable records. |
| 2 — field ownership | Trial 2 reported PASS for identity/evidence collection. | `ModifySlab.py` demonstrates `GetElement` → `SlabElement.Properties` → `SetProperties`/`ModifyElements` for a Slab element; it does not establish M4 project-attribute ownership or a `ChangeAttributes` contract for the conflicting Slab/MultiSlab lineage. Keep writes blocked. |
| 3 — layer/no-op | Trial 3 reported PASS for the W1 no-op stage. | No detailed raw log was supplied. The stage result does not expand accepted scope for W1 changes or grouped Undo. |
| 4 — typed delete, material and selection | 0.29.0 grouped Column delete/Undo remains accepted for its tested scope. Trial 4 material previews failed closed before Apply with zero changes/setters. | Repair and reverify the Wall material guard. Native UI selection has no established arbitrary replace/clear/readback setter; highlight is a separate operation. |
| 5 — attributes | Trial 5 confirms four scalar family/type pairs with fresh typed readback and Undo. | Complete family/type coverage and date/vector/object codecs. `AttributeDate` and `AttributeDoubleVec` constructors alone do not define an adapter `ChangeAttributes` payload or typed readback contract. |

These are scoped trial outcomes, not closure of the full priorities 1–5. The
[API evidence note](m4-editing-api-0.30.0.md) records the inspected examples and
remaining native/runtime prerequisites.

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

The 0.30.0 combined session has reported results for all five priorities.
Preserve its scoped outcomes in the
[owner observation](test-results/m4-owner-observation-0.30.0-2026-10-23.md).
The detailed trial 5 log and persisted requests are linked above. The only
current native follow-up is the
[0.31.0 Wall material trial](m4-single-drawing-0.31.0.pl.md). Do not repeat
accepted Column grouped delete/Undo from 0.29.0 or the four completed scalar
write/Undo pairs from trial 5. Record fixture gaps as `fixture_missing` and
unresolved API work as BLOCKED.

1. Preserve the unresolved Slab/MultiSlab lineage in the
   [0.27.0 owner observation](test-results/m4-owner-observation-0.27.0-2026-10-23.md).
   The log records model/view UUIDs and a parent-lineage conflict for the Slab
   child. Trial 2 in 0.30.0 is owner-reported PASS for identity/evidence only;
   it does not establish the field owner. Do not write to either result.
2. The owner reports W1 read/write and one UI Undo per changed element and a
   PASS for trial 3's W1 no-op stage. Its detailed log was not supplied. Do not
   repeat the accepted writes, readbacks or Undo; preserve the no-op outcome at
   the reported scope.
3. Candidate 0.28.0 implements parent-edge matching for typed deletion and
   0.29.0 adds one plural native delete call for the reviewed Column group.
   The owner reports PASS for all steps of the 0.29.0 trial, including one UI
   Undo restoring all three Columns. Do not repeat this accepted Column
   deletion/Undo, the Wall 240 mm deletion or Beam W1 moves. The 0.30.0 native
   material trial failed; retain the failure and repair the guarded path before
   proposing another attempt. Native selection remains unsupported.
4. Continue the [development plan](office-editing-development-plan.pl.md) for
   field-owner resolution, material repair, date/vector codecs, unaccepted
   families/types, multi-file and whole-project work. Trial 5 accepts only the
   four logged scalar pairs; the 0.30.0 owner observation records remaining
   fixture gaps and the limits on trials 1–4. Priorities 1–5 remain partial.
   Preserve journal state and all write safeguards.

M4 remains partially accepted. The latest results do not establish native
selection, native material updates, all six families, multi-file execution, or
whole-project access. Preserve target binding, write revalidation, journaling,
unknown-result blocking, replay and Undo safeguards.

For earlier bounded native outcomes and historical evidence, use
[validation status](validation-status.md) and the retained owner observations in
`test-results/`. Do not use superseded owner-test instructions or commands.
