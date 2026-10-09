# M2 crash evidence and dispatcher containment — 0.6.1

Date **2026-10-09**. **121 portable tests PASS; targeted native 0.6.1 test PASS.**
[Native evidence and bounded UAT-04 acceptance](m2-acceptance-0.6.1.md).
[Completed owner test](../m2-stability-batch.md). The earlier crash's precise cause
remains unproven without its matching stack.

## Confirmed incident evidence

Uploaded collection, preserved byte-for-byte:

- [Crash JSON](evidence/diagnostics-crash-20261009.json), 305061 bytes,
  SHA-256 `5e0c63cd63aa02c4073d26e6e3d826746b8a6050b062aa8381a8f4c0169d000b`.
- [Crash summary](evidence/diagnostics-crash-20261009.md), 6777 bytes,
  SHA-256 `f12f278186df314623722b9459e6dc11db1e7971b613072e8771213278a327c9`.

Allplan.log records exception handling at **12:50:12.730 Europe/Warsaw** and
exception **0xE0434352** at **12:50:12.737**. The absolute exception address is
0x00007FFE90A941CA; no module-relative offset is established. This code indicates
a CLR/managed exception; it does not identify its managed type, message or module.
Three WER 1001 records (71756/71757/71765) refer to stages of the same APPCRASH
report a35dfec4-b6eb-4017-84fa-c7f7817f32f7, not three crashes.

The crash falls within the recorded second tool interval **12:50:07.761–12:50:15.195**
(wrapper/approval overhead included). That request is **101efe01-58e9-4296-aa93-e1a2c18b60b4**,
profile_id=native-model-qa-demo, drawing_files=[101,102], include_passive=true,
visibility=api_select_all. It lost its host response (execution_unknown) and was
not retried. The earlier 101-only audit completed correctly at about 12:48:13.

Current crash trace identifies Allplan **2026-1-7 39.1617.8659.814**; current
file version remains **16.1617.8659.814**. Current executable ProductVersion string
2026-1-7 differs from the earlier diagnostics' numeric fixed-resource
product_version=2026.0.1.0. Preserve both sources; do not treat them as the same field.

The incident dump is missing; the WER archive/temporary XML remained access-denied.
No matching Application Error 1000 was collected. Available minidumps belong to
older incidents, and contemporaneous LiveKernelEvent records refer to older
WATCHDOG dumps. None supplies this crash's faulting module or stack. No bridge
console transcript was persisted by 0.6.0. Those limits remain unresolved.

## Concrete defect and causal limits

The unchanged demo profile permits **only file 101**. The recorded second scope
must raise invalid_payload before native document/element enumeration; it is not
an accepted audit of passive 102. Production 0.6.0 sends this semantic error to
the host. BridgeServer.execute dispatches a Python callback through WPF
Dispatcher.Invoke(Func[Object]). That callback previously raised BridgeError
without catching it. The HTTP worker's outer try/except runs outside the UI
callback and cannot guarantee containment of an exception entering WPF's native
UI exception handling.

A portable comparison against the **original delivered 0.6.0 transport extracted
from its unchanged ZIP** reproduces the recorded scope rejection crossing the
simulated managed callback. The fixed transport returns primitive error data
from the callback and raises invalid_payload on the HTTP worker after dispatch
returns. This proves the code defect and containment change. It does **not**
prove the unobserved CLR stack of the actual incident. The defect and managed
exception code provide a plausible mechanism. The successful native 0.6.1 gate
confirms controlled error/recovery behavior; a matching incident stack would be
needed to establish the precise historical cause.

## Delivered correction

- UI callback catches typed BridgeError and unexpected Python exceptions,
  including SystemExit/KeyboardInterrupt, and returns result/error data. It
  passes no live exception/traceback objects through Func[Object]. The worker
  restores HTTP status/code/message; unexpected errors become host_error/500.
  Native fatal faults are outside this Python exception boundary.
- Host audit validation now runs before native build/document calls. Public
  typed MCP/diagnostic validation also rejects scopes exceeding the profile
  before contacting Allplan. Duplicate drawing-file IDs are rejected there too.
  The demo profile still permits only 101; no silent expansion or clipping occurs.
- Host startup configures a bounded persistent log at
  Local/.allplan-mcp/logs/bridge.log, UTC timestamps, 1 MiB with two backups.
  Request starts, response/rejection outcomes, sessions and request IDs persist;
  unexpected handler tracebacks are logged on the HTTP worker. File logging
  failure falls back to the existing console. Request bodies/model values are
  not added to ordinary request logs; exception traces may contain diagnostic
  exception text. Logs persist across host restarts without duplicate handlers.
- M2 Stability.cmd first verifies matching installed host/MCP versions,
  verified bridge integrity and a runtime marker emitted by the loaded fixed
  transport. It stops before model/context reads and negative probes if these
  checks fail, including metadata updated on disk while old transport remains
  loaded. It then saves two explicit valid read responses, public rejection,
  one direct protected host rejection and post-rejection host health. It stops
  on failure and never automatically retries a lost read. JSON/TXT remain
  separate from an owner acceptance verdict.

No setters, highlight or repair operations were added. Original 0.6.0 archive,
M1 profiles and native diagnostic evidence are preserved. New runtime changes
use **0.6.1**; the tested 0.6.0 artifact is not rebuilt.

## Portable verification

Frozen sync succeeds. Linux Python **3.12.14**, FastMCP **3.2.4**, uv **0.12.19**.
Full suite: **121 tests PASS**, including 7 additional targeted cases over the
114-test baseline and an expanded existing public-input test.

Tests exercise typed 400 errors, unexpected 500 errors, SystemExit containment,
JSON-only UI/worker handoff, subsequent healthy requests, queued cancellation,
persistent log bounds/deduplication/failure, and the exact incident scope with
zero native document/enumeration calls. Actual MCP HTTP tests reject the incident
scope before bridge calls and exercise the stability CLI's two reads, direct
host rejection, final health and stop-on-failure behavior, plus refusal to probe
an old/mismatched installation or a host without the loaded boundary marker.

Portable fake dispatchers do not execute WPF/pythonnet or Allplan. The separate
[native 0.6.1 run](m2-acceptance-0.6.1.md) supplies typed-error recovery and
repeated-audit evidence. Longer-term stability, all exception classes in WPF,
native log rotation/traceback persistence, and a new remote CI matrix PASS are
not claimed. Wheel/sdist and deterministic Windows package/integrity checks
passed with the new launcher. The [owner card](../m2-stability-batch.md) is completed.
