# Next-model handoff

## Current handoff — 2026-10-09, package 0.6.1

## Checkout for the next chat

Continue from GitHub branch **`codex/m2-audit-accepted`** in
`blandjelly/allplan-mcp-server-python`. This branch contains the complete M2
implementation, 0.6.1 callback correction, original UAT/crash evidence and bounded
UAT-04 acceptance. In a fresh checkout:

```sh
git fetch origin
git switch --track origin/codex/m2-audit-accepted
```

Read this handoff and [M2 acceptance](test-results/m2-acceptance-0.6.1.md) before
continuing. The older `feature/m2-audit-foundations` branch is a separate early
schema draft, not the accepted M2 implementation. The exact delivered Windows
archives remain outside Git under ignored `dist/`; the owner retains the tested
0.6.1 ZIP. Do not replace it with a rebuild using the same version. Future runtime
changes require a new package version. The full 121-test suite passed again
before this GitHub handoff commit.

## Accepted implementation state

**M0 and M1 are closed; UAT-00–UAT-03 PASS within the recorded scope** on
Allplan 2026-1-7 / local Windows Codex. M1 is merged through
[PR #1](https://github.com/blandjelly/allplan-mcp-server-python/pull/1): local
baseline and freshly checked origin/main both point to `bc5137339f3a6fa2049b322d7c726e659b523279`.

**M2.1–M2.3 are closed; UAT-04 PASS within the retained read-only fixture scope
on package 0.6.1.** [Native evidence and limits](test-results/m2-acceptance-0.6.1.md).
Package 0.6.1 exposes `model_audit` through `/model-audit`, versioned typed
rules/string missing policies, fresh full snapshot evaluation, severity/raw
findings, coverage and readable reports. File/mark/model-local box/center and
session/project/document/model refs locate findings without native highlighting.
References remain nondurable read evidence and cannot authorize writes.

Read [architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [M1 reads](tool-reference.md),
[M2 contract](m2-audit-contract.md) and
[portable evidence](test-results/m2-audit-portable-0.6.0.md).
The M1 read profile remains schema m1-profile-1 / revision **1.0.2** unchanged;
the separate audit profile is schema m2-profile-1 / revision **2.0.0**. Both bind
resources freshly and remain inactive for writes.

The [native 0.6.0 capture](test-results/m2-audit-runtime-0.6.0.md) reports
six columns, five findings on five targets, one duplicate group, complete coverage
and zero unchecked checks. The owner confirms UI correspondence and unchanged model.
The [uploaded crash evidence and correction](test-results/m2-dispatch-fix-0.6.1.md)
confirm a managed-exception crash at 12:50:12.737 Europe/Warsaw during a second
request for [101,102]/include_passive=true, ID `101efe01-58e9-4296-aa93-e1a2c18b60b4`.
That scope exceeds the demo profile's file-101 contract and should be rejected.
No incident dump/managed stack/faulting module is available; causation is unproven.

**0.6.1 contains a concrete dispatcher error-boundary fix:** callbacks return
primitive result/error data, while HTTP workers raise errors after dispatch.
Public and host preflight reject invalid audit scope before native reads;
a bounded persistent bridge log retains request outcomes/exception traces.
The original 0.6.0 artifact and evidence are preserved. Full local suite:
**121 tests PASS**, including former callback escape, typed/generic errors,
exact incident scope, logs and stop-on-failure diagnostic checks.

The [0.6.1 targeted owner gate](m2-stability-batch.md) is completed: both full
101-only audits, public/direct-host rejection of [101,102] and post-error health
pass in the same host session. All 18 installed bridge hashes match the tested
archive; the loaded boundary marker is present. The reports are identical apart
from request IDs, and all per-element source hashes/raw evidence/locators match
the earlier UI-confirmed capture. The owner now confirms Allplan and host remain
running; the earlier unchanged-model/UI confirmation is not reattributed to this
later statement. Static report acceptance flags remain unchanged.

**No further M2 owner batch is required within this scope.** Preserve the tested
0.6.1 archive. M3 is planned and unimplemented; do not infer authorization for
repairs or native writes from M2 acceptance. Native longer-term stability,
concurrent multi-chat requests and persistent log behavior remain unverified.
The cloud workspace cannot execute Windows/Allplan tests.

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
| `allplan-mcp-0.6.0-windows-evaluation.zip` (native report verified; crash unresolved) | `6fc6e37fa4abd09ffec5b7a72d2b34a3a67c49a1ad2eef4cd480426428be2dd7` |
| `allplan-mcp-0.6.1-windows-evaluation.zip` (bounded UAT-04 PASS) | `b47cba9ab08cce800f9e1900d03a232153c4441d054818f1bc116e8cc4a617f7` |

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

M2 work requested by the owner is complete; no further owner test is pending
within the recorded scope. The next implementation stage is M3 when requested.
Crash timing and second request arguments are established. A concrete UI
callback exception defect is fixed and the native controlled error/recovery gate
passes; its role in the actual CLR crash remains a hypothesis without the incident
stack. UAT-04 is closed for the retained fixture, not for arbitrary native faults.

The demo preserves C03's literal `<niezdefiniowany>` in raw evidence while its
explicit QA policy classifies that literal, absence, null and empty/whitespace
strings as missing. Unknown reads/types and passive API absence remain
not_checked. The tested six-column audit has five findings and one duplicate
group. A zero result cannot bypass incomplete coverage. Missing bindings reject
the audit; remedies remain suggestions. M3 is unimplemented/unrun.

Current portable verification: **121 tests PASS** on Linux Python **3.12.14**,
including the real MCP/HTTP transport with a fake native host and JSON/TXT CLI
output. Frozen sync, wheel/sdist build and Windows archive/integrity checks pass.
This is separate from native acceptance and from the earlier 95-test CI result.
No remote current M2 CI run is claimed. The 0.6.0 native report, crash collection
and successful 0.6.1 native gate have separate original evidence. The latest
JSON/TXT are preserved byte-for-byte; their hashes are in the acceptance record.
Persistent bridge.log was not supplied and its native rotation/traceback behavior
is not included in this acceptance.


Baseline box tools lack automatic readback and durable write deduplication.
Queued cancellation has portable simulated-dispatch evidence; closing the listener
does not undo an already running write. Static diagnostics flags
`runtime_verified=false` / `allplan_acceptance=not_run` are not a live acceptance
registry. Native M2 audit is accepted only for the recorded fixture/profile;
all repair tools and Claude/cloud-to-Windows integration remain unaccepted.
Neither inspected repository has a license; public redistribution remains
unresolved and no release publication is recorded.

Keep Allplan APIs inside the host, use typed workflows and shared preview/apply,
and report missing data as `not_checked`. Verify per-type/property writes and
readback on Allplan 2026. The model owns code, checks and ready-to-use test packages;
the owner observes the UI. Record accepted task IDs, evidence, remaining scope
and the next action here after each completed slice.
