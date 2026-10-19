# Allplan MCP 0.23.0 — confirmed journal maintenance

Runtime source: `8c71de958c47ab4cb418a62fbd2d55ce76cbc4db`.
[PR #19](https://github.com/blandjelly/allplan-mcp-server-python/pull/19) targets develop/m4.

[Windows ZIP](allplan-mcp-0.23.0-windows-evaluation.zip) ·
[Checksum](allplan-mcp-0.23.0-windows-evaluation.zip.sha256) ·
[Short Polish trial](../../docs/m4-journal-cleanup-0.23.0.pl.md) ·
[M4 completion assessment](../../docs/m4-completion-status-2026-10-20.pl.md) ·
[Owner observation](../../docs/test-results/m4-agent-observation-2026-10-20.md)

The owner confirms the latest slab/column attribute outcomes match Allplan, but
had to clear a size-full journal manually. The supplied log omits the exact
capacity error, so no particular limit is assumed: the diagnostic trace has a
1 MiB cap, active execution history holds 128 records, and each execution has a
separate 1 MiB verification/persistence cap.

Use `fix_model_issues` with `preview_journal_cleanup`, choosing `native_trace`
or `repair_records`. The agent displays scope/bytes/protected entries and asks
whether to clean. Only after confirmation does it send `cleanup_journal` with
the exact unchanged snapshot and `confirmed_journal_cleanup`.

Trace cleanup atomically archives exact bytes and lets a new active file start.
Append/rotation share an OS lock. Record cleanup archives verified resolved
executions, keeping original IDs available for setter-free replay after restart.
Unknown/running, corrupt, oversized, unsafe or colliding records stay protected.
A stale snapshot requires fresh preview and confirmation; partial batches keep
each execution active or archived. No deletion, model edit or automatic model
retry occurs. Archives still consume disk space; retention/export is separate.

The final [CI 39336895867](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39336895867)
passed **505 tests on each Windows/Ubuntu Python 3.12 job**, then one package
job. The original CI artifact transferred with its GitHub digest verified;
there was no local rebuild. The **exact delivered ZIP** passed checksum/payload,
registration, frozen sync/import, upgrade from 0.22.1 and restore. All **38 bridge
hashes** matched. Active journal/trace/bridge-log markers and archived execution
and trace markers survived upgrade/restore.

Validation evidence:

- [Focused checks](focused-verification.json): 140 unique affected/dependent
  tests, including HTTP capacity hints, missing confirmation, exact-byte archive,
  continued preview, archived replay, conflicts, partial failure and bounds.
- [Full source CI](source-ci.json) · [Exact ZIP verification](package-verification.json) ·
  [Verification log](package-verification.log) · [Verifier](verify_package.py) ·
  [Artifact hashes](artifact-hashes.json).
- **Native maintenance acceptance: not_run.** Use only the short new maintenance
  trial; preserve accepted slab/column attributes, layer lookup and highlights.

Install with `Setup.cmd`, then restart StartPythonHost and the MCP connection.
Preserve runtime journals and archives. M4 K1–K6 completion gaps are recorded in
the linked assessment; no full M4 acceptance or main integration is claimed.

ZIP SHA-256: `2b774862943000e9cb7e73062cb095e60ea696aa59e86a0afef9657480b3932a`.

The delivery commit adds evidence and updates documentation status only. The ZIP
remains the unchanged clean CI source identified above.
