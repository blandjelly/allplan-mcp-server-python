# M1 profile setup correction — 0.5.2

2026-10-08. Full M1 native acceptance remains pending. This is a sanitized
record of technical findings; it does not publish the uploaded report or screenshots.

## Owner findings, separate from automated checks

0.5.1 installed integrity has no mismatches and MCP transport succeeds.
Profile remains not_checked: both GetAttributeID calls return -1 and both
GetIDByShortName calls with full names return 0. No later name/type reads occur.
Signatures match the documented Allplan 2026 argument order.

Owner layer screenshot shows actual short names SZ_OGÓ01/SZ_OGÓ02 opposite
full names Ogólne01/Ogólne02. Attribute screenshot shows demo-named entries in
the left Attribute group tree and an empty right Attributes list for the selected
group. This supports creation of groups rather than the required definitions;
The owner then corrects the setup: the latest screenshot shows MCP_QA_MARK
and MCP_QA_STATUS in the right Attributes list under group MCP_QA. Exact
IDs/type compatibility still require the next native preflight.

## Change and owner action

Profile 1.0.2 packages corrected short names; 1.0.0/1.0.1 remain accepted.
No change to native resource lookup APIs or model state. Existing groups may
remain. The owner has corrected the definitions in a user group; preserve them.
Required string/input definitions have empty default and no unit/formula/enum;
those details still need native verification. Install 0.5.2/start the host and
run only M1 Profile.cmd.
Do not repeat accepted owner batches or build the final fixture until binding.

[Updated owner card](../m1-final-batch.md).

## Portable validation

Six relevant checks PASS: corrected Unicode short names with both older profile
revisions accepted; exact name/type/ID binding via fake resource services; failed
lookup diagnostics; version/lock agreement; deterministic package integrity/fresh
registration; real MCP profile-resource/batch transport with a fake native bridge.
Wheel/sdist build PASS. No native success or full M1 acceptance is inferred.
No accepted owner batch or unrelated geometry test was repeated.

## Exact artifact

`allplan-mcp-0.5.2-windows-evaluation.zip`, clean source commit
`c4cfbd52938328c6e41405998ba110314bca8930`, source_modified=false. SHA-256:
`7748a2020b8f5968aba377e6674917f3ee419e7ccb11502684ca945cbf0d6605`.
Wheel profile matches canonical JSON. Older evaluation archives are unchanged.
This identification record is a separate documentation-only commit.

## Native read-resource preflight PASS — 2026-10-08

Owner upload `diagnostics-20261008T184008Z.json` reports package/bridge 0.5.2,
source c4cfbd52938328c6e41405998ba110314bca8930, installed integrity verified
without mismatches, successful MCP transport and profile revision 1.0.2
**bound_for_read**. Sanitized observations:

| Role | Observed native definition | ID | Type |
| --- | --- | --- | --- |
| mark | MCP_QA_MARK | 5001 | 67 / string |
| status | MCP_QA_STATUS | 5002 | 67 / string |
| structure | SZ_OGÓ01 (Ogólne01) | 3700 | layer |
| review | SZ_OGÓ02 (Ogólne02) | 3701 | layer |

All four reads are observed; exact name/type round trips succeeded, IDs are
positive and distinct within their resource kinds. File 101 is foreground and
raw project offset is zero. IDs are observations in this tested resource context,
not constants to hard-code or durable identities.

The **bounded resource-binding owner gate PASS** is separate from the six
portable checks. Write eligibility remains not_checked and active_for_write=false.
No geometry, hierarchy, nonzero-offset, display-unit or full M1 acceptance is
inferred. Attribute input-control/unit/default/enum details were not independently
inspected by this action; string type is verified. No original diagnostic or
private environment paths/project/session identifiers are published here.

Next: build the fixture once and collect final A/B/C captures using the same
0.5.2 archive and [owner card](../m1-final-batch.md). Do not repeat M1 Profile.cmd
alone or the already accepted 0.2.1/0.3.0/0.4.0 batches. The final batch's own
fresh read binding remains necessary context validation. No code, archive or
automated test changes accompany this evidence record.
