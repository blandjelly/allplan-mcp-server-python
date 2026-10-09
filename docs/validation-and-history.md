# Validation, delivery and historical evidence

## Current main baseline

Main contains accepted M0–M2, package **0.6.1**. The portable suite has **121 tests**;
native acceptance is separately recorded for
[M1](test-results/m1-acceptance-0.5.3.md) and
[M2](test-results/m2-acceptance-0.6.1.md).

[M2 PR CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37929480307)
and [post-merge main CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/37930519639)
both passed all six Windows/Ubuntu × Python 3.11/3.12/3.13 jobs.
The workflow runs frozen dependency sync, the portable tests, wheel/sdist build
and deterministic Windows ZIP checks. Passing CI does not execute Allplan.

The separate [draft M3 PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
reports 134 portable tests and delivered 0.7.0 artifacts. It is not merged into
main and its native owner verification is pending.

## Tested Windows archives

These identify the original delivered archives, not a new build of the current
documentation. Keep the owner-retained files unchanged; runtime changes need a
new package version. The accepted ZIPs below are outside main under ignored dist/.

| Version / recorded status | SHA-256 |
| --- | --- |
| 0.1.2 / M0 accepted | `d97b6761b13f8cd6e80c7954f1c91de513d4a813a5b236c6917b14b0882ac528` |
| 0.2.1 / bounded context accepted | `26ca92690be0365eca3d580b947c52b443e536cc8ee10d8b1ca7b1de594bc6e8` |
| 0.5.3 / bounded M1 accepted | `15262b1f029d818e5fea871a0b669603d90a5b6ca68e80d5355457b8656ed104` |
| 0.6.0 / audit UI match; later crash unresolved | `6fc6e37fa4abd09ffec5b7a72d2b34a3a67c49a1ad2eef4cd480426428be2dd7` |
| 0.6.1 / bounded M2 accepted | `b47cba9ab08cce800f9e1900d03a232153c4441d054818f1bc116e8cc4a617f7` |

0.5.3's clean source is `4f685766e1577cddb681ee3726bbabd3f2b3d743`.
0.6.1's manifest records M1 baseline `bc5137339f3a6fa2049b322d7c726e659b523279`
with source_modified=true; original archive/per-file hashes identify the tested
source. Documentation cleanup does not rebuild or replace these packages.

## Archived reports and logs

Superseded batch cards, intermediate test reports and raw diagnostics were
removed from the current tree on 2026-10-09. The originals remain in the
[immutable pre-cleanup documentation](https://github.com/blandjelly/allplan-mcp-server-python/tree/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs) and
[raw evidence directory](https://github.com/blandjelly/allplan-mcp-server-python/tree/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence). Historical pending/next-action text
describes the state at capture time; use the current handoff for current work.

Earlier context/query/metadata batches supplied the accepted project/file
identity, small-page/full-summary and passive-versus-active attribute evidence.
Passive API omission is not proof of absence. The old profile setup issues were
resolved before the accepted M1 A/B/C captures. M1 had 56 targeted completion
checks and 14 observed-family correction checks; the integrated pre-M2 suite
had 95 tests. M2's portable suite grew from 114 to 121 with dispatcher containment.

The original 0.6.0 audit matched the five-finding fixture and the owner's UI;
the later invalid-scope request coincided with a CLR crash. The
[0.6.1 correction record](test-results/m2-dispatch-fix-0.6.1.md) retains the
confirmed incident, the fix and unresolved causal limits. The 0.6.1 recovery
gate passed separately; earlier 0.6.0 stability is not retroactively accepted.

Archived files can be recovered from Git without reintroducing their logs to
current documentation or the evaluation package:

```sh
git show 73b704fd3054b29c4e7c741a7891b8cc53e1b7cd:docs/test-results/evidence/diagnostics-20261009T113712Z.json
```

Original evidence hashes (including the original TXT/Markdown line endings):

| Archived file | Bytes | SHA-256 |
| --- | --- | --- |
| [allplan-model-query-results-0.3.0.md](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/allplan-model-query-results-0.3.0.md) | 6587 | `fbd7211871b14c5b6a724483b5cc81b7152ef00c22f7febc7bc6af4641819fd2` |
| [diagnostics-20261007T132549Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T132549Z.json) | 13185 | `b793bbcada5d540eb5b12ffbd777dadd2f33418c6e6abeb8599c2cd045db28c6` |
| [diagnostics-20261007T132700Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T132700Z.json) | 12221 | `acf137c1655c3ce13d6ac620ac88745ed14c34231b6d8ac865080d31aa68575f` |
| [diagnostics-20261007T132822Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T132822Z.json) | 18953 | `b1db2cc225066c307862de810005985d66ba0031f00a11c9a71712f3745be90b` |
| [diagnostics-20261007T163342Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T163342Z.json) | 14021 | `47dced744f2577d62edfb89aa9c1e38551398025fd4fe63a978ddf4fefdde22c` |
| [diagnostics-20261007T163433Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T163433Z.json) | 14021 | `afb18e05d439c3e7dc05ad6b57ec0b6ee4065f2288682d17c2c6997bd53429b5` |
| [diagnostics-20261007T163602Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T163602Z.json) | 14021 | `4fb315a9015e17a875ddd6f9cd6f155fa4968ccb164694362fd6c5ecb981aab1` |
| [diagnostics-20261007T191342Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T191342Z.json) | 2275 | `9f3246907e7a29db74b5de2415edf7596fd3106ba8921bb303f0916d8e90e5a0` |
| [diagnostics-20261007T191428Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T191428Z.json) | 2275 | `88df77bc257172626f67e6b2dc3960d13c0d3e458903842ced8fc21dc8c7188b` |
| [diagnostics-20261007T191757Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T191757Z.json) | 21960 | `ae7612cf4d50f65b0b296d3d446dc2994cc99f0dd18232f4687aa638f6bfd713` |
| [diagnostics-20261007T191833Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261007T191833Z.json) | 21959 | `eb570629afc26492829f2a7bcee6846b6b1d04957966f52f1aad5e9713ff7029` |
| [diagnostics-20261008T182010Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261008T182010Z.json) | 18905 | `83493579ded8faf972a9d9d32b3f59d9376fb532f96d5523f1c6db958967b1ed` |
| [diagnostics-20261009T104813Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261009T104813Z.json) | 95238 | `b7924dd3e2217b73b8583402f04c544d692ff18ea8866784bfc1e12795556628` |
| [diagnostics-20261009T104813Z.txt](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261009T104813Z.txt) | 1566 | `43fe30060d0510f580822480f76b1cad606858839afc3dcf1a5498c6eb70a4a3` |
| [diagnostics-20261009T113712Z.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261009T113712Z.json) | 246528 | `d12c893fbc624eaf577f4953504207b5da4438a57599ba395c0a5a39c4a8a9f3` |
| [diagnostics-20261009T113712Z.txt](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-20261009T113712Z.txt) | 1740 | `aeda6cd78e0531d587ea79bdc9817e59779438aced697d64940b091889dff2ec` |
| [diagnostics-crash-20261009.json](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-crash-20261009.json) | 305061 | `5e0c63cd63aa02c4073d26e6e3d826746b8a6050b062aa8381a8f4c0169d000b` |
| [diagnostics-crash-20261009.md](https://github.com/blandjelly/allplan-mcp-server-python/blob/73b704fd3054b29c4e7c741a7891b8cc53e1b7cd/docs/test-results/evidence/diagnostics-crash-20261009.md) | 6777 | `f12f278186df314623722b9459e6dc11db1e7971b613072e8771213278a327c9` |
