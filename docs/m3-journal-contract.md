# Repair journal inspection — 0.15.0

`fix_model_issues` accepts `{"action":"inspect_journal"}`. The dependency-free
host validates this request before any native API/document lookup. It acquires
the existing journal writer lock and returns schema `m3-journal-inspection-1`:
verified execution summaries, record count/limit, remaining slots and blockers.
`M3 Journal.cmd` saves the same read-only response in package logs.

This is inspection of installed Local history, not model reconciliation or a
backup. It creates the journal directory/lock if absent, but never changes,
deletes or recovers execution records. No model scan, setter, Apply replay or
Undo is requested. Completed/applied summaries remain historical after Undo.
Use saved-ID Recover on the original copy to observe current values.

At most 128 records of 1 MiB each are inspected. A 129th file makes `complete`
false, `record_count` null and adds capacity_exceeded; the bounded subset is not
a complete inventory. Exactly 128 records adds journal_full. Running/unknown
records add recovery_required, retaining their original execution IDs. Invalid
JSON, oversized records, hash mismatches and invalid identity/outcome structures
add invalid_record; other verified entries are still shown. The same structural
validation now protects exact-ID replay and new-write journal scanning.
An unavailable directory or competing writer returns repair_journal_unavailable.

The existing journal limit, no-eviction policy and saved-ID guards are unchanged.
`state=available` means these storage checks passed; it does not establish native
writability, copy identity or current model values. A completed final-slot write
may correctly leave the journal full while its saved replay/recovery remain usable.
Preserve Local/.allplan-mcp/repairs, project and logs before migration; Setup and
Restore preserve records but bridge backups do not back them up. There is no
rollover, restore/import or pruning operation. Do not delete identities to gain slots.

Portable validation uses real journal files and MCP/bridge HTTP with stateful
native fakes. [Bounded native 0.15.0 acceptance](m3-selected-mark-acceptance-0.15.0.md)
verifies healthy journal summaries 6 → 7 → 7 records alongside one selected C04
mark write/replay and Undo/recovery. It does not establish native capacity,
corruption, unresolved-record handling, migration or pruning. Original recovery
acceptance keeps its recorded 0.14.1 scope. No completed gate needs repeat;
further work is paused at the owner's request.
