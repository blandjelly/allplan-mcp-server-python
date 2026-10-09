# M3 execution acceptance — 0.8.1, bounded native gate PASS

Recorded **2026-10-10 Europe/Warsaw**. Capture filename times are UTC:
Apply **00:16:35**, Check Undo **00:20:07**, Recover **00:22:17** local time
on October 10 (22:16:35, 22:20:07, 22:22:17 UTC on October 9).
**The retained two-column write/readback, exact-ID replay, two-step native Undo,
and recovery across host sessions pass.** M3/UAT-05/UAT-06 remain open for native
manual-edit conflict evidence and broader implementation. No repeated Apply
batch is requested for this gate.

## Original evidence and package

All six uploaded JSON/TXT files are preserved byte-for-byte under
[the evidence directory](evidence/m3-execution-0.8.1-20261009T221635/).
[Original-file manifest](evidence/m3-execution-0.8.1-20261009T221635/evidence-manifest.json)
records sizes and SHA-256 hashes;
[independent verification](evidence/m3-execution-0.8.1-20261009T221635/verification.json)
records the checked package, hashes, sessions and observations.

| Original file | Bytes | SHA-256 |
| --- | ---: | --- |
| m3-apply-20261009T221635402173Z.json | 384471 | `09491f5bbd2cf76f26b4080ffb01228f2a23ca40cbbfb56d5cbfd7d058d29f2c` |
| m3-apply-20261009T221635402173Z.txt | 430 | `3b957a21ad6381c93afea8aeebb7df3c72030c746e3c84ce179b859923f6fb37` |
| m3-check-undo-20261009T222007660555Z.json | 352952 | `991cbba97da9a21c4b6a5e063bc231f60b11f3d50e630c33f7d4615ae3b5f3a0` |
| m3-check-undo-20261009T222007660555Z.txt | 318 | `43da7b3c8d5676b7d7efe5633074447900ae62b72b77c9454e5de27c3b1a5ecf` |
| m3-recover-20261009T222217236441Z.json | 337202 | `fd8191e5a825a1742793b7d6df5d42fc6a97eb0a705accbcc267d948786e16b2` |
| m3-recover-20261009T222217236441Z.txt | 322 | `a183550362dca7eb3b75a5bb5702b66859535810c17cda10a9c596806e5f8cd5` |

The unchanged [0.8.1 Windows ZIP](../../evaluation-packages/0.8.1/README.md)
has SHA-256 `b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47`,
471793 bytes, clean source `8074905536ff5c95e20de4a59a70d513f8694314`.
All **22 installed bridge file hashes** independently match that exact archive
(installed Library/PythonHost maps to source Library/PythonParts).
Host/MCP report 0.8.1 and verified installation without mismatches.
The tested archive, delivery manifest and raw log acceptance flags are unchanged.

Native API **2026.1**, executable file/product resources
**16.1617.8659.814 / 2026.0.1.0**, embedded CPython **3.13.13**, external Python
**3.14.8**. UI **2026-1-7** was previously owner-identified; these logs do not
independently establish the UI hotfix. Read/audit profiles remain 1.0.2/2.0.0.

## Observed sequence

Execution `82ce52f62acb4590b1e62765612f219e`;
plan `ca0e44ad4bf8499eafc79043db36e80e`;
plan hash `4eb6ae8f12143e9985c612f5d77c0d588bc285ad54f181f0cee4afd8324be26a`;
request hash `18b340095203c7705096652e810c0a1f1f33fef974579bd7c8dbfeb8d1cde0b9`.
Both hashes independently recompute from the returned plan/expanded host request.
All four distinct audit report hashes recompute, and TXT agrees with JSON.

| Stage | Host session | Current observations |
| --- | --- | --- |
| Apply and same-ID replay | `75199ff8-9924-4c3a-83a0-bb7b4d072d1c` | completed, applied/applied; audited_fields_match_plan=true; audit 3; replay read_only=true |
| Check Undo and persisted replay | `dbc129b9-db32-4f74-bfe5-f5c8b30cb511` | old_value_observed/old_value_observed; audit 5; saved execution replayed read-only |
| Recover after owner-confirmed Redo, and persisted replay | `0aa79834-c9cd-4372-9cd0-ca15487bfd81` | new_value_observed/new_value_observed; audit 3; saved execution replayed read-only |

Read-only preflight passes all five checks: package/boundary, exactly two
proposals/three exclusions, unchanged revalidation, identical complete
five-finding audit and health. Apply freshly resolves the exact Column roots
and records **IsInMacro=true for both**, confirming the corrected parent-flag
eligibility on these native targets. All other required flags pass.

| Target | Native identity | Old → applied → Undo → Redo/Recover |
| --- | --- | --- |
| C05/S05 layer | file 101, `51db6258-4f95-4fab-ac80-8948e13bfd21` | 3701/SZ_OGÓ02 → 3700/SZ_OGÓ01 → 3701/SZ_OGÓ02 → 3700/SZ_OGÓ01 |
| C06/S06 MCP_QA_STATUS | file 101, `d26a3d87-2981-4657-b592-65c894ce41ba`, attribute 5002 | NWE → NEW → NWE → NEW |

The post-Apply full audit has six elements, 24 checks, three remaining mark
findings, zero unchecked checks and complete requested-scope coverage.
Undo restores five findings; Redo/Recover returns to three. Audit `state=fail`
is expected for remaining intentional mark defects. Health responds with a
verified installation after both read-only batches. Different host session IDs
and persisted exact-request results establish journal use across host sessions
for this fixture; they do not establish persistence through OS/power failure.

## Owner observations and acceptance limits

The owner reports that S05's layer and S06's status changed correctly, and that
Undo reverted the changes separately, requiring **two Undo steps**. The owner
ran Recover last rather than before Undo, then clarified:
**“Użyłem Ponów (Redo), przywracając obie naprawy.”** This accounts for Recover
observing both new values. No extra Apply or automatic replayed setters are
needed to explain this sequence. Historical `outcomes=applied` correctly remain
historical after Undo; `recovery.observations` describes current values.

Decision: **PASS for bounded two-target native apply/readback, audited collateral
verification, exact-ID deduplication across host sessions, manual two-step Undo,
and read-only recovery after Redo.** One-step grouped Undo is not implemented or
accepted; the owner card explicitly allowed observing one or two steps.

The owner did not separately attest that every other model property/element
remained unchanged or restate the UI version. The full post-Apply comparison
checks all six elements' audited fields against only the planned changes;
acceptance is bounded to that evidence and the reported target UI observations.
Raw `allplan_acceptance=not_run` / `runtime_verified=false` are preserved; this
document records the native test decision without rewriting source evidence.

Native same-session manual-edit conflicts remain **not_run**. Lost-response,
partial/unknown outcomes, journal failure, arbitrary types/files, cross-copy
identity, full application/OS restart and crash/power-loss behavior retain their
existing limits. Successful recovery of this completed execution does not prove
unknown-outcome recovery or mutation causality. Broader M3.3 services and generic
writable registry guarantees are unimplemented/unaccepted.

Next owner gate: [the focused manual-edit conflict card](../m3-conflict-batch.md).
Use the current repaired disposable copy and installed 0.8.1; do not repeat
M1/M2, rebuild the fixture, reinstall or rerun the accepted two-write test.
[149 portable tests and six-job CI](m3-execution-portable-0.8.1.md) remain
separate from this native evidence. This update changes documentation/evidence
only and publishes no new executable package or GitHub release.
