# Diagnostics and recovery

Use local Windows Codex with StartPythonHost and **Launch Allplan MCP.cmd**
running. **Diagnostics.cmd** saves read-only discovery/version/integrity/context
data under package logs. [Windows setup](windows-setup.md).

Read health/context and a fresh explicit-scope audit before planning a change.
Historical execution results do not establish current values after Undo/Redo.
Unknown data remains not_checked.

## Unknown results

After a lost reply or partial/unknown result, preserve the original request and
execution IDs, project, logs and **Local/.allplan-mcp/repairs**. Do not send a
new Apply or overwrite/delete pointers. New IDs can bypass deduplication.

```json
{"action":"recover","execution_id":"<saved 32-hex execution ID>"}
```

Recover observes old/new/conflicting/unknown values in the original copy; it
does not resume skipped targets, retry, Undo or prove write causality. Exact-ID
replay returns historical outcomes without setters. After host restart, use
recovery for the saved execution and a fresh preview for any new authorized work.

| Launcher | Saved pointer under package logs |
| --- | --- |
| M3 Workflow Recover.cmd | m3-last-workflow-execution.json |
| M3 Numbering Recover.cmd | m3-last-numbering-execution.json |
| M3 Conflict Recover.cmd | m3-last-conflict-execution.json |
| M3 Selected Mark Recover.cmd / Undo Check.cmd | m3-last-selected-mark-execution.json |
| M3 Recovery Inspect.cmd / Undo Check.cmd | m3-last-recovery-execution.json, plus retained per-execution copies |
| M3 Recover.cmd | m3-last-execution.json, older exact-ID replay/recovery route |

An uncertain conflict/recovery guard probe has a separate saved identity;
inspect that probe and fresh model/journal evidence before further writes.
Completed writing launchers need no repeat; their saved pointers prevent reruns.
Original walkthroughs/reports remain in [historical records](validation-status.md#historical-records).

## History and capacity

**M3 Journal.cmd** or fix_model_issues action=inspect_journal reports verified
historical summaries, slots and invalid/unresolved blockers without native model
access or reconciliation. It is not a backup or proof of current values.
At **128 records**, stop new writes. Never delete IDs to gain slots. Before
migration/restoration close Allplan/MCP and preserve the entire journal, original
project and logs; bridge backups do not include journal history. Use the
[M3 contract](m3-execution-contract.md#journal-lifecycle-and-inspection) for limits.
