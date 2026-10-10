# Next-model handoff

## Current handoff — 2026-10-10, 0.11.0 workflow writes ready for owner test

The owner supplied a completeness audit of ad146f6 and requested work through
the next necessary native test. First priority implemented: shared executor
accepts 1–32 existing status/layer changes on native Column roots in one
foreground file, independent of demo IDs/counts. Typed office-standard/rule-based
Apply/Revalidate/Recover now reuse it. Full-source hashes, selection exceptions,
native preflight/readback, journal/write-ahead state and exact-ID deduplication
remain. Legacy acknowledgement is restricted to its original gate; mark plans
still refuse Apply. [Contract/lifecycle](m3-workflow-execution-contract.md).

**Next owner action:** [0.11.0 workflow card](m3-workflow-apply-batch.md). Restore
S05 review-layer and S06 NWE on the original disposable copy before starting the
host, then use M3 Workflow Apply.cmd. Two separately confirmed one-target
standard/selected plans, audits 5 → 4 → 3, exact-ID read-only replay, unchanged
host session/integrity and final UI observation. Preserve Local journal, old
packages and original JSON/TXT. No repeated old two-target/Undo/stale-Apply gate.
No native writes are performed from cloud. Expanded acceptance is not_run.
[178 portable tests PASS](test-results/m3-workflow-portable-0.11.0.md), frozen sync
and wheel/sdist build pass. [0.11.0 delivery](../evaluation-packages/0.11.0/README.md):
clean source 26d70b27bd06e2916cda74213cb8995aa9f0f19a, publication
daabd57f8ecbc24ba5dae62d0cb79fb04e6b30bb, ZIP 719947 bytes / SHA-256
29fcfaed0a10108b630892da3710da3cdf05701c2d25a08a014ff4ab177ee031.
Two builds are byte-identical; extracted integrity/all 22 registered bridge
hashes and journal preservation by Setup/Restore pass.
[Source CI 38063710029](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38063710029)
is **6/6 PASS**, Windows/Ubuntu Python 3.11–3.13 test/build/ZIP jobs.
Later artifact/documentation CI is separate; the archive is not rebuilt. [Review response](reviews/m3-completeness-response-0.11.0.md).

M3/UAT-05/UAT-06 stay open. Next implementation after this observation: mark
assignment and deterministic numbering in a versioned standard, then supported
native same-session conflicts and controlled partial/unknown-result recovery.
Native completed recovery after Redo does not accept unknown recovery. Journal
capacity/copy/restore limits are documented; final UAT/main integration remain.
Do not count labels/file moves/universal setters as newly required M3 scope.
Old archives/raw evidence remain byte-exact.

## Prior handoff — 2026-10-10 Europe/Warsaw, 0.10.0 native marks-preview PASS

