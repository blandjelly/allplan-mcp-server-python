# M4 — poprawka próbki ściany 0.18.2

W [próbie 0.18.1](m4-native-observation-0.18.1-2026-10-17.md) host działał,
lecz `wall_sample` zatrzymał się z `probe_scope_unavailable` i komunikatem
„Wall sample has ambiguous adapter representations”. Nie zwrócił właściwości
ściany. Załączone logi nie zawierają natywnego trace, więc nie pokazują dokładnej
hierarchii adapterów w tej próbie.

Kod wymagał identyczności obiektów Pythona (`is`) dla wszystkich reprezentacji
korzenia. M1 może dojść do tej samej ściany przez jej oś i warstwę, otrzymując
osobne wrappery. Test regresji odtwarza ten przypadek i ten sam błąd 0.18.1.
0.18.2 wybiera jeden adapter po pełnym skanie M1: jeden plik, UUID modelu,
jeden UUID widoku i zgodne pola korzenia, w tym typ. Nie dodaje nowych metod
natywnych. Sprzeczne pola, różne widoki, nieczytelna tożsamość i rodzic w innym
pliku nadal blokują odczyt. Raport dodaje `sample.adapter_resolution` z metodą,
UUID widoku i liczbą reprezentacji.

To nadal pojedynczy odczyt właściwości, bez podświetlania i bez zmiany materiału.
Runtime Columns i poprawka transportu 0.18.1 pozostają bez zmian.
[Nowy pakiet i wyniki weryfikacji](../evaluation-packages/0.18.2/README.md).
Natywna próba poprawki ma status **ready_for_owner_test**, a nie PASS.

## Jedna krótka próba w Allplanie

1. Zachowaj istniejącą kopię MCP_QA_DEMO, rysunek **101 foreground**, ścianę
   jednowarstwową **200 × 4000 × 3000 mm**, dziennik napraw i wcześniejsze logi.
   Zamknij Allplan i MCP. Rozpakuj pełny ZIP **0.18.2** do nowego folderu;
   uruchom **Setup.cmd** z tym samym katalogiem Local.
2. Otwórz kopię testową, uruchom **StartPythonHost**, następnie
   **Launch Allplan MCP.cmd** z nowego pakietu. Użyj raz
   **M4 Wall Properties.cmd**. Launcher sprawdza wersję/integralność **0.18.2**,
   zapisuje żądanie przed wysłaniem i nie ponawia odczytu automatycznie.
3. Oczekuj `health_before`, jednej odpowiedzi `one_wall_sample` i
   `health_after` w tej samej sesji. Dla zachowanej ściany oczekuj
   `state=observed`, `tier_count=1`, grubości API **200 mm** i
   `matches_assuming_native_mm=true` (200 < 240). Porównaj grubość i dokładny
   surowy materiał z UI. Liczba `adapter_resolution.representations` może być
   większa niż jeden; nie oznacza wielu odczytanych ścian.
4. Zgłoś PASS/FAIL/BLOCKED dla odczytu, grubości, materiału, obu health oraz
   braku zmian w modelu. Zachowaj `logs/wall-properties-*.json` i `.txt`,
   `Local/.allplan-mcp/logs/m4-native-probe.jsonl` i `bridge.log`.
   Przy błędzie lub utracie odpowiedzi zakończ próbę bez ponawiania.

Próba nie wymaga Undo. Jednostki natywne nadal wymagają potwierdzenia;
`units_runtime_verified=false` i zapis materiału pozostaje niedostępny.
Przy potrzebie wycofania zamknij Allplan i MCP, użyj **Restore bridge.cmd**,
a potem uruchom ponownie host i poprzedni pakiet. Instalacja i wycofanie
zachowują dziennik napraw oraz logi.
