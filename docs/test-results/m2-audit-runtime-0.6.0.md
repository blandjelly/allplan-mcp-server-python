# M2 native audit capture — 0.6.0, historical crash follow-up

**Superseded acceptance status:** [0.6.1 targeted native test](m2-acceptance-0.6.1.md)
passed and closes UAT-04 within the retained fixture scope. The record below
preserves the earlier 0.6.0 outcome and open-gate reasoning; it does not certify
0.6.0 stability or resolve the precise crash cause.

Date: **2026-10-09**, capture started **12:48:09 Europe/Warsaw**
(10:48:09 UTC); filename timestamp 10:48:13 UTC. Package **0.6.0**, audit
profile **2.0.0**, preserved M1 read profile **1.0.2**.

**Report/fixture checks PASS; owner UI correspondence and unchanged model
confirmed. Overall UAT-04 is OPEN pending crash diagnosis.** The owner then
reported an Allplan crash. Subsequent [crash collection and correction](m2-dispatch-fix-0.6.1.md)
establish the crash time, exception code and second request arguments, but not
the incident stack/faulting module. A concrete callback exception escape is
fixed in 0.6.1; its [targeted native stability test](../m2-stability-batch.md) is
pending. Do not mark M2 closed or begin M3 repairs from this capture.

## Original evidence and package identity

- [JSON capture](evidence/diagnostics-20261009T104813Z.json), retained byte-for-byte:
  SHA-256 `b7924dd3e2217b73b8583402f04c544d692ff18ea8866784bfc1e12795556628`.
- [Readable TXT](evidence/diagnostics-20261009T104813Z.txt), retained byte-for-byte including Windows CRLF:
  SHA-256 `43fe30060d0510f580822480f76b1cad606858839afc3dcf1a5498c6eb70a4a3`.
- Original Windows archive SHA-256:
  `6fc6e37fa4abd09ffec5b7a72d2b34a3a67c49a1ad2eef4cd480426428be2dd7`.
  Keep that delivered archive unchanged; this evidence/documentation update does
  not rebuild it. Its manifest records baseline commit `bc5137339f3a6fa2049b322d7c726e659b523279`
  and `source_modified=true`; file hashes identify the delivered M2 implementation.

The host reports bridge 0.6.0 with SHA-256-verified installation and zero
mismatches. All **18** installed bridge file hashes match the delivered archive,
including the native host handler and audit modules. MCP discovers all eight
tools and reports external package 0.6.0. Embedded CPython is **3.13.13**,
external Python **3.14.8**, native API release **2026.1**. Executable
file/product versions **16.1617.8659.814 / 2026.0.1.0** match the accepted
baseline. The current log does not independently identify the UI hotfix;
2026-1-7 remains the previously owner-reported build, not a metadata mapping.

Audit request ID: `f8b09464-39a2-4ffe-9c23-87450ea6208f`.
Host session: `7273e304-ddd3-4f89-bbc4-5a46020bd6d5`.
Query session: `d735de037d62466eb06840a1f5fbe85e`.
Report fingerprint: `56bb6e8189ce28eb6c96d6a6e8d770ab15167a582f3340198753f64eaa2894ce`.
The report hash recomputes correctly after removing transport-added request/host
IDs. Its profile hash matches the packaged audit profile; TXT matches the JSON
report text after normalizing line endings.

## Observed native outcome

Project **MCP_QA_DEMO**, drawing file **101 active foreground**, **102 passive
background**, 103 absent from the loaded inventory; project offset **0/0/0**.
The explicit audit scope includes only 101 and excludes passive files. Mark and
status resources bind to native IDs **5001/5002**, string type code **67**;
structure/review layers bind to **3700/3701**, SZ_OGÓ01/SZ_OGÓ02 respectively.
Binding is read-only and inactive for writes.

