# Next-model handoff

## Latest runtime handoff — 2026-10-07, package 0.2.1

**M0 is closed. The bounded M1.1 context/identity batch passed. Full M1 remains in
progress.** This is the latest handoff after the M1 probe, not full M1 acceptance.
No implementation/runtime acceptance changed during the 2026-10-09 documentation
cleanup. Historical setup tasks and duplicate reports have been removed; current
implementation facts and the latest original diagnostics remain here.

Read [architecture](architecture.md), [features](features.md) and
[stages](implementation-plan.md), then inspect the current working tree and code.
The demo [profile](../profiles/examples/native-model-qa.demo.json) remains
**unbound and inactive**; the server does not consume it.

## Verified baseline

- Fork: `blandjelly/allplan-mcp-server-python`; upstream: `AlejoDuarte23/allplan-mcp-server-python`.
- M0.1–M0.5 accepted with **UAT-00/UAT-01 PASS** on Allplan UI build **2026-1-7**,
  local Windows Codex, package **0.1.2**. Owner confirmed installation, box count/
  dimensions, ESC/restart, minimize/restore, project switching and cleanup.
- Observed API release **2026.1**, executable file/product versions
  **16.1617.8659.814 / 2026.0.1.0**, embedded CPython **3.13.13**, external Python
  **3.14.8**. UI hotfix is owner-reported; executable metadata is not a hotfix mapping.
  Windows/Codex app versions remain unspecified.
- Last recorded portable validation: **31 tests PASS**, Linux Python **3.12.14**,
  FastMCP **3.2.4**, uv **0.12.19**. This is separate from Allplan runtime acceptance.
  GitHub Actions matrix execution is not claimed.

Keep the tested archives unchanged; do not overwrite them with rebuilt packages.
Use a new package version for further runtime changes. Their recorded hashes are:

| Tested archive | SHA-256 |
| --- | --- |
| `allplan-mcp-0.1.2-windows-evaluation.zip` | `d97b6761b13f8cd6e80c7954f1c91de513d4a813a5b236c6917b14b0882ac528` |
| `allplan-mcp-0.2.1-windows-evaluation.zip` | `26ca92690be0365eca3d580b947c52b443e536cc8ee10d8b1ca7b1de594bc6e8` |

## Latest M1 runtime evidence

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
were read, but UI unit comparison and nonzero-offset normalization were not tested.

Original diagnostic SHA-256 values, retained byte-for-byte:

```text
132549: b793bbcada5d540eb5b12ffbd777dadd2f33418c6e6abeb8599c2cd045db28c6
132700: acf137c1655c3ce13d6ac620ac88745ed14c34231b6d8ac865080d31aa68575f
132822: b1db2cc225066c307862de810005985d66ba0031f00a11c9a71712f3745be90b
```

## Next work and unresolved limits

1. Finish **M1.1** explicit scope, unit/offset conversion and identity contracts.
   Project key is a non-durable name/host/path fingerprint; copy/rename/move
   semantics, levels, file write eligibility and full component coverage are unresolved.
2. Implement **M1.2** read-only type/layer/attribute queries, then **M1.3** paging,
   reusable selections, deduplication and stale-state checks. Adapter samples are
   not component counts, selections or write targets.
3. Complete **M1.4** metadata/profile binding and the exact UI fixture recipe.
   Full UAT-02/UAT-03 and the M1 exit gate remain pending. No repeat of the passed
   0.2.1 correction batch is needed without a relevant change or defect.
4. Continue **M2–M3** for the first search/audit/cleanup MVP.

Baseline box tools lack automatic readback and durable write deduplication.
Queued cancellation has portable simulated-dispatch evidence; closing the listener
does not undo an already running write. Static diagnostics flags
`runtime_verified=false` / `allplan_acceptance=not_run` are not a live acceptance
registry. No other workflow tools or Claude/cloud-to-Windows integration are accepted.
Neither inspected repository has a license; public redistribution remains
unresolved and no release publication is recorded.

Keep Allplan APIs inside the host, use typed workflows and shared preview/apply,
and report missing data as `not_checked`. Verify per-type/property writes and
readback on Allplan 2026. The model owns code, checks and ready-to-use test packages;
the owner observes the UI. Record accepted task IDs, evidence, remaining scope
and the next action here after each completed slice.
