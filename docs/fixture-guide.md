# Reference fixture for M1–M3

This is the reusable setup for the accepted M1/M2 fixture, not a request to
reinstall or repeat completed tests. [M1 acceptance](test-results/m1-acceptance-0.5.3.md)
and [M2 acceptance](test-results/m2-acceptance-0.6.1.md) define its verified scope.
The MCP read commands do not construct or repair this fixture.

## Project and resources

Use a disposable `MCP_QA_DEMO` project or copy. Reserve empty drawing files
**101** (foreground), **102** (loaded passive) and **103** (unloaded). Use mm,
zero offset and visible relevant layers for the initial baseline. Occupied
files require a separately prepared profile; never overwrite a model.

Through the Allplan UI, use two ordinary free-text attributes named
**MCP_QA_MARK** and **MCP_QA_STATUS**, with empty defaults and no units,
formulae or enumerated choices. Existing definitions are reused. The recorded
owner setup groups them under MCP_QA. Use the existing layer short names
**SZ_OGÓ01** (Ogólne01, structure) and **SZ_OGÓ02** (Ogólne02, review).
The owner does not choose API IDs or edit JSON. Attribute 498 (Nazwa obiektu)
is not the demo mark/status binding.

**M1 Profile.cmd** verifies distinct attribute/layer IDs, name/type round trips
and `bound_for_read`; it creates no resource. Missing or incompatible resources
must be resolved before profile queries/audits. Read compatibility does not
establish write eligibility.

## Geometry and values

Create six ungrouped ordinary native columns in file 101, with center insertion,
section **400 × 400 mm**, bottom/top **0 / 3000 mm**, and a consistent sample
material such as C30/37. C01–C06 identify recipe positions, not extra attributes.

| Position | Center X/Y (mm) | MCP_QA_MARK | Layer | MCP_QA_STATUS |
| --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | SZ_OGÓ01 | NEW |
| C02 | 6000 / 0 | S02 | SZ_OGÓ01 | NEW |
| C03 | 12000 / 0 | Empty | SZ_OGÓ01 | NEW |
| C04 | 0 / 6000 | S02 | SZ_OGÓ01 | NEW |
| C05 | 6000 / 6000 | S05 | SZ_OGÓ02 | NEW |
| C06 | 12000 / 6000 | S06 | SZ_OGÓ01 | NWE |

C03 was observed as literal `<niezdefiniowany>`. Queries preserve this raw
string; M2 profile 2.0.0 explicitly classifies it as missing.

Keep two native 300 × 500 mm beams between C01/C02 and C02/C03 at a documented
elevation. The accepted fixture uses SkeletonBeam roots; ordinary Beam roots
are also supported. Add a separate 200 × 4000 × 3000 mm single-layer wall and
4000 × 4000 × 200 mm aggregate slab, away from C01's spatial test box (for
example beyond X=20000 mm). The accepted slab is MultiSlab with Slab tiers.
Expected file-101 count: **10 top-level components**, including six columns.
Add one separate ordinary S02 column in each of files 102 and 103. Restore
101 foreground, 102 passive, 103 unloaded and retain the zero-offset baseline.

## Expected read results

M1 Final.cmd runs the packaged read batch, summaries and page traversal.
The accepted A capture verifies **10/6/2/1** file-101 components / profile
columns / S02 matches / C01 spatial-height matches. Broad scope includes one
reference from 102 and explicitly omits unloaded 103. B changes display units
to metres with unchanged canonical mm geometry; it separately restores passive
102 and C05's review layer. C uses a saved copy with offset
**(100000,200000,0) mm**: global geometry equals local geometry plus offset
exactly once. C01 base-center UI coordinates are **100/200/0 m**; its whole-box
center is **(100000,200000,1500) mm**. Nonzero Z offsets were not tested.

M2 Audit.cmd reads only the six file-101 columns. Expected **24 checks**:
18 pass, 5 fail, 1 not_applicable, 0 not_checked; **5 findings on 5 columns**:
missing C03 mark, duplicate C02/C04 marks, C05 review layer and C06 NWE status.
C01 passes; reference columns outside file 101 do not create duplicate findings.
The report's fail state is the intentional fixture outcome, not a transport error.

The separate [M3 preview PR](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
proposes C05 layer SZ_OGÓ02 → SZ_OGÓ01 and C06 status NWE → NEW without writes.
Apply remains unavailable. Future accepted application would leave three mark
findings; it must use a reviewed plan and native readback/Undo evidence.
