# Repository branches — M4 consolidation

Updated **2026-10-17 Europe/Warsaw**. The shared development branch is
[`develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/tree/develop/m4).
New M4 topic branches start there and their PRs target **develop/m4**.
`main` remains a separate accepted baseline; this consolidation neither updates
main nor opens a runtime integration PR to it. The existing M3 PR is unchanged.

## Preserved history

`develop/m4` was created at **cf3c4bb92e54903efa8e7c886d06b31a56b52d3b**,
the latest `fix/m4-wall-sample` head. All older M4 heads below are ancestors;
each had **zero commits missing** from that source. No runtime merge, squash,
cherry-pick or history rewrite was needed.

| Retained legacy ref | Head included at consolidation | Historical PR |
| --- | --- | --- |
| `codex/m4-property-discovery` | `e7f61dbbe6d8c96de7c676eea7bcd7f4eb470c2e` | [#5](https://github.com/blandjelly/allplan-mcp-server-python/pull/5) |
| `codex/m4-0.18.0` | `0dbe7cf9ba509555e9098c288a962183ae4e7ecc` | [#6](https://github.com/blandjelly/allplan-mcp-server-python/pull/6), originally headed by `codex/m4-0.17.0` |
| `fix/m4-host-timeout` | `0860438bb5f11483ffbe6ab75bc1d6b833cb1e0d` | [#7](https://github.com/blandjelly/allplan-mcp-server-python/pull/7) |
| `fix/m4-wall-sample` | `cf3c4bb92e54903efa8e7c886d06b31a56b52d3b` | [#8](https://github.com/blandjelly/allplan-mcp-server-python/pull/8) |

PRs **#5, #7 and #8** are closed as superseded by the common branch. PR **#6**
was already closed and now links to the common branch as well. Their original
descriptions, evidence and scoped acceptance remain in place. Closed here does
not mean merged into their former targets or acceptance of the entire M4 scope.

Legacy branches remain available for package/evidence URLs. After this
documentation update, `fix/m4-wall-sample` is fast-forwarded to the same
consolidation snapshot as `develop/m4`, so links from main's existing handoff
lead to the new branch instructions. It is a compatibility ref, not a second
development line. Do not develop on or delete legacy refs during this cleanup.

## Continuing work

Read [AGENTS.md](../AGENTS.md), [testing policy](testing-policy.md) and
[current handoff](next-model-handoff.md), then use the common branch:

```sh
git fetch origin
git switch develop/m4
git pull --ff-only origin develop/m4
git switch -c topic/m4-description
```

Open the topic PR with **base `develop/m4`** and keep it draft while iterating.
Use affected/dependent tests; a final code candidate follows the testing policy.
Do not restart the superseded PR chain or merge M4 into main as part of this task.

This consolidation changes only refs, PR metadata and documentation. Runtime,
dependency lock, CI workflow, version **0.18.2**, frozen packages and native
evidence are unchanged. Validation is ancestry checks, documentation diff and
links; no full suite, build or native observation is repeated. The confirmed
single-Wall read remains scoped to 240 mm / `Beton`; full-Wall filtering,
highlighting and material writes remain unverified.
