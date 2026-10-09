# Final M1 owner verification — 0.5.3

Status: **accepted_on_build: Allplan 2026-1-7; M1 CLOSED** on 2026-10-09.
[Acceptance, exact artifact and limits](test-results/m1-acceptance-0.5.3.md).
Preflight and A/B/C pass; owner independently confirms dimensions/coordinates,
unchanged appearance and retained original baseline. C adds the configured
100/200/0 m offset exactly once; local geometry and 10/6/2/1 counts are unchanged.
B separately verifies 102 passive and C05/S05 review layer. Keep the installed
0.5.3 artifact. **No reinstall, repeated capture or further M1 test is requested.**
The setup/capture recipe below is retained for reference, not a new owner task.

No model edits are made by either packaged diagnostic command. Audit/repair
tools belong to M2/M3 and are not exercised here.

## Install and resource preflight

Keep accepted archives unchanged. Close Allplan and the MCP console; extract
`allplan-mcp-0.5.3-windows-evaluation.zip` into a new folder and run **Setup.cmd**
against the same Allplan Local folder. Reopen Allplan and **Launch Allplan MCP.cmd**.
The seven-tool catalog is unchanged. Restart **StartPythonHost** after normal
Allplan commands/file-state changes that end its interactor. An open MCP console
alone does not mean the in-process Allplan host is running.

Use a new disposable project **MCP_QA_DEMO**, with initially zero project offset.
Reserve **empty files 101, 102 and 103**. If any is occupied, stop and report the
conflict; the supplied profile/batch uses these exact files and must be prepared
again before using different numbers. Do not overwrite an existing model.

The latest owner screenshot shows both actual attribute definitions in the
right-hand Attributes list inside user group **MCP_QA**. They are already
created; do not recreate them. The two required names are:
**MCP_QA_MARK** and **MCP_QA_STATUS**, both ordinary free text, initially empty,
without enumerated choices, units, formulas or links to native geometry.
Use the two existing layers whose short names the owner supplied:
**SZ_OGÓ01** (full name Ogólne01) for structure and **SZ_OGÓ02**
(full name Ogólne02) for review. Keep both visible.
Existing attribute groups may remain; no deletion is required.
Both actual attribute names now appear in the right-hand Attributes list. Use string/text data type, ordinary input control, empty default and
no unit/formula/enum. If Define new attribute is disabled, open the selection
through normal Assign/Modify attributes on a disposable model element; do not
change native attributes or insert text into a group name/value field.
No new layer creation or renaming is required. The owner chooses no API IDs
and edits no JSON. These manual
setup changes are separate from the read-only server. If names already exist,
check their text definitions instead of creating duplicates.

The owner has already passed **M1 Profile.cmd** on 0.5.2; do not repeat it
separately. Continue to fixture construction. For a genuinely changed resource
setup, the standalone preflight remains available with file 101 foreground and
StartPythonHost running. The JSON in `logs` contains fresh names/IDs/types and layer
names/IDs. Expected: `mcp.model_query.status=bound_for_read`; mark/status have
distinct IDs and the configured observed text type code 67; layers have distinct
positive IDs. This is a read binding, not tested write eligibility. If it is
`not_checked`, retain the log and stop fixture construction; the implementation
model resolves the cause. Do not guess IDs or rename a different native field.
Attribute 498 is **Nazwa obiektu**, not the demo mark/status.

The earlier group/full-name setup issue is resolved. Keep the existing two
attribute definitions and layers. The native reader correction requires the
new 0.5.3 package, but no standalone preflight is required. The six-request
final batch still includes a fresh resource binding as normal query-context validation.

## Build the fixture once

Use millimetres, zero offset, ungrouped **ordinary native columns** (not
Structural Framing columns), common center insertion reference and manual bottom/top
levels **0 / 3000 mm**. Create six columns, **400 × 400 mm**, in file 101:

| Label for the recipe | Center X / Y (mm) | MCP_QA_MARK | Layer | MCP_QA_STATUS |
| --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | SZ_OGÓ01 | NEW |
| C02 | 6000 / 0 | S02 | SZ_OGÓ01 | NEW |
| C03 | 12000 / 0 | empty | SZ_OGÓ01 | NEW |
| C04 | 0 / 6000 | S02 | SZ_OGÓ01 | NEW |
| C05 | 6000 / 6000 | S05 | SZ_OGÓ02 | NEW |
| C06 | 12000 / 6000 | S06 | SZ_OGÓ01 | NWE |

