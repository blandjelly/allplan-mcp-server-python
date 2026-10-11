# 0.14.1 corrected controlled recovery evaluation

The 0.14.0 owner attempt blocked before Apply at numbering_preview because
UUID order placed C04 ahead of C03. No execution ID or native write was reached.
[Diagnosis](../../docs/m3-recovery-blocked-0.14.0.md). 0.14.1 preserves generated
spatial numbering assignment order before hashing the reviewed plan. Exact
CLI/host C03-first guards remain enforced; inspection/replay never resume C04.
Native recovery remains **ready_for_owner_test**, with no acceptance yet.

[Windows ZIP](allplan-mcp-0.14.1-windows-evaluation.zip),
[checksum](allplan-mcp-0.14.1-windows-evaluation.zip.sha256),
[Polish instructions](TEST-ALLPLAN-0.14.1.md), [TXT](TEST-ALLPLAN-0.14.1.txt),
[wheel](allplan_mcp_server-0.14.1-py3-none-any.whl),
[delivery record](delivery-0.14.1.json), [portable log](portable-tests.log),
[build log](build.log), [frozen sync](frozen-sync.log),
[exact package verification](package-verification.json).

Clean source **1810e4fa284311e204b9133deee3245f8427697b**, source_modified=false.
ZIP **301564 bytes**, SHA-256:

```text
b5a7702f556ff68533e3e090252617dc7f76025dc4615a0b3a9169119b9ccd83
```

Final **207 portable tests PASS**, one full run on Linux CPython 3.12.14.
Focused host control/ordinary numbering and real HTTP recovery tests use the
owner UUID order; restart/Undo inspection, collateral fields, replay/no-resume,
lost responses and pre-Apply rejection/retry pass. Frozen sync, wheel/sdist
builds and exact extracted installation/integrity/restore PASS. All **23** bridge
hashes match; the journal is preserved and previous bridge fixture restored.
These local fakes/HTTP checks execute no native Allplan.
[Source CI 38179275055](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38179275055)
**6/6 PASS**, Windows/Ubuntu Python 3.11–3.13, including tests/builds.
[Job/step observations](source-ci-0.14.1.json) are separate from local checks. The approximately 98-MiB sdist stays local.

For this confirmed pre-Apply block, leave the original project unchanged:
**no Undo**. Preserve 0.14.0 logs and Local/.allplan-mcp/repairs. Close Allplan/MCP,
extract the new ZIP into its own folder and run Setup.cmd against the same Local.
Repeat only the uncompleted recovery gate on the same retained disposable copy:
Test → restart StartPythonHost → Inspect → one Undo → Undo Check. End saved
after Undo. Once an execution ID has been saved, never repeat the writing gate;
use inspection for unknown results. [Exact walkthrough](TEST-ALLPLAN-0.14.1.md).

Older packages remain unchanged. M3/UAT-05/UAT-06 and first MVP remain open;
PR #2 stays draft into main, with no merge/release.
