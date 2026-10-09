# Evaluation delivery — 0.8.1

Status **bounded native execution gate PASS**, 2026-10-10 Europe/Warsaw:
[original six owner logs and acceptance](../../docs/test-results/m3-execution-acceptance-0.8.1.md).
The two retained writes/readbacks, audited-field comparison, exact-ID replay
across host sessions, **two-step native Undo**, and recovery after confirmed Redo
pass. Do not repeat Apply; use the installed package and repaired copy for the
[next stale-Apply rejection card](../../docs/m3-stale-apply-batch.md).
The subsequent UI action interrupted the host; native same-session conflict
is blocked, while [old-plan rejection after restart passes](../../docs/test-results/m3-plan-restart-acceptance-0.8.1.md).
The [stale Apply rejection gate also passes](../../docs/test-results/m3-stale-apply-acceptance-0.8.1.md),
with identical complete before/after audits and unchanged UI values/appearance.
Do not repeat these accepted gates. The next M3.3 read-only preview test uses
the separately versioned [0.9.0 package](../0.9.0/README.md).
The delivery manifest and embedded archive record the original pre-test state;
this document supersedes that acceptance status without changing the artifacts.
The 0.8.0 request was rejected before setters by an overly broad IsInMacro check.
[Evidence and diagnosis](../../docs/test-results/m3-apply-rejection-0.8.0.md).
The original archive and four owner logs are unchanged.

Download and completely extract
[allplan-mcp-0.8.1-windows-evaluation.zip](allplan-mcp-0.8.1-windows-evaluation.zip).
Follow [the updated Polish write/restart/Undo card](../../docs/m3-apply-batch.md).
The write card retains the original test procedure; no reinstall or new Apply
is required after the accepted test. The failed 0.8.0 request needs no Undo/Recover.

Exact clean source **8074905536ff5c95e20de4a59a70d513f8694314**.
Windows ZIP SHA-256:

```text
b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47
```

[Delivery manifest](delivery-0.8.1.json) records sizes/hashes of the unchanged
ZIP, companion hash, wheel and sdist. The embedded handoff records the clean-source
state; later publication/CI documentation does not rebuild this artifact.

149 local tests PASS;
[CI run 37997427257](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37997427257)
passes all six Windows/Ubuntu Python 3.11–3.13 jobs for artifact commit
`25dc292cf72776663feea80cc5bbe13b975ceff5`. Frozen sync, build and deterministic Windows package/
integrity/recursive registration checks pass. Portable tests and API reference
remain separate from the bounded native decision above. M3/UAT-05/UAT-06 remain open.
No GitHub release or redistribution/license claim is made by this delivery.