Continue **codex/m3-repair-preview**, draft [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
The owner supplied original 0.10.0 JSON/TXT and confirmed **model unchanged,
host uninterrupted**. [Bounded acceptance](test-results/m3-marks-acceptance-0.10.0.md)
closes the [marks-preview owner card](m3-marks-preview-batch.md); no repetition,
Apply, Recover or Undo is requested.

All ten native steps pass on the retained repaired six-column file-101 fixture:
C03 missing mark → S03 and C04 S02 → S04 give two proposals/no final defects;
the C04 exception leaves only S03 and the existing S02 duplicate group;
C03 → S06 detects the expected collision with the existing excluded S06 peer.
All three exact plans revalidate unchanged. Both complete audits match except
transport request IDs: 24 checks, 20 pass, 3 fail, 1 not_applicable, 0 not_checked.
One host session **6856cef1-a336-4ef5-a51a-e6663545492d** spans all ten responses.
Source fingerprint **8055a1b63bae34a3c0dcf379a4e2c8b2439d22dccf746874de4643ce21077799**;
report fingerprint **6f2bfd929ec01cca512e430517057666fdae69a79e494676ecadeee4dd8cb658**.
Both audit hashes and all three expanded-request plan hashes independently
recompute; original MCP text/decoded responses and TXT agree.

Original upload bytes, size/hash manifest and independent verification are
under [evidence/m3-marks-0.10.0-20261010T141319](test-results/evidence/m3-marks-0.10.0-20261010T141319/).
All 22 installed bridge hashes in each health capture independently match
clean source **ebf2c752440a0f72b538527f35175668322395a4**; the same source blobs
remain on inspected M3 head **742f0ebf51ee17caf554595bec49670ea3226d2d**.
The delivered ZIP and publication manifest remain unchanged; binary archive
comparison was unavailable through the text-only connector in this analysis.
Recorded delivery SHA-256 remains
**5a3e2ba0d75ebd798204922cf44da70d602bc2e41b8cdbe2f2f7f5c3b3c67888**.
Existing 165-test/six-job CI evidence concerns its original commits; no runtime
code, package version or archive was changed by this acceptance update.
Static original flags remain historical and unedited.

**Next action:** continue M3 implementation from this accepted preview baseline,
reviewing the remaining execution/standards requirements before defining a new
bounded slice. No new owner test is requested by this documentation update.
M3/UAT-05/UAT-06 remain open: mark/selected writes, numbering, graphical labels,
wider standards/types, native unknown outcomes, grouped Undo and crash/power-loss
guarantees remain unaccepted. Earlier 0.8.1 layer/status execution, separate Undo,
Redo/recovery, restart and stale-Apply gates and the 0.9.0 preview gate retain
their separate acceptance. Same-session UI-edit conflict stays blocked in the
observed interactive-host lifecycle; do not repeat it there.
Main/base reconciliation, integration and release remain separate. Preserve
original uploads and delivery artifacts; continue on M3 without rebuilding them.

## Prior handoff — 2026-10-10 Europe/Warsaw, 0.9.0 native PASS / 0.10.0 marks ready

Continue **codex/m3-repair-preview**, draft [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2), base codex/m2-audit-accepted.
The owner requests continued M3 work until native testing is required and
explicitly instructs **commit/push everything to GitHub**. Authorization persists;
no merge or release is performed.

**New native gate PASS:** [0.9.0 standard/selection preview acceptance](test-results/m3-standards-acceptance-0.9.0.md).
Two original uploads are byte-identical under evidence/m3-standards-0.9.0-20261010T112517,
with size/SHA-256 manifest and independent verification. Capture 13:25:17.193
Europe/Warsaw. All ten steps pass: versioned standard zero proposals, layer-3700
selection excluding S06 selects 5/excludes 1, opposite predicate selects 0;
all three exact plans revalidate unchanged. Complete six-column before/after
audits match except request IDs, with 3 mark findings/zero unchecked checks.
Source **3b23bc810ba9b39b7f365dae48f4f2781ad0b146d45a3d495ff5f876e0b25547**,
report **852027bc3ad4b210cd98f7dcd8098ba7cfbad712a9be1f90dc5d28fd004a1e7f**.
Both audit hashes and all three expanded-wrapper plan hashes independently
recompute after removing unhashed request_id/host_session_id transport metadata.
All 22 bridge hashes in each health capture match the exact unchanged 0.9.0 ZIP
(clean source 61c7579645d497a9df1e3ff0cb5640861225b56c). Host session
**3bec3644-20ac-42ef-b33e-0c2322fea12a** stays the same. Owner confirms
**model unchanged and host uninterrupted**. S05 layer 3700, S06 status NEW remain.
No repeat, Undo or recovery is needed. Static original acceptance flags remain
unchanged. Earlier 0.8.1 write/Undo/Redo/recovery/restart/stale-Apply gates remain
accepted within their distinct scope. Same-session UI edit conflict remains
blocked by the earlier host cancellation; do not repeat on that lifecycle.

**Next implementation: 0.10.0 explicit mark previews, ready_for_owner_test.**
[Contract](m3-marks-contract.md), [165 portable tests](test-results/m3-marks-portable-0.10.0.md),
[Polish next card](m3-marks-preview-batch.md).
fix_model_issues and preview-only rule_based_edit accept selected required/unique
mark rule choices with exact canonical model_uuid and explicit nonmissing string.
Both mark rules must participate; distinct assignments per element, maximum 32 choices.
Invalid choices reject before context; absent/compliant/wrong-rule targets are
finding_stale. Same full audit snapshot generates findings, selection and final
mark simulation. Excluded/unchosen peers retain current marks; full normalized
file/family uniqueness detects proposed collisions and marks conflict, unknown
reads block readiness. Reported remaining defects describe hypothetical values.
Assignment/validation metadata enters immutable plan hash; full revalidation,
TTL/restart/cache protections remain. Native executor refuses every mark-metadata
plan, including when filtering leaves only the former two layer/status changes.
No mark setter/numbering/graphical label/write authorization is introduced.
Existing office standard 1.0.0 definition and dependencies remain unchanged.

165 local tests PASS on Linux CPython 3.12.14, FastMCP 3.2.4, uv 0.12.19; frozen
sync and wheel/sdist build pass. Ten new tests cover explicit positive proposals,
normalization, proposed/excluded-peer collisions, same-scan/stale/unknown inputs,
pre-context validation, apply bypass refusal, full real MCP/HTTP owner collector
and stop-on-wrong-fixture. M3 Marks Preview.cmd is packaged at the root. New
collector retains original MCP text as well as decoded responses.
Exact [0.10.0 delivery](../evaluation-packages/0.10.0/README.md): clean source
**ebf2c752440a0f72b538527f35175668322395a4**, source_modified=false; ZIP **660447 bytes**,
SHA-256 **5a3e2ba0d75ebd798204922cf44da70d602bc2e41b8cdbe2f2f7f5c3b3c67888**. Two builds are byte-identical;
exact extracted integrity and recursive 22-file registration pass.
Accepted older ZIPs/evidence are never rebuilt.
[CI run 38049405544](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38049405544)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
clean source **ebf2c752440a0f72b538527f35175668322395a4**. Exact artifact publication is
commit **44776b7123f384802dec4d293e542f4de9236c17**; later artifact/documentation CI
is separate. This exact delivered ZIP is unchanged.
Earlier 0.9.0 CI remains separate.

**Next action requires owner Allplan:** install exact 0.10.0 into a new folder,
Setup.cmd with the same Local, keep old archives/logs/journal. Use the **same
repaired disposable six-column copy in file 101**, S05 SZ_OGÓ01 and S06 NEW,
with the three mark findings still present. Start host/MCP and run **M3 Marks
Preview.cmd**, no model edits during reads. Expected ten OK steps:
C03 missing→S03 and C04 duplicate S02→S04: 2 proposals/no final duplicates or missing;
C04 exception: 1 proposal/one remaining duplicate group;
C03→S06 with existing S06 excepted: expected conflict/one collision group with both
exact UUIDs. All three revalidations unchanged, full before/after audit (3 findings) identical,
same-session health. Return original logs/m3-marks-preview-*.json/TXT and unchanged
values/appearance/host observation. Do not Apply, Recover, Undo, rebuild the
fixture or repeat an accepted old gate.

M3/UAT-05/UAT-06 remain open. Native new positive mark proposals/collisions are
not_run; mark/selected writes, numbering, labels/filemoves, wider standards/types,
unknown native outcomes, grouped Undo, full app/OS restart and crash/power-loss
behavior remain deferred. Base/main documentation reconciliation and integration
remain separate. Preserve every raw evidence byte and archive version identity.

## Prior handoff — 2026-10-10 Europe/Warsaw, 0.9.0 M3.3 preview ready

Continue **`codex/m3-repair-preview`**, draft [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
The owner requests continued M3 work until native testing is required and
explicitly instructs **commit/push everything prepared to GitHub**. Authorization
persists; no main/PR merge or release is performed.

**New 0.8.1 owner gate PASS:** [stale Apply rejection and originals](test-results/m3-stale-apply-acceptance-0.8.1.md).
Three byte-identical uploads preserved with manifest/verification under
`test-results/evidence/m3-stale-apply-0.8.1-20261009T225321`.
Execution **62c9e25cb67027df3c5126057a4d2cbe** uses old plan
**500b57e169df4a6d99e982d413282542** and its exact hash. In host session
**3ccecb6b-5695-44b6-b44b-3329acafa0cd**, Apply returns
**rejected/native_setters_started=false/read_only=true/error.code=plan_expired**.
Before/after complete six-column audits have identical source/report hashes;
S05 layer remains **3700/SZ_OGÓ01**, S06 status **NEW**. Same-session health
and all 22 bridge hashes in each health capture match the unchanged 0.8.1 ZIP.
Owner confirms **values and appearance unchanged**. Saved request matches the
embedded request. Audit hashes independently recompute from original MCP text;
structuredContent has some float-to-integer normalization and alone does not
reproduce the float-preserving host hash. Preserve original text blocks.
No Undo/Recover/repeated test is required. Earlier write/Undo/Redo/recovery and
restart invalidation remain PASS. Same-session manual-edit conflict remains
blocked by UI host cancellation; do not repeat it on this lifecycle/build.

**Delivered next slice 0.9.0: ready_for_owner_test.**
[M3.3 contract](m3-standards-contract.md),
[155 portable tests PASS](test-results/m3-standards-portable-0.9.0.md),
[Polish next card](m3-standards-preview-batch.md).
`apply_office_standard` takes preview only, explicit preset
native-model-qa-demo-layer-status **1.0.0**, active scope and optional selection.
Its versioned resource defines layer/status remedies, not marks/numbering.
`rule_based_edit` takes preview only, typed audit/explicit repair choices and
required predicate/model-UUID exceptions. Both compose the shared planner.
Selection and findings use one full fresh audit snapshot; exceptions/false/
unknown predicates retain separate reasons and counters. Unknown under negation
blocks readiness. Predicate fields are bounded to audited mark/status/layer/
file state/explicit dimension fields; invalid inputs reject before context;
absent exception UUIDs reject. Full audit/revalidation includes excluded elements.
Immutable workflow/selection/standard metadata enters the plan hash. Native
executor refuses all selection/workflow plans even if the changes match the
old two-target fixture. No generic/standard/selected native writes are added.

155 tests PASS on Linux Python 3.12.14; real MCP/HTTP checks prove wrappers,
before-context validation, selected Apply refusal and read-only owner launcher.
Old lost-reply, crash/disk, source/replay checks remain passing. Frozen sync and
wheel/sdist build pass. Dependencies unchanged; local uv.lock version only.
New package has **M3 Standards Preview.cmd**. Exact 0.9.0 artifacts are under
[`evaluation-packages/0.9.0`](../evaluation-packages/0.9.0/README.md).
Clean source **61c7579645d497a9df1e3ff0cb5640861225b56c**;
ZIP **624503 bytes**, SHA-256
**c4cf31d6b08c651c10e4020062d5c0d0dba6d5ea0380b748c16b6c8f9d349e33**.
Exact extracted integrity, recursive registration of 22 bridge files and clean
source deterministic rebuild verify. Publication docs do not rebuild this ZIP.
Never rebuild accepted versions.
[CI run 38002888441](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38002888441)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
clean source **61c7579645d497a9df1e3ff0cb5640861225b56c**. Exact artifact
publication is commit **65ac8ef032d36226b7af3d294e51a664f722fd5d**; later
artifact/documentation CI is separate. The owner ZIP is unchanged.
All existing archives/logs remain unchanged. CI results belong to their exact
commits; do not transfer old six-job results to 0.9.0 or later documentation.

**Next action requires owner Allplan:** install the exact 0.9.0 ZIP into a new
folder/Setup.cmd with the same Local, keep 0.8.1/archive/journal, open the same
repaired disposable copy (S05 SZ_OGÓ01, S06 NEW, 3 mark findings). Start host/MCP
and **M3 Standards Preview.cmd**, without UI editing during reads. Expected:
standard zero proposals; layer-3700 selection excluding S06 selects 5/excepts 1;
opposite layer predicate selects 0; all three revalidations unchanged;
identical full before/after audit and same-session health. Return original
JSON/TXT plus unchanged-value/appearance and host UI observations. No Apply,
Recover, Undo, fixture rebuild or repeated earlier owner gate.

M3/UAT-05/UAT-06 remain open. New M3.3 native preview is not_run;
marks/numbering/file moves, selected writes, wider types/scopes, unknown native
outcomes, grouped Undo, full OS/application restart and crash/power-loss behavior
remain deferred/unaccepted. Recheck main/base documentation reconciliation and
remote state before eventual integration.

## Prior handoff — 2026-10-10 Europe/Warsaw, 0.8.1 restart invalidation PASS

Continue **`codex/m3-repair-preview`**, draft [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
The owner supplied four original local-Codex read-only preview/revalidation
files. After the first test, a UI click interrupted the host; the owner restarted
it before the second test and reports **other columns unchanged**.
[Native restart record and originals](test-results/m3-plan-restart-acceptance-0.8.1.md)
establish **PASS for old-plan rejection after restart**, **BLOCKED for native
same-session manual-edit conflict**. Do not ask to repeat that blocked scenario
on this build. The host is an interactive PythonPart; cancellation stops its
server/palette/timer, and new RequestHandler instances get an empty plan cache.
Do not preserve old plans/adapters or weaken restart invalidation to manufacture
a same-session pass. No cancellation callback trace was uploaded.

First capture **00:35:48.998 local**: 0 changes, 3 excluded findings, 3 audit
findings, complete coverage; read-only preview_ready and immediate unchanged
revalidation, 296 seconds remaining. Plan **500b57e169df4a6d99e982d413282542**,
hash **8687e394b90923fd99ca666fdc3f3ee588fe92dec7b5effdd483e16268dfa420**,
host **fdca1b5c-b147-4ac4-9c9e-4019eda2203b**.
Second capture **00:38:45.545 local**: host
**22d3d4d9-7334-4260-9126-97960bffb6fc**, healthy, changed session, exact old
plan revalidate raises **plan_expired**. No conflict/source_unchanged/read_only
fields accompany that tool error; no stale Apply was called.
All 22 installed bridge hashes in both sessions independently match the exact
unchanged 0.8.1 ZIP; the plan hash recomputes using the card request/bundled
profile; response text/structuredContent and TXT identifiers/results agree.
Originals/manifests/verification are under
`test-results/evidence/m3-plan-restart-0.8.1-20261009T223548`.
No post-edit audit or explicit S06 restoration was supplied; do not infer its
current value from filenames or assume the host interruption caused an edit.

The earlier **two-target write/readback, two-step Undo, Redo and persisted
read-only recovery/replay gate remains PASS**; see the prior handoff and
[execution acceptance](test-results/m3-execution-acceptance-0.8.1.md).
This owner observation adds unchanged-other-columns UI evidence for the retained
fixture, not a whole-project/every-property guarantee. No runtime code or package
changes are made by this evidence/documentation update. Clean source
8074905536ff5c95e20de4a59a70d513f8694314 and ZIP SHA-256
b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47 remain unchanged.
149 portable tests/six-job CI run 37997427257 concern the published artifact
commit, not later documentation commits.

**Next owner boundary:** [one stale Apply rejection test](m3-stale-apply-batch.md).
Use installed 0.8.1/same disposable copy/current state. No reinstall, rebuilding,
new preview, M3 Apply.cmd or UI editing. Local Windows Codex checks healthy
verified 0.8.1 in a session different from the original above; captures a complete
six-column audit; saves one fresh execution ID/exact stale-plan Apply request
without overwriting m3-last-execution.json; sends once, expecting
rejected/native_setters_started=false/read_only=true/error.code=plan_expired.
Only after explicit rejection, capture matching post-audit/same-session health.
Return originals plus unchanged UI observations. Other errors stop without retry.
This tests rejection at the mutation entry point in the supported restarted-host
workflow. Cloud cannot perform this owner-native test.

M3/UAT-05/UAT-06 remain open; same-session manual-edit/source conflict has portable
evidence but no runnable native gate in this observed lifecycle. Native stale
Apply rejection, unknown-outcome recovery, grouped Undo, arbitrary scopes/types,
full application/OS restart, crash/power-loss persistence and broader M3.3 remain
unaccepted. After the next supported-lifecycle gate, continue shared-service
office-standard/rule-based implementation with explicit scope/limits and a new
package version if runtime code changes. Do not rebuild the accepted 0.8.1 ZIP.
GitHub authorization persists; no main/PR merge or release. Recheck remote state
and main/base documentation reconciliation before future integration.

## Prior handoff — 2026-10-10 Europe/Warsaw, 0.8.1 execution gate PASS

Continue **`codex/m3-repair-preview`**, draft [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
The owner supplied six original Apply/Check Undo/Recover logs and confirms both
native repairs worked, with **two separate Undo steps**. A clarification confirms
**Redo restored both repairs before Recover**. This explains the differing
current observations; do not misread historical applied outcomes as new setters.

[Native acceptance and original evidence](test-results/m3-execution-acceptance-0.8.1.md)
establish **bounded execution gate PASS**: completed/applied-applied,
audited_fields_match_plan=true, full audit 3, same-ID read-only replay; Check Undo
old-old/audit 5; later Recover new-new/audit 3. Three distinct host sessions
retain the exact execution/request and replay it read-only. Current observations
are separate from historical outcomes. Health after both read-only batches passes.
All **22 installed bridge hashes**, plan and request hashes, four distinct audit
hashes and TXT/JSON agreement independently verify. The six originals remain
byte-identical under `test-results/evidence/m3-execution-0.8.1-20261009T221635`.
Execution **82ce52f62acb4590b1e62765612f219e**; sessions are listed in the record.
Both native targets have IsInMacro=true and pass the corrected root eligibility.

The exact installed **0.8.1 ZIP remains unchanged**: clean source
**8074905536ff5c95e20de4a59a70d513f8694314**, SHA-256
**b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47**.
Original delivery manifest/embedded handoff/raw flags describe the pre-test state;
this acceptance supersedes it without rebuilding or rewriting those artifacts.
149 portable tests and six-job CI run 37997427257 remain separate evidence for
artifact commit 25dc292cf72776663feea80cc5bbe13b975ceff5; do not claim that run
tested later evidence/documentation commits. This update changes no runtime code.

**Next owner boundary:** [focused read-only manual-edit conflict card](m3-conflict-batch.md).
Use installed 0.8.1 and the current repaired disposable copy after Redo;
do not repeat Apply/M1/M2, reinstall, rebuild columns or reintroduce both defects.
Local Windows Codex prepares a fresh preview (zero proposals on the repaired
fixture is valid) and immediate unchanged revalidation. Owner manually changes
S06 status NEW → EXISTING; revalidate the exact retained plan in the same host
session within five minutes, expecting conflict. Restore NEW manually and return
original responses plus host-survival/model UI observations. If UI ends the host,
plan_expired after restart is separate protection, not native same-session
conflict acceptance. Cloud cannot perform this owner-native step.

M3/UAT-05/UAT-06 remain open for native manual-edit/stale-plan evidence and
broader required behavior. M3.3 office-standard/rule-based services and generic
writable registry behavior are still unimplemented. Unknown-outcome recovery,
whole-model UI collateral verification, grouped Undo, full application/OS restart,
crash/power-loss persistence and arbitrary types/scopes remain unaccepted.
The owner only attested the two target changes/Undo/Redo, not every model property.
GitHub authorization persists. No main/PR merge or release is performed; recheck
remote/base/main documentation reconciliation before future integration.

## Prior handoff — 2026-10-09, package 0.8.1 (historical, before native retest)

Continue **`codex/m3-repair-preview`**, draft [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
The owner supplied four original write-gate logs and reports that the tool did
not work, Allplan/server still run, and no model changes are visible.
[Rejection record and exact evidence](test-results/m3-apply-rejection-0.8.0.md)
establish **BLOCKED before setters** for execution
`9232c4149bd9497496b42c92a5dc0aed`: host `target_not_writable`, IsInMacro.
All 22 installed bridge hashes match the unchanged 0.8.0 archive; preview and
its audit/revalidation/health pass. The CLI's `unknown` and pointer's
`apply_pending` are incorrect/incomplete client labels, not evidence of a write.
No Undo or replay of that rejected plan is required.

**Correction 0.8.1, ready_for_owner_test:** IsInMacro is parent-object diagnostic
evidence, not a macro-only veto. Required native parent traversal must terminate
at the reviewed exact Column root; macro/unknown ancestors, ambiguous identity,
null/deleted/invalid/passive/inactive/label targets still block writes. Execution
records retain root/flag observations. The MCP wrapper categorizes known pre-setter
errors as `rejected/native_setters_started=false`; owner CLI finalizes that pointer
and never sends recovery/replay for a rejected request. Journal, unexpected and
transport errors remain conservatively unknown. No automatic retry/Undo added.

149 portable tests PASS on Linux Python 3.12.14, including native-style
IsInMacro=true Column roots, macro/unknown ancestor rejection, real MCP/HTTP
explicit rejection and no recovery replay; previous crash/disk/lost-reply checks
remain. New exact artifacts are delivered under
[`evaluation-packages/0.8.1`](../evaluation-packages/0.8.1/README.md).
Clean source **8074905536ff5c95e20de4a59a70d513f8694314**;
Windows ZIP SHA-256 **b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47**.
Delivery manifest records all sizes/hashes. All previous archives are unchanged.
[CI run 37997427257](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37997427257)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
published artifact commit **25dc292cf72776663feea80cc5bbe13b975ceff5**.
Later documentation-only CI is separate; the recorded 0.8.1 ZIP is unchanged.

**Next owner action:** install **0.8.1** and run [the write card](m3-apply-batch.md)
on the same unchanged disposable project copy. It creates a fresh plan/ID;
do not replay the failed 0.8.0 request. If write/readback succeeds, continue
restart/recovery and manual UI Undo/readback. Return original JSON/TXT and UI
observations. Do not repeat accepted M1/M2 or rebuild the fixture. Native writes,
Undo and UAT-05/UAT-06 remain unaccepted; broader M3 work still waits for this gate.
GitHub authorization from the owner remains valid; no main/PR merge is performed.

## Prior handoff — 2026-10-09, package 0.8.0 (historical)

Continue on **`codex/m3-repair-preview`**, existing draft
[PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2).
The owner requested continued M3 work until user testing is required and
explicitly authorized GitHub actions. The previously accepted 0.7.0 preview
archive/evidence remain unchanged; M0–M2 acceptance is preserved.

**Delivered next slice: ready_for_owner_test**, native writes/Undo **not_run**.
Read [execution contract](m3-execution-contract.md),
[portable checks](test-results/m3-execution-portable-0.8.0.md) and
[Polish write/Undo card](m3-apply-batch.md). New-version artifacts are under
[`evaluation-packages/0.8.0`](../evaluation-packages/0.8.0/README.md); the delivery
manifest records clean source **d1b406318a24b52792cacc8560745e4a596cd1f3**.
Windows ZIP SHA-256 **e21fe594372dde28d88d2fece2842fa8263d023f8410592c1239a7c052f8278c**.
Never rebuild under an accepted artifact's version. Artifact/documentation
commits preserve this exact ZIP and do not change its embedded clean-source handoff.

Implemented bounded native ChangeLayer/ChangeAttributes evaluation apply for
exactly the retained C05/S05 layer and C06/S06 status repairs in foreground
file 101, with a reviewed plan/hash and explicit disposable-copy acknowledgement.
Full fresh audit/source/TTL checks and all-target root resolution/eligibility
precede setters. Each target is checked again, written once and freshly read
back; failure stops later targets. Final audit expects three mark findings and
all returned audited fields to match only the two planned changes. Collateral
audited changes/unavailable post-checks fail verification. Generic writable
profiles/refs remain inactive; other native types/scopes are unavailable.

Local OS serialization and atomically persisted write-ahead execution records
deduplicate exact execution IDs across restart/plan expiry/UI Undo. Conflicting
IDs, full/corrupt/unwritable journals and unresolved outcomes block new writes.
Recover is read-only: it reconciles observed current old/new values, never
resumes setters and does not prove mutation causality or cross-copy identity.
The owner CLI saves an execution request before sending, has no automatic retry,
and provides **M3 Apply.cmd**, **M3 Recover.cmd**, **M3 Check Undo.cmd**.
Undo is manual native UI observation; no grouping/rollback API is assumed.

**Next action requires the owner:** install 0.8.0 on a disposable copy, review
the two values and run the write/readback/replay → host restart/recovery → UI
Undo/readback card. Return original JSON/TXT, UI target/value/unchanged-other-
elements observations and number of Undo steps. No repeat of accepted M1/M2
or standalone 0.7.0 preview batch is requested. Stop at this native gate;
M3.3, broader apply/registry behavior and native manual-edit conflicts remain
pending. M3 and UAT-05/UAT-06 are not closed. Cloud cannot run Windows/Allplan.

Portable validation: **146 tests PASS**, Linux Python 3.12.14; frozen sync,
wheel/sdist build, deterministic source-only Windows ZIP, integrity and recursive
registration. Real MCP/HTTP tests include lost completed response with saved ID
and no automatic retry. [CI run 37937853438](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37937853438)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
published artifact commit **24b65eaaab9e6e1100cbd7c4bce0726d512c575b**.
Later documentation-only CI state is separate; the recorded ZIP is unchanged.
Main's independent documentation cleanup remains outside this
M3 slice; no main/PR merge is performed. Recheck remote state before integration.

## Prior handoff — 2026-10-09, package 0.7.0 (historical)

Continue from **`codex/m3-repair-preview`**, based on accepted M2 commit
`bedb264`. The owner explicitly approved publishing all prepared work to GitHub
and has supplied the completed read-only preview test. The delivered evaluation artifacts are in
[`evaluation-packages/0.7.0`](../evaluation-packages/0.7.0/README.md).
The exact Windows ZIP remains unchanged from the local delivery: source commit
`22f18db27faf5e0873de18c1e079d1217da736fb`, SHA-256
`e47a103b8a280bf786877f22bab8faf8bfd183f4de9531d8918305bd87cf56c6`.
The archive's embedded handoff records the earlier publication block; this
GitHub handoff supersedes that publication status. The bounded preview acceptance
below supersedes its pending native gate. The documentation update does not rebuild that ZIP.
The owner requested continuation from M2 until native owner testing
is required. The first read-only M3.1/M3.2 slice now has
**bounded native preview gate PASS**: [acceptance and original evidence](test-results/m3-preview-acceptance-0.7.0.md),
[contract](m3-repair-contract.md),
[portable validation](test-results/m3-preview-portable-0.7.0.md),
[completed Polish owner card](m3-preview-batch.md).

Delivered: `fix_model_issues` explicit layer/status repair choices, fresh full
audit preview, optional exact finding IDs, exact old/new values, locators,
exclusions, immutable returned copies, session-local plan ID/hash, five-minute
lifetime, eight-plan/8 MiB cache and full fresh revalidation. Manual changes,
additions, resource/project/document/file-state changes conflict; hash mismatch,
expiry, eviction and restart cannot reuse a plan. Multiple rules cannot propose
two values for one property. API callable/docstring inspection does not invoke
setters and does not claim writability or Undo.

Current portable suite: **134 tests PASS** on Linux Python **3.12.14**, including
real MCP/HTTP transport with fake native adapters and the new JSON/TXT owner CLI.
Frozen sync, wheel/sdist build and Windows ZIP/integrity/registration checks are
recorded separately from native acceptance. New package **0.7.0** preserves the
accepted 0.6.1 archive; its source-only ZIP and SHA-256 companion are in ignored
`dist/`, with exact copies committed under `evaluation-packages/0.7.0`.
Use the delivered archive rather than rebuilding under an accepted
version number. [CI run 37929065543](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37929065543)
passes all six Windows/Ubuntu Python 3.11–3.13 jobs for published commit
`433a83b`, including tests and builds; later documentation commits have separate
CI state. Freshly checked main is `75e80bd` (M2 and documentation cleanup merged);
PR #2 remains open/draft against `codex/m2-audit-accepted`. Recheck refs and main
documentation changes before integration; no merge is performed by this update.

**Completed owner gate — 15:01 Europe/Warsaw, 2026-10-09:** original JSON/TXT
`diagnostics-20261009T130124Z` verify all 20 installed bridge hashes, matching
0.7.0 MCP/host, exactly two proposals (C05 layer 3701/SZ_OGÓ02 → 3700/SZ_OGÓ01,
C06 attribute 5002/MCP_QA_STATUS NWE → NEW), immediate `unchanged` revalidation,
identical complete five-finding audit and same-session health. Plan/report hashes
independently recompute and TXT agrees. Owner states Allplan/host run and targets/
values agree with UI. That statement does not separately claim whole-model
unchanged UI; evidence establishes unchanged audited fields. Acceptance is
bounded accordingly. Native manual-edit conflict was not supplied.
**No repeated M1/M2/M3 preview batch is requested.**

**Next work:** implement the controlled native apply/readback/recovery slice,
then prepare a new-version disposable-copy write/Undo owner gate.
M3 remains incomplete: `apply` is unavailable/rejected before native context
lookup. No write adapter, apply readback, serialized mutation journal, durable
request deduplication, unknown-outcome recovery or tested Undo exists. M3.3 and
M3.4 are pending. All references/profiles remain inactive for writes. After the
preview gate, implement and probe the dedicated 2026 `ChangeAttributes` /
`ChangeLayer` adapter on a disposable copy with explicit target/value limits,
readback and Undo observations; symbol presence alone cannot authorize it.

## Accepted M2 handoff — package 0.6.1 (historical baseline)

## Checkout for the next chat

Continue from GitHub branch **`codex/m2-audit-accepted`** in
`blandjelly/allplan-mcp-server-python`. This branch contains the complete M2
implementation, 0.6.1 callback correction, original UAT/crash evidence and bounded
UAT-04 acceptance. In a fresh checkout:

```sh
git fetch origin
git switch --track origin/codex/m2-audit-accepted
```

Read this handoff and [M2 acceptance](test-results/m2-acceptance-0.6.1.md) before
continuing. The older `feature/m2-audit-foundations` branch is a separate early
schema draft, not the accepted M2 implementation. The exact delivered Windows
archives remain outside Git under ignored `dist/`; the owner retains the tested
0.6.1 ZIP. Do not replace it with a rebuild using the same version. Future runtime
changes require a new package version. The full 121-test suite passed again
before this GitHub handoff commit.

## Accepted implementation state

**M0 and M1 are closed; UAT-00–UAT-03 PASS within the recorded scope** on
Allplan 2026-1-7 / local Windows Codex. M1 is merged through
[PR #1](https://github.com/blandjelly/allplan-mcp-server-python/pull/1): local
baseline and freshly checked origin/main both point to `bc5137339f3a6fa2049b322d7c726e659b523279`.

**M2.1–M2.3 are closed; UAT-04 PASS within the retained read-only fixture scope
on package 0.6.1.** [Native evidence and limits](test-results/m2-acceptance-0.6.1.md).
Package 0.6.1 exposes `model_audit` through `/model-audit`, versioned typed
rules/string missing policies, fresh full snapshot evaluation, severity/raw
findings, coverage and readable reports. File/mark/model-local box/center and
session/project/document/model refs locate findings without native highlighting.
References remain nondurable read evidence and cannot authorize writes.

Read [architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [M1 reads](tool-reference.md),
[M2 contract](m2-audit-contract.md) and
[portable evidence](test-results/m2-audit-portable-0.6.0.md).
The M1 read profile remains schema m1-profile-1 / revision **1.0.2** unchanged;
the separate audit profile is schema m2-profile-1 / revision **2.0.0**. Both bind
resources freshly and remain inactive for writes.

The [native 0.6.0 capture](test-results/m2-audit-runtime-0.6.0.md) reports
six columns, five findings on five targets, one duplicate group, complete coverage
and zero unchecked checks. The owner confirms UI correspondence and unchanged model.
The [uploaded crash evidence and correction](test-results/m2-dispatch-fix-0.6.1.md)
confirm a managed-exception crash at 12:50:12.737 Europe/Warsaw during a second
request for [101,102]/include_passive=true, ID `101efe01-58e9-4296-aa93-e1a2c18b60b4`.
That scope exceeds the demo profile's file-101 contract and should be rejected.
No incident dump/managed stack/faulting module is available; causation is unproven.

**0.6.1 contains a concrete dispatcher error-boundary fix:** callbacks return
primitive result/error data, while HTTP workers raise errors after dispatch.
Public and host preflight reject invalid audit scope before native reads;
a bounded persistent bridge log retains request outcomes/exception traces.
The original 0.6.0 artifact and evidence are preserved. Full local suite:
**121 tests PASS**, including former callback escape, typed/generic errors,
exact incident scope, logs and stop-on-failure diagnostic checks.

The [0.6.1 targeted owner gate](m2-stability-batch.md) is completed: both full
101-only audits, public/direct-host rejection of [101,102] and post-error health
pass in the same host session. All 18 installed bridge hashes match the tested
archive; the loaded boundary marker is present. The reports are identical apart
from request IDs, and all per-element source hashes/raw evidence/locators match
the earlier UI-confirmed capture. The owner now confirms Allplan and host remain
running; the earlier unchanged-model/UI confirmation is not reattributed to this
later statement. Static report acceptance flags remain unchanged.

**No further M2 owner batch is required within this scope.** Preserve the tested
0.6.1 archive. At that handoff M3 was planned and unimplemented; do not infer authorization for
repairs or native writes from M2 acceptance. Native longer-term stability,
concurrent multi-chat requests and persistent log behavior remain unverified.
The cloud workspace cannot execute Windows/Allplan tests.

## Verified baseline

- Fork: `blandjelly/allplan-mcp-server-python`; upstream: `AlejoDuarte23/allplan-mcp-server-python`.
- M0.1–M0.5 accepted with **UAT-00/UAT-01 PASS** on Allplan UI build **2026-1-7**,
  local Windows Codex, package **0.1.2**. Owner confirmed installation, box count/
  dimensions, ESC/restart, minimize/restore, project switching and cleanup.
- Observed API release **2026.1**, executable file/product versions
  **16.1617.8659.814 / 2026.0.1.0**, embedded CPython **3.13.13**, external Python
  **3.14.8**. UI hotfix is owner-reported; executable metadata is not a hotfix mapping.
  Windows/Codex app versions remain unspecified.
- Portable pre-merge validation: **95 tests PASS** locally on Linux Python
  **3.12.14**; Windows/Ubuntu Python **3.11–3.13** matrix, wheel/sdist and Windows
  ZIP checks [PASS for 99abad8](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37859752410).
  This is separate from Allplan acceptance and does not replace checks for later
  commits. FastMCP **3.2.4** and uv **0.12.19** remain pinned.

Keep the tested archives unchanged; do not overwrite them with rebuilt packages.
Use a new package version for further runtime changes. Their recorded hashes are:

| Tested archive | SHA-256 |
| --- | --- |
| `allplan-mcp-0.1.2-windows-evaluation.zip` | `d97b6761b13f8cd6e80c7954f1c91de513d4a813a5b236c6917b14b0882ac528` |
| `allplan-mcp-0.2.1-windows-evaluation.zip` | `26ca92690be0365eca3d580b947c52b443e536cc8ee10d8b1ca7b1de594bc6e8` |
| `allplan-mcp-0.5.3-windows-evaluation.zip` | `15262b1f029d818e5fea871a0b669603d90a5b6ca68e80d5355457b8656ed104` |
| `allplan-mcp-0.6.0-windows-evaluation.zip` (native report verified; crash unresolved) | `6fc6e37fa4abd09ffec5b7a72d2b34a3a67c49a1ad2eef4cd480426428be2dd7` |
| `allplan-mcp-0.6.1-windows-evaluation.zip` (bounded UAT-04 PASS) | `b47cba9ab08cce800f9e1900d03a232153c4441d054818f1bc116e8cc4a617f7` |

The accepted 0.5.3 artifact uses clean source
`4f685766e1577cddb681ee3726bbabd3f2b3d743`; documentation/test-only integration
does not rebuild or replace that artifact.

## Accepted M1 reads

M1.1–M1.4 implement explicit file scope, typed predicates, bounded geometry/
hierarchy, metadata, full selections/pages/summaries and fresh profile binding.
The [acceptance record](test-results/m1-acceptance-0.5.3.md) preserves exact
scope and limits; the [completed fixture recipe](m1-final-batch.md) is reference,
not a request to reinstall or repeat captures.

Native A/B/C verify ten roots in 101 (six Column, two SkeletonBeam, Wall and
MultiSlab), one reference in passive 102, and unloaded 103 omission. Filters
column/S02/C01 return 6/2/1; six child representations are deduplicated. Resources
resolve MCP_QA_MARK / MCP_QA_STATUS and SZ_OGÓ01 / SZ_OGÓ02. B verifies passive
102 and C05/S05 on the review layer separately from display-unit invariance.
C adds (100000,200000,0) mm to every global box exactly once; model-local geometry,
dimensions and counts remain unchanged. Independent UI offset 100/200 m and C01
base-section center 100/200/0 m agree. Owner confirms unchanged A/B/C appearance
and retains the zero-offset baseline. Static runtime_verified flags remain
unchanged; acceptance applies only to the recorded build/fixture.

Changed-source staleness, TTL/eviction/restart and other predicate variants retain
portable evidence. The demo is bound_for_read and active_for_write=false.
Configured levels are not native BWS. Durable references, writable properties/
Undo, arbitrary native trees, nonzero Z offsets and exact solid intersections
remain outside acceptance.

## Earlier context evidence — 0.2.1

`get_model_context` is read-only: project, foreground/loaded file states, input
unit enums, raw offset and optional **0–20 raw adapter** model/view UUID samples.
The 0.2.1 correction resolves project lookup, including the tested alternate
`GetProjectPath(host_name, project_name)` order: error 0/nonempty path, where the
published name/host order returned -1/empty path on this build.

| Original diagnostic | Observed result |
| --- | --- |
| [132549](test-results/evidence/diagnostics-20261007T132549Z.json) | `Nowy projekt 1`: file 1 foreground, file 2 passive; active/passive model and view UUIDs read separately. |
| [132700](test-results/evidence/diagnostics-20261007T132700Z.json) | Same project: unloaded file 2 excluded from inventory/sample, file-1 UUIDs unchanged. |
| [132822](test-results/evidence/diagnostics-20261007T132822Z.json) | Switched to `test`: file 21 foreground, file 1 active background; changed project fingerprint. |

The owner confirmed **“Nazwy projektu sie zgadzaja, model bez zmiany”** (names
match, model unchanged). Each capture has a different host session ID;
`document_id=0` is not project identity. Unit enums **3/1** and offset **[0,0,0]**
were read without UI unit comparison/nonzero-offset tests in these early captures.
The accepted 0.5.3 captures supply that later separate evidence.

Original diagnostic SHA-256 values, retained byte-for-byte:

```text
132549: b793bbcada5d540eb5b12ffbd777dadd2f33418c6e6abeb8599c2cd045db28c6
132700: acf137c1655c3ce13d6ac620ac88745ed14c34231b6d8ac865080d31aa68575f
132822: b1db2cc225066c307862de810005985d66ba0031f00a11c9a71712f3745be90b
```

## Next work and unresolved limits

M2 work requested by the owner is complete; no further owner test is pending
within the recorded scope. The first requested M3 slice is now delivered above;
native preview acceptance and subsequent mutation implementation are pending.
Crash timing and second request arguments are established. A concrete UI
callback exception defect is fixed and the native controlled error/recovery gate
passes; its role in the actual CLR crash remains a hypothesis without the incident
stack. UAT-04 is closed for the retained fixture, not for arbitrary native faults.

The demo preserves C03's literal `<niezdefiniowany>` in raw evidence while its
explicit QA policy classifies that literal, absence, null and empty/whitespace
strings as missing. Unknown reads/types and passive API absence remain
not_checked. The tested six-column audit has five findings and one duplicate
group. A zero result cannot bypass incomplete coverage. Missing bindings reject
the audit; remedies remain suggestions. M3 native apply is unimplemented/unrun;
the new read-only preview contract is separate from accepted M2 evidence.

Current portable verification: **121 tests PASS** on Linux Python **3.12.14**,
including the real MCP/HTTP transport with a fake native host and JSON/TXT CLI
output. Frozen sync, wheel/sdist build and Windows archive/integrity checks pass.
This is separate from native acceptance and from the earlier 95-test CI result.
No remote current M2 CI run is claimed. The 0.6.0 native report, crash collection
and successful 0.6.1 native gate have separate original evidence. The latest
JSON/TXT are preserved byte-for-byte; their hashes are in the acceptance record.
Persistent bridge.log was not supplied and its native rotation/traceback behavior
is not included in this acceptance.


Baseline box tools lack automatic readback and durable write deduplication.
Queued cancellation has portable simulated-dispatch evidence; closing the listener
does not undo an already running write. Static diagnostics flags
`runtime_verified=false` / `allplan_acceptance=not_run` are not a live acceptance
registry. Native M2 audit is accepted only for the recorded fixture/profile;
all repair tools and Claude/cloud-to-Windows integration remain unaccepted.
Neither inspected repository has a license; public redistribution remains
unresolved and no release publication is recorded.

Keep Allplan APIs inside the host, use typed workflows and shared preview/apply,
and report missing data as `not_checked`. Verify per-type/property writes and
readback on Allplan 2026. The model owns code, checks and ready-to-use test packages;
the owner observes the UI. Record accepted task IDs, evidence, remaining scope
and the next action here after each completed slice.
