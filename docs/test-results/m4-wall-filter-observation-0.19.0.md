# M4 Wall thickness filter — owner observation on 0.19.0

**PASS / accepted_on_build 0.19.0**, scoped to the two single-tier Walls in
active foreground drawing **101**, the strict **<240 mm** filter, visible
highlighting of the 20 cm Wall, explicit highlight clear and continued host
operation. The owner confirmed the UI result and that the host was not
interrupted on **2026-10-17 Europe/Warsaw**. This completed trial needs no repeat.

The filter report is named `20261017T152053490160Z` and the clear report
`20261017T152208657656Z` (UTC; approximately **17:20 and 17:22 CEST**).
Health reports identify MCP/bridge **0.19.0**, source
`e455f35cf4d546d9b77cf6ae5f59edcc026cc875`, installed integrity `verified`,
Allplan API `2026.1`, executable file/product
`16.1617.8659.814 / 2026.0.1.0`. The runtime hotfix field is `not_checked`.

## Observed result

| Wall model UUID | Native thickness | Strict `<240 mm` |
| --- | --- | --- |
| `06d71e4d-193b-483e-8a32-344ade3d612c` | 240.0 mm | false |
| `545bb0a2-a054-4c91-ac6c-ec552d5b0c18` | 200.0 mm | true |

Both records are `observed`, with one tier and source
`single_tier_native_Thickness`. M1, read and criterion coverage are complete;
`criterion_complete=true`, `is_full_wall_filter=true`, and there are no omissions.
Counts are **2 Walls, 1 match, 0 exclusions, 0 unreadable, 0 unprocessed**.
One model identity/adapter was submitted to highlight. The owner confirmed
that the 20 cm Wall was correctly highlighted and then cleared.

The separate `model_selection` request uses `action=clear_highlight` and returns
`state=submitted`. Its clear scope is all highlights in the current document.
This is highlight removal, not evidence of native UI selection/deselection.

All **four health replies** (before/after filtering and before/after clear)
are healthy and share host session
`d68ec7d3-4418-41ca-aa67-c6d3e17c7541`; both action replies carry that session.
The owner's confirmation additionally establishes uninterrupted host operation
through this observed workflow.

## Evidence and acceptance limits

Original JSON/TXT uploads are preserved unchanged. Their
`awaiting_owner_observation`, `allplan_acceptance=not_run`,
`runtime_verified=false`, `units_runtime_verified=false` and null visible-count
fields reflect the automated reports before owner confirmation. The scoped
native PASS above combines those reports with the owner's UI observation;
it does not rewrite the runtime flags or establish general unit verification.

Both reports state no model setters were requested; the action responses report
`model_data_changed=false` and `usable_for_write=false`. No independent geometry
comparison or material/attribute write, readback or Undo was performed.
Native trace and bridge.log were not among these four uploads; the health and
action replies plus owner confirmation support this observation.

Excluded targets, zero-match clear, rotated/multi-tier Walls, larger result sets,
multiple drawings, native UI selection and material binding/writes remain
outside this acceptance. It does not complete all K2 requirements or all M4.
Frozen packages and original delivery/verification JSON retain their build-time
status; this is a documentation/evidence update without tests or rebuilds.

Original uploads and derived inspection:

- [Filter JSON](../../evaluation-packages/0.19.0/native-acceptance/20261017-owner/wall-filter-20261017T152053490160Z.json)
- [Filter TXT](../../evaluation-packages/0.19.0/native-acceptance/20261017-owner/wall-filter-20261017T152053490160Z.txt)
- [Clear JSON](../../evaluation-packages/0.19.0/native-acceptance/20261017-owner/m4-properties-clear-20261017T152208657656Z.json)
- [Clear TXT](../../evaluation-packages/0.19.0/native-acceptance/20261017-owner/m4-properties-clear-20261017T152208657656Z.txt)
- [Inspection](../../evaluation-packages/0.19.0/native-acceptance/20261017-owner/inspection.json)

[delivery and automated evidence](../../evaluation-packages/0.19.0/README.md).
