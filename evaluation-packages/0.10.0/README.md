# Evaluation delivery — 0.10.0

Current native status: **bounded explicit marks-preview gate PASS** on
2026-10-10. [Acceptance, original uploads and verification](../../docs/test-results/m3-marks-acceptance-0.10.0.md)
record all ten steps, positive proposals, exception, excluded-peer collision,
unchanged revalidation/audits and owner-confirmed unchanged model/uninterrupted
host. No repetition is requested. The original delivery manifest and embedded
package documents retain their historical ready_for_owner_test/not_run flags;
this acceptance update does not rewrite them or rebuild any archive.
The [0.9.0 native read-only standard/selection gate passes](../../docs/test-results/m3-standards-acceptance-0.9.0.md),
including unchanged model and uninterrupted host. Its exact archive and original
uploads remain unchanged. M3/UAT-05/UAT-06 remain open.

Original owner-test archive:
[allplan-mcp-0.10.0-windows-evaluation.zip](allplan-mcp-0.10.0-windows-evaluation.zip).
The [completed read-only mark owner card](../../docs/m3-marks-preview-batch.md)
retains the procedure for reference.
The recorded test uses the repaired disposable six-column copy in file 101,
S05 SZ_OGÓ01 and S06 NEW, keeping the existing mark defects.
**M3 Marks Preview.cmd** checks two
explicit mark proposals, a UUID exception, an expected collision with an excluded
peer, three exact-plan revalidations, complete before/after audit and same-session
health. It retains original MCP text and decoded responses and invokes no
Apply/Recover/Undo. No earlier owner batch or fixture rebuild is requested.

Mark plans remain preview-only and the native executor refuses them even when
filtering leaves the previously accepted layer/status pair. No automatic
numbering, graphical labels or mark native writes are added.
[Contract](../../docs/m3-marks-contract.md).

Clean source **ebf2c752440a0f72b538527f35175668322395a4**, source_modified=false.
Windows ZIP **660447 bytes**, SHA-256:

```text
5a3e2ba0d75ebd798204922cf44da70d602bc2e41b8cdbe2f2f7f5c3b3c67888
```

[Delivery manifest](delivery-0.10.0.json) records ZIP/hash/wheel/sdist sizes and
hashes. Two clean-source ZIP builds are byte-identical. Exact extracted integrity
and recursive registration pass for all 22 bridge files. Publication documentation
does not rebuild this archive or replace earlier accepted versions.

[165 local tests PASS](../../docs/test-results/m3-marks-portable-0.10.0.md),
frozen sync and wheel/sdist build pass.
[CI run 38049405544](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38049405544)
passes all six Windows/Ubuntu Python 3.11–3.13 test/build/Windows-ZIP jobs for
clean source **ebf2c752440a0f72b538527f35175668322395a4**. Exact artifact publication is
commit **44776b7123f384802dec4d293e542f4de9236c17**; later artifact/documentation CI
is separate. This exact delivered ZIP is unchanged.
This is portable verification, not native mark-preview acceptance.
No merge or GitHub release is performed.
