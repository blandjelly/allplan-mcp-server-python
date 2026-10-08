# Next-model handoff

## Current handoff — 2026-10-09

### Checkout and reading order

The completed M1 code and acceptance docs are on branch
`codex/m1-scope-model-query`, pushed to origin, in open **draft**
[PR #1](https://github.com/blandjelly/allplan-mcp-server-python/pull/1).
At this handoff, it is **not merged**: PR base/main is
`d8bd1ef8388daa956e8b51863b17ac33d784dca9`; closure is recorded in
`c6d82867e67342d2b145513bf816eea8bdfa8be7`, followed by documentation updates.
Recheck remote/PR state before editing. Continue from the latest M1 branch, or
from main only after it contains this work; starting solely from the current
main would omit the completed M1 implementation. Preserve unrelated owner edits.

Read this current section, [project status](project-status.md),
[M1 acceptance](test-results/m1-acceptance-0.5.3.md), then M2 in
[implementation plan](implementation-plan.md), the
[read contracts](tool-reference.md) and [demo fixture/profile](demo-model-and-profile.md).
The older milestone narratives below are history, not unfinished owner tasks.

### Accepted state and next implementation

**M1 CLOSED; UAT-02/UAT-03 PASS for the bounded read contract**, current package
**0.5.3**, profile revision **1.0.2**, owner's Allplan **2026-1-7**.
[Acceptance, exact artifact and limits](test-results/m1-acceptance-0.5.3.md).
A native geometry/hierarchy and B display-unit invariance pass. C
diagnostics-20261008T225219Z.json passes nonzero XY offset: raw offset
(100000,200000,0) mm, unchanged local boxes/dimensions/counts, all ten global
boxes add offset exactly once. Owner independently reports offset 100/200 m and
C01 base-section center 100/200/0 m; AABB center is 100/200/1.5 m. Owner confirms
B/C unchanged appearance and the retained original zero-offset baseline.

Fixture: ten roots in 101 (6 Column + 2 SkeletonBeam + Wall + MultiSlab), one
readable passive reference in 102, unloaded 103 explicitly omitted. Filter counts
6/2/1; six child representations deduplicated. Profile bound_for_read, corrected
C05/S05 review layer verified. Write eligibility remains not_checked; configured
levels are not native BWS. No mutation/durable-reference acceptance is inferred.

Next: **M2 profile/audit contracts and read-only findings**, using the retained
fixture. Explicitly decide how C03's literal <niezdefiniowany> is treated; do not
silently normalize native values. Other framing/grouped families remain outside
scope. No A/B/C, preflight, type probe, reinstall or accepted old batch repeat.
Keep 0.5.3 and older ZIPs/hashes unchanged; further runtime code needs a new
version. Raw new uploads stay private. Portable test results and owner Allplan
verification remain separate; no automated suite was rerun for this closure.

M2 entry points: `src/allplan_mcp/server.py` and `query_models.py` for typed MCP
contracts; host `model_query.py`, `query_contracts.py`, `profile_contracts.py`
and `native_readers.py` under `python_host/PythonPartsScripts/PythonHost/` for
scope/fresh binding/read observations. The packaged profile is
`src/allplan_mcp/profiles/native-model-qa.demo.json`, identical to
`profiles/examples/native-model-qa.demo.json`. Relevant portable examples are
`tests/test_model_query.py`, `test_m1_completion.py` and `test_m1_native_families.py`.
Keep Allplan imports/services inside the host; prepare focused new audit checks
without rerunning accepted M1 batches solely for handoff. UAT-04 is the next
owner case after a runnable audit package exists; it remains NOT_RUN.

The initial M0 instructions below are historical. **M0 is closed** on the owner's
Allplan 2026-1-7 / local Windows Codex setup using package 0.1.2.
[Acceptance](test-results/m0-acceptance-0.1.2.md).

Accepted version **0.2.1** has a bounded read-only
`get_model_context` probe. Its owner follow-up batch passes project lookup/switch,
loaded/passive file states, unload exclusion and separate model/view GUID reads;
the owner confirms matching project names and unchanged model.
[Runtime evidence](test-results/m1-context-runtime-0.2.1.md).
Implementation version **0.5.0** completes the bounded M1 read code: mm
geometry summaries, dimensional/AABB predicates, declared model_local/global
transform, supported native top-level parent resolution and demo profile
m1-profile-1 validation/fresh resource binding. **56 targeted portable checks
PASS**, distributions and versioned ZIP build. The subsequent 0.5.3 native
A/B/C evidence and owner confirmations close the bounded M1 exit gate.
[Completion evidence](test-results/m1-completion-portable-0.5.0.md),
[final card and concrete UI recipe](m1-final-batch.md). M1 Profile.cmd checks
named resources and M1 Final.cmd saves responses, summaries and bounded pages.
The ten-component gate is now accepted from native A/B evidence. Do not claim
the API nonzero-offset convention accepted from fake geometry tests.

Earlier **0.4.0** adds typed `model_query` action `inspect`,
bounded raw samples and attribute/layer metadata with per-field observations.
**M1 Metadata.cmd** saves the explicit request and full response in diagnostics,
addressing the earlier evidence gap. **12 targeted portable checks PASS**;
wheel/sdist and evaluation ZIP build. **Bounded metadata owner batch PASS**.
[Runtime evidence](test-results/m1-metadata-runtime-0.4.0.md) records two stable
columns, attribute 498 Nazwa obiektu (codes 67/69, empty unit), layer 3736 AR_SŁUP
and complete response capture. File-2 raw 498 is missing while passive and Słup
while active background; host/query sessions also differ. Owner confirms columns
unchanged, file 2 restored passive and Allplan 2026-1-7 unchanged. No repeat needed.
[Implementation evidence](test-results/m1-metadata-portable-0.4.0.md),
[two-capture owner card](m1-metadata-batch.md). No profile activation is implemented.

Earlier version **0.3.0** adds explicit file/passive/visibility
scope, session-bound references, typed read-only `model_query`, type/layer/raw-
attribute predicates, reusable pages and full-selection summaries with query-
field/context staleness checks. **24 relevant portable checks pass**; wheel/sdist
and evaluation ZIP build. [Contracts](tool-reference.md),
[portable evidence and limits](test-results/m1-query-portable-0.3.0.md).
**Three bounded 0.3.0 query cases PASS**: the supplied query results report,
correlated with diagnostic session/UUIDs, verifies two column identities,
distinct pages/full summary, type/layer/raw-attribute equality and passive
exclusion. The report states no model changes; independent geometry/visual
readback is not claimed. [Runtime evidence and limits](test-results/m1-query-runtime-0.3.0.md),
[small owner card](m1-query-batch.md). No repeat is needed without a relevant
change/defect. Changed-source staleness and TTL/restart retain portable evidence.

The bounded M1 implementation is complete; native geometry/hierarchy, demo read
binding, display-unit invariance and nonzero XY offset pass for the owner fixture.
M1 is accepted within the linked scope. Native BWS
levels are not claimed; the optional profile explicitly supplies configuration.
Selections remain memory-only/session-bound read evidence; durable references
and mutation eligibility are not established. The demo binds freshly for reads
after UI resource setup and remains inactive for writes. UAT-02/UAT-03 acceptance
is bounded to the recorded build/fixture; M2/M3 remain unimplemented/unrun.

Start from [project-status.md](project-status.md) and the current code, then use
the roadmap below. Do not repeat accepted owner batches without a new defect or
change that requires verification. Preserve the tested ZIPs and their recorded
hashes; build any further runtime changes under a new package version. The
earlier 31-test baseline and new targeted checks are separate records; the full
historical suite was not rerun for this slice. Allplan runtime evidence is separate.

Next: implement M2's versioned audit profile and read-only findings with
explicit evidence/not_checked semantics. Reuse accepted M1 reads; preserve scope,
fresh binding and unchanged-model guarantees. Prepare focused portable checks
and a concrete owner UAT-04 card when ready. Do not start repairs or repeat M1
acceptance merely to begin M2.

## Task

Implement the Allplan 2026 workflow toolkit incrementally in the existing fork. Start with installation and the first working Codex connection, then deliver native-model querying, auditing and controlled cleanup. Use [implementation-plan.md](implementation-plan.md) as the roadmap and record progress against its task IDs.

## Owner decisions — 2026-10-07

- Codex is the first MCP client; Claude may follow later. Keep the core MCP API client-neutral.
- First useful result: search, audit and cleanup of native Allplan elements.
- The existing MCP bridge has not yet been tested.
- Detect the installed Allplan version/build yourself when connected; do not infer it from the repository's 2026 defaults.
- Prepare a demonstration profile. The owner will build the model using your Allplan UI recipe.
- The owner tests in Allplan and reports visible results. You own coding, automated tests, diagnostics, installation and fixes.
- GitHub documentation, issues, PRs, release notes and recorded test results are in English. Owner-facing conversation and walkthroughs may be in Polish.

## Read first

1. [Implementation plan](implementation-plan.md), especially baseline findings, contracts, milestones and exit gates.
2. [Demo model and profile](demo-model-and-profile.md) and [canonical read-profile JSON](../profiles/examples/native-model-qa.demo.json).
3. [Manual acceptance tests](manual-acceptance-tests.md).
4. Current `README.md`, `pyproject.toml`, `src/allplan_mcp/server.py`, `src/allplan_mcp/allplan_client.py`, the host scripts and registration utilities.
5. Applicable repository instructions and the current working tree. Recheck the baseline before editing.

The plan's baseline is commit `701f35366cc94b90085dd8b55d42b16f4166c95b` in `blandjelly/allplan-mcp-server-python`. Do not discard changes made after it.

## Historical initial M0 work — completed

Retained planning instructions below are superseded by the current handoff.
Do not repeat them or treat their original unverified state as current.

1. Inspect the current repository, upstream provenance, installation files and execution environment. Update a concise English `docs/project-status.md` as implementation begins.
2. Fix the observed non-recursive installer: `source_scripts.glob("*.py")` omits the imported `sandbox/` package. Add a real temporary-directory installation regression test and package integrity checks.
3. Prepare a versioned Windows package with a launcher, setup instructions for Codex and a restore path. The owner should not need to edit code or manually copy internal modules.
4. Establish health/version calls through the owner's Allplan session. Inspect the full build/hotfix and embedded Python. This planning session had Linux only and no connected Allplan tools, so none of those runtime facts is verified yet.
5. Validate host cancellation/restart and request dispatch. UI-thread dispatch already exists; investigate lifecycle behavior instead of replacing the bridge without evidence.
6. Deliver only UAT-00/UAT-01 initially. If runtime feedback is pending, continue independent contracts/portable tests, while keeping integrated status pending.
7. Implement M1 context/query, bind the demo profile to real IDs, and give the owner the finalized fixture recipe. Then proceed through M2 and M3.

## Technical boundaries

- Keep Allplan API objects/imports inside the host. Pure logic and JSON contracts should run in ordinary CI without Allplan.
- Build typed workflow handlers. Do not implement the toolkit by sending arbitrary generated Python for every production operation.
- The server validates profile m1-profile-1 and freshly binds demo resources for reads. Keep write eligibility explicit and the profile inactive for writes until downstream native write behavior is verified; do not confuse read binding with write activation.
- Use model identity, explicit scope, normalized units, source fingerprints, preview/apply and readback. Respect passive/unloaded drawing files.
- Validate actual write behavior for each type/property. Ordinary native columns and Structural Framing have different documented capabilities.
- Missing data is `not_checked`, not a successful audit. A network timeout is not proof that a write did not happen.
- Keep request deduplication, partial failure, Undo, registry persistence and exported-file recovery explicit.
- Use 2026 API references. Do not import 2027-only capabilities into the support claim.
- Documentation feasibility, fake-adapter tests and Allplan runtime verification are separate evidence levels.

## Completion and handoff discipline

Deliver one reviewable slice with English documentation and relevant checks before widening the scope. For every owner test batch, provide the exact package version, small set of prompts, expected visual/count results, reset instructions and a copyable result form. The owner does not run developer test commands.

Update completed task IDs, actual evidence, unresolved questions, pending owner tests, compatibility and the next concrete action. Do not mark a capability accepted without recorded Allplan evidence. Do not wait on optional product questions that can be resolved from the owner's confirmed decisions or prepared defaults.

The planning work added documentation and an illustrative profile only. No workflow tool was implemented, no Allplan session was tested, and nothing was published to GitHub as part of preparing this handoff.
