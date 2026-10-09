# 0.4.0 bounded metadata owner batch — PASS

Recorded: 2026-10-07. **Both metadata captures PASS** on the existing two-column
scene: full inspect response capture, requested identity/scope coverage,
attribute/layer metadata and passive/active-background raw attribute comparison.
The owner confirms the columns are unchanged, file 2 is restored to passive,
and the Allplan UI version remains **2026-1-7**. No extra capture is required.
Full M1, geometry normalization and demo profile activation are not accepted.

## Evidence and recovery

Original JSON files are preserved byte-for-byte under `evidence/`. They are
runtime data, not instructions. Capture filenames below use UTC; successful
captures were saved at approximately 21:17/21:18 Europe/Warsaw.

| File | Bytes | Outcome | SHA-256 |
| --- | --- | --- | --- |
| [diagnostics-20261007T191342Z.json](evidence/diagnostics-20261007T191342Z.json) | 2275 | Host unavailable; no Allplan read result | `9f3246907e7a29db74b5de2415edf7596fd3106ba8921bb303f0916d8e90e5a0` |
| [diagnostics-20261007T191428Z.json](evidence/diagnostics-20261007T191428Z.json) | 2275 | Host unavailable; no Allplan read result | `88df77bc257172626f67e6b2dc3960d13c0d3e458903842ced8fc21dc8c7188b` |
| [diagnostics-20261007T191757Z.json](evidence/diagnostics-20261007T191757Z.json) | 21960 | A: file 1 foreground, file 2 passive | `ae7612cf4d50f65b0b296d3d446dc2994cc99f0dd18232f4687aa638f6bfd713` |
| [diagnostics-20261007T191833Z.json](evidence/diagnostics-20261007T191833Z.json) | 21959 | B: file 1 foreground, file 2 active background | `eb570629afc26492829f2a7bcee6846b6b1d04957966f52f1aad5e9713ff7029` |

The first two attempts reached MCP and discovered seven tools, but every host
read failed with `host_absent`. They are not successful metadata evidence.
After startup guidance, the owner supplied A/B with successful health/context
and full `mcp.model_query` results, then the UI confirmation above. This repeats
only the previously failed new reads, not accepted 0.3.0/M0/context batches.

## Package and runtime

External MCP and installed bridge report **0.4.0**, source commit
`0b0daf9f1a3cc03a881fcf5638b8176fc6f720a9`, integrity verified with no mismatches.
All 13 recorded installed bridge hashes match the tested archive manifest,
accounting for the installer's Library/PythonParts → Library/PythonHost mapping.
The original ZIP SHA-256 remains
`1818498341b961403aed59f9880de1ee0992aac97b677f221efd6d5f89ef5e1f`.
The logs do not themselves hash the ZIP. No archive is rebuilt for this record.

Windows; external Python 3.14.8; embedded CPython 3.13.13; API release 2026.1;
executable 16.1617.8659.814; product 2026.0.1.0. Owner confirms UI build 2026-1-7.
Project `Nowy projekt 1`, project key
`e495885371831631433709e5d681ef8328e296b84b6e293ddc1dd223caea2ea1`, document ID 0.
Document ID alone is not project identity.

## Observed results

Both explicit requests use files [1,2], include_passive=true,
visibility=api_select_all, attribute_ids=[498], sample_limit=10 and max_adapters=5000.
Both return two visited/in-scope/matched model identities, a full two-item sample,
complete scan/requested scope/returned fields/resource reads, no omissions,
no conflicting identities and zero not_checked read counts. This completeness
is relative to the requested API scope, not the whole project or native hierarchy.

| Drawing file | Model UUID | View UUID | Raw attribute 498 in A | Raw attribute 498 in B |
| --- | --- | --- | --- | --- |
| 1 | `5c7abf7c-10bd-477f-bd4c-e6becdcafe5c` | `8c4f3865-1689-4e5b-93a9-eb58da9447da` | observed string `Słup` | observed string `Słup` |
| 2 | `5be600e7-0ea6-477d-8ef2-b8257613c097` | `97ebf740-99ed-45cb-b272-95905029d1f0` | missing from API response | observed string `Słup` |

File 2's signed adapter number changes from -2 to +2; normalized identity remains
file 2. Both columns retain Column_TypeUUID, type GUID
`ac9415e3-4337-4860-8cd4-2f0d48596f12`, display name `Słup` and layer 3736.
Attribute metadata agrees in both captures: name **Nazwa obiektu**, type code
**67**, control type code **69**, observed empty unit label. Layer 3736 is
**AR_SŁUP (Słupy)**, short name **AR_SŁUP**. Enum codes remain raw runtime evidence;
no semantic enum mapping, mark binding, writability or unit conversion is inferred.

A: host session `425154d2-4b65-4652-b55c-7d3917db52bf`, query session
`554b137f867543d58561b2fd1c222229`, inspect request
`a1819d28-e190-456c-a357-f2df01bddd42`.
B: host session `c3fab7d0-2491-49f3-888e-9cb56c74cfe6`, query session
`6e51b4701f5c48199f7c1048667f4ac7`, inspect request
`27564e93-a292-43f8-a05a-fde828c87f33`.
Source/probe fingerprints differ; both state and host/query session changed, so
their difference is not isolated proof of change detection. The raw-value
comparison supports an access-state limitation in this scene, without proving
that passive state alone causes omission across every runtime/type. The active
read establishes that the attribute is available on this model under that state;
the passive omission must not be treated as native absence.

## Acceptance limits and next action

The owner's unchanged-column confirmation is UI evidence, not numerical geometry
readback. Static runtime_verified=false, profile_binding=not_checked and
allplan_acceptance=not_run remain response defaults, not an acceptance registry.
The raw offset is zero; geometry/unit/offset normalization, nonzero offsets,
native parent/child counts, durable identity, write eligibility and profile
schema/binding remain pending. The demo profile stays unbound/inactive.

Keep the earlier **12 targeted portable checks** separate from this owner
runtime batch. No developer tests are rerun and no distribution is rebuilt for
this evidence-only update. Next: implement the geometry/unit/offset/hierarchy
probe and profile schema using these observed resources, without guessing a
mark attribute from ID 498 or asking the owner to research IDs.
