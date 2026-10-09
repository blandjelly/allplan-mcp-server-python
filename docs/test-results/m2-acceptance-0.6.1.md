# M2 acceptance — 0.6.1, UAT-04 PASS within the recorded scope

Date **2026-10-09**. Capture began **13:37:07 Europe/Warsaw**
(11:37:07 UTC); filename timestamp 11:37:12 UTC. **M2.1–M2.3 / UAT-04 PASS**
for the retained six-column demo fixture on the previously owner-identified
Allplan **2026-1-7**, local Windows MCP/host package **0.6.1**, audit profile
**2.0.0**, unchanged M1 read profile **1.0.2**.

## Original evidence and artifact identity

Original evidence is available byte-for-byte in Git history, including Windows
TXT line endings; raw logs are excluded from the current documentation tree:

- [JSON](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261009T113712Z.json), **246528 bytes**,
  SHA-256 `d12c893fbc624eaf577f4953504207b5da4438a57599ba395c0a5a39c4a8a9f3`.
- [TXT](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261009T113712Z.txt), **1740 bytes**,
  SHA-256 `aeda6cd78e0531d587ea79bdc9817e59779438aced697d64940b091889dff2ec`.
- Tested `allplan-mcp-0.6.1-windows-evaluation.zip`, **340007 bytes**,
  SHA-256 `b47cba9ab08cce800f9e1900d03a232153c4441d054818f1bc116e8cc4a617f7`.

All **18 installed bridge file hashes** match that original archive. Host and
external MCP report 0.6.1; installed integrity is verified with no mismatches.
The loaded transport emits `ui_dispatch_exception_boundary=contained_result_error_v1`
both before and after the controlled host rejection. The manifest records
baseline commit `bc5137339f3a6fa2049b322d7c726e659b523279` and
`source_modified=true`; the archive and per-file hashes identify the actual
tested source. This documentation update does not rebuild the archive.

Native API release is **2026.1**; executable file/product resource versions are
**16.1617.8659.814 / 2026.0.1.0**. Embedded CPython **3.13.13** and external
Python **3.14.8** match earlier captures. These resource versions do not
independently identify the UI hotfix.

## Observed stability gate

`m2_stability.checks_complete=true`; all six recorded steps are OK:

| Step | Observed result |
| --- | --- |
| host_boundary_preflight | Host/MCP 0.6.1, verified installation, loaded boundary marker |
| audit_1 | Full read of file 101; 6 columns, 5 findings on 5 targets |
| audit_2 | Same complete report; separate request ID |
| mcp_scope_rejection | Public validation rejects scope 101/102 with the expected scope message |
| host_scope_rejection | Direct host rejects the same invalid scope with `invalid_payload` and a request ID |
| host_health_after_rejection | Same host session responds with Allplan version, verified bridge 0.6.1 and loaded marker |

Both rejection paths report **Requested audit files exceed the explicit profile
scope.** This is the scope involved in the earlier incident; it remains invalid,
and no passive-file audit or scope expansion is accepted.

Both reports contain **24 checks: 18 pass, 5 fail, 1 not_applicable,
0 not_checked**, one duplicate group, three error findings and two warnings.
Requested scope, returned fields, rule inputs and audit coverage are complete;
whole-project coverage remains false. Scan counts remain 17 raw adapters,
16 in scope, six deduplicated representations, six matching column identities
and four nonmatching native roots. No omissions or unchecked samples are returned.
The audit state `fail` is the expected outcome for the intentional fixture issues.

QA-001 identifies C03's raw `<niezdefiniowany>` mark; QA-002 identifies the
C02/C04 S02 duplicate pair; QA-003 identifies C05's review layer; QA-004
identifies C06's NWE status. C01 passes all rules. All six model UUIDs and
per-element source fingerprints match the
[previous native capture](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/m2-audit-runtime-0.6.0.md). All 24 checks and five
findings match after removing session-derived IDs; raw evidence, geometry,
locators and binding are unchanged. This comparison establishes equality of
the audited data, not a whole-project or post-test mutation trace.

The two new report objects differ only in their transport request IDs.
Both report fingerprints recompute to
`2cde65e9a92998c0aeb34bcae4c2cdeac61008d1e3f1c8e1bfae95e75f8a4310`.
TXT exactly matches the JSON report text and six step outcomes after normalizing
line endings. No repair/highlight is applied; references remain nondurable and
`usable_for_write=false`.

## Owner evidence, decision and limits

The owner previously confirmed **“Tak, wskazania zgadzają się i model jest bez
zmian”** for the same findings and locations. After this 0.6.1 stability run,
the owner supplied both logs and confirmed **“to sa logi, allplan dziala, host
dziala”**. The latest statement confirms continued Allplan/host operation;
it does not separately repeat a whole-model unchanged/UI comparison. The earlier
UI confirmation, identical audited evidence and successful native error/recovery
gate support closing **UAT-04 within this retained read-only fixture scope**.
No repeated M1 or M2 owner batch is required for this scope.

The original crash and its missing managed stack remain documented in the
[correction record](m2-dispatch-fix-0.6.1.md). The native run now verifies recovery
from the controlled typed error with the fixed loaded boundary. It does not prove
the precise cause of the earlier CLR crash, longer-term stability, concurrent
requests from multiple chats, arbitrary native faults, or every Python exception
class in WPF. Persistent `bridge.log` was not supplied; native log rotation and
traceback persistence are not claimed from this capture.

Static report fields `runtime_verified=false`, `allplan_acceptance=not_run` and
`implemented_runtime_pending` are preserved; they are not an acceptance registry.
This record combines observed native results with explicitly attributed owner
observations. Portable **121-test PASS** remains separate evidence. Later Windows/Ubuntu
CI results are recorded in [validation and history](../validation-and-history.md). Acceptance does not extend to additional profiles/files,
dimension-range or unavailable-input native cases, native highlighting, durable
references, writable resources, repair/apply/readback/Undo, or cloud-to-Windows
connectivity. M3 preview exists separately in [draft PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2);
it is not part of this acceptance or main. Native repairs remain unaccepted.
