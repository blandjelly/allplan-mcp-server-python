# 0.28.0 candidate record

Status: **full CI and exact fallback ZIP verification passed; native Allplan
trial not run.** This is the verified candidate record for source commit
`b59ef15d9bfd4dfb42476b240e31b5b300268d2d`.

- Version: `0.28.0`
- Source commit: `b59ef15d9bfd4dfb42476b240e31b5b300268d2d`
- Branch: `fix/m4-owner-views-0.28.0`
- Pull request: [#26 targeting `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/26)
- Package: [Download verified Windows ZIP](allplan-mcp-0.28.0-windows-evaluation.zip) · [SHA-256 file](allplan-mcp-0.28.0-windows-evaluation.zip.sha256)

## Candidate scope

Component deletion now matches parent-child ownership by drawing, model UUID
and type across alternate view wrappers. It preserves the actual parent view
UUIDs in `child_parent_edges` and `descendant_parent_edges` bound to the
preview/revalidation evidence, while keeping the selected target's exact view
UUID bound to the reviewed plan. Slab/MultiSlab write blockers remain in place.

Journal capacity increases to 512 active execution records, with the 1 MiB
per-record bound retained. The active diagnostic trace limit is 8 MiB, trace
inspection is bounded at 32 MiB, and cleanup inventory is bounded at 1 GiB and
1024 files. Cleanup continues to preserve unresolved, corrupt, oversized or
otherwise unverifiable records.

## Focused verification

The candidate passed **170 unique affected/dependent focused checks**. The
breakdown is recorded in [focused-verification.json](focused-verification.json):

- 107 identity, delete and dependent unit/HTTP checks
  ([log](identity-focused.log));
- 54 journal, trace, probe and repair unit checks;
- 2 journal cleanup HTTP checks;
- 6 selected-mark HTTP checks;
- 1 version/lock check.

The first selected-mark HTTP run had six failures because installed editable
package metadata still reported 0.27.0 after the source version bump. All six
passed after frozen sync to 0.28.0. The health gate was not weakened. The
verification used the repository virtual environment because global Python
lacked FastMCP. HTTP loopback required network permission, and frozen sync used
`UV_CACHE_DIR=/tmp/allplan-uv-cache`. See the retained
[journal HTTP logs](journal-http-initial.log) and
[journal HTTP rerun log](journal-http-rerun.log).

The full local suite was not run under the repository testing policy. Full CI
[39871551499](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39871551499)
passed 601 tests on each Windows and Ubuntu Python 3.12 job plus the package
job. Original CI artifact ID `12466447229` (digest
`52f5a8533673c7347de2a9fe6d3e12f49a24ecc460585cf4acd8687f25922649`) was not
delivered: the connector file reference failed one normal-proxy URL transfer
with `URLError` before an HTTP status. Under the testing policy, one fallback
build was made from a clean detached worktree at the exact source
(`source_modified=false`). The exact ZIP passed verification on its first
attempt. It contains 186 payload files and has SHA-256
`74099ec341cdf8b2bc87def42487fafbbbcdb963ec6f4b8859a412f7b6d064ed`.
Checksum/payload, exact registration, frozen sync/import, `drawing_identity`
schema, source safety limits, upgrade from and restore to 0.27.0, 42 bridge
hashes, and active/archive journal, trace and log markers passed. See
[CI record](source-ci.json), [artifact hashes](artifact-hashes.json),
[build provenance](build.log), [exact ZIP result](package-verification.json)
and [verification log](package-verification.log).

Native Allplan 0.28.0 acceptance is **not run**. The next narrow native trial
covers only the exact W1 Column deletion targets, full descendant verification
and per-element Undo; see the [trial plan](../../docs/m4-single-drawing-0.28.0.pl.md).

Priorities 1–5 remain partially open: journal restart/replay evidence,
Slab/MultiSlab ownership, explicit W1 no-op/zero-setter evidence, native Column
delete/cascade/Undo, native selection/material acceptance and full family/value
coverage remain outstanding as recorded in the
[current handoff](../../docs/next-model-handoff.md).
