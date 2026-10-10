# Development fixture

Use the existing disposable **MCP_QA_DEMO** project/copy for M1–M3.
This defines reusable data; it does not request a repeated accepted test.
Read current values before further M3 work: previous Undo/Redo may have changed
them. Keep the original baseline and installed Local repair journal.

## Resources and scope

The demo [read profile](../profiles/examples/native-model-qa.demo.json), revision
**1.0.2**, resolves existing **MCP_QA_MARK** and **MCP_QA_STATUS** text attributes
and **SZ_OGÓ01** (structure) / **SZ_OGÓ02** (review) layer short names freshly.
Both attributes are ordinary free text with empty defaults, no units, formulas,
enumerated choices or geometry links. Do not recreate resources that already
exist or guess API IDs. Attribute 498 is Nazwa obiektu, not mark/status.
The profile is `bound_for_read`, `active_for_write=false`.

Initial baseline: millimetres, zero project offset, relevant layers visible,
file **101 foreground**, **102 loaded passive**, **103 unloaded**. Reserve empty
files only; different IDs require a separately validated profile.
Ordinary UI/file-state commands may end StartPythonHost. Prepare the model
before starting it and restart from Library when necessary.

## Geometry and values

Use ungrouped ordinary native columns, center insertion, bottom/top **0/3000 mm**,
section **400 × 400 mm**, consistent material such as C30/37.
C01–C06 are recipe positions, not extra attributes or graphical labels.

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

## Expected observations

Read counts: **10/6/2/1** components/columns/S02/spatial-height C01 matches.
Display units do not change canonical mm dimensions. Accepted XY offset adds
**(100000,200000,0) mm** once to global coordinates, preserving local geometry.
Configured levels are not native BWS.

The [audit profile](../profiles/examples/native-model-qa.audit.json) examines
only the six columns in 101: QA-001 missing C03 mark; QA-002 duplicate C02/C04
mark (two findings, one group); QA-003 C05 review layer; QA-004 C06 NWE status.
Baseline: **5 findings on 5 columns**, complete coverage; C01 passes.
Repairing C05 layer then C06 status leaves **4 then 3 findings**; remaining issues
concern marks. Explicit C03=S03/C04=S04 preview simulates zero findings;
0.12.0 implements mark setters and deterministic numbering; the retained
two-target native gate passed writes, replay/no-op and Undo/recovery. Numbering leaves two findings in the original five-finding fixture
or zero in the repaired three-finding fixture. See [acceptance](m3-numbering-acceptance-0.12.0.md).
The owner left marks after two Undo operations: C03 missing, C04=S02.
C05 structure layer/C06 NEW remain; current complete audit has three mark findings.

See [validation limits](validation-status.md) and [current handoff](next-model-handoff.md).
