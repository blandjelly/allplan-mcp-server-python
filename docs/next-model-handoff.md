# Next-model handoff

## Current handoff — 2026-10-09, package 0.5.3

**M0 and M1 are closed; UAT-00–UAT-03 PASS within the recorded scope** on
Allplan 2026-1-7 / local Windows Codex. Completed M1 is on
`codex/m1-scope-model-query` in [PR #1](https://github.com/blandjelly/allplan-mcp-server-python/pull/1),
ready for review. Recheck PR/remote state before editing; use main only once it
contains M1. The main documentation cleanup is integrated into this branch.

Read [architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [read contracts](tool-reference.md)
and [M1 acceptance](test-results/m1-acceptance-0.5.3.md).
The packaged demo profile is schema m1-profile-1 / revision **1.0.2**. It binds
actual named resources freshly for reads and remains inactive for writes.

## Verified baseline

- Fork: `blandjelly/allplan-mcp-server-python`; upstream: `AlejoDuarte23/allplan-mcp-server-python`.
- M0.1–M0.5 accepted with **UAT-00/UAT-01 PASS** on Allplan UI build **2026-1-7**,
  local Windows Codex, package **0.1.2**. Owner confirmed installation, box count/
  dimensions, ESC/restart, minimize/restore, project switching and cleanup.
- Observed API release **2026.1**, executable file/product versions
  **16.1617.8659.814 / 2026.0.1.0**, embedded CPython **3.13.13**, external Python
  **3.14.8**. UI hotfix is owner-reported; executable metadata is not a hotfix mapping.
  Windows/Codex app versions remain unspecified.
- Portable pre-merge validation: **95 tests PASS** locally on Linux Python
  **3.12.14**; Windows/Ubuntu Python **3.11–3.13** matrix, wheel/sdist and Windows
  ZIP checks [PASS for 99abad8](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37859752410).
  This is separate from Allplan acceptance and does not replace checks for later
  commits. FastMCP **3.2.4** and uv **0.12.19** remain pinned.

Keep the tested archives unchanged; do not overwrite them with rebuilt packages.
Use a new package version for further runtime changes. Their recorded hashes are:

| Tested archive | SHA-256 |
| --- | --- |
| `allplan-mcp-0.1.2-windows-evaluation.zip` | `d97b6761b13f8cd6e80c7954f1c91de513d4a813a5b236c6917b14b0882ac528` |
| `allplan-mcp-0.2.1-windows-evaluation.zip` | `26ca92690be0365eca3d580b947c52b443e536cc8ee10d8b1ca7b1de594bc6e8` |
| `allplan-mcp-0.5.3-windows-evaluation.zip` | `15262b1f029d818e5fea871a0b669603d90a5b6ca68e80d5355457b8656ed104` |

The accepted 0.5.3 artifact uses clean source
`4f685766e1577cddb681ee3726bbabd3f2b3d743`; documentation/test-only integration
does not rebuild or replace that artifact.

## Accepted M1 reads

M1.1–M1.4 implement explicit file scope, typed predicates, bounded geometry/
hierarchy, metadata, full selections/pages/summaries and fresh profile binding.
The [acceptance record](test-results/m1-acceptance-0.5.3.md) preserves exact
scope and limits; the [completed fixture recipe](m1-final-batch.md) is reference,
not a request to reinstall or repeat captures.

Native A/B/C verify ten roots in 101 (six Column, two SkeletonBeam, Wall and
MultiSlab), one reference in passive 102, and unloaded 103 omission. Filters
column/S02/C01 return 6/2/1; six child representations are deduplicated. Resources
resolve MCP_QA_MARK / MCP_QA_STATUS and SZ_OGÓ01 / SZ_OGÓ02. B verifies passive
102 and C05/S05 on the review layer separately from display-unit invariance.
C adds (100000,200000,0) mm to every global box exactly once; model-local geometry,
dimensions and counts remain unchanged. Independent UI offset 100/200 m and C01
base-section center 100/200/0 m agree. Owner confirms unchanged A/B/C appearance
and retains the zero-offset baseline. Static runtime_verified flags remain
unchanged; acceptance applies only to the recorded build/fixture.

Changed-source staleness, TTL/eviction/restart and other predicate variants retain
portable evidence. The demo is bound_for_read and active_for_write=false.
Configured levels are not native BWS. Durable references, writable properties/
Undo, arbitrary native trees, nonzero Z offsets and exact solid intersections
remain outside acceptance.

## Earlier context evidence — 0.2.1

`get_model_context` is read-only: project, foreground/loaded file states, input
unit enums, raw offset and optional **0–20 raw adapter** model/view UUID samples.
The 0.2.1 correction resolves project lookup, including the tested alternate
`GetProjectPath(host_name, project_name)` order: error 0/nonempty path, where the
published name/host order returned -1/empty path on this build.

| Original diagnostic | Observed result |
| --- | --- |
| [132549](test-results/evidence/diagnostics-20261007T132549Z.json) | `Nowy projekt 1`: file 1 foreground, file 2 passive; active/passive model and view UUIDs read separately. |
| [132700](test-results/evidence/diagnostics-20261007T132700Z.json) | Same project: unloaded file 2 excluded from inventory/sample, file-1 UUIDs unchanged. |
| [132822](test-results/evidence/diagnostics-20261007T132822Z.json) | Switched to `test`: file 21 foreground, file 1 active background; changed project fingerprint. |

The owner confirmed **“Nazwy projektu sie zgadzaja, model bez zmiany”** (names
match, model unchanged). Each capture has a different host session ID;
`document_id=0` is not project identity. Unit enums **3/1** and offset **[0,0,0]**
were read without UI unit comparison/nonzero-offset tests in these early captures.
The accepted 0.5.3 captures supply that later separate evidence.

Original diagnostic SHA-256 values, retained byte-for-byte:

```text
132549: b793bbcada5d540eb5b12ffbd777dadd2f33418c6e6abeb8599c2cd045db28c6
132700: acf137c1655c3ce13d6ac620ac88745ed14c34231b6d8ac865080d31aa68575f
132822: b1db2cc225066c307862de810005985d66ba0031f00a11c9a71712f3745be90b
```

## Next work and unresolved limits

Next: **M2.1–M2.3 profile/audit contracts and read-only findings**, then only
UAT-04 once runnable. Retain C03's literal `<niezdefiniowany>` as native evidence
and explicitly define missing-value semantics. M2 audits and M3 repairs remain
unimplemented/unrun. Do not begin native repairs or repeat accepted M1 batches.

Baseline box tools lack automatic readback and durable write deduplication.
Queued cancellation has portable simulated-dispatch evidence; closing the listener
does not undo an already running write. Static diagnostics flags
`runtime_verified=false` / `allplan_acceptance=not_run` are not a live acceptance
registry. Audit/repair tools and Claude/cloud-to-Windows integration are not accepted.
Neither inspected repository has a license; public redistribution remains
unresolved and no release publication is recorded.

Keep Allplan APIs inside the host, use typed workflows and shared preview/apply,
and report missing data as `not_checked`. Verify per-type/property writes and
readback on Allplan 2026. The model owns code, checks and ready-to-use test packages;
the owner observes the UI. Record accepted task IDs, evidence, remaining scope
and the next action here after each completed slice.
