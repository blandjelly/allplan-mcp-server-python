# M3 0.8.1 regression validation

This report records the pre-owner-test portable validation. The subsequent
**bounded native execution gate PASS** on 2026-10-10 Europe/Warsaw is recorded
[separately with six original logs](m3-execution-acceptance-0.8.1.md).
[Native 0.8.0 rejection](m3-apply-rejection-0.8.0.md) and original uploaded files
are preserved; previous archives remain unchanged.

**149 portable tests PASS** on Linux Python 3.12.14, FastMCP 3.2.4, uv 0.12.19.
Frozen synchronization, wheel/sdist build, deterministic Windows ZIP/integrity
and recursive registration are verified separately from native acceptance.

Added regressions establish:

- Terminal native Column roots with IsInMacro=true can pass the independent
  required hierarchy/eligibility checks, execute exactly two setters, retain
  raw flags and produce three remaining findings with verified audited fields.
- Macro/MacroPlacement/unknown ancestors cannot resolve to the reviewed
  terminal Column and do not invoke setters.
- Real MCP/HTTP explicit native eligibility rejection is structured `rejected`,
  records `native_setters_started=false` and finalizes the client recovery pointer.
  Recovery of that rejected request sends neither a recovery request nor an
  apply replay. Required inactive/label/invalid-target checks still reject.
- Existing lost-response, crash, disk failure, corruption, concurrency,
  persistent replay and UI-Undo simulation regressions remain passing; journal/
  transport failures are not misclassified as safe pre-write rejections.

Only known host codes that escape before the current request's setters are
classified; no message-text parsing is used. Portable adapters do not prove native
parent semantics, writability or mutation effects. The corrected
[write/restart/Undo card](../m3-apply-batch.md) is complete for the retained
fixture; do not repeat that test. The manual-edit UI action interrupted the host;
[native restart invalidation passes](m3-plan-restart-acceptance-0.8.1.md), while
same-session source conflict remains blocked. The next native evidence is the
[stale-Apply rejection card](../m3-stale-apply-batch.md).

[CI run 37997427257](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37997427257)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
published artifact commit **25dc292cf72776663feea80cc5bbe13b975ceff5**.
This is separate from Allplan acceptance and later documentation-only CI.
