# 0.17.2 — highlight matching Columns already on W1

This package is retained as a historical candidate. The later 0.18.1 owner
observation exercised its no-op highlighting behavior; see the
[retained observation](../../docs/m4-native-observation-0.18.1-2026-10-17.md).
Do not repeat the candidate's trial.

The [0.17.1 owner observation](../../docs/m4-column-layer-observation-0.17.1.md)
confirmed the correct classification binding, two W1 updates and healthy
same-session replies. It also exposed the missing highlight for Column 1:
its fire classification was undefined, but it was already on W1.

0.17.2 binds separate `highlight_targets` and `changes` into the reviewed plan.
Highlighting covers all criterion matches, including existing-W1 no-ops;
setters still receive only actual changes. The launcher checks the submitted
count against `highlight_targets`. An all-no-op plan highlights its matches
without confirmation or Apply. Zero matches clear existing highlights. Clear
operates on all highlights in the current document, including other sources.
Unknown/omitted reads, explicit exclusions, source/resource checks, the 32-change
limit, the shared executor and journal/recovery guards retain their scope.
Broad property discovery remains quarantined; the 0.16.0 crash cause is unknown.

Validation for clean source **6e87f56fc3e200c16d229d23e0bf85c483ce1220**:

- **275 portable tests PASS**, CPython 3.12.14, 109.405 seconds;
  [final full log](portable-tests.log). The new six-Column regression highlights
  1/5/6, writes only 5/6, then highlights three no-ops without further writes.
  Real MCP HTTP tests also cover count mismatch rejection, zero matches,
  pending execution identity and recovery after a lost reply.
- **32 affected tests PASS** during implementation; [focused log](focused-tests.log).
  This preceded a documentation-layout correction; the final full run above
  includes that correction and all dependent read/audit/executor/package checks.
- Frozen sync, wheel/sdist and Windows ZIP builds PASS; [build log](build.log).
- Exact ZIP checksum/payload verification, fresh installation, upgrade from
  0.17.1 and restore PASS: **29 installed bridge hashes**, journal and native
  trace bytes preserved. [Verification](package-verification.json),
  [script](verify_package.py). This is portable installation simulation.
- [Source CI 38785067377](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38785067377):
  **6/6 PASS**, Windows/Ubuntu × Python 3.11–3.13, including frozen sync, tests,
  wheel/sdist and Windows package builds; [recorded results](source-ci-0.17.2.json).

[Delivery manifest and artifact hashes](delivery-0.17.2.json).
The artifacts were built once from the clean source above. Later delivery and
status documentation commits do not rebuild that source or alter old archives.

The delivery's native status fields record `not_run` at build time. The owner
later confirmed the corrected no-op highlighting through the same handler in
0.18.1; see the [scoped observation](../../docs/m4-native-observation-0.18.1-2026-10-17.md).
That observation does not accept geometry, writes, Undo or M4 overall.
