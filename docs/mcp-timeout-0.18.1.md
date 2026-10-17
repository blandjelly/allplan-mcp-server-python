# Host response timeout investigation — 0.18.1 candidate

The owner reported that Codex could discover MCP but every attempted operation
timed out on 2026-10-17. StartPythonHost was running. Both supplied logs refer to
health request `54ac288c-8d0b-4289-86c9-bf6ee1470829`.

The bridge log records these events (UTC; add two hours for Europe/Warsaw):

| Time | Event |
| --- | --- |
| 10:36:03.950 | Host session started. |
| 10:36:53.838 | Health POST `/get-allplan-version` read by the host. |
| 10:36:57.058 | Host reached `send_response(200)`. |
| 10:37:29.488 | Response lost, with no `response_sent`. |
| 10:37:31.962 | Host stopped. |

An earlier health request at 10:35:35.870 also reached `send_response(200)` at
10:35:41.403 and then lost its reply. The MCP log shows `urllib` timing out
while reading the host's HTTP status. These records establish host response
failure, not an MCP startup failure. A `200` access-log entry is emitted before
headers/body are written and does not prove delivery. The console timestamp for
the matching timeout precedes the bridge's `request_started`; cross-thread log
timestamps alone cannot establish when the client actually sent the request.

No evidence attributes the incident to the OAuth discovery 404s, the GET 406s,
or Python 3.14's Proactor connection-reset messages. The old host log lacks
dispatch-start/finish and send-stage timing, so it cannot prove a CLR deadlock,
GIL starvation, socket cause, or a particular native call as the root cause.

## Candidate change

0.18.1 replaces the HTTP worker's unbounded synchronous WPF `Dispatcher.Invoke`
round trip with a Python queue processed by the existing 50 ms UI timer. Native
calls stay on Allplan's UI thread, and Python exceptions stay contained. Each
timer tick yields the GIL for 1 ms so HTTP workers can read requests and send
responses even while the embedded runtime is otherwise idle. This addresses
plausible scheduling failure points; portable tests do not reproduce or prove
the Windows embedded-runtime cause.

A queued request that has not started within three seconds returns HTTP 503
`ui_dispatch_unavailable`. Its future is cancelled atomically, preventing a
timed-out queued write from executing when UI processing resumes. Started native
work is not cancelled or retried; a lost write reply remains `execution_unknown`.
Nested timer callbacks cannot run another operation during a running handler.
Host cancellation releases queued workers and prevents old-session execution.

The bridge logs `ui_dispatch_queued`, `ui_dispatch_started`,
`ui_dispatch_finished`, `response_started` and `response_sent` with request IDs
and timings. Lost replies include their exception type and send time. Health
reports the loaded `ui_dispatch_mode=timer_queue_v1`, independently of metadata
on disk. Read-only HTTP timeouts use `host_timeout` and identify the host URL
and recovery log; they no longer imply that a health check may have written.

## Owner check — Polish

The [0.18.1 delivery](../evaluation-packages/0.18.1/README.md) passed 306 portable
tests, six source CI configurations and exact ZIP installation/upgrade/restore.

1. Zamknij Allplana i konsolę MCP. Rozpakuj pełny nowy pakiet **0.18.1** do
   osobnego folderu. Uruchom **Setup.cmd** i wybierz ten sam folder Local.
2. Otwórz projekt, uruchom **StartPythonHost**, potem **Launch Allplan MCP.cmd**
   z nowego folderu. Zachowaj dziennik napraw i wcześniejsze logi.
3. W lokalnym Codexie poproś: „Wywołaj tylko `allplan_health`. Podaj wersję
   pakietu, `runtime.ui_dispatch_mode` i `request_id`. Nie wykonuj innych narzędzi”.
   Oczekiwane: `ok=true`, obie wersje **0.18.1**, tryb **timer_queue_v1**.
4. Jeśli pierwszy odczyt przejdzie, powtórz sam health po zminimalizowaniu
   Allplana i po jego przywróceniu. Na tym kończy się sprawdzenie tej poprawki.
5. Przy timeout/503 zachowaj konsolę MCP i
   **Local/.allplan-mcp/logs/bridge.log**. Nowe wpisy pokażą ostatni zakończony
   etap. Nie uruchamiaj jeszcze testów zapisu ani ponownie prób zapisu
   z utraconą odpowiedzią. Pakiet można wycofać przez **Restore bridge.cmd**
   po zamknięciu Allplana i MCP.

Native recovery remains **not_run** until that observation. The original 0.18.0
archives and their recorded checks remain unchanged; this candidate does not
accept the Wall read, material writes, or expand M4 acceptance.
