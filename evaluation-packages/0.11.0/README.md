# Evaluation delivery — 0.11.0

Current status: **bounded native workflow-write gate PASS**, 2026-10-10.
[Original four uploads and acceptance](../../docs/test-results/m3-workflow-acceptance-0.11.0.md)
record all ten steps, standard/selected single-target writes/readbacks, exact-ID
read-only replay, complete audits 5 → 4 → 3 and same-session verified 0.11.0.
Owner confirms both changes, host survival, other elements unchanged and two-step
Undo. No repeat is requested. Original embedded docs/delivery manifest retain
pre-test flags; this documentation update rewrites no original capture/manifest
and rebuilds no archive.
This delivers the first implementation priority from the M3 completeness audit:
shared execution of 1–32 existing string-status/layer changes on native Column
roots in one validated foreground file, including standard/selection plans.
Plan/source hashes, exceptions, native preflight/readback, audited collateral
verification, durable execution IDs and read-only recovery remain required.
Mark plans still refuse Apply; numbering remains required open M3 work.

Download [allplan-mcp-0.11.0-windows-evaluation.zip](allplan-mcp-0.11.0-windows-evaluation.zip)
and see the [completed Polish procedure](../../docs/m3-workflow-apply-batch.md).
The following preserves the original test recipe; no repeat is requested.
Use the **original disposable six-column copy**, restore only S05's review
layer and S06's NWE status **before** starting the host, then run
**M3 Workflow Apply.cmd**. The two separate prompts are NAPRAW STANDARD and
NAPRAW REGULE. Each authorizes one displayed target, uses a distinct saved
execution ID and checks read-only exact-ID replay. Complete audits must go
5 → 4 → 3; ten steps and unchanged session/integrity plus owner UI observation
are required. Send original JSON/TXT. No repeat of the old two-target/Undo gate.

**M3 Workflow Recover.cmd** sends only Recover for the last saved workflow
execution, without Apply replay/resume/Undo. Preserve
Local/.allplan-mcp/repairs, original project copy and all package logs.
[Current contract and journal capacity/copy/restore limits](../../docs/m3-workflow-execution-contract.md).

Clean source **26d70b27bd06e2916cda74213cb8995aa9f0f19a**, source_modified=false.
ZIP **719947 bytes**, SHA-256:

```text
29fcfaed0a10108b630892da3710da3cdf05701c2d25a08a014ff4ab177ee031
```

[Delivery manifest](delivery-0.11.0.json) records exact ZIP/hash/wheel/sdist and
verification-log sizes/hashes. Two clean-source ZIP builds are byte-identical.
[Extracted-package verification](package-verification-0.11.0.json) checks
package integrity and all 22 registered bridge hashes; Setup and Restore
preserve a retained journal in the installation fixture. This is a portable
installation check, not native Allplan execution.

[178 local portable tests PASS](../../docs/test-results/m3-workflow-portable-0.11.0.md),
[original test log](portable-tests-0.11.0.txt), frozen sync and
[wheel/sdist build PASS](build-0.11.0.txt). New HTTP tests include two separate
workflow writes/replays, known rejection, wrong fixture/cancellation and a
lost reply followed by Recover only. Earlier native evidence/archives are
unchanged. **Source CI PASS 6/6:** [run 38063710029](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38063710029),
Windows/Ubuntu Python 3.11–3.13 tests, wheel/sdist and Windows ZIP builds for
source 26d70b27bd06e2916cda74213cb8995aa9f0f19a. [Job/step observation](source-ci-0.11.0.json).
Artifact publication commit daabd57f8ecbc24ba5dae62d0cb79fb04e6b30bb has separate
CI; subsequent documentation changes do not rebuild this exact archive.

Publishing this directory does not rebuild the source archive. Previous native
0.8.1 execution/Undo/recovery and 0.9.0/0.10.0 previews do not accept these
expanded writes. M3/UAT-05/UAT-06 remain open; actual mark writes/numbering,
native supported-lifecycle conflicts and partial/unknown recovery, final UAT and
main integration remain future work. No merge or release is performed.
