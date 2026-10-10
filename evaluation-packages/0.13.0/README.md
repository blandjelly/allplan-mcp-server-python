# 0.13.0 same-session source-conflict evaluation

Native gate: **ready_for_owner_test**; no 0.13.0 Allplan observation yet.
M3/UAT-05/UAT-06 remain open. The shared executor still invalidates all plans
at execution start. Invalidated evidence is retained for one read-only source
comparison within the original shared TTL/count/byte limits; it never renews
Apply authorization, including after Undo.

Source: **752e54795a1cfa676217b5ffba0ce5d301383269**, source_modified=false.
The exact ZIP is **277253 bytes**, SHA-256:

```text
7a7fceab96a1979e71009b327dacf77b3fc4665a3b3a41a8d2de665254bd0180
```

[Windows evaluation ZIP](allplan-mcp-0.13.0-windows-evaluation.zip),
[checksum](allplan-mcp-0.13.0-windows-evaluation.zip.sha256),
[wheel](allplan_mcp_server-0.13.0-py3-none-any.whl),
[delivery record](delivery-0.13.0.json),
[portable log](portable-tests.log), [build log](build.log).
Archives are preserved exactly from the clean source; documentation publication
repeats no tests/builds. The approximately 98 MiB sdist was built and verified
locally under dist; it is omitted from this Git delivery because it includes
nested historical delivery archives. Its exact local identity is in the record.

Local verification: **195 tests PASS** on Linux CPython 3.12.14, one full final
candidate run after focused plan/HTTP checks. Frozen sync and wheel/sdist build
PASS. Exact extracted registration/integrity/restore fixture PASS: all **23**
bridge hashes match; registration and restore preserve the journal sentinel
and restore the previous bridge fixture. These checks do not execute Windows
Setup UI or Allplan. Source compatibility CI is recorded separately below.

Source CI **6/6 PASS** for clean source 752e54795a1cfa676217b5ffba0ce5d301383269:
[run 38079063575](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38079063575),
Windows/Ubuntu Python 3.11–3.13, including full tests, wheel/sdist and Windows ZIP
builds. [Exact job/step observations](source-ci-0.13.0.json) are retained.


The new [Polish Markdown](TEST-ALLPLAN-0.13.0.md) / [text](TEST-ALLPLAN-0.13.0.txt)
walkthrough requires no code/JSON edits. Install this package, keep the original
disposable project/file 101 and host/MCP running, then use **M3 Conflict.cmd**.
The launcher creates two selected previews, executes only separately reviewed
C03 undefined → S03, rejects the stale C04 plan and compares its retained full
source evidence against the changed excluded peer. Expected 12 steps pass in
one host session; C04/C02 remain S02. One owner Undo restores C03; use
**M3 Conflict Recover.cmd** for current-value read-only observation.

This is a new conflict/inspection gate, not a repeat of accepted two-target
numbering or layer/status gates. It does not accept native manual UI editing,
partial/unknown execution recovery, wider scopes, cross-copy identity or crash
persistence. Partial/unknown native recovery follows evaluation of this lifecycle
result. Preserve Local journal/logs and the original project; no new Apply after
an uncertain result. The stale rejection probe has a separate saved identity
if its reply is lost. Existing 0.11.0/0.12.0 artifacts remain unchanged.
