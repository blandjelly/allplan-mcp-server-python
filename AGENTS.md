# Instructions for future work

The canonical M4 development branch is **develop/m4**. Start M4 topic branches
from it and target PRs to it. Keep main separate. See the current checkout and
handoff instructions in [the M4 handoff](docs/next-model-handoff.md).

At the start of each chat, read [the documentation policy](docs/documentation-policy.md),
[the testing policy](docs/testing-policy.md), [the current handoff](docs/next-model-handoff.md)
and [the development plan](docs/office-editing-development-plan.pl.md).
Follow the documentation policy when updating project state; keep the handoff and
plan concise and current, without adding release histories or redundant files.
Identify the checkout, branch, source state, and change scope before choosing
checks. Keep focused, full CI, and native Allplan results distinct.
Follow the testing policy as the single source of truth for test and build
decisions and the responsibility split below. An explicit owner pause takes precedence.

- Codex owns analysis, implementation, focused affected/dependent tests, version
  consistency checks, commit, push and PR preparation. Keep the PR in draft
  during iteration; mark the final candidate Ready for review, hand over the
  commit SHA and PR link, then end the task.
- GitHub Actions runs the required full CI matrix and automatically builds
  artifacts after successful tests, as defined in the testing policy.
- The owner monitors CI, checks required jobs and the tested commit, downloads
  the ZIP, verifies the package and required installation/upgrade/restore
  procedures, and merges into develop/m4 only after all required gates pass.
  The owner supplies failed-test logs to Codex for diagnosis.
- Codex performs CI supervision, artifact retrieval, fallback builds, full CI
  reruns or PR merges only when explicitly requested by the owner; see the
  testing policy for the exact boundaries.
- For documentation/evidence only, check diff and links, without runtime tests
  or builds. Preserve completed native observations and all runtime
  write/journal/hash safeguards.
