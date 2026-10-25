# Diagnostics and recovery

Use local Windows Codex with StartPythonHost and **Launch Allplan MCP.cmd**
running. **Diagnostics.cmd** saves read-only discovery/version/integrity/context
data under package logs. [Windows setup](windows-setup.md).

`ui_dispatch_unavailable` means the queued operation was cancelled before native
execution. `host_timeout` identifies a lost read-only host response; a lost write
still returns `execution_unknown`. OAuth discovery 404s alone do not diagnose
the downstream host. A host access-log `200` is not proof that its reply arrived.

Read health/context and a fresh explicit-scope audit before planning a change.
Historical execution results do not establish current values after Undo/Redo.
Unknown data remains not_checked.

## Native material preview failures

Candidate 0.36.0 adds nested durable records to
`Local/.allplan-mcp/logs/m4-native-probe.jsonl` during material observations
in `model_edit.observe`. SDK imports, identity/ownership reads, native material,
properties and geometry operations record `started` before execution and
`returned` or `failed` afterwards. Entries share the enclosing `probe_id` and
carry the drawing-file, model UUID and root view UUID from the completed M1
scan. Those IDs identify the root being observed; they are not the identities
of every auxiliary child read inside that observation. Property values and
native exception messages are not logged.

After a process crash, retain the first interrupted observation and its nested
entries together with `bridge.log`, the original request and the Allplan crash
log. The last `started` entry without completion narrows the failing operation;
compound operations can still contain multiple SDK accesses. Material reads
precede the full criterion filter, so the requested thickness alone does not
identify the failing root. A missing dump does not justify repeating the crash
on an unchanged candidate. The current bounded next trial is in the
[handoff](next-model-handoff.md).

Tracing preserves the existing 5-second read budget and 8 MiB trace limit.
Storage or budget failures stop the operation; they do not authorize cleanup,
fallback setters or automatic retry.

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
The active execution history holds at most **512 records**, and an individual
record has a separate **1 MiB** limit. The active diagnostic trace has an
**8 MiB** limit. At any capacity error, preserve the journal and trace. Never
delete execution IDs to gain slots. Reviewed, confirmed archival through
`fix_model_issues` preserves unresolved, corrupt and unverifiable records.
See [validation status](validation-status.md) for its accepted scope and the
[handoff](next-model-handoff.md) for current work. Before
migration/restoration close Allplan/MCP and preserve the entire journal, original
project and logs; bridge backups do not include journal history. Use the
[M3 contract](m3-execution-contract.md#journal-lifecycle-and-inspection) for limits.
