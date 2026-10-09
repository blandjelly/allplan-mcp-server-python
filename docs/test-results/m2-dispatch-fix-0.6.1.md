# M2 dispatcher correction and crash limits — 0.6.1

Recorded 2026-10-09. **121 portable tests PASS**; the separate
[native 0.6.1 recovery gate passed](m2-acceptance-0.6.1.md).

## Confirmed incident

The original collection is archived as
[crash JSON](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-crash-20261009.json)
and [crash summary](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-crash-20261009.md);
[original hashes](../validation-and-history.md#archived-reports-and-logs) identify both.
Allplan.log records exception handling at **12:50:12.730 Europe/Warsaw** and
CLR exception **0xE0434352** at **12:50:12.737**. Three WER records concern one
APPCRASH report, not three independent crashes.

This falls inside a second audit request, ID
`101efe01-58e9-4296-aa93-e1a2c18b60b4`, using demo scope [101,102] with
include_passive=true. Its host response was lost and it was not retried.
The earlier 101-only audit completed successfully and matched the owner's UI.
The demo profile permits only file 101; the second request must be rejected.

No matching incident dump, managed stack, faulting module or module-relative
offset was obtained. Older minidumps and WATCHDOG events do not identify this
incident's cause. The managed exception code alone does not identify its type.

## Fixed defect

0.6.0 could raise BridgeError inside the WPF Dispatcher.Invoke callback. An
outer HTTP-worker catch cannot guarantee containment in the UI callback.
A portable comparison against the transport from the original 0.6.0 ZIP
reproduced this exception escape with the incident's invalid scope.

0.6.1 catches typed and unexpected Python exceptions inside the callback and
returns primitive result/error data. The HTTP worker restores the error after
dispatch; exception objects do not cross the WPF delegate. Public and host audit
validation reject unsupported scopes before native reads. Native fatal faults
remain outside this Python boundary.

Persistent bounded request/error logging and the loaded-boundary preflight
support diagnosis. [Diagnostic commands](../diagnostics.md) describe the
two-read, scope-rejection and health gate. No setters, highlighting or repairs
were introduced, and the original delivered 0.6.0/0.6.1 ZIPs remain unchanged.

## Verification and causal limits

Portable tests cover typed/generic errors, SystemExit containment, JSON-only
callback handoff, subsequent health, cancellation, log bounds/fallback,
preflight refusal, the exact invalid scope with zero native enumeration and
real MCP/HTTP/CLI behavior with fake native adapters. Frozen sync, wheel/sdist
and Windows package checks passed. Later six-job CI results are recorded in
[validation and history](../validation-and-history.md).

The native 0.6.1 run verifies repeated valid audits and controlled typed-error
recovery with the fixed boundary loaded. This proves the correction's tested
behavior; it does not establish the missing stack of the earlier CLR incident.
Longer-term/concurrent stability, arbitrary native faults, all exception classes
in WPF and native log rotation/traceback persistence remain unverified.
