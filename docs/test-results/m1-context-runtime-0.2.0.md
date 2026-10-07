# M1.1 owner runtime feedback — 0.2.0

Received 2026-10-07. Owner reports the test was performed and supplies three
diagnostic JSONs. **Partial runtime evidence; project identity FAIL**. M1.1 is
still in progress. M0 acceptance is unchanged.

Subsequent **0.2.1 correction batch PASS** resolves this project lookup failure
and verifies unload exclusion; see [the new evidence](m1-context-runtime-0.2.1.md).
The observations below remain the historical 0.2.0 result.

## Evidence

Original uploaded bytes are retained under `evidence/`. All reports show server
and installed bridge version **0.2.0**, verified bridge hashes, successful MCP
discovery of six tools and successful health/context transport. Allplan API
release is **2026.1**, executable file version **16.1617.8659.814**, product
version **2026.0.1.0**, embedded CPython **3.13.13**, external Python **3.14.8**.
The previously supplied UI build was 2026-1-7; these logs do not read the hotfix.

| File (UTC filename) | Foreground | Loaded files | Raw identity sample |
| --- | --- | --- | --- |
| [131055](evidence/diagnostics-20261007T131055Z.json) | 1 | 1 foreground; 2 active background | One column on file 1 |
| [131446](evidence/diagnostics-20261007T131446Z.json) | 1 | 1 foreground; 2 passive background | Column on signed file -2, inactive; column on file 1, active |
| [131542](evidence/diagnostics-20261007T131542Z.json) | 21 | 1 active background (`Osie`); 21 foreground (`Parter`) | Ten bounded adapters: eight grid entries on file 1, slab and wall on file 21 |

All three host session IDs differ. Model/view GUIDs are readable and separate
in every returned item. The second capture proves passive adapter inclusion and
the documented negative file number; active-background file 1 in the third
capture has positive file numbers with `in_active_document=false`. This flag
alone is therefore not a write-eligibility rule. These samples are not component
counts and cannot prove complete model coverage.

Input length/angle enum codes are **3 / 1**; project offset is **[0, 0, 0]** in
all three reports. UI unit correspondence and nonzero offset semantics are not
verified by these logs. Document ID is **0** in all reports and cannot establish
project identity.

## Defect and interpretation

Every report returns `project.status=not_checked`, reason `ValueError`. The
0.2.0 implementation couples project name/host to path lookup, so any path
failure suppresses even successfully read name/host. The report does not retain
enough information to identify the exact native return value or failure stage.
The original path call follows the published 2026 signature; older reference
material uses the opposite positional argument order. An argument-order issue
is a hypothesis, not established runtime evidence.

The third capture is consistent with a changed drawing-file context after the
owner's project-switch step; project name/key verification **fails**. File 2
remains loaded in both first and second captures. Its active-to-passive transition
is observed; **unload exclusion is not demonstrated**. The owner has not supplied
an explicit visual-unchanged or UI correspondence result form. No complete
UAT-02/UAT-03 or M1 acceptance is claimed.

## Follow-up — 0.2.1

The replacement preserves project name/host when path resolution fails and
reports each path lookup's argument order, native error and path independently.
A second read-only lookup tries the alternate argument order if the first cannot
resolve a key. Unknown/boolean statuses and exceptions cannot manufacture a key.
The key remains a non-durable name/host/path fingerprint. New portable tests
exercise fallback, failure retention and absence of project switching.

**31 portable tests PASS**; wheel/sdist and versioned ZIP prepared. Runtime fix
verification remains pending. [Short follow-up batch](../m1-context-fix-batch.md).

Source upload SHA-256:

```text
131055: 627c5e56dcf43111c9d788876e8e715ed3894c4c37a7df2457bac956a4b24b33
131446: cb2e18cd453e91409a96048a93ca5b44344f25e75980f8d4f691fea21fe450eb
131542: b6690ca7772563424ba31fdd7b2f288b52cb4142356f3e0eaf0943fd998b9bb7
```
