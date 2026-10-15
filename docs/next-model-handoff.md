# Current handoff

Updated 2026-10-15 Europe/Warsaw. Current candidate **0.17.2**; package and
automated verification are being prepared. Owner testing is appropriate after
those checks are recorded in the [0.17.2 delivery README](../evaluation-packages/0.17.2/README.md).
No main integration.

The owner requested the full first scenario and explicitly accepted highlighting:
Columns without fire resistance classification → matching targets highlighted →
existing W1. The owner clarified the field as **Klasa odporności ogniowej**, with
F30/F60 values. The [0.17.1 observation](m4-column-layer-observation-0.17.1.md)
confirmed the exact binding and two writes but exposed that the already-W1
matching no-op was omitted from highlighting.

0.17.2 assigns hash-bound `highlight_targets` to all matched `change` and
`no_op` Columns, while `changes` contains only layer setters. A full plan with
no changes can still highlight all matches; it cannot be confirmed or applied.
Unknown values block the action, and more than 32 changes remain blocked. Once
automated verification/package evidence is in place, test only the changed
highlight semantics and no-op behavior using the
[short 0.17.2 owner guide](m4-column-layer-0.17.2.pl.md).

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
the shared RepairExecutor/journal. Unknown/absent-from-ReadAll values block the
action; matched Columns already on W1 are no-op. 0.17.2 highlights all matched
Columns (changes plus no-ops), but applies setters only for changes. Full
source/resource revalidation, native writability, readback and bounded journal
guards remain. The old isolated probe launcher remains available, but the new
task uses **M4 Columns to W1.cmd** and **M4 Columns Recover.cmd**.

The next owner check is constrained to the 0.17.2 changes: leave the model after
0.17.1 (Columns 1, 5, 6 on W1; 2, 3, 4 at F120), confirm a no-op preview has
three highlight targets and zero changes, and stop without `ZMIEN`/Apply. An
optional second scenario restores only Columns 5 and 6 to their old layer before
starting a fresh preview; expect three highlight targets, two changes and one
no-op. See the [owner guide](m4-column-layer-0.17.2.pl.md) for safe sequencing.
Preserve source/CI/package scopes, all logs and Local/.allplan-mcp/repairs. After
unknown results use saved-ID Recover, never a new Apply. This is not blanket
acceptance of M4 or a repeat of completed M3 gates.

M3 acceptance remains limited to its historical fixture/build/single- and
two-change cases. See [validation](validation-status.md) and [testing policy](testing-policy.md).
