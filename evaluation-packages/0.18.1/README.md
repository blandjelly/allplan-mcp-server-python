# 0.18.1 — host transport timeout candidate

Download [the complete Windows ZIP](allplan-mcp-0.18.1-windows-evaluation.zip).
This candidate addresses HTTP worker/UI scheduling and records where a host
reply stops. The owner-supplied 0.18.0 logs prove incomplete health replies;
they do not prove a specific native root cause. The owner later confirmed host
response on 0.18.1 in scoped M4 observations; see the
[observation report and original uploads](../../docs/m4-native-observation-0.18.1-2026-10-17.md).

The UI timer now processes a Python request queue and briefly yields to HTTP
workers. Queued work that does not start within three seconds is cancelled;
it cannot execute later. Running native work is never retried. Health reports
the loaded `ui_dispatch_mode=timer_queue_v1`; bridge logs include dispatch and
send stages. Read-only host timeouts no longer imply an unknown model write.
The Wall/Columns native handlers, write guards and previous archives are unchanged.

Validation of clean source **f477f138231f2a8f45690c03bd761364c7e94ab6**:

- **306 portable tests PASS**, CPython 3.12.14, 126.423 seconds.
  [Full log](portable-tests.log). New HTTP coverage includes stalled UI,
  cancelled late writes, same-session MCP recovery, UI thread execution,
  shutdown, callback exception containment and read-only timeout diagnostics.
- Frozen sync, wheel/sdist and Windows ZIP build PASS. [Build log](build-0.18.1.log).
- Exact ZIP checksum/payload validation, 30 installed bridge hashes, frozen
  sync/import from the extracted ZIP, upgrade from 0.18.0 and restore PASS.
  Journal, native trace and bridge log preserved; only native payload changes
  are `StartPythonHost.py` and `transport.py`.
  [Verification](package-verification.json), [script](verify_package.py),
  [log](package-verification.log).
- [Source CI 39026387338](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39026387338):
  **6/6 PASS**, Windows/Ubuntu × Python 3.11–3.13, frozen sync, full tests,
  wheel/sdist and ZIP builds. [Recorded results](source-ci-0.18.1.json).

[Delivery manifest and artifact hashes](delivery-0.18.1.json).
The artifacts are frozen from the clean source above. Later delivery/documentation
commits do not rebuild them or expand the tested scope.
The owner check confirmed host health/response delivery. The Columns observation
supports owner-confirmed highlight visibility and same-session health only; the
Wall sample was blocked before native read. Writes, Undo/recovery and full M4
acceptance remain pending. The PR remains a draft.

## Krótka próba

1. Zamknij Allplana i konsolę MCP. Rozpakuj pełny ZIP do nowego folderu.
   Uruchom **Setup.cmd**, wybierając ten sam folder Local.
2. Uruchom projekt → **StartPythonHost** → **Launch Allplan MCP.cmd** z nowego
   pakietu. W lokalnym Codexie poproś o samo `allplan_health`, bez innych narzędzi.
3. Oczekiwane: `ok=true`, pakiet/host **0.18.1**,
   `runtime.ui_dispatch_mode=timer_queue_v1`. Jeśli działa, sprawdź sam health
   po zminimalizowaniu i przywróceniu Allplana.

Przy błędzie zachowaj konsolę MCP i **Local/.allplan-mcp/logs/bridge.log**.
Na tym kończy się próba tej poprawki; wcześniejsze wyniki zapisów pozostają
w dzienniku. [Szczegóły, obserwacje i wycofanie](../../docs/mcp-timeout-0.18.1.md).
