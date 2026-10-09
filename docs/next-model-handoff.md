# Current project handoff

Updated 2026-10-09 (Europe/Warsaw). **`main` contains accepted M0–M2**, package
**0.6.1**, M1 read profile **1.0.2** and M2 audit profile **2.0.0**.
M2 was merged through [PR #3](https://github.com/blandjelly/allplan-mcp-server-python/pull/3)
at `73b704fd3054b29c4e7c741a7891b8cc53e1b7cd`.

## Checkout and reading order

```sh
git fetch origin
git switch main
git pull --ff-only origin main
```

Read [architecture](architecture.md), [features](features.md),
[implementation stages](implementation-plan.md), [M1 read contracts](tool-reference.md)
and [M2 audit contract](m2-audit-contract.md). Installation is documented in
[Windows setup](windows-setup.md); [fixture setup](fixture-guide.md) and
[diagnostic commands](diagnostics.md) are reusable references.

## Accepted baseline

| Stage | Accepted scope on Allplan 2026-1-7 / local Windows Codex |
| --- | --- |
| M0 / UAT-00–UAT-01 | Package 0.1.2: install/update/restore, health/version/names/box, ESC/restart, minimize/restore and project switching. |
| M1 / UAT-02–UAT-03 | Package 0.5.3: explicit scope, six supported native root families, selections/pages/summaries, resource binding, canonical geometry, display-unit invariance and nonzero XY offset. [Evidence and limits](test-results/m1-acceptance-0.5.3.md). |
| M2 / UAT-04 | Package 0.6.1: retained six-column read-only fixture, five locatable findings, complete coverage, repeated audits and controlled error/recovery. [Evidence and limits](test-results/m2-acceptance-0.6.1.md). |

Native API release is 2026.1; executable file/product resources are
16.1617.8659.814 / 2026.0.1.0. Embedded CPython is 3.13.13; the recorded Windows
external Python is 3.14.8. These observations do not map a hotfix by themselves.
Static runtime_verified/allplan_acceptance fields are not a live acceptance registry.
No further M1/M2 owner batch is pending for the accepted fixture/build.

## Work outside main

[Draft PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2),
branch `codex/m3-repair-preview`, contains the **0.7.0 read-only M3 preview**
and its delivered owner-test package. Its reported 134 portable tests are
separate from main's 121-test suite. Native owner verification is pending;
apply/readback/Undo remain unavailable. Continue that PR for M3 work; do not
restart its implementation from main or treat the preview as accepted repairs.

`feature/m2-audit-foundations` was an independent early schema draft and has
been deleted. The accepted implementation uses `m2-profile-1`, not that draft's
`audit-profile-1`. `codex/m2-audit-accepted` is retained as PR #2's base.

## Delivery and remaining limits

Keep the owner-retained tested 0.6.1 ZIP unchanged. Its SHA-256 is
`b47cba9ab08cce800f9e1900d03a232153c4441d054818f1bc116e8cc4a617f7`.
Main does not contain this delivered ZIP; rebuilding source is not a replacement
for that artifact. Use a new version for future runtime changes.
[Validation and history](validation-and-history.md) records CI, artifact hashes
and immutable links to removed logs and superseded reports.

The 0.6.1 dispatcher contains Python callback exceptions and rejects invalid
audit scope before native reads. Its controlled native recovery gate passed;
the precise cause of the earlier CLR crash remains unproven without its stack.
[Correction and limits](test-results/m2-dispatch-fix-0.6.1.md).

Long-term/concurrent native stability, native log rotation/traceback persistence,
nonzero Z offsets, arbitrary component trees, native highlighting, durable
references, writable properties/Undo and cloud-to-Windows access remain outside
acceptance. The read demo is bound_for_read and inactive for writes. M0 box
commands lack automatic readback and durable write deduplication; reconcile a
lost write response before retrying. The cloud workspace cannot run Allplan.

Keep Allplan APIs inside the host, use typed workflows, preserve raw values and
report unavailable data as not_checked. Record scope, evidence and the next
action here after each completed stage. The fork and upstream have no recorded
license; no release publication is recorded.
