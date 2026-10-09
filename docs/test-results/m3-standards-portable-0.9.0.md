# M3.3 portable validation — 0.9.0

Status **ready_for_owner_test**, native new-workflow preview **not_run**.
**155 tests PASS** on Linux CPython 3.12.14, FastMCP 3.2.4, uv 0.12.19.
Frozen synchronization and wheel/sdist build pass; deterministic Windows ZIP,
integrity and recursive registration are covered by the portable package suite.
Loopback network permission is used for the real HTTP/MCP tests.

Six new tests cover:

- Fresh selection and findings from exactly one complete native scan; explicit
  model-UUID exceptions and source conflicts caused by excluded-element edits.
- Unknown predicate values under negation; unknowns block readiness rather
  than silently matching. Unavailable fields/malformed exceptions reject before
  native document lookup; absent valid UUID exceptions reject without a plan.
- Immutable hashed workflow metadata and native executor refusal of a standard
  plan even when its two changes match the accepted evaluation fixture.
- Real MCP/HTTP standard/rule tool discovery, typed preview-only actions,
  selection with negation, revalidation, and generic Apply refusal for a selected
  plan before setters.
- The full owner CLI on real transport with a repaired fake fixture: three
  previews/revalidations, one exception, zero-selection boundary, identical
  full before/after audits and no setters/Apply/Recover calls.

Existing two-target native-fake execution, source/TTL checks, persisted replay,
lost replies, disk failure, corruption and recovery regressions remain passing.
No new native write API, dependency or broad write authorization is introduced.
uv.lock changes only the local package version from 0.8.1 to 0.9.0.

[Contract](../m3-standards-contract.md) and
[read-only owner card](../m3-standards-preview-batch.md) define the next native
boundary. Accepted 0.8.1 [stale Apply rejection](m3-stale-apply-acceptance-0.8.1.md)
and its three original logs are preserved separately. Portable validation is
not native new-tool acceptance; M3/UAT-05/UAT-06 remain open.

Exact clean-source artifact identity and any GitHub CI results are recorded in
the 0.9.0 delivery manifest/README after publication. CI-generated archives do
not replace the exact owner-delivery ZIP. No test result for a later commit is
inferred from an earlier CI run.

[CI run 38002888441](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38002888441)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
clean source **61c7579645d497a9df1e3ff0cb5640861225b56c**. Exact artifacts are
[delivered under 0.9.0](../../evaluation-packages/0.9.0/README.md), publication
commit **65ac8ef032d36226b7af3d294e51a664f722fd5d**. Later artifact/documentation
commits have separate CI state; the delivered ZIP is not rebuilt.
