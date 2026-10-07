# M1.1 context correction — owner runtime PASS on 0.2.1

Recorded 2026-10-07. **The bounded context/identity follow-up batch PASS** on the
owner's Allplan 2026-1-7 setup. This verifies the 0.2.1 correction and file-state
tests, not complete M1.1 or milestone M1 acceptance. The owner explicitly confirms
project names match the UI and the visible model is unchanged.

## Exact tested artifact and environment

Archive: `allplan-mcp-0.2.1-windows-evaluation.zip`.
SHA-256: `26ca92690be0365eca3d580b947c52b443e536cc8ee10d8b1ca7b1de594bc6e8`.
The existing archive is unchanged; this result and evidence were recorded later.

All three reports show external server and installed bridge **0.2.1**, verified
installed bridge integrity, MCP discovery of six tools and successful context
calls. Allplan API release **2026.1**, executable file version
**16.1617.8659.814**, product version **2026.0.1.0**, embedded CPython **3.13.13**,
external Python **3.14.8**, Windows. UI build 2026-1-7 was previously supplied by
the owner; it is not inferred from executable metadata. Codex/Windows application
versions are still unspecified.

## Observations

| Evidence | Project | Foreground / loaded files | Result |
| --- | --- | --- | --- |
| [132549](evidence/diagnostics-20261007T132549Z.json), captured 13:25:45 UTC | `Nowy projekt 1` | 1 foreground; 2 passive background | Name and key observed. Sample includes passive column on signed file -2 and active column on file 1. |
| [132700](evidence/diagnostics-20261007T132700Z.json), captured 13:26:57 UTC | `Nowy projekt 1` | Only 1 foreground | File 2 absent from inventory and sample; same project key and active-column model/view UUIDs. Unload exclusion PASS. |
| [132822](evidence/diagnostics-20261007T132822Z.json), captured 13:28:19 UTC | `test` | 21 foreground; 1 active background | Project name/host/path fingerprint differs; new context contains grid/slab/wall adapters. Project switch PASS. |

All captures have different host session IDs. `document_id=0` in all three is
not a project identity. Each sample has valid, separately reported model/view
UUIDs; returned items are bounded raw adapters, not deduplicated component counts.

The 0.2.0 project lookup failure is now explained by runtime evidence. In all
three reports `GetProjectPath(project_name, host_name)` returns **error -1 and an
empty path**. The alternate **host_name, project_name** order returns **error 0
and a nonempty path**. The implemented fallback successfully resolves the key.
This is evidence for the tested Allplan build despite the published signature.
The name/host/path-derived key remains explicitly non-durable; project copying,
renaming and moving have no accepted identity semantics yet.

Owner statement: **“Nazwy projektu sie zgadzaja, model bez zmiany”** — project
names match and model unchanged. This supplies the requested UI check; the JSON
alone would not prove visible-model preservation.

## Remaining scope and next work

Input length/angle enum reads are **3 / 1** and offsets **[0, 0, 0]**. No explicit
UI unit/offset comparison was supplied. Geometry normalization, nonzero offset
units/application, available levels, write eligibility, full model coverage and
durable element/project references remain unverified. `runtime_verified=false`
and `allplan_acceptance=not_run` in diagnostics are static fields, not an
acceptance registry for this batch.

No additional repeat of this correction batch is required. Next implementation:
complete explicit scope/identity contracts and deliver M1.2 read-only type/layer/
attribute queries, followed by M1.3 paging/staleness and M1.4 demo profile binding.
The profile remains unbound/inactive. Full UAT-02/UAT-03 and M1 exit gate remain
pending. Portable checks for this artifact: **31 tests PASS**, previously run;
this evidence-only documentation update does not rerun or change the code.

## Source integrity

Original uploads retained byte-for-byte under `evidence/` (native strings are
preserved as data):

```text
132549: b793bbcada5d540eb5b12ffbd777dadd2f33418c6e6abeb8599c2cd045db28c6
132700: acf137c1655c3ce13d6ac620ac88745ed14c34231b6d8ac865080d31aa68575f
132822: b1db2cc225066c307862de810005985d66ba0031f00a11c9a71712f3745be90b
```
