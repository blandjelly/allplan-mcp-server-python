# Next-model handoff

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
