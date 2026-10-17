# Candidate CI procedure — verification on 2026-10-17

The owner approved focused iteration, final-candidate CI replacing duplicate
full local runs, one package build, and instructions that persist across chats.
Root [AGENTS.md](../../AGENTS.md) requires reading the
[testing policy](../testing-policy.md) and the branch handoff first.

Verification of source **52d7d071a2ae572050a59383f05eb62f5f8cc03b**, based on
main's accepted M0–M2 baseline (0.6.1), in
[PR #9](https://github.com/blandjelly/allplan-mcp-server-python/pull/9):

- **23 focused stdlib tests PASS** locally. Cases cover draft/docs skips,
  two-platform candidates, project-version-only TOML changes, real dependency
  and interpreter changes, main integration and missing-history fallback.
  Tests exercise real temporary Git repositories and GitHub output files.
- Workflow YAML and documentation links checked. No full local product suite
  or local package build was repeated.
- [Final-candidate CI 39029955557](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39029955557):
  **6/6 Windows/Ubuntu × Python 3.11–3.13 test jobs PASS** and **one package job
  PASS**, after configuration. Each test job runs the full suite; the Windows
  3.12 log records **144 tests PASS** (121 baseline tests plus 23 policy tests).
  This full matrix is appropriate for this workflow change and main integration.
  The one package job builds wheel/sdist/ZIP and uploads
  `candidate-52d7d071a2ae572050a59383f05eb62f5f8cc03b`.

The same procedural files were copied unchanged to the M4 development branch
in **02f816320d3435fda12a6d314ca7d1dfa4e99c00**. This does not integrate M4
runtime into main or replace M4's separately scoped automated/native evidence.

- The selector was exercised against the actual 0.18.1 → 0.18.2 source diff
  (`194088c` → `47ec1ad`): a ready feature candidate selects **two jobs**, as
  the project-version bump changes neither locked dependencies nor build settings.
- [Draft M4 PR CI 39030028417](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39030028417):
  configuration **PASS**, portable and package jobs **skipped**. The change
  correctly did not repeat M4's full product suite or package build while draft.

Subsequent documentation-only commits preserve these source scopes and do not
repeat the product jobs. No new owner-test package, runtime version or native
Allplan acceptance is claimed by this procedural change.
