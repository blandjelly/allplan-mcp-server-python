# Implementation plan

M4 development uses **develop/m4**; main integration is separate.
Read the [current handoff](next-model-handoff.md) for the version and next task,
the [office editing plan](office-editing-development-plan.pl.md) for the
backlog, and the [testing policy](testing-policy.md) for checks and builds.

## Accepted fixture baseline

| Stage | Accepted scope |
| --- | --- |
| M0 | Installation, update/restore, health/version/box tools and host lifecycle. |
| M1 | Explicit model context, typed query, selection pages, summaries, resource binding and canonical geometry. |
| M2 | Read-only audit profile, coverage, evidence and locatable findings. |
| M3 | Bounded preview/apply/revalidate, layer/status/mark repairs, stale guards, journaling, replay/readback and controlled unknown-result recovery. |

Acceptance is limited to the retained fixture and recorded scopes in
[validation status](validation-status.md). It does not establish arbitrary
multi-file writes, universal project identity or whole-project coverage.
M4 remains partially accepted; its remaining gates are maintained only in
the office editing plan.

## Later scope

Model generation, layouts, issue exports and whole-project documentation are
future work. Specify their inputs, ownership, conflicts, recovery and native
acceptance independently; they do not expand the accepted M4 scope.
