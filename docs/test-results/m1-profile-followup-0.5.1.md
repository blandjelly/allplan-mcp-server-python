# M1 profile follow-up — 0.5.1

2026-10-08. Native read binding and full M1 exit gate remain pending.

## Owner evidence, separate from portable tests

Original [0.5.0 preflight](evidence/diagnostics-20261008T182010Z.json) is preserved
byte-for-byte. Package/host 0.5.0, clean source b3336c48, verified installed
integrity, seven tools, project MCP_QA_DEMO, file 101 foreground, zero offset.
Both named demo attributes and both configured layers returned
not_checked/BridgeError. Returned lookup IDs were not captured; this does not
prove native absence. No geometry/hierarchy acceptance follows from this report.

Owner subsequently confirms both MCP_QA_MARK and MCP_QA_STATUS were created,
and supplies existing layer short names Ogólne01/Ogólne02 after difficulty
creating new layers. No other resource ID/type or successful binding is inferred.

## Change and validation

0.5.1 packages demo profile revision 1.0.1 using those distinct existing layers.
Schema m1-profile-1 and old revision 1.0.0 remain accepted. Failed binding reads
retain the API stage and validated returned numeric ID/name/type metadata.
Native exception messages/object representations are not exposed. Nonpositive
IDs still fail closed before metadata reads; unbound queries create no selection.

Nine targeted portable checks PASS: three new failure-diagnostic/Unicode/old-
revision checks, five relevant binding/alias/staleness regressions and version-
lock agreement. Native lookup behavior is not proven by fake resource services.
Two additional checks PASS: real MCP profile-resource/diagnostic transport with
a fake native bridge, and deterministic package integrity/fresh registration.
Total: **11 targeted portable checks PASS**. Accepted owner batches are not repeated.

## Owner next action

Install 0.5.1 in a new folder using Setup.cmd with Allplan/MCP closed. Reopen
both and start StartPythonHost. Run **only M1 Profile.cmd** and submit its JSON.
No new layers, renamed native attributes, guessed IDs, fixture reconstruction or
M1 Final.cmd is requested before read binding succeeds. Once bound_for_read,
use the [updated final card](../m1-final-batch.md) with Ogólne01/Ogólne02.
