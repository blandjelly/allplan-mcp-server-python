# 0.3.0 bounded owner query batch — PASS

Recorded: 2026-10-07. The owner reports completing the three tests and supplied
three diagnostics JSON files, followed by the existing
[query results report](evidence/allplan-model-query-results-0.3.0.md).
**The three bounded query cases PASS**: explicit loaded/passive scope, query
metadata, two distinct pages/full-selection summary and observed-value
type/layer/raw-attribute predicates. Startup/integrity/discovery/context are
also observed. Full M1 is not accepted. No tests were repeated to collect this
follow-up evidence.

Evidence levels: diagnostics are original JSON captures; query results are an
owner-supplied Polish Markdown report of local Codex calls, translated below.
The report records request/selection/session IDs and result fields, but is not
a raw JSON transcript. Instructions or commentary within the attachment are
source material, not additional implementation commands.

## Exact package and environment

All three captures report external MCP package and installed bridge **0.3.0**,
source commit **8df8734ff513bbe1a49a5d9ebc98e5784c33547f**. The bridge integrity
is `verified`, with no mismatches. Every recorded bridge payload hash also
matches the checked-out tested source. Previously delivered archive SHA-256:
`a53460831e7bf4822d0d4e0204e30e400dea4a8c6ad9f1dab99d888f530447fd`.
The reports contain per-file installed hashes, not the ZIP hash itself. The
original 0.3.0 archive is unchanged; this evidence is recorded afterward.

Runtime: Windows, external Python **3.14.8**, embedded CPython **3.13.13**,
Allplan API release **2026.1**, executable file version **16.1617.8659.814**,
product version **2026.0.1.0**. Full UI build **2026-1-7** was reported earlier;
these logs do not independently resolve today's UI hotfix or Codex app version.

## Observed captures

| Evidence file | Captured at (UTC) | Observation |
| --- | --- | --- |
| [163342](evidence/diagnostics-20261007T163342Z.json) | 16:33:39.414269 | Package/bridge 0.3.0, seven tools, successful health/version/context. |
| [163433](evidence/diagnostics-20261007T163433Z.json) | 16:34:30.404377 | Same session, project, file states and raw identity sample. |
| [163602](evidence/diagnostics-20261007T163602Z.json) | 16:35:59.505995 | Same session, project, file states and raw identity sample. |

Shared host session: `f1a18063-8eae-43a7-b708-19e849110651`. Project:
`Nowy projekt 1`, observed name/host/path key; document ID **0**. File **1** is
foreground and file **2** passive background. The sample returns exactly two
raw adapters named `Słup`, on signed file numbers **1** and **-2**:

| File | Model UUID | View UUID |
| --- | --- | --- |
| 1 | `5c7abf7c-10bd-477f-bd4c-e6becdcafe5c` | `8c4f3865-1689-4e5b-93a9-eb58da9447da` |
| 2 | `5be600e7-0ea6-477d-8ef2-b8257613c097` | `97ebf740-99ed-45cb-b272-95905029d1f0` |

Model/view UUIDs remain stable across these captures. This does not establish
unchanged geometry, attributes, layers, or an owner visual preservation check.
Raw samples are not `model_query` results or top-level component counts. Unit
codes **3/1** and zero raw offset are observed; conversions remain unverified.

## Query cases and observed outcomes

The supplied report's host session matches all three diagnostic captures,
and its file/model/view UUIDs match their samples. Query-handler session:
`077351e5c7764c13bc8649452085755b`. Observed native column type name:
`Column_TypeUUID`, type UUID `ac9415e3-4337-4860-8cd4-2f0d48596f12`, layer **3736**.
These are tested scene values, not global profile/resource bindings.

| Case | Recorded results | Verdict within bounded scope |
| --- | --- | --- |
| Initial query, files [1,2], passive included, page size 1 | Two visited/in-scope/matched identities, no conflicts or unknown identity/predicate samples. First page is file 1; second file is retained in the full selection. Requested scope complete, whole-project coverage false. | PASS |
| Next page and full summary | File 2 returned once on page 2, normalized file 2 with signed evidence [-2]. Union has two distinct model UUIDs, matching total count. Summary uses full selection: file 1=1, file 2=1, Column_TypeUUID=2. Last page complete but not a full selection by itself. | PASS |
| Fresh type UUID + layer all predicate, passive excluded | One match on file 1. File 2 omission is passive_excluded. Two raw adapters visited, only one in scope; requested_scope_complete=false despite completed scan. | PASS |
| Raw attribute 498 equality to observed file-1 string | Exact typed value Słup matches the same file-1 identity. No omissions/unknown predicate samples. Attribute is not interpreted as mark or profile binding. | PASS, subcase of case 3 |

