# 0.3.0 owner diagnostics — query outcomes awaiting evidence

Recorded: 2026-10-07. The owner reports completing the three tests and supplied
three diagnostics JSON files. **0.3.0 installation, bridge integrity, MCP
discovery and context reads are observed. Query/filter/paging outcomes have no
recorded verdict yet.** This is neither a failed query batch nor M1 acceptance.
Retrieve existing Codex responses or owner observations; do not repeat tests
solely because the diagnostics omitted their responses.

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

## Evidence gap and next action

`model_query` appears in `mcp.discovered_tools`, but no report contains a
`model_query` response, selection ID, cursor, source fingerprint, type UUID/name,
layer ID, attribute 498 result, query exclusions or summary. The 0.3.0
`collect_diagnostics` implementation invokes health/version/context only; it
does not capture other calls from the Codex chat. Three diagnostics captures
therefore do not map automatically to three query-case outcomes. The static
`allplan_acceptance: not_run` field is not an acceptance registry and does not
contradict the owner's statement that the tests were performed.

Pending existing responses or owner observations for: query count and new
metadata, distinct complete pages and full-selection summary, observed-value
type/layer/attribute predicates and passive-file exclusion. Visible model
preservation also awaits an explicit owner observation. No failure or PASS is
invented. No new developer tests were run for this evidence/documentation-only
update; the 24 portable checks remain their separate earlier record.

Next: obtain those already-produced results from the local Codex chat and record
bounded outcomes. If no query calls were actually made, provide only the missing
query prompts on the already-installed 0.3.0 package. No reinstall, repeated M0
or repeated 0.2.1 correction batch is needed.

## Uploaded source integrity

The original uploads are preserved byte-for-byte (14021 bytes each):

```text
163342: 47dced744f2577d62edfb89aa9c1e38551398025fd4fe63a978ddf4fefdde22c
163433: afb18e05d439c3e7dc05ad6b57ec0b6ee4065f2288682d17c2c6997bd53429b5
163602: 4fb315a9015e17a875ddd6f9cd6f155fa4968ccb164694362fd6c5ecb981aab1
```
