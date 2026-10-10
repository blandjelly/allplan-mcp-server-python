# M3 explicit marks preview — 0.10.0 native gate PASS

Recorded **2026-10-10 Europe/Warsaw**, filename capture timestamp
**16:13:19.981755** local (14:13:19.981755 UTC). Owner:
**“wykonalem test wersji 0.10.0, wysylam logi, model w allplan bez zmian, host nieprzerwany”**.
Decision: **PASS for three read-only mark-preview scenarios on the retained
repaired six-column copy in drawing file 101**. No repetition is required.
M3/UAT-05/UAT-06 remain open.

## Original evidence and identity

The [original JSON/TXT](evidence/m3-marks-0.10.0-20261010T141319/),
[manifest](evidence/m3-marks-0.10.0-20261010T141319/evidence-manifest.json)
and [independent verification](evidence/m3-marks-0.10.0-20261010T141319/verification.json)
preserve both uploads byte-for-byte, including Windows line endings.

| Original | Bytes | SHA-256 |
| --- | ---: | --- |
| m3-marks-preview-20261010T141319981755Z.json | 318299 | `e88d1dc8fcc765874b75e437057892fa32ad5cb1d3945b4015f4a214c4376db9` |
| m3-marks-preview-20261010T141319981755Z.txt | 4773 | `ce73088b9b86ab9a2345008df4db015a4f1c0ebf7098a09a1d920b6fb25e72c7` |

Both health captures identify MCP/bridge **0.10.0**, embedded CPython **3.13.13**,
external Python **3.14.8**, Allplan API **2026.1**, verified installation and no
integrity mismatches. Executable file/product resources are
**16.1617.8659.814 / 2026.0.1.0**; this capture does not independently identify
the UI hotfix. The loaded exception boundary is `contained_result_error_v1`.

All **22 reported bridge-file SHA-256 hashes** independently match source bytes
at clean commit `ebf2c752440a0f72b538527f35175668322395a4`; each source blob is
unchanged on inspected M3 head `742f0ebf51ee17caf554595bec49670ea3226d2d`.
Library/PythonParts/StartPythonHost.pyp maps to installed Library/PythonHost.
The [unchanged 0.10.0 delivery](../../evaluation-packages/0.10.0/README.md)
records ZIP **660447 bytes**, SHA-256
`5a3e2ba0d75ebd798204922cf44da70d602bc2e41b8cdbe2f2f7f5c3b3c67888`.
This analysis verifies source/installed hashes, not binary equality to the ZIP:
the connector rejected binary archive reads. No archive is rebuilt or replaced.

## Native scenarios

All **10 steps are OK**:

| Scenario | Observed result |
| --- | --- |
| health_preflight / health_after | Verified 0.10.0; same host session. |
| audit_before / audit_after | Complete six-column audits, identical except request IDs; three mark findings, zero unchecked checks. |
| explicit_marks / revalidate | C03 undefined mark → S03 and C04 S02 → S04, attribute 5001: two proposals; zero proposed collisions, remaining duplicates or missing marks; exact plan unchanged. |
| mark_exception / revalidate | C04 explicitly excluded: only C03 → S03 proposed; one existing S02 duplicate group remains; exact plan unchanged. |
| excluded_peer_collision / revalidate | C03 → S06 collides with the existing S06 peer despite its explicit selection exception; one collision group with both exact UUIDs; exact plan unchanged. |

Both selected scenarios report **5 selected, 1 exception, 0 unchecked predicates**.
Mark validation uses the **full six-element snapshot**, including excluded peers.
The proposed collision state `conflict` and audit state `fail` are expected test
results, not failed operations. Revalidation compares unchanged source evidence,
so even the collision plan correctly revalidates as `unchanged`.

Both audits contain **24 checks: 20 pass, 3 fail, 1 not_applicable,
0 not_checked**. QA-001 identifies the missing mark; QA-002 identifies both
members of the S02 duplicate group. QA-003/QA-004 pass for all six columns.
The repaired layer/status fixture is retained; this does not rerun the older
five-finding pre-repair M2 gate.

Source fingerprint:
`8055a1b63bae34a3c0dcf379a4e2c8b2439d22dccf746874de4643ce21077799`.
Report fingerprint:
`6f2bfd929ec01cca512e430517057666fdae69a79e494676ecadeee4dd8cb658`.
Both report hashes and all three plan hashes independently recompute from
original MCP text and expanded wrapper requests/profile. The plan hashes are:

- explicit_marks: `74eb332a265cd7ec2a7fb7e3a8eb6601d8ef80d9ba1b9de3f99f23a61ef3ebf6`.
- mark_exception: `4ed035f16791228a33780fa2895ccc604756312fb8414046f0f83a72adcbe5e1`.
- excluded_peer_collision: `c533a30e4f6e9c47850ca5bb4eb37da801c879083a9efc1e7e1059b8b279a66b`.

All three revalidations preserve exact plan IDs/hashes and matching source/report
fingerprints with `source_unchanged=true`. All ten responses identify host session
`6856cef1-a336-4ef5-a51a-e6663545492d`, corroborating the owner's uninterrupted-host
observation. Original MCP text equals decoded responses; TXT exactly reconstructs
from JSON after newline normalization.

## Acceptance and limits

The owner confirms **model unchanged and host uninterrupted**. Logs establish
equality of audited data before/after; the owner observation supplies the UI
confirmation. Every plan/revalidation keeps `apply_available=false`,
`evaluation_apply_available=false` and `usable_for_write=false`.
No Apply, Recover or Undo request occurs in this batch.

Original `allplan_acceptance=not_run`, `runtime_verified=false`,
`ready_for_ui_observation` and the TXT header `Execution: not_started` are
historical capture fields and remain unedited. The recorded ten read-only
steps completed; this separate record supplies the bounded acceptance decision.

Earlier 0.8.1 layer/status write/readback, two separate Undo steps, Redo/recovery,
restart invalidation and stale-Apply rejection remain accepted in their separate
scope. This new gate does not establish mark setters, selected/standard writes,
automatic numbering, graphical labels, wider types/files, native unknown-outcome
recovery, grouped Undo or crash/power-loss persistence. Same-session UI-edit
conflict remains blocked in the observed interactive-host lifecycle.
Existing 165-test/six-job CI results belong to the original delivery commits;
this evidence/documentation update changes no runtime code, dependency or version
and does not claim a new portable test run. Continue M3 from the accepted preview
baseline; no new owner batch is requested by this update.
