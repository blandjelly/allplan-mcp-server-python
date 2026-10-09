# M3 preview acceptance — 0.7.0, bounded read-only gate PASS

Date **2026-10-09**. Capture began **15:01:19 Europe/Warsaw**
(13:01:19 UTC); filenames use 13:01:24 UTC. **The first read-only M3.1/M3.2
preview gate passes for the retained fixture.** This does not close M3 or
UAT-05/UAT-06. Native apply, readback and Undo remain unimplemented/unrun.

## Original evidence and tested package

Uploads are preserved byte-for-byte, including TXT line endings:

- [JSON](evidence/diagnostics-20261009T130124Z.json): **194077 bytes**, SHA-256
  `956ee86767ffdec23819cd686d25c48073458361d0c96b1955b226b8ae4f36b0`.
- [TXT](evidence/diagnostics-20261009T130124Z.txt): **545 bytes**, SHA-256
  `7d56cbe242ebee3e3c007a3d8d4fb9d1e4fae4871c82a35dd045e78bcc97fb28`.
- [Tested Windows ZIP](../../evaluation-packages/0.7.0/README.md): **382353 bytes**,
  SHA-256 `e47a103b8a280bf786877f22bab8faf8bfd183f4de9531d8918305bd87cf56c6`.
  Its clean source commit is `22f18db27faf5e0873de18c1e079d1217da736fb`.

Host and external MCP report **0.7.0**. All **20 installed bridge file hashes**
independently match the tested ZIP and its manifest; installed integrity is
`verified`, with no mismatches. The loaded boundary marker remains
`contained_result_error_v1`. This evidence/documentation update does not rebuild
or replace the tested archive.

Native API release **2026.1**, executable file/product resource versions
**16.1617.8659.814 / 2026.0.1.0**, embedded CPython **3.13.13**, external Python
**3.14.8**. Allplan UI build **2026-1-7** is the previously owner-identified
fixture environment; this log does not independently read the UI hotfix.
Read/audit profiles remain **1.0.2 / 2.0.0**.

## Observed read-only sequence

`m3_preview.checks_complete=true`; all five steps report OK:

| Step | Observed result |
| --- | --- |
| host_boundary_preflight | Matching host/MCP version, verified installation, loaded boundary and discovered tool |
| preview | Exactly 2 proposals, 3 excluded mark findings, complete audit coverage |
| revalidate | `unchanged`, same source/report fingerprints and plan ID/hash; 299 seconds remain |
| audit_after_preview | Same complete audited source/report; still 5 findings on 5 of 6 columns |
| host_health_after_preview | Same host session responds after the batch |

Host session: `e088efb4-0747-4de4-811e-3f75f54c43bb`.
Query session: `ab03affd2b184fbfb8a140d6e7d4bccd`.
Plan: `af6d9e4c16704c3a90c8925eefbc9b98`.
Plan hash: `dce2f1115124cc417784a070802f2c3a9373a76272e6f216bde804188d46a1d2`.

| Request | ID |
| --- | --- |
| Initial host health | `1aa764ac-cff1-48f5-830a-6b3f02313c88` |
| Preview | `f92d66a5-40bd-4e1e-8e26-c046f95b65a7` |
| Revalidate | `ec530234-8391-40c3-b354-a66cc0efa2a8` |
| Follow-up audit | `31aa582a-2b69-4772-8b24-c38e0401ab81` |
| Final host health | `c1956b9a-6fb6-478b-8e48-284ee637e0f5` |

Requested scope is only active foreground file **101**, `include_passive=false`.
The exact proposals are:

| Target | Model UUID | Model-local center (mm) | Old → proposed value |
| --- | --- | --- | --- |
| C05 / S05, QA-003 | `51db6258-4f95-4fab-ac80-8948e13bfd21` | 6000, 6000, 1500 | Layer 3701 / SZ_OGÓ02 → 3700 / SZ_OGÓ01 |
| C06 / S06, QA-004 | `d26a3d87-2981-4657-b592-65c894ce41ba` | 12000, 6000, 1500 | Attribute 5002 / MCP_QA_STATUS: NWE → NEW |

QA-001 C03 and QA-002 C02/C04 are excluded with `rule_not_selected`.
No mark is assigned. Audit has **24 checks: 18 pass, 5 fail,
1 not_applicable, 0 not_checked**, one duplicate group, three errors and two
warnings. Requested-scope, returned-field and rule-input coverage are complete;
whole-project coverage remains false. `fail` is expected for this intentionally
unrepaired fixture.

All three source reads match fingerprint
`52d0849293b2c8645d392b1484f197cbf09947f55a70738b603715f1464f3f1e`.
Audit report fingerprint recomputes to
`9fdbd2b408a809adced51a3efaf62fc074251fbf76cff271199076123527447a`.
The plan hash independently recomputes from the returned plan and exact expanded
request after removing transport IDs. JSON's duplicate response objects agree;
TXT exactly matches plan text and step outcomes after line-ending normalization.

Both `ElementsAttributeService.ChangeAttributes` and
`ElementsLayerService.ChangeLayer` are present/callable, with native docstrings
matching the prepared API paths. They were inspected, not invoked. All preview
and revalidation responses retain `read_only=true`, `apply_available=false` and
`usable_for_write=false`.

## Owner observations, acceptance and limits

The owner supplied both logs and stated **“logi, allplan i host dzialaja,
wskazania i wartosci zgadzaja sie”**. This confirms continued Allplan/host
operation and UI correspondence of the proposed targets/values. The owner did
not separately state “model bez zmian” in this message. The recorded unchanged
revalidation and identical subsequent audit establish unchanged **audited
source fields** during the sequence; they do not establish every property of
the whole model or a separately attributed whole-model UI observation.

Decision: **PASS for this bounded read-only preview/unchanged-evidence/target-UI
gate on the retained fixture.** No repeated preview batch is requested.
The optional manual-edit conflict test was not supplied and remains native
unverified; expiry/eviction/restart/conflicts retain portable evidence only.
Symbol presence proves neither target writability nor successful native writes,
readback, Undo, durable deduplication or unknown-outcome recovery. Concurrency,
longer-term stability and other profiles/files are outside this capture.
Static `runtime_verified=false` / `allplan_acceptance=not_run` values in the
original evidence are unchanged; this document records the bounded decision.

Portable evidence is separate: **134 local tests PASS** and
[GitHub CI run 37929065543](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37929065543)
**PASS** for published commit `433a83bd40c10629129ca3d1984e7ebbbcb6cc56`.
All six Windows/Ubuntu Python **3.11–3.13** jobs pass the test, wheel/sdist and
Windows ZIP build steps. Those CI-generated archives do not replace the native
tested ZIP identified above. No CI result for a later documentation commit is
claimed here.

Next implementation stage: bounded native layer/status apply with fresh
re-resolution/writability checks, reviewed plan authorization, serialized writes,
per-target readback, explicit partial/unknown outcomes, retry recovery and tested
Undo limits. It needs a new package version and a separate disposable-copy
owner gate before any write capability is accepted.
