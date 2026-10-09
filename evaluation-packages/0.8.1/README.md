# Evaluation delivery — 0.8.1

Status **ready_for_owner_test**; corrected native write/readback/Undo **not_run**.
The 0.8.0 request was rejected before setters by an overly broad IsInMacro check.
[Evidence and diagnosis](../../docs/test-results/m3-apply-rejection-0.8.0.md).
The original archive and four owner logs are unchanged.

Download and completely extract
[allplan-mcp-0.8.1-windows-evaluation.zip](allplan-mcp-0.8.1-windows-evaluation.zip).
Follow [the updated Polish write/restart/Undo card](../../docs/m3-apply-batch.md).
Use the same unchanged disposable project copy with a fresh preview/ID; do not
replay the failed 0.8.0 request. No Undo/Recover is required for that rejection.

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
do not establish native write effects or Undo. M3/UAT-05/UAT-06 remain open.
No GitHub release or redistribution/license claim is made by this delivery.
