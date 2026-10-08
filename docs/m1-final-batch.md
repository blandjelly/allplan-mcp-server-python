# Final M1 owner verification — 0.5.1

Status: **ready_for_owner_test**, not accepted in Allplan yet. The bounded
0.2.1/0.3.0/0.4.0 batches remain accepted; do not repeat them. This card closes
the remaining geometry/unit/offset, native hierarchy and demo-binding gate.
No model edits are made by either packaged diagnostic command. Audit/repair
tools belong to M2/M3 and are not exercised here.

## Install and resource preflight

Keep accepted archives unchanged. Close Allplan and the MCP console; extract
`allplan-mcp-0.5.1-windows-evaluation.zip` into a new folder and run **Setup.cmd**
against the same Allplan Local folder. Reopen Allplan and **Launch Allplan MCP.cmd**.
The seven-tool catalog is unchanged. Restart **StartPythonHost** after normal
Allplan commands/file-state changes that end its interactor. An open MCP console
alone does not mean the in-process Allplan host is running.

Use a new disposable project **MCP_QA_DEMO**, with initially zero project offset.
Reserve **empty files 101, 102 and 103**. If any is occupied, stop and report the
conflict; the supplied profile/batch uses these exact files and must be prepared
again before using different numbers. Do not overwrite an existing model.

The owner has already created the two user text attributes. Verify their
definitions in Allplan's attribute-definition management:
**MCP_QA_MARK** and **MCP_QA_STATUS**, both ordinary free text, initially empty,
without enumerated choices, units, formulas or links to native geometry.
Use the two existing layers whose short names the owner supplied:
**Ogólne01** for structure and **Ogólne02** for review. Keep both visible.
No new layer creation or renaming is required. The owner chooses no API IDs
and edits no JSON. These manual
setup changes are separate from the read-only server. If names already exist,
check their text definitions instead of creating duplicates.

With file 101 foreground, start StartPythonHost and double-click
**M1 Profile.cmd**. The JSON in `logs` contains fresh names/IDs/types and layer
names/IDs. Expected: `mcp.model_query.status=bound_for_read`; mark/status have
distinct IDs and the configured observed text type code 67; layers have distinct
positive IDs. This is a read binding, not tested write eligibility. If it is
`not_checked`, retain the log and stop fixture construction; the implementation
model resolves the cause. Do not guess IDs or rename a different native field.
Attribute 498 is **Nazwa obiektu**, not the demo mark/status.

The 0.5.0 preflight returned `BridgeError` for all four bindings. It does not
prove that the owner-created attributes are absent. The 0.5.1 profile revision
1.0.1 uses the existing owner layers and adds failure-stage/returned-ID/name/type
diagnostics. Reinstall 0.5.1 and repeat **only M1 Profile.cmd** first. If it still
returns `not_checked`, submit that JSON and stop; do not recreate the attributes,
guess IDs, or continue to M1 Final.cmd. Changing the selected UI layer alone
does not change profile bindings.

## Build the fixture once

Use millimetres, zero offset, ungrouped **ordinary native columns** (not
Structural Framing), common center insertion reference and manual bottom/top
levels **0 / 3000 mm**. Create six columns, **400 × 400 mm**, in file 101:

| Label for the recipe | Center X / Y (mm) | MCP_QA_MARK | Layer | MCP_QA_STATUS |
| --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | Ogólne01 | NEW |
| C02 | 6000 / 0 | S02 | Ogólne01 | NEW |
| C03 | 12000 / 0 | empty | Ogólne01 | NEW |
| C04 | 0 / 6000 | S02 | Ogólne01 | NEW |
| C05 | 6000 / 6000 | S05 | Ogólne02 | NEW |
| C06 | 12000 / 6000 | S06 | Ogólne01 | NWE |

Labels C01–C06 are recipe positions; no extra C01 attribute or graphical label
is required. Assign the two demo attributes to each column through normal UI.

Add in file 101: two ordinary beams (300 × 500 mm) between the C01/C02 and
C02/C03 axes at a documented elevation; one single-layer wall (200 mm thick,
4000 mm long, 3000 mm high); one slab (4000 × 4000 mm, 200 mm thick). Put wall
and slab away from C01's test box, for example beyond X=20000 mm. Do not group
these components or add openings for this bounded fixture. Expected file 101:
**10 supported top-level components = 6 columns + 2 beams + wall + slab**.

Add a separate ordinary column marked S02 in file 102 and one in file 103,
using the same dimensions and demo attributes. Restore **101 foreground,
102 passive, 103 unloaded**. Keep the relevant layers visible. Save a baseline
copy and note the visible C01 dimensions/center and the UI coordinate unit.
The reference columns are outside the demo uniqueness scope.

## Three final captures

Start StartPythonHost after each setup change. Run **M1 Final.cmd** for each
capture below and retain the resulting `logs/diagnostics-*.json`. It runs six
packaged read requests with full responses, summaries and bounded page traversal:

| Capture | UI setup | Expected result |
| --- | --- | --- |
| A | Original fixture, zero offset, mm display | Resource read binding; 10 components in 101 and one accessible reference in 102; explicit unloaded 103 omission; six profile columns, two marks S02, one spatial/dimension match C01. Column boxes are 400 × 400 × 3000 mm; C01 center (0,0,1500). |
| B | Same fixture and file states; change only displayed length unit to metres | Same physical dimensions, identities, 10/6/2/1 counts and C01 result. Canonical numbers remain mm. |
| C | Separate saved copy; configured offset X=100000, Y=200000, Z=0 mm (enter 100/200/0 if the dialog uses metres) | Raw offset agrees with UI; dimensions/counts stay unchanged. Compare C01's model-local center with its global center; the declared transform adds offset exactly once. Record an independent UI coordinate reading and its unit. |

The implemented API source-frame convention is **model_local in mm**. Its
nonzero-offset interpretation is a required runtime gate, not a fact already
proved by portable arithmetic. If Allplan's returned coordinates or the UI
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
requested. Submit the preflight JSON, A/B/C JSON and this short result form:

```text
Package: 0.5.1
Allplan UI build: [actual]
Preflight / capture A / B / C filenames: [...]
All columns/components visibly unchanged during captures: yes / no / not checked
C01 UI dimensions: [..., with unit]
C01 UI coordinates and displayed unit in offset copy: [...]
Offset UI values and unit: [...]
Original baseline retained; reference 102 passive / 103 unloaded: yes / no
Unexpected counts, read failures or UI behavior: [...]
```

M1 closes only after these remaining runtime gates pass. The earlier accepted
batches do not need new evidence. The planned five audit findings and two repairs
remain future M2/M3 acceptance; this card verifies the read foundation only.
