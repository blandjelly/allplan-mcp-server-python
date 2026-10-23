# 0.30.0 candidate record

Status: **142 unique focused checks passed; full CI and exact fallback ZIP
verification passed; native Allplan trial not run.** This record covers source commit
[`9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6`](https://github.com/blandjelly/allplan-mcp-server-python/commit/9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6).

- Version: `0.30.0`
- Branch: `feat/m4-combined-evidence-0.30.0`
- Pull request: [#28 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/28)
- Focused verification: **142 unique affected/dependent checks passed** ([record](focused-verification.json)).
- Full CI: [run 39993048110](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39993048110) passed 622 tests on Windows and 622 on Ubuntu, Python 3.12, plus the package job. Job IDs: Windows 120549507669, Ubuntu 120549507705, package 120553695686.
- CI artifact 12518373563 was not delivered: the connector returned a file-service reference and the single normal-proxy transfer failed with `URLError` before an HTTP response. Per policy, one fallback build was made from a clean detached worktree at the exact source (`source_modified=false`).
- Verified fallback ZIP: [Windows evaluation ZIP](allplan-mcp-0.30.0-windows-evaluation.zip) · [SHA-256](allplan-mcp-0.30.0-windows-evaluation.zip.sha256) · `78b7b24c98749ebbd28814f84d70a2fc9cbeab80b477b9fd1585e5c10e63af8e`.
- Exact ZIP verification passed on the first attempt: 196 payload files, 43 bridge hashes, checksum/payload integrity, exact registration, frozen sync/import, `drawing_identity` and `attribute_evidence` schema validation, native source safety limits, upgrade from and restore to 0.29.0, and preservation of active/archive journal, trace and log markers. See [verification result](package-verification.json), [verification log](package-verification.log), [artifact hashes](artifact-hashes.json), [build provenance](build.log), and [verification script](verify_package.py).
- Native Allplan: not run. See the [single-session 0.30.0 trial plan](../../docs/m4-single-drawing-0.30.0.pl.md).
- CI/build provenance: [source-ci.json](source-ci.json) · [fallback build log](build.log).

## Candidate scope

This candidate prepares one session across priorities 1–5. It adds a bounded,
read-only `model_property_probe phase=attribute_evidence` for one exact
foreground drawing/model/view and 1–16 requested attribute IDs, with separate
ancestry, children, stored/computable reads, native representation and runtime
type evidence. `evidence_complete` requires wrapper consensus and complete
requested observations; partial evidence retains data with `state=not_checked`.
SDK member matches do not establish field ownership or setter payload.

Complete no-op preview and revalidation return bounded fresh `no_op_evidence`
and `setter_calls_started=0`; no-op plans have no Apply path. The combined
trial covers journal inspection/archive/restart/replay using an existing
resolved execution ID without invoking setters, exact Slab/MultiSlab evidence,
W1 no-op, native-selection unsupported versus separate highlight behavior,
eligible guarded Wall material Apply, and available scalar/Enum writes on new
safe family/type fixtures. It does not repeat the accepted 0.29.0 Column
grouped delete/Undo.

## Remaining blockers

Full completion of priorities 1–5 remains the goal. The candidate does not add
the missing Slab/MultiSlab field-owner contract, date/vector setter payload and
typed readback, or native selection set/clear/readback. These remain blocked
until their contracts and native evidence exist. Missing safe fixture
definitions must be reported as `fixture_missing`; do not treat diagnostics or
an SDK type match as a pass.

The 0.30.0 owner trial has not been run. The 142 focused checks, full CI,
exact ZIP verification and native Allplan remain separate results.
See the
[current handoff](../../docs/next-model-handoff.md),
[API evidence and limits](../../docs/m4-editing-api-0.30.0.md), and
[coverage matrix](../../docs/m4-single-drawing-coverage-0.24.0.md).
