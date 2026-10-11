# 0.15.0 selected-mark and journal evaluation

**ready_for_owner_test**; native Allplan acceptance of this new scope is pending.
The new gate writes only C04 S02 → S04 through rule_based_edit with C02 explicitly
excluded. It checks full-scope collision/source evidence, readback/replay,
journal history, complete six-column snapshots and one owner Undo/Recover.
Expected 13 + 6 steps, audits **3 → 1 → 3**. Old accepted gates need no repeat.

[Windows ZIP](allplan-mcp-0.15.0-windows-evaluation.zip),
[checksum](allplan-mcp-0.15.0-windows-evaluation.zip.sha256),
[Polish walkthrough](TEST-ALLPLAN-0.15.0.md), [TXT](TEST-ALLPLAN-0.15.0.txt),
[wheel](allplan_mcp_server-0.15.0-py3-none-any.whl),
[delivery record](delivery-0.15.0.json),
[full portable log](portable-tests.log), [focused HTTP log](selected-mark-focused-tests.log),
[build log](build.log), [frozen sync](frozen-sync.log),
[exact extracted installation](package-verification.json).

Clean source **7e3657bc33ecf913376d302da900af386b3b8a23**, source_modified=false.
ZIP **318792 bytes**, SHA-256:

```text
0935043688c97bb950e8c97d1e9c34a0b7c0b69a15ad75ddca53be7fb120db23
```

Final **219 portable tests PASS**, one full local run on Linux CPython 3.12.14,
90.899 seconds. Focused journal/executor/real-HTTP checks cover capacity,
invalid/unknown history, writer lock, historical outcomes after Undo, selected
mark exceptions, excluded-peer source conflict, lost write replies, pre-setter
rejection, durable pointers and complete snapshot/collateral verification.
Frozen sync and wheel/sdist build PASS. The exact ZIP verifies all **23** installed
bridge hashes, retains journal bytes across registration/restore and restores
the previous bridge fixture. These are Linux portable checks; native Allplan
and the Windows Setup UI were not run locally. The approximately 99-MiB sdist
is retained locally and is not committed.

[Source CI 38181795091](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38181795091)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including full tests, builds
and Windows ZIP generation. [Original job/step observations](source-ci-0.15.0.json)
verify the exact source commit. Publication is documentation/artifacts only;
it repeats no product tests/builds or old artifact hash verification.

Install the complete new ZIP against the same Local after closing Allplan/MCP.
Use the same original disposable project after accepted 0.14.1 Undo:
C02=S02, C03 undefined, C04=S02, C05 structure/C06 NEW. Run
M3 Selected Mark.cmd, review the one change and type ZMIEN C04. After its
successful report and UI confirmation, perform one Undo and run
M3 Selected Mark Undo Check.cmd. Leave/save the same copy after Undo.
A lost response uses M3 Selected Mark Recover.cmd only; preserve the saved ID,
Local journal and logs. M3 Journal.cmd inspects historical capacity/blockers
without native model reads, reconciliation or pruning.

Broader 1–32-change acceptance, journal rollover, cross-copy identity, grouped
Undo and crash/power-loss recovery remain unaccepted. Old archives are unchanged.
M3/UAT-05/UAT-06 remain open; PR #2 stays draft into main without merge/release.