Enumeration visits 17 raw adapters, 16 in scope, deduplicates six
representations and yields six column identities. Four noncolumn native roots
are rejected by the family predicate. No identities, hierarchy, predicates,
fields or requested files are unchecked/conflicting/omitted. Requested scope,
returned fields and audit coverage are complete; whole-project coverage is false.

**24 checks = 18 pass + 5 fail + 1 not_applicable + 0 not_checked**.
Exactly **5 findings on 5 columns**, **1 duplicate group**, **3 errors and
2 warnings**. Audit state `fail` means the five intentional fixture violations
were found; it is not an execution error.

| Rule | Fixture/mark | Evidence | Model-local center, mm |
| --- | --- | --- | --- |
| QA-001 | C03 / `<niezdefiniowany>` | Raw literal retained; explicit missing-value policy applies | 12000 / 0 / 1500 |
| QA-002 | C02 / S02 | Two-member file-101 column duplicate group | 6000 / 0 / 1500 |
| QA-002 | C04 / S02 | Same duplicate group, separate model reference | 0 / 6000 / 1500 |
| QA-003 | C05 / S05 | Observed layer 3701; expected 3700 | 6000 / 6000 / 1500 |
| QA-004 | C06 / S06 | Observed NWE; allowed NEW/EXISTING | 12000 / 6000 / 1500 |

C01 model UUID `eb88c850-0cac-408a-8091-f118872d74c2` passes all four rules.
C03's unique-mark check is not_applicable. Both S02 findings share the same group
ID and exactly the two file-101 member references. All five locators have observed
model-local boxes of 400 × 400 × 3000 mm and observed centers matching the fixture;
small floating-point residues at Z≈0 do not change these dimensions. Offset is
zero and not applied to local coordinates. No remedy/highlight is applied and
all references remain nondurable, unusable for writes.

## Owner observations and crash follow-up

The owner explicitly confirmed: **“Tak, wskazania zgadzają się i model jest bez
zmian”** (findings/locations match the UI, model unchanged). This supplies the UI
and unchanged-model evidence requested by the UAT card.

The subsequent report is: **“allplan mial crash XD ale nie wiem czy to zwiazane
z naszym narzedziem”** (Allplan crashed; relationship to the tool is unknown).
Asked about timing, the owner first selected **“Po zapisaniu raportu, bez
dalszych działań”** (after the report was saved, no further actions), then added
**“wykonalem w innym chacie polecenie model_audit, chyba wtedy”** (invoked
model_audit in another chat, probably then). This suggests a possible second
request after the completed diagnostic; it does not identify its arguments,
or precise ordering. Do not claim the recorded first capture crashed.

The owner then supplied the second chat's result: the audit lost its host
response with **execution_unknown**, request ID
**101efe01-58e9-4296-aa93-e1a2c18b60b4**; it was not retried. That result
is unknown. This is user-supplied response text, not a second original JSON
capture or crash dump. It confirms a distinct failed response, but does not
establish the faulting module or whether the native operation completed.

No causal conclusion is established. The JSON/TXT contain a complete successful
read response, not a Windows crash event, stack trace or post-response lifecycle
trace. They do not record faulting modules or later UI actions.

Code inspection confirms M2 obtains one fresh snapshot through the existing
UI-dispatched M1 native readers; rule evaluation and returned locators use JSON
data, with no native writes/highlight. Native geometry/attribute/hierarchy reads
and host lifecycle still interact with Allplan and need crash evidence before
their role can be assessed. This first capture alone did not identify a defect. Subsequent second-request
evidence revealed that an invalid scope raised an exception through the UI
callback, now contained in 0.6.1; see the linked correction record.

The historical follow-up collected the second arguments and Windows/Allplan
crash records. That collection is preserved alongside this first capture.
**Next: [0.6.1 native stability check](../m2-stability-batch.md)**, with two valid
reads and controlled public/host scope rejection. Keep UAT-04 open until it passes
and the owner confirms Allplan remains open/model unchanged. Static runtime_verified/
allplan_acceptance fields remain unchanged and are not a live acceptance registry.
