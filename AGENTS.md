# Instructions for future work

The canonical M4 development branch is **develop/m4**. Start M4 topic branches
from it and target PRs to it. Keep main separate. See the current checkout and
handoff instructions in [the M4 handoff](docs/next-model-handoff.md).

At the start of each chat, read [the testing policy](docs/testing-policy.md) and
[the current handoff](docs/next-model-handoff.md). Identify the checkout and
branch, source state, and change scope before choosing checks. Keep focused,
full CI, and native Allplan results distinct; the model owns automated checks
and GitHub CI, while the owner performs only the brief Allplan trial requested
for a candidate. Follow the policy as the single source of truth for test and
build decisions. An explicit owner pause takes precedence.

- During iteration, run affected/dependent tests only; keep the PR in draft.
- For documentation/evidence only, check diff and links, without runtime tests or builds.
- For a final candidate, use full CI instead of repeating the full suite locally.
- Standard candidate: Windows/Ubuntu on Python 3.12; compatibility changes and
  main integration/release: six configurations. A project-version bump alone is exempt.
- Build once after CI and verify the exact delivered ZIP once. Preserve completed
  native observations and all runtime write/journal safeguards.
