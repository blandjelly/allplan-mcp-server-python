# M3 shared workflow execution — portable verification, 0.11.0

Date: 2026-10-10. Status **portable PASS / ready_for_owner_test**.
Expanded native execution **not_run**; M3/UAT-05/UAT-06 remain open.

The full suite passed **178 tests** on Linux/Python 3.12.14 using the frozen
lock (FastMCP 3.2.4, Pydantic 2.13.4). Real local HTTP/MCP tests ran with the
environment's explicit network permission; ordinary sandbox socket denial is
not a product result. Frozen offline sync and wheel/sdist build also pass.
These observations do not constitute Windows/Allplan runtime acceptance.

New supported-execution cases cover one status write leaving four findings,
one selected layer write with an exception, three changes with full snapshot
verification and read-only replay, standard workflow identity mismatch before
setters, a validated foreground file 201 and explicit EXISTING status, excluded
peer source conflict, retained legacy-ack boundary, mark refusal, malformed
typed inputs before native context, and unsupported/incomplete/oversize plans.
Existing partial failure, journal failure/limit, unknown write-ahead recovery,
restart/deduplication, no rollback and native hierarchy checks still pass.

Four new real MCP/HTTP workflow-launcher tests establish:

- Two separately confirmed single-target standard/rule writes, audit 5 → 4 → 3,
  ten successful steps, distinct saved execution IDs and one setter per target.
- A lost reply after the first applied write retains its durable identity;
  recovery sends **only Recover**, observes that one value and leaves S06 NWE.
- Known pre-setter rejection persists rejected and recovery sends no request.
- An incorrect fixture blocks before confirmation; cancelling the second
  confirmation preserves the completed first write without the second setter.

The Windows ZIP contains M3 Workflow Apply.cmd / M3 Workflow Recover.cmd;
package tests check deterministic builds, extracted integrity, full recursive
registration and version/lock consistency. The delivered archive's clean source,
sizes, hashes and exact extracted registration are recorded separately in the
[0.11.0 delivery](../../evaluation-packages/0.11.0/README.md).
Original earlier archives and native evidence remain unchanged.

Next required observation: [native workflow-write card](../m3-workflow-apply-batch.md).
Actual mark writes/numbering, native same-session conflict and partial/unknown
recovery, storage/copy identity guarantees and final integration remain open.
