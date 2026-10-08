# Next-model handoff

## Current handoff — 2026-10-09

Current package **0.5.3**, profile revision **1.0.2**. Native capture A
diagnostics-20261008T223235Z.json passes bounded geometry/hierarchy reads:
10 roots in 101 (6 columns + 2 SkeletonBeam + wall + MultiSlab), one reference
in 102, six child representations deduplicated, readable geometry throughout.
Columns/S02/C01 counts 6/2/1; C01 400x400x3000 mm centered XY=(0,0), beams
6000x300x500 and slab 4000x4000x200 mm. Owner independently confirms unchanged
appearance and matching beam/slab UI dimensions in A.

Capture B diagnostics-20261008T224141Z.json **PASS for bounded native display-unit
read invariance**. Input-length enum changes 0 to 3 (mm to metres); all five
queries retain exactly equal canonical geometry, result identities/type IDs and
counts. Query/summary/pages agree within each capture. Profile binding/integrity
pass. Declared setup corrections are verified separately: 102 is now passive,
C05/S05 uses bound review layer SZ_OGÓ02 (3701); all other column fields match A.
103 remains explicitly unloaded. Full M1 exit gate remains pending C and final
owner UI observations; unchanged appearance in B is not independently reported.

Next: keep installation/geometry and original zero-offset baseline; **C only**,
on a separate saved project copy with offset X=100000/Y=200000/Z=0 mm. Collect
C's M1 Final.cmd report plus independent UI offset values/unit, C01 coordinates/
unit, B/C unchanged-appearance and retained-baseline confirmation. Restart the
host after setup changes. Do not infer nonzero-offset source-frame semantics
from portable arithmetic; compare C with the documented transform and UI values.
No A/B, standalone profile/type probe, reinstall or accepted old batch repeat.
C03 remains literal <niezdefiniowany>; no silent missing-value normalization.
Supported new roots are exactly SkeletonBeam and MultiSlab; other framing/grouped
families remain outside scope. [Native evidence](test-results/m1-native-families-0.5.3.md),
[owner card](m1-final-batch.md). Raw new uploads are not published; old ZIPs intact.

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
PASS**, distributions and versioned ZIP build. **ready_for_owner_test**; the full
M1 exit gate is pending final Allplan evidence.
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
binding and display-unit invariance pass for the owner fixture. Nonzero-offset
C and final UI observations remain pending. Native BWS
levels are not claimed; the optional profile explicitly supplies configuration.
Selections remain memory-only/session-bound read evidence; durable references
and mutation eligibility are not established. The demo binds freshly for reads
after UI resource setup and remains inactive for writes. Do not claim full
UAT-02/UAT-03 acceptance until the final card has recorded results.

Start from [project-status.md](project-status.md) and the current code, then use
the roadmap below. Do not repeat accepted owner batches without a new defect or
change that requires verification. Preserve the tested ZIPs and their recorded
hashes; build any further runtime changes under a new package version. The
earlier 31-test baseline and new targeted checks are separate records; the full
historical suite was not rerun for this slice. Allplan runtime evidence is separate.

Next: evaluate the remaining 0.5.3 capture C and independent UI observations,
fix any native frame discrepancy, then close M1 only with linked runtime
evidence. Continue M2 after that read foundation is accepted. Attribute 498 was observed on file 1
but returned missing on passive file 2; do not infer native absence or mark
binding without further evidence. Do not ask the owner to research identifiers
or construct the final unbound fixture prematurely.

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
2. [Demo model and profile](demo-model-and-profile.md) and [draft profile JSON](../profiles/examples/native-model-qa.demo.json).
3. [Manual acceptance tests](manual-acceptance-tests.md).
4. Current `README.md`, `pyproject.toml`, `src/allplan_mcp/server.py`, `src/allplan_mcp/allplan_client.py`, the host scripts and registration utilities.
5. Applicable repository instructions and the current working tree. Recheck the baseline before editing.

The plan's baseline is commit `701f35366cc94b90085dd8b55d42b16f4166c95b` in `blandjelly/allplan-mcp-server-python`. Do not discard changes made after it.

## Immediate work

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
- Treat the draft JSON profile as unbound. The current server does not consume it; implement and validate the schema before activation.
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
