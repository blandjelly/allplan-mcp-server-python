# Current handoff

Updated 2026-10-14 Europe/Warsaw. Candidate **0.17.0**, based on M4
`e7f61dbbe6d8c96de7c676eea7bcd7f4eb470c2e`; no main integration or native acceptance.

The owner requested the full first scenario and explicitly accepted highlighting:
Columns without fire resistance → exact targets highlighted → existing W1.
[Implementation, limits and owner walkthrough](m4-column-layer-0.17.0.pl.md).

The uploaded 0.16.1 report contains one successful raw Column read bracketed by
healthy replies from the same host. The owner reports no crash. Names, layers,
UI and writes were not requested, so this is not acceptance of the new workflow.
The 0.16.0 native root cause is still unknown; retain its FAIL_CRASH record and
quarantine. New workflow avoids broad definition/enum calls and retains native
container owners through writes/readback. Do not infer native crash containment.

`column_layer` previews criteria directly, without fake audit findings, and uses
the shared RepairExecutor/journal. Unknown/absent-from-ReadAll values block Apply;
matched Columns already on W1 are no-op. Full source/resource revalidation,
exact highlight, native writability, readback and bounded journal guards remain.
The old isolated probe launcher remains available, but the new task uses
**M4 Columns to W1.cmd** and **M4 Columns Recover.cmd**.

Next: new 0.17.0 observation in the retained copy, not a repeat of old M3 gates.
Preserve source/CI/package scopes, all logs and Local/.allplan-mcp/repairs.
After unknown results use saved-ID Recover, never a new Apply. Check UI and Undo;
do not label this accepted_on_build before receiving native evidence.

M3 acceptance remains limited to its historical fixture/build/single- and
two-change cases. See [validation](validation-status.md) and [testing policy](testing-policy.md).
