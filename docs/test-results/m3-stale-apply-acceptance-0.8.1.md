# M3 stale Apply rejection — 0.8.1 native gate PASS

Recorded **2026-10-10 Europe/Warsaw**. Saved request timestamp **00:52:50.135**
local; result capture **00:53:21.785** local (2026-10-09 22:52:50.135 /
22:53:21.785 UTC). The owner states **“wartosci i wyglad bez zmian”**.

Decision: **PASS for rejection of the old plan at the native Apply entry point,
with unchanged audited fields and owner-observed values/appearance**. No Undo,
Recover or repeated batch is required. This complements accepted
[restart revalidation](m3-plan-restart-acceptance-0.8.1.md) and
[bounded write/Undo/recovery](m3-execution-acceptance-0.8.1.md).

## Original evidence

All three original uploads are preserved byte-for-byte in
[the evidence directory](evidence/m3-stale-apply-0.8.1-20261009T225321/), with
[size/SHA-256 manifest](evidence/m3-stale-apply-0.8.1-20261009T225321/evidence-manifest.json)
and [independent verification](evidence/m3-stale-apply-0.8.1-20261009T225321/verification.json).

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| allplan_stale_apply_request_62c9e25cb67027df3c5126057a4d2cbe.json | 1238 | `35594cd871352bde8f914eb1db60aff08ee6fd6431673c9530eeceb5b1633222` |
| allplan_stale_apply_rejection.json | 236741 | `0c26c1c95f0dcf2596248b533b4b4e6bf9040952bd5ae99889097b107eaaf700` |
| allplan_stale_apply_rejection.txt | 856 | `dd4b0363a63987b8fc7c0abc96883b0fc66f390330fc4a9514b9bf3cc62fb41c` |

Both healthy/integrity-verified host captures independently match all **22**
bridge hashes from the unchanged [0.8.1 ZIP](../../evaluation-packages/0.8.1/README.md),
SHA-256 `b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47`,
clean source `8074905536ff5c95e20de4a59a70d513f8694314`.
Host/MCP 0.8.1, API 2026.1, embedded Python 3.13.13, external Python 3.14.8.
Original files and historical acceptance flags remain unchanged.

## Exact request and observations

Execution **62c9e25cb67027df3c5126057a4d2cbe** uses the old plan
**500b57e169df4a6d99e982d413282542**, hash
**8687e394b90923fd99ca666fdc3f3ee588fe92dec7b5effdd483e16268dfa420**,
with the exact disposable-copy acknowledgement. The separate saved request
equals the report's embedded request record. Its timestamp precedes the result
capture; the capture itself is not an independent filesystem write-order trace.

The active host session **3ccecb6b-5695-44b6-b44b-3329acafa0cd** differs from
the plan's original **fdca1b5c-b147-4ac4-9c9e-4019eda2203b** and stays unchanged
through health/audit before and after the request. Apply returns:

```json
{"state":"rejected","read_only":true,"native_setters_started":false,
 "error":{"code":"plan_expired"}}
```

This is the known pre-setter rejection classification. No execution replay,
fresh preview or new repair result is present in this capture.
Both complete file-101 audits contain six columns and zero unchecked checks;
their source and report fingerprints match exactly:

- Source: `8339836f7441cbdb1ba1b76ae4aa8ea8a1fdd90a8e75a2da2bb2ce0a6c49c0b7`.
- Report: `251071b962416d7e7ade3c32e5d87500d518ba4f42151e6dce80ee2d4973e074`.

The report hash independently recomputes from the **original MCP text content**
in both responses. The structured copy normalizes some integral floats to
integers during JSON serialization; it compares numerically equal but cannot
alone reproduce the host's float-preserving hash. Keep the original text content.
TXT identifiers and results agree with JSON; comparison flags independently agree
with the full responses. S05 layer remains **3700/SZ_OGÓ01** and S06 status
remains **NEW**. The owner additionally confirms unchanged values and appearance.

Acceptance is bounded to this old-plan rejection, returned audited fields and
the owner's UI observation on the retained copy. Same-session source conflict
remains blocked by the observed interactive-host UI cancellation; unknown-outcome
recovery, wider mutation, grouped Undo and crash/power-loss behavior remain
outside native acceptance. No repetition of the cancelled-host conflict test
is requested. M3/UAT-05/UAT-06 are not closed.

Next implementation slice is the shared-service M3.3 versioned standard and
predicate/exception repair previews, delivered separately as **0.9.0**. That
slice has no standard/selected-plan Apply authorization and needs its own
[read-only owner card](../m3-standards-preview-batch.md).
