# M3 execution portable validation — 0.8.0

Status **ready_for_owner_test**; native write/readback/Undo **not_run**.
The [owner gate](../m3-apply-batch.md) is required before native acceptance.
The [accepted 0.7.0 ZIP](../../evaluation-packages/0.7.0/README.md) and original
native evidence are unchanged.

Implemented: bounded two-Column foreground-file-101 evaluation apply, fresh
full audit/source and target checks, exact old/new values, documented
ChangeLayer short-name / ChangeAttributes tuple/list APIs, stop-on-failure,
fresh target readback, whole returned audited-field comparison and final audit.
Local OS lock and atomic write-ahead execution records prevent same-ID replay
from calling setters after restart or UI Undo. Read-only recovery observes
old/new/conflict/unknown values without resuming writes or invoking Undo.

Validation on Linux Python **3.12.14**, pinned FastMCP **3.2.4** and uv **0.12.19**:

- Full portable suite: **146 tests PASS**.
- Frozen dependency synchronization; wheel/sdist build; deterministic Windows
  source-only ZIP and fresh recursive registration/integrity checks pass.
- Stateful fake adapter tests check both exact API argument shapes, all-target
  preflight, manual-source conflicts, denied native eligibility, no-change
  readback, exceptions, crash after the write-ahead marker, post-write disk
  failure, journal corruption, writer exclusion, capacity/no eviction, replay
  after restart/Undo, recovery project mismatch and collateral audited changes.
- Real MCP/HTTP owner workflow checks cancellation without setters, two writes,
  three remaining findings, stored-ID replay, read-only recovery/Undo inspection
  and lost completed reply with saved identity and no automatic retry.

The scripts save original JSON/TXT and the recovery execution request before
any HTTP mutation call. The Windows launchers require no Python/JSON editing.
Portable tests do not prove native eligibility semantics, setters, persistent
storage on the Windows host, one/two-step Undo or model appearance. Neither
power-loss durability nor identity across project copies/machines is accepted.
Remote CI must be checked for the published commit separately; no unobserved
CI result is inferred here. [Contract and limits](../m3-execution-contract.md).
