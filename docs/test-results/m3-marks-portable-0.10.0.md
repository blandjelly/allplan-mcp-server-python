# M3 explicit mark preview — portable validation 0.10.0

Status **ready_for_owner_test**, native mark proposal/collision gate **not_run**.
**165 tests PASS** on Linux CPython 3.12.14, FastMCP 3.2.4, uv 0.12.19.
Frozen synchronization and wheel/sdist build pass. Dependencies unchanged;
uv.lock updates only the local package version. Real MCP/HTTP tests run with
loopback network permission.

Ten new meaningful tests verify:

- Two exact-target missing/duplicate proposals from one fresh full scan; raw old
  values and mark resource binding, unchanged revalidation, immutable caller copies.
- Distinct per-element assignments under the same unique-mark rule.
- Collisions against excluded peers and between proposed values; audit-policy
  trim/case normalization, remaining unmodified duplicate/missing counts.
- Public and direct-host malformed/blank/missing/control-character/UUID/duplicate
  assignment rejection before native context. Required/unique rules must both
  participate. Stale, compliant and wrong-rule targets store no plan.
- Unknown excluded peers prevent validated readiness; excluded-peer edits still
  invalidate exact-ID/hash revalidation over the full audited source.
- A request containing mark metadata cannot use native Apply even if filtering
  leaves only the previously accepted two layer/status proposals. No setters or
  mutation journal writes occur.
- Real MCP/HTTP rule_based_edit mark inputs and generic Apply refusal, plus the
  full M3 Marks Preview.cmd collector: two proposals, one exception, expected
  collision, three revalidations, identical complete audits and health, original
  MCP text retention. Wrong fixture stops before any proposal request.

All earlier read, preview, standards, persistence/replay, lost-reply, native-fake
execution and crash/disk regressions remain passing. Package tests include the
new root launcher, deterministic build, integrity and recursive registration.
This portable result does not establish native mark proposals or writes.
[Contract](../m3-marks-contract.md), [next owner card](../m3-marks-preview-batch.md).
The independently verified [0.9.0 owner gate PASS](m3-standards-acceptance-0.9.0.md)
has separate original JSON/TXT evidence; no repeat is requested.

Exact clean-source artifact hashes and later CI results belong to the
[0.10.0 delivery](../../evaluation-packages/0.10.0/README.md).
Never infer results for this commit from a prior version's CI; no old archive is
rebuilt. M3/UAT-05/UAT-06 remain open; mark/selected writes, automatic numbering,
labels, wider scopes and native unknown-outcome/crash recovery remain deferred.

[CI run 38049405544](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38049405544)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
clean source **ebf2c752440a0f72b538527f35175668322395a4**. Exact artifact publication is
commit **44776b7123f384802dec4d293e542f4de9236c17**; later artifact/documentation CI
is separate. This exact delivered ZIP is unchanged.
