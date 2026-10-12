# Evaluation delivery — 0.14.1

13/13 + 6/6 + 6/6 controlled unknown/restart/replay/Undo, audits 3 → 2 → 3.
[Original report](https://github.com/blandjelly/allplan-mcp-server-python/blob/b0678da6d9d5565951c8576db8d83972331158c1/docs/m3-recovery-acceptance-0.14.1.md); [current scope/limits](../../docs/validation-status.md).

Clean source **1810e4fa284311e204b9133deee3245f8427697b**.

## Artifacts and evidence

- [Windows ZIP](allplan-mcp-0.14.1-windows-evaluation.zip), [checksum](allplan-mcp-0.14.1-windows-evaluation.zip.sha256).
- [Delivery manifest](delivery-0.14.1.json): source, checks and artifact identities.
- [Source CI observations](source-ci-0.14.1.json).
- [Exact installation/restore](package-verification.json).
- [Original native uploads/inspection](native-acceptance/20261012-owner/).
- [Portable test log](portable-tests.log).
- [Build log](build.log).
- [Frozen sync log](frozen-sync.log).

Archives, checksums, manifests, raw logs/uploads and embedded walkthroughs are
unchanged. Their pre-test status is historical. Completed writing gates need no
repeat; preserve the original copy after Undo and its Local journal/logs. Use
[setup](../../docs/windows-setup.md) and [recovery](../../docs/diagnostics.md).
