# Diagnostics and repair recovery

## Connection and current state

On the Windows machine running Allplan, keep StartPythonHost and
**Launch Allplan MCP.cmd** running. **Diagnostics.cmd** saves a read-only report
under the extracted package's `logs`: discovery, runtime versions, installed
integrity, session/request IDs and model context. Use local Windows Codex;
cloud localhost cannot reach the bridge. See [Windows setup](windows-setup.md).

Before another repair, read health/context and a fresh full `model_audit` of the
original disposable project with explicit file scope. Use current references and
values. Completed history does not establish current state after Undo/Redo.
Unknown/incomplete data remains not_checked.

## Journal inspection and selected-mark gate

**M3 Journal.cmd** returns capacity, verified historical execution summaries
and invalid/unresolved blockers without native model access or reconciliation.
Use `fix_model_issues` with `{"action":"inspect_journal"}` from local Codex.
An available journal does not establish current model values or writability.
[Inspection contract](m3-journal-contract.md).

**M3 Selected Mark.cmd** is the new 0.15.0 bounded C04 mark gate with excluded
C02. [Polish walkthrough](m3-selected-mark-owner-test.md) defines its exact
retained starting state. **M3 Selected Mark Recover.cmd** and
**M3 Selected Mark Undo Check.cmd** use logs/m3-last-selected-mark-execution.json
and send Recover only, never Apply replay/resume. Retain the immutable identity;
do not rerun the writing gate once a pointer exists.

## Lost replies and recovery

**M3 Conflict.cmd** retains the accepted 0.13.0 same-session source-conflict gate,
with one separately reviewed C03 write. [Owner instructions](m3-conflict-owner-test.md).
**M3 Conflict Recover.cmd** reads `logs/m3-last-conflict-execution.json` and
observes only that C03 execution without Apply replay or resume. An uncertain
stale C04 probe has a separate saved identity; inspect it separately with local
Codex and a fresh audit before any further write. The launcher blocks a rerun
while its pointer records an unresolved execution/probe.

**M3 Numbering.cmd** retains the completed reviewed mark gate from 0.12.0. See
[owner instructions](m3-numbering-owner-test.md). It persists the execution ID
before Apply; it never resumes or rolls back a failed write. The separate
**M3 Numbering Recover.cmd** reads logs/m3-last-numbering-execution.json and
uses read-only recovery, including after UI Undo/host restart.
This accepted batch needs no repeat.

Do not send a new Apply after a lost reply or partial/unknown result. Preserve
the original request/execution ID, project, package logs and installed journal
**Local/.allplan-mcp/repairs**. New IDs can bypass historical deduplication.

**M3 Workflow Recover.cmd** reads `logs/m3-last-workflow-execution.json` and
recovers only the last saved workflow execution. It invokes no Apply replay,
resume or Undo. **M3 Recover.cmd** is retained for the older two-repair record
in `logs/m3-last-execution.json`; its exact-ID replay uses saved history and
cannot repeat setters. Both require the original copy and local bridge.
For other saved executions, the typed MCP request is:

```json
{"action":"recover","execution_id":"<saved 32-hex execution ID>"}
```

Recovery observes old/new/conflicting/unknown values; it does not prove causality
or resume skipped changes. Historical applied outcomes remain historical after
UI Undo. Native acceptance additionally covers [controlled C03 unknown-outcome
recovery after restart](m3-recovery-acceptance-0.14.1.md); crash/power-loss recovery
and broader identity guarantees remain open.

The journal has **128 records**, no automatic eviction/pruning. At capacity,
stop new writes. Setup/Restore preserve it, but bridge backups do not include it.
Before machine migration/restoration, close Allplan/MCP and preserve the entire
journal with the project and package logs. See [execution/recovery](m3-execution-contract.md)
and [journal lifecycle](m3-workflow-execution-contract.md#journal-lifecycle-and-the-128-record-limit).

Completed milestone launchers and repository copies of old logs were removed.
Local owner logs/journals and delivered archives remain untouched; archived
procedures are available through [Git history](validation-status.md#historical-records).

## Controlled unknown-result test — 0.14.1

The [owner walkthrough](m3-recovery-owner-test.md) is completed with
[bounded PASS](m3-recovery-acceptance-0.14.1.md); no repeat is requested.
M3 Recovery Test.cmd writes C03 once and preserves the actual running/unknown
write-ahead record with C04 skipped. Restart StartPythonHost before M3 Recovery
Inspect.cmd; after successful inspection, one Undo and M3 Recovery Undo Check.cmd.
The writing launcher refuses to overwrite any saved recovery-test identity.
All three phases save JSON/TXT under logs/m3-recovery-*. The latest pointer is
logs/m3-last-recovery-execution.json, with an additional per-execution copy.
Preserve both; a lost guard-probe reply retains its separate ID and blocks the
walkthrough pending local Codex inspection. Do not delete journal records or
retry Apply. Read-only inspection/replay can persist current journal observations
but never writes model values or resumes skipped C04.