C03 is intended as a blank mark. Allplan returned the literal string
<niezdefiniowany> in the owner capture; retain/report this native value rather
than silently treating it as missing. Future M2 QA normalization is separate.

Labels C01–C06 are recipe positions; no extra C01 attribute or graphical label
is required. Assign the two demo attributes to each column through normal UI.

Keep the two owner-created structural beams (SkeletonBeam_TypeUUID,
300 × 500 mm) in file 101 between the C01/C02 and C02/C03 axes at a documented
elevation. Ordinary Beam_TypeUUID beams also remain supported. Keep one
single-layer wall (200 mm thick, 4000 mm long, 3000 mm high) and one native
aggregate slab (MultiSlab_TypeUUID with Slab_TypeUUID tier geometry),
4000 × 4000 mm and 200 mm thick. Put wall
and slab away from C01's test box, for example beyond X=20000 mm. Do not group
these components or add openings for this bounded fixture. Expected file 101:
**10 supported top-level components = 6 columns + 2 beams + wall + slab**.

Add a separate ordinary column marked S02 in file 102 and one in file 103,
using the same dimensions and demo attributes. Restore **101 foreground,
102 passive, 103 unloaded**. Keep the relevant layers visible. Save a baseline
copy and note the visible C01 dimensions/center and the UI coordinate unit.
The reference columns are outside the demo uniqueness scope.

## Three final captures

**A/B/C are complete.** Keep the earlier reports; do not repeat this recipe.
Start StartPythonHost after each setup change. Run **M1 Final.cmd** for each
capture below and retain the resulting `logs/diagnostics-*.json`. It runs six
packaged read requests with full responses, summaries and bounded page traversal:

| Capture | UI setup | Expected result |
| --- | --- | --- |
| A | Original fixture, zero offset, mm display | Resource read binding; 10 components in 101 and one accessible reference in 102; explicit unloaded 103 omission; six profile columns, two marks S02, one spatial/dimension match C01. Column boxes are 400 × 400 × 3000 mm; C01 center (0,0,1500). |
| B | Geometry unchanged; restore 102 passive/C05 review layer as declared setup corrections, then change displayed length unit to metres | Same physical dimensions, identities, 10/6/2/1 counts and C01 result. Canonical numbers remain mm. |
| C | Separate saved copy; configured offset X=100000, Y=200000, Z=0 mm (enter 100/200/0 if the dialog uses metres) | Raw offset agrees with UI; dimensions/counts stay unchanged. Compare C01's model-local center with its global center; the declared transform adds offset exactly once. Record an independent UI coordinate reading and its unit. |

The implemented API source-frame convention is **model_local in mm**. Its
nonzero XY offset interpretation passed native C plus the independent owner UI
reading; nonzero Z offset is not tested. Portable arithmetic alone is insufficient. If Allplan's returned coordinates or the UI
disagree, preserve the log/UI values and mark the offset case FAIL/NOT_CHECKED;
do not adjust the expected values silently. Changed project/session bindings
between copies are expected; UUID equality across project copies is not required.
No numeric geometry readback is inferred from a successful transport alone.

The first broad component scan has incomplete requested scope because file 103
is unloaded; that is expected. The file-101 profile scans should be complete.
Passive metadata/attributes can be unavailable; never report them as successful
native-absence checks. Failed wall-tier or parent reads make the component/
geometry gate not_checked, even if some counts happen to match.

Reset: keep the original zero-offset baseline, restore preferred display units,
and leave reference file 102 passive and 103 unloaded. No cleanup or repair is
requested. All reports and required UI observations are already supplied; this
result form is retained for reference:

```text
Package: 0.5.3
Allplan UI build: [actual]
Preflight / capture A / B / C filenames: [...]
All columns/components visibly unchanged during captures: yes / no / not checked
C01 UI dimensions: [..., with unit]
C01 UI coordinates, measured point and displayed unit in offset copy: [...]
Offset UI values and unit: [...]
Original baseline retained; reference 102 passive / 103 unloaded: yes / no
Unexpected counts, read failures or UI behavior: [...]
```

M1 is closed for the recorded read scope. No accepted batch needs new evidence. The planned five audit findings and two repairs
remain future M2/M3 acceptance; this card verifies the read foundation only.
