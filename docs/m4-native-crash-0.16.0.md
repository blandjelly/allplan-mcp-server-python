# M4 0.16.0 — native crash, 2026-10-13

Native result: **FAIL_CRASH**. Broad property discovery is **blocked_after_native_crash**.
The existing 233-test/6-job portable PASS remains historical source evidence and
does not establish native support.

The owner ran M4 Properties on Allplan **2026-1-7**. Health reported matching
0.16.0 source **8ac5e97563c881f3427fc47ef752b5c5362786ee**, verified installed bridge
hashes, embedded Python 3.13.13 and external Python 3.14.8. The uploaded crash XML
independently reports 2026-1-7 on the executable module; no version blame is inferred.

At **20:32:45.220 Europe/Warsaw** (18:32:45.220 UTC), bridge.log records
request **4fb64cc5-c87e-4580-ba15-adfda4f95c70**, route **/model-properties**.
The XML crash time is **20:32:45.389**, 169 ms later. That request has no response,
host_handler_failed or Python traceback entry. The client received execution_unknown.
Its only completed step was health_before; no metadata response, query/highlight
stage, Apply or model setter was requested.

The exception address belongs to KERNELBASE.dll; a parameter references CLR and
the XML supplies an exception parameter 0xffffffff80131604. The upload contains
no native stack or managed inner exception. These details do not identify a
particular Allplan API reader, nor demonstrate that its Python exception boundary
could catch this process failure. The exact API/root cause is **unknown**.

Code review found unconditional GetEnumValues calls on every sampled attribute.
They were removed because enum applicability was unproven. This is a code issue,
**not a proven causal explanation** of the crash. The public broad route now
rejects valid requests before any native build/document read; no opt-in bypass exists.

0.16.1 instead provides an isolated Column sample in one foreground file with
durable before/after records for new native readers. The old M1 scan is a named,
coarse boundary. The client saves exact pending requests before contacting the
host, and the launcher stops after this one sample and health. Definitions,
enum reads and UI presentation are not automatic. No claim of native fault
containment or repaired property discovery is made.

[Inspection and relevant bridge excerpt](../evaluation-packages/0.16.0/native-acceptance/20261013-owner/).
The four original uploads are identified by their new upload hashes. Raw crash
environment/private paths and the full historical bridge log are not published;
the submitted files remain in the chat/workspace.
[Next isolated observation](m4-isolated-probe-owner-test.pl.md).
