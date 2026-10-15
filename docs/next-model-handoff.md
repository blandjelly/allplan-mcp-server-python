# Current handoff

Updated 2026-10-15 Europe/Warsaw. Candidate **0.17.1**; native acceptance pending.
Source/package/CI results are scoped in the delivery record. No main integration.

The owner requested the full first scenario and explicitly accepted highlighting:
Columns without fire resistance classification → exact targets highlighted → existing W1.
The owner clarified the field as **Klasa odporności ogniowej**, with F30/F60 values.
[Implementation, limits and owner walkthrough](m4-column-layer-0.17.1.pl.md).

The 0.17.0 owner run on **2026-10-15 at 19:40 Europe/Warsaw** was **BLOCKED**.
It bound `Odporność ogniowa` (1398), absent from ReadAll on all six Columns;
the six unknown states blocked before highlighting/Apply/setters. This is a
semantic field-binding error, not acceptance of the requested criterion merely
because the write guard stopped. `health_before` was healthy; `journal_before`
was available with seven records and no blockers. There is no `health_after`, so
the report does not establish host health throughout or after the run.
[Original JSON](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.json),
[original TXT](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.txt).

0.17.1 defaults to exact names `Klasa odporności ogniowej` /
`Fire resistance classification`, with runtime ID/name roundtrip and no fallback
to 1398. Official 2026-1 documentation identifies 935 as Fire resistance
classification and the SDK uses 935 with F30; 935 is evidence, not a hardcoded
runtime binding. Keep the existing ReadAll reader and genuine omissions unknown.
Do not add computed reads or broad metadata discovery to compensate for the wrong name.

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

Next: check the 0.17.1 delivery evidence, then observe the corrected binding
in the retained copy. [Delivery](../evaluation-packages/0.17.1/README.md).
Preserve source/CI/package scopes, all logs and Local/.allplan-mcp/repairs.
After unknown results use saved-ID Recover, never a new Apply. Check UI and Undo;
do not label this accepted_on_build before receiving native evidence.

M3 acceptance remains limited to its historical fixture/build/single- and
two-change cases. See [validation](validation-status.md) and [testing policy](testing-policy.md).
