# 0.14.0 controlled unknown-result/restart recovery evaluation

Native gate: **ready_for_owner_test**, no native acceptance yet. This new gate
writes only C03, retains the actual running/unknown write-ahead marker before
readback, and leaves C04 skipped. Recover and exact-ID replay never resume it.
Previous conflict/numbering gates need no repeat. M3/UAT-05/UAT-06 remain open.

[Polish MD instructions](TEST-ALLPLAN-0.14.0.md), [TXT instructions](TEST-ALLPLAN-0.14.0.txt),
[Windows ZIP](allplan-mcp-0.14.0-windows-evaluation.zip),
[checksum](allplan-mcp-0.14.0-windows-evaluation.zip.sha256),
[wheel](allplan_mcp_server-0.14.0-py3-none-any.whl),
[delivery record](delivery-0.14.0.json), [portable log](portable-tests.log),
[build log](build.log), [exact extracted package verification](package-verification.json).

Source **7ead0e9798c6c93a843fbfc8e9b5e33a58763fdd**, source_modified=false.
ZIP 297645 bytes; SHA-256:

```text
dbd4e25a0df13cf384a54e7e253e939729c4a0510e37b44cef095d81ad987d66
```

Final **205-test portable PASS** on Linux CPython 3.12.14, following focused
control/executor/real-HTTP checks. A previous 204-test candidate passed; the
explicit pre-setter rejection correction added an HTTP test and required the
new final run. Frozen sync and wheel/sdist builds PASS. The approximately
98-MiB sdist remains local because it includes older delivery archives.
Exact extracted registration/integrity/restore PASS: **23** installed bridge
hashes, prior bridge fixture restored and journal preserved. Native Allplan
was not run here. Pre-setter rejection is explicit and inspection sends no
Recover for a request rejected before setters.

Final source [CI 38175934542](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38175934542)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including full portable tests and builds.
[Original job/step observations](source-ci-0.14.0.json) are separate from local checks.

Start with the original disposable project saved after 0.13.0 Undo: C03
undefined, C04/C02=S02; C05 structure and C06 NEW retained. Keep Local journal/logs.
Run M3 Recovery Test.cmd → restart StartPythonHost → M3 Recovery Inspect.cmd →
one Undo → M3 Recovery Undo Check.cmd. The gate saves each identity before Apply
and blocks repeating its writing launcher. End by saving the same copy after Undo.
[Contract and limits](../../docs/m3-recovery-contract.md).

Original 0.11.0/0.12.0/0.13.0 artifacts are unchanged. Documentation publication
must not rebuild or substitute this package; a future runtime change needs a new version.
PR #2 remains draft into main, with main ancestry reconciled but no M3 merge/release.
