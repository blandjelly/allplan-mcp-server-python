# Evaluation delivery — 0.8.0

Status **ready_for_owner_test**. Native writes/readback/Undo **not_run**.
Download and completely extract
[allplan-mcp-0.8.0-windows-evaluation.zip](allplan-mcp-0.8.0-windows-evaluation.zip).
Follow the [Polish disposable-copy write/Undo card](../../docs/m3-apply-batch.md)
included in the ZIP; no Python/JSON editing is needed.

Built from clean source **d1b406318a24b52792cacc8560745e4a596cd1f3**.
Windows ZIP SHA-256:

```text
e21fe594372dde28d88d2fece2842fa8263d023f8410592c1239a7c052f8278c
```

[Delivery manifest](delivery-0.8.0.json) records all exact file hashes/sizes.
Wheel/sdist are preserved for reproducibility; Windows owner testing uses the ZIP.
The package's embedded handoff is the clean-source handoff, before artifact
publication and later CI observations. Updated repository documentation may
record those observations without rebuilding/replacing this ZIP.

146 local portable tests pass, including real MCP/HTTP with stateful fake native
adapters and mutation/recovery/failure cases. Portable checks do not establish
Allplan writability, API effects, model appearance, restart persistence or Undo.
Keep the tested 0.7.0 and earlier archives unchanged. Preserve execution records
in the real Allplan `Local/.allplan-mcp/repairs` and package `logs` across restart.
If an apply response is lost, use **M3 Recover.cmd**; do not rerun **M3 Apply.cmd**.
No GitHub release or public distribution/license claim is made by this delivery.
