# Evaluation delivery — 0.9.0

Status **ready_for_owner_test**, native standard/selected preview **not_run**.
The accepted 0.8.1 [stale Apply gate and original uploads](../../docs/test-results/m3-stale-apply-acceptance-0.8.1.md)
remain unchanged. 0.9.0 adds preview-only standard and predicate/exception
repair workflows over the shared audit/planner; standard/selected Apply is
unavailable. [Contract](../../docs/m3-standards-contract.md).

Download and completely extract
[allplan-mcp-0.9.0-windows-evaluation.zip](allplan-mcp-0.9.0-windows-evaluation.zip),
then follow [the read-only owner card](../../docs/m3-standards-preview-batch.md).
Use the current repaired disposable six-column copy, S05 SZ_OGÓ01 and S06 NEW.
The new **M3 Standards Preview.cmd** checks standard, selected/excepted and empty
previews with revalidation and complete before/after audit. It invokes no
Apply/Recover/Undo. No earlier native batch or fixture rebuild is requested.

Exact clean source **61c7579645d497a9df1e3ff0cb5640861225b56c**.
Windows ZIP **624503 bytes**, SHA-256:

```text
c4cf31d6b08c651c10e4020062d5c0d0dba6d5ea0380b748c16b6c8f9d349e33
```

[Delivery manifest](delivery-0.9.0.json) records all ZIP/hash/wheel/sdist sizes
and hashes. The ZIP has source_modified=false; two builds from the clean source
are byte-identical. Exact extracted-package integrity and recursive registration
pass with all 22 bridge files. Publication documentation does not rebuild it.

[155 local tests PASS](../../docs/test-results/m3-standards-portable-0.9.0.md),
frozen sync and wheel/sdist build pass. GitHub CI status is recorded separately
for its exact commit/run. Portable evidence is not native new-tool acceptance.
M3/UAT-05/UAT-06, marks/numbering and selected native writes remain open.
No GitHub release or redistribution/license claim is made by this delivery.
