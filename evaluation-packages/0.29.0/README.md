# 0.29.0 candidate record

Status: **full CI and exact fallback ZIP verification passed; native Allplan
trial not run.** This record covers source commit
`df050afc71b9e0c2303594d6acbd3da463df3e89`.

- Version: `0.29.0`
- Branch: `fix/m4-batch-undo-0.29.0`
- Pull request: [#27 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/27)
- Focused verification: **99 unique affected/dependent checks passed** ([record](focused-verification.json)).
- Full CI: [run 39971389774](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39971389774) passed 607 tests on each Windows and Ubuntu Python 3.12 job, plus the package job. Configuration-only run 39971367200 also passed. Job IDs: Windows 120474777242, Ubuntu 120474777333, package 120480104149; configuration job 120474694358.
- Verified package: [Windows evaluation ZIP](allplan-mcp-0.29.0-windows-evaluation.zip) · [SHA-256](allplan-mcp-0.29.0-windows-evaluation.zip.sha256)

## Candidate scope

For a delete-only plan, one reviewed change template expands over the complete
exact target set and calls `DeleteElements` once with all bound root adapters.
The execution journals unknown outcomes for all targets before the native call,
applies final guards to the batch, and records fresh per-target and descendant
results. After a returned native call, complete readback that confirms absence
records the target as applied, complete readback that confirms its presence
records it as failed, and partial or unreadable subtree evidence records it as
unknown. An exception from batch submission leaves all targets unknown.
Unknown outcomes are recovered under the same execution ID without repeating
deletion. These safeguards do not establish UI Undo grouping.

## Focused verification

The candidate passed 99 unique focused unit and HTTP checks. Coverage includes
one native batch call, pre-call unknown journaling for all roots, final guard
drift, legacy adapter rejection, partial native failure, interruption and
recovery without a repeated setter. See [focused-verification.json](focused-verification.json).

## CI and exact package verification

The CI connector returned artifact 12510270932 with digest
`3d509667620fb3a23fc7a1daf0c9303f68e2ede98cccac1c4ee08d7b00e615da`, but the
file-service reference could not be transferred: the single normal-proxy
attempt failed with `URLError` before an HTTP response. Following the testing
policy, one fallback build was made from a clean detached checkout at the exact
source (`source_modified=false`). The exact ZIP passed verification on its
first and only attempt. It has 191 payload files and SHA-256
`0e4211b7a28f69a0b0400c13e2a90efeca9c230d34e42599adc6e8a2932d5aa5`.
Checksum and payload integrity, exact registration, frozen sync/import,
`drawing_identity` schema, native source safety limits, upgrade from and restore
to 0.28.0, 42 bridge hashes, and active/archive journal, trace and log markers
passed. See [CI record](source-ci.json), [artifact hashes](artifact-hashes.json),
[build provenance](build.log), [package result](package-verification.json) and
[verification log](package-verification.log).

## Native owner trial

Native Allplan 0.29.0 is **not run**. The 0.28.0 owner report is historical and
limited: one Undo restored only one of three deleted Columns, and further Undo
was unavailable. The new [0.29.0 trial](../../docs/m4-single-drawing-0.29.0.pl.md)
requires one plural delete call, fresh absence reads for each target and
descendant, then one UI Undo restoring all three roots and descendants.

Priority 1's bounded journal cleanup scope remains accepted. Priorities 2–5
remain partial, as recorded in the [current handoff](../../docs/next-model-handoff.md)
and [coverage matrix](../../docs/m4-single-drawing-coverage-0.24.0.md).
