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

## Lost replies and recovery

**M3 Numbering.cmd** runs only the new reviewed mark gate in 0.12.0. See
[owner instructions](m3-numbering-owner-test.md). It persists the execution ID
before Apply; it never resumes or rolls back a failed write. The separate
**M3 Numbering Recover.cmd** reads logs/m3-last-numbering-execution.json and
uses read-only recovery, including after UI Undo/host restart.

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
UI Undo. Native recovery acceptance covers a completed execution after Redo;
controlled native unknown-outcome recovery remains open.

The journal has **128 records**, no automatic eviction/pruning. At capacity,
stop new writes. Setup/Restore preserve it, but bridge backups do not include it.
Before machine migration/restoration, close Allplan/MCP and preserve the entire
journal with the project and package logs. See [execution/recovery](m3-execution-contract.md)
and [journal lifecycle](m3-workflow-execution-contract.md#journal-lifecycle-and-the-128-record-limit).

Completed milestone launchers and repository copies of old logs were removed.
Local owner logs/journals and delivered archives remain untouched; archived
procedures are available through [Git history](validation-status.md#historical-records).