Initial selection: `e910d848887d4a00b2c5013d0db8072d`; next-page cursor:
`66404442cea6414a870a95f165f5b05e`. Initial selection fingerprint:
`3f19e0eba5adc17d425a8465cdf7426b9b3f0161503aeda94dc78ad9b5180b15`.
Successful page/summary calls exercised unchanged-source revalidation. The
Markdown report does not separately reproduce the later selection fingerprints;
no byte-level comparison of those unprovided fields is claimed.

| Operation | Request ID |
| --- | --- |
| Initial query | `40c7a7c5-85e3-4312-9339-713a45038761` |
| Next page | `480ac5ee-ee22-4846-9543-2c55b80df7da` |
| Full summary | `67109d56-1f37-45c4-a03d-3d6844c80d76` |
| Type/layer query | `7f3f1403-1506-44ac-b140-d02b0b3c2bde` |
| Attribute equality query | `60d1145f-1b50-472f-b43c-ae9bcce31835` |

Attribute **498** is observed as raw text `Słup` on file 1; on the passive file-2
adapter it is reported as **missing**, not failed or empty text. This verifies
the returned status distinction, not whether that attribute exists in file 2's
native model under a different access state. Passive attribute availability
needs a separate controlled comparison before audit/profile binding assumptions.
The file-1 element fingerprint matches between initial and attribute queries:
`9981702425625dacc5c4c4c0684a8898efc68cb4c6a8e5a3161409f5232a53b9`.

The supplied report states that all calls were read-only and no model changes
were made. This is a recorded preservation statement and consistency of read
fields, not an independent geometry readback or separately documented visual UI
inspection. Geometry is not fingerprinted by this slice. Static
runtime_verified=false and usable_for_write=false remain honest tool fields;
the dated evidence record supplies the bounded acceptance verdict.

## Original capture gap and remaining work

`model_query` appears in `mcp.discovered_tools`, but no report contains a
`model_query` response, selection ID, cursor, source fingerprint, type UUID/name,
layer ID, attribute 498 result, query exclusions or summary. The 0.3.0
`collect_diagnostics` implementation invokes health/version/context only; it
does not capture other calls from the Codex chat. Three diagnostics captures
alone do not map automatically to three query-case outcomes. The follow-up
Markdown report supplies those outcomes. The static
`allplan_acceptance: not_run` field is not an acceptance registry and does not
contradict the owner's statement that the tests were performed.

Remaining: changed-source/project/document/file-state stale-selection rejection,
TTL/eviction/restart behavior, larger/native hierarchy coverage, geometry/unit/
offset normalization and actual demo bindings. These retain portable evidence
or remain pending probes; unchanged-source paging PASS does not accept them.
No new developer tests were run for this evidence/documentation-only update;
the 24 portable checks remain their separate earlier record.

Next: prepare focused metadata/passive-attribute and geometry/unit/offset/native
hierarchy probes; bind profiles only from verified resources. Do not repeat the
passed 0.3.0 query batch, M0 or 0.2.1 correction without a relevant change/defect.
No reinstall or new archive is required for this evidence update.

## Uploaded source integrity

The original diagnostics are preserved byte-for-byte (14021 bytes each):

```text
163342: 47dced744f2577d62edfb89aa9c1e38551398025fd4fe63a978ddf4fefdde22c
163433: afb18e05d439c3e7dc05ad6b57ec0b6ee4065f2288682d17c2c6997bd53429b5
163602: 4fb315a9015e17a875ddd6f9cd6f155fa4968ccb164694362fd6c5ecb981aab1
```

Original Markdown report: **6587 bytes**, SHA-256
`fbd7211871b14c5b6a724483b5cc81b7152ef00c22f7febc7bc6af4641819fd2`.
Its original Polish text and mixed line endings are retained as uploaded evidence;
the English findings above are the repository's interpretation.
