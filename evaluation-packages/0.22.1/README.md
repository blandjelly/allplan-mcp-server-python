# Allplan MCP 0.22.1 — evaluation candidate

Runtime source: `35d4744bec47bf765116956a68a23bed1b6b199f`.
[PR #18](https://github.com/blandjelly/allplan-mcp-server-python/pull/18) targets develop/m4.

[Windows ZIP](allplan-mcp-0.22.1-windows-evaluation.zip) ·
[Checksum](allplan-mcp-0.22.1-windows-evaluation.zip.sha256) ·
[Short Polish trial](../../docs/m4-journal-recovery-0.22.1.pl.md) ·
[Owner follow-up](../../docs/test-results/m4-agent-followup-2026-10-19.md)

The follow-up exposes a concrete mismatch: query/preview merges agreeing views
of one model, but native write/recovery resolution required exactly one view.
Recovery and post-write verification now read all exact live representations,
including distinct wrappers with the same view UUID. Only unanimous typed old/new
observations reconcile an unknown result. Different or unreadable values remain
blocked. Recovery checks the original project/document and never retries setters.

New previews hash-bind one exact view for a single setter per change, after
agreement across representations and the existing native/foreground checks.
A missing bound view cannot silently select another. Raw common readback remains
in the journal; per-view hashes bound diagnostic size. Layer lookup is unchanged;
the owner's accepted full/short name result does not need another trial.

The final [CI 39307523821](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39307523821)
passed **486 tests on each Windows/Ubuntu Python 3.12 job**, followed by one
package job. The original CI artifact was downloaded and its GitHub SHA-256 verified, without
any local rebuild. The **exact delivered ZIP** passed payload/checksum integrity,
registration, frozen sync/import, upgrade from 0.22.0 and restore. All **37 bridge
hashes** matched, and journal/trace/bridge-log markers survived both transitions.

- [Focused verification](focused-verification.json): 76 affected/dependent tests,
  including legacy multi-view journals, conflicting wrappers, missing bound views,
  bounded readback diagnostics and continued writes through MCP HTTP. Another
  16 Wall-filter tests pass with a deterministic behavior-test clock; the separate
  explicit-expiry test still checks the unchanged production budget. An initial
  CI run exposed filesystem-latency interference in the existing exclusion test;
  that run produced no package.
- [Full source CI](source-ci.json) · [Exact ZIP verification](package-verification.json) ·
  [Verification log](package-verification.log) · [Verifier](verify_package.py) ·
  [Artifact hashes](artifact-hashes.json).
- **Native Allplan: not_run for the new recovery/write behavior.** Use the short
  trial above: retain the journal, recover execution
  `4388b04e39a14fac811db4f58723d01f`, then try one requested write and check UI.
  Do not repeat accepted layer-name, filter, highlight or fire/U checks.

Install using `Setup.cmd` from the extracted ZIP. Existing one-foreground-file,
32-setter, fresh-preview and journal safeguards remain. Main integration is separate.

Delivered ZIP SHA-256: `ca0c2bebb96a326238167c93d3d8e1470c94aebb997deb09678af33726e09adc`.

The delivery commit adds package evidence and an explicit restart instruction to
the linked trial. The ZIP remains the unchanged clean CI source identified above.
