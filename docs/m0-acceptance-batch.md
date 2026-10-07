# M0 owner acceptance batch — 0.1.2

Task IDs: M0.3 / M0.4 / M0.5. Run **UAT-00 and UAT-01 only**. Status: **PASS on Allplan 2026-1-7**, confirmed by the owner on 2026-10-07. [Acceptance record](test-results/m0-acceptance-0.1.2.md). This card is retained for retesting; portable fake-host tests are separate evidence.

Package: `allplan-mcp-0.1.2-windows-evaluation.zip`. The package manifest identifies its base commit, modified-source flag and every payload hash; the adjacent `.zip.sha256` identifies the exact archive. The owner reports Allplan 2026-1-7 from the UI. Automatic build/hotfix discovery and embedded Python remain pending until diagnostics is received. The draft profile is inactive and not used in M0.

## Baseline and reset

Use a disposable test project or project copy, with a new empty active drawing file and space around the model origin. Record the project/file in your result. Save the baseline before the geometry test. No native-column fixture or QA layers are needed yet. After the test, delete the one test box through Allplan UI, or restore the disposable project copy. Do not repeat a failed write until the model has been inspected.

## UAT-00 — installation and first connection

Follow [Windows setup](windows-setup.md). Start StartPythonHost in Library and the MCP launcher; connect/restart local Codex. Use these exact owner prompts (Polish is supported):

> Sprawdź połączenie narzędziami `allplan_health` i `get_allplan_version`. Nie zmieniaj modelu. Podaj wersję pakietu, identyfikator sesji hosta, wersję Allplan, wersje obu środowisk Python oraz informacje o buildzie/hotfixie. Brakujące dane oznacz jako nieustalone.

Expected: Codex discovers **five** baseline tools (`allplan_health`, `get_allplan_version`, `get_all_object_names`, `create_cube`, `create_box`) plus the bundled skill resources. `execute_python` is absent. Health/version responses identify the actual running application, the installed bridge package and embedded runtime. Major 2026 compatibility is distinct from a verified hotfix. Run **Diagnostics.cmd** to save the report.

> Odczytaj `get_all_object_names` dla bieżącego dokumentu i podaj wynik. To odczyt nazw, nie pełny przegląd projektu; niczego nie zmieniaj.

Expected: the response describes the current document; an empty test file can have no names. This does not establish stable element identity or a full-project scan.

## UAT-01 — one box and host lifecycle

> W bieżącym pustym pliku testowym utwórz dokładnie jeden prostopadłościan 1000 × 1000 × 1000 mm narzędziem `create_box`. Wywołaj je tylko raz. Podaj identyfikator żądania; jeśli odpowiedź zaginie lub nastąpi timeout, nie ponawiaj operacji automatycznie.

Expected: **one** 1000 × 1000 × 1000 mm generic solid appears at the existing tool's insertion location near the origin. Inspect its dimensions through Allplan's ordinary measurement/properties UI. A `submitted: true` result means the host API call returned; `readback_verified: false` requires this visible check. It is not a native column and does not implement future workflows.

1. Press **ESC** to cancel StartPythonHost. Ask Codex for a health check; expect a readable `host_absent` error and the restart instruction. Keep the MCP launcher open.
2. Restart StartPythonHost from Library. Ask for health/version again; expect success and a **new host session ID**. No extra box should appear. Save Diagnostics again.
3. Minimize Allplan, repeat a read-only health/version call from Codex, restore the window and check responsiveness. If it fails or freezes, report that separately.
4. Switch to a second disposable project with an empty active file. If the normal UI command ends the interactor, restart it from Library. Ask for health and object names. Expect the current session/document; no stale box or write is requested. Return to the first project, restarting the host if necessary.
5. Delete the test box or restore the saved copy. Record the reset performed.

Do not engineer an in-flight race or run developer commands. The implementation model's portable probe covers an HTTP request queued behind a simulated UI dispatcher during cancellation; native UI/dispatcher behavior remains pending. No automatic write retry or durable deduplication is claimed for the baseline box tools.

## Copyable result

Send the filled result and the generated `logs\diagnostics-*.json` reports. Screenshots are optional; the box measurement and lifecycle observations matter. The implementation model records an English acceptance report.

```text
Package: 0.1.2 evaluation
Archive / manifest reference: (model records the supplied artifact)
Codex version:
Allplan version / full build / hotfix: (diagnostics + About dialog if missing)
Project / drawing file:
UAT-00: PASS | FAIL | BLOCKED
Health and names observed:
UAT-01 box: PASS | FAIL | BLOCKED
Box count / measured dimensions:
ESC / restart: PASS | FAIL | BLOCKED
Minimize / restore: PASS | FAIL | BLOCKED
Project switch: PASS | FAIL | BLOCKED
Diagnostic report filenames:
Unexpected behavior:
Reset performed:
```

Unattempted cases remain `NOT_RUN`. Report a prerequisite failure as `BLOCKED` only after attempting the case. Acceptance is recorded per exact package and observed Allplan build; The original M0 batch is accepted; future retests need their own results.
