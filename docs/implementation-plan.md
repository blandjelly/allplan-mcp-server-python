# Implementation plan

Current M4 status and remaining acceptance gates are in the
[current handoff](next-model-handoff.md) and the detailed
[office editing development plan](office-editing-development-plan.pl.md).
Choose checks and package builds from the [testing policy](testing-policy.md).

## Accepted fixture baseline

| Stage | Accepted scope |
| --- | --- |
| M0 | Installation, update/restore, health/version/box tools and host lifecycle. |
| M1 | Explicit model context, typed query, selection pages, summaries, resource binding and canonical geometry. |
| M2 | Read-only audit profile, coverage, evidence and locatable findings. |
| M3 | Bounded preview/apply/revalidate, layer/status/mark repairs, stale guards, journaling, replay/readback and controlled unknown-result recovery. |

M0–M3 acceptance is limited to the retained test project and recorded scopes in
[validation status](validation-status.md). It does not establish universal
project identity, arbitrary multi-file writes, or whole-project coverage.

## M4 — editing workflows

M4 development uses **develop/m4**; main remains separate. The current package
candidate is **0.23.0**. The latest owner report confirms concrete attribute
operations on Slabs and Columns, but lacks an exact installed manifest. The
journal cleanup path is implemented and its short native trial is still
pending. Keep accepted results and remaining gaps distinct; do not repeat
accepted owner observations. The handoff and office editing plan identify the
next scoped work.

## Later scope

Model generation, layouts, issue exports, and whole-project documentation are
future work. Defer them until their inputs, ownership, conflict behavior,
recovery, and native acceptance can be specified independently. They do not
expand the accepted M4 scope by implication.
