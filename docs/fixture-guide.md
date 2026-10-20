# Test fixture

Use the original disposable **MCP_QA_DEMO** copy. Completed M1–M3 gates need no
repeat. Preserve the project, package logs and installed Local repair journal;
read current values before any new plan.

## Resources and scope

The demo [read profile](../profiles/examples/native-model-qa.demo.json), revision
**1.0.2**, resolves existing **MCP_QA_MARK** and **MCP_QA_STATUS** text attributes
and **SZ_OGÓ01** (structure) / **SZ_OGÓ02** (review) layer short names freshly.
Both attributes are free text with empty defaults, no units/formulas/geometry links.
Do not recreate resources or guess IDs. Attribute 498 is object name, not mark/status.
The profile is `bound_for_read`, `active_for_write=false`.

Baseline: millimetres, zero project offset, relevant layers visible,
file **101 foreground**, **102 loaded passive**, **103 unloaded**.
Different file IDs require a separately validated profile.
Ordinary UI/file-state commands may end StartPythonHost. Prepare the model
before starting it and restart from Library when necessary.

## Geometry and values

Use ungrouped ordinary native columns, center insertion, bottom/top **0/3000 mm**,
section **400 × 400 mm**, consistent material such as C30/37.
C01–C06 identify recipe positions.

| Position | Center X/Y (mm) | Mark | Layer | Status |
| --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | SZ_OGÓ01 | NEW |
| C02 | 6000 / 0 | S02 | SZ_OGÓ01 | NEW |
| C03 | 12000 / 0 | Empty | SZ_OGÓ01 | NEW |
| C04 | 0 / 6000 | S02 | SZ_OGÓ01 | NEW |
| C05 | 6000 / 6000 | S05 | SZ_OGÓ02 | NEW |
| C06 | 12000 / 6000 | S06 | SZ_OGÓ01 | NWE |

Allplan returned C03's mark as literal `<niezdefiniowany>`; preserve the raw
value. Audit profile **2.0.0** explicitly classifies it as missing.
Add two **300 × 500 mm** beams along C01–C02/C02–C03 at a documented common
elevation, one separate **200 × 4000 × 3000 mm** single-layer wall and one
**4000 × 4000 × 200 mm** native slab beyond the C01 query box. Accepted beam
roots are SkeletonBeam; slab is MultiSlab with Slab tiers. Expected:
**10 top-level components** in 101. Child representations must not inflate counts.
Add an S02 reference column to each of 102/103; those are outside audit uniqueness.

Later owner observation, **2026-10-17**, found two Walls in drawing 101,
described as **24 cm and 20 cm**. The 0.18.2 probe counted both and intentionally
read only the first Wall in model UUID order: **240 mm**, raw material
**`Beton`**, owner-confirmed against UI. The 20 cm Wall's properties were not
read. The ten-component baseline above remains historical evidence, not a
fresh count of this later fixture state. Keep both Walls; do not alter the
fixture to force selection of the 200 mm Wall.
[Observation and original reports](test-results/m4-wall-observation-0.18.2.md).

## Accepted observations and current state

Read counts: **10/6/2/1** components/columns/S02/spatial-height C01 matches.
Display units do not change canonical mm dimensions. Accepted XY offset adds
**(100000,200000,0) mm** once to global coordinates, preserving local geometry.
Configured levels are not native BWS.

The [audit profile](../profiles/examples/native-model-qa.audit.json) examines
only the six columns in 101: QA-001 missing C03 mark; QA-002 duplicate C02/C04
mark (two findings, one group); QA-003 C05 review layer; QA-004 C06 NWE status.
Baseline: **5 findings on 5 columns**, complete coverage; C01 passes.
Layer/status repairs leave **5 → 4 → 3** findings; numbering from the repaired
state gives **3 → 0 → 3** after Undo. [Acceptance and evidence](validation-status.md).

The owner confirms the saved copy after accepted Undo: **C02/C04=S02,
C03 missing, C05 structure layer, C06 NEW**. Its complete audit has three mark
findings. Keep that state; no Redo or repeated writing gate is requested.

See [validation limits](validation-status.md) and [current handoff](next-model-handoff.md).
