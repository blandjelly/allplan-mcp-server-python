> **WYCOFANA PRÓBA NATYWNA / FAIL_CRASH (13.10.2026): nie uruchamiaj M4 Properties z 0.16.0.**
> Pierwsze żądanie spowodowało crash Allplana. Poniższe przygotowanie/portable PASS
> jest historyczne i nie oznacza odbioru natywnego. Użyj wyłącznie nowej próby 0.16.1
> po zainstalowaniu całej nowej paczki; źródła i archiwum 0.16.0 pozostają dowodem.

# M4 property discovery / UI probe — 0.16.0

Status: **ready_for_owner_test**. Native Allplan acceptance: **not_run**.
Native UI selection: **BLOCKED_current_interactor**. This delivery advances K1
and the early K2 experiment in the [editing plan](../../docs/office-editing-development-plan.pl.md);
it does not close those milestones or enable new model writes.

Download the complete [Windows ZIP](allplan-mcp-0.16.0-windows-evaluation.zip)
([checksum](allplan-mcp-0.16.0-windows-evaluation.zip.sha256)), extract it and follow
the [short Polish walkthrough](../../docs/m4-properties-owner-test.pl.md).
The package has **M4 Properties.cmd** and **M4 Clear Highlight.cmd** at its root.
Run only these new observation steps; keep the original project after Undo and
Local/.allplan-mcp/repairs. No repeated M3 writing gate is requested.

Clean source: **8ac5e97563c881f3427fc47ef752b5c5362786ee**, branch
**codex/m4-property-discovery**, based on M3. [Draft PR #5](https://github.com/blandjelly/allplan-mcp-server-python/pull/5).
One final local full suite: **233 tests PASS**, Linux CPython 3.12.14.
Frozen sync, wheel/sdist builds and exact ZIP installation/restore simulation PASS:
129 payload files, 27 installed host hashes, journal bytes preserved and previous
portable installation fixture restored. This simulation does not execute the
Windows setup UI or Allplan. [Source CI 38299080569](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38299080569)
completed **6/6 PASS**, Windows/Ubuntu × Python 3.11–3.13, tests and builds included.

## Delivered behavior

- `model_properties`: sampled native Column/Wall attribute values, exact
  project name/ID resolution, raw type/unit/enum metadata and per-family property
  support. Definitions, ownership, reads and write acceptance remain separate.
- `model_query`: default open drawings, including passive read files, with explicit
  file states/omissions and stale detection when the loaded scope changes.
- `model_selection`: highlight the full freshly revalidated result across all
  pages, optional UUID exceptions and document-wide clear. API submission alone
  does not prove visible highlighting; `select` returns unsupported without UI calls.

This is not a full project property catalog or native thickness/material adapter.
Actual fire-resistance semantics/W1 availability require the new observation.
C35, native selection, criterion-based writing and additional families remain pending.
[Existing M3 acceptance/limits](../../docs/validation-status.md) are preserved.

## Artifacts and evidence

- [Delivery manifest](delivery-0.16.0.json), [source CI](source-ci-0.16.0.json),
  [exact installation/restore](package-verification.json).
- [Portable test log](portable-tests.log), [build log](build.log), [frozen sync](frozen-sync.log).
- [Wheel](allplan_mcp_server-0.16.0-py3-none-any.whl).
- [Walkthrough copy](TEST-ALLPLAN-0.16.0.md) / [plain text](TEST-ALLPLAN-0.16.0.txt).

The ZIP contains documents frozen at its source commit. Later delivery-only
documentation commits do not rebuild the artifact or change its tested source.
The approximately 99 MiB sdist was built locally and is not committed.
