# Documentation policy

At the start of each session read this file, the [testing policy](testing-policy.md),
the [handoff](next-model-handoff.md) and the [development plan](development-plan.md).
Before finishing, update the existing state descriptions if tasks, version,
verification results or blockers changed.

**Language:** all project documentation is written in English. The owner may
give instructions in Polish; record decisions in English. Keep project data
exactly as observed (for example attribute names such as `Materiał` or layer
names), and keep raw evidence files unchanged.

## Three places with key information

- The **handoff** gives the next agent the concrete next step and current
  state. It must be enough to resume work without reading chat history.
- The **development plan** holds current tasks, dependencies, unresolved
  errors and closure criteria. It is one backlog, not a release chronicle.
- The **[coverage matrix](m4-coverage-matrix.md)** is the single table of
  family × field/type × operation status. Update its cells instead of
  repeating per-pair status in prose.
- Do not copy long descriptions between files. In the handoff give a short
  summary and link the plan task. Evidence may be linked, but the essential
  result, its limits and its effect on further work must be in these files;
  do not move them only into a separate report.

## Updating the handoff

Keep this order:

1. **Next task:** goal, exact scope, start conditions, concrete action and
   completion criterion. Name blockers and accepted trials that must not be
   repeated. When the task is done, replace it with the next one.
2. **Latest version:** current candidate or version, key behaviour,
   branch/revision and delivery link if needed. Briefly separate focused
   checks, full CI, package verification and native result. Never equate
   implementation or automated tests with acceptance in Allplan.
3. **Key errors and necessary earlier context:** keep only information needed
   for the next step, for protecting unresolved state or for avoiding repeats
   of accepted trials. Give symptom/diagnostics, status and a link to the task
   or evidence; keep required execution IDs and result limits.

After a new version, replace the description of the previous one. Reduce older
versions to a short summary only where they still affect work. Remove stale
advice, duplicated results, old build details and resolved blockers. History
stays in Git. Never remove unknown-outcome information or write safeguards just
to shorten the text.

## Updating the development plan

Update existing tasks and their status instead of adding per-version sections.
For open work state what remains, the current blocker/dependency, and the
evidence or condition for closure. Distinguish a bug, a missing API contract,
a missing fixture and a pending native trial. A confirmed resolution removes
the task or leaves a one-sentence result if still needed. Shorten the current
version and next step to a link to the handoff; do not copy delivery, test or
repair chronology.

## When to create a separate file

By default update the handoff, plan and coverage matrix. Do not create separate
handoffs, changelogs, release notes, single-trial plans, session summaries or
status reports. Record a short procedure for the next task and its result in
the existing files. Update installation and test instructions where they live.

The exception is **API behaviour descriptions and API findings**. First extend
the matching document ([editing API notes](m4-editing-api.md), [attribute API
evidence](m4-attribute-api-evidence.md), [type coverage](m4-attribute-type-coverage.md),
[selection API](m4-native-selection-api.md)); create a new one only for a
distinct topic. Give sources, API/build scope, established contracts, limits
and open questions. Separate SDK documentation, hypothesis and native
observation. Do not add a second release history or backlog to an API note;
summarize results relevant to further work in the handoff and update the plan.

Keep raw evidence and machine artifacts required by the testing policy or
diagnosis unchanged in their existing places (`docs/test-results/evidence/`;
raw bridge captures from `logs/evidence/` of the package). Link them instead
of rewriting logs, hashes and full results into documentation.

## Check before finishing

Check that the handoff, plan and coverage matrix agree, remove contradictory or
duplicated information, verify links and review the diff. For
documentation-only changes follow the [testing policy](testing-policy.md):
no runtime tests or builds.
