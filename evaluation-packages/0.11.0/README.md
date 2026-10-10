# Evaluation delivery — 0.11.0

[Windows evaluation ZIP](allplan-mcp-0.11.0-windows-evaluation.zip),
[checksum](allplan-mcp-0.11.0-windows-evaluation.zip.sha256),
[delivery manifest](delivery-0.11.0.json).
Clean source **26d70b27bd06e2916cda74213cb8995aa9f0f19a**, ZIP **719947 bytes**,
SHA-256 **29fcfaed0a10108b630892da3710da3cdf05701c2d25a08a014ff4ab177ee031**.

The bounded native workflow-write gate passed on 2026-10-10: two separately
reviewed single-target writes/readbacks, read-only replay, audits 5 → 4 → 3,
host survival, unchanged other elements and owner-confirmed two-step Undo.
See [acceptance limits](../../docs/validation-status.md),
[setup](../../docs/windows-setup.md), [current handoff](../../docs/next-model-handoff.md)
and [recovery/journal guidance](../../docs/diagnostics.md).
Mark assignment/numbering, native conflicts and unknown recovery remain open.

Delivered ZIP/wheel/sdist/checksum and delivery manifest are unchanged. Their
embedded docs and launchers reflect original source. The manifest's pre-test
status is historical; current acceptance is recorded separately above.
Old build/test/verification logs listed there are available in
[the original delivery](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/evaluation-packages/0.11.0).
Documentation cleanup neither rebuilds this archive nor asks to repeat its test.
