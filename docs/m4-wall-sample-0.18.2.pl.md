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
Natywna próba z 17 października 2026 ma wynik **PASS / accepted_on_build 0.18.2**
dla jednej odczytanej ściany: **240 mm**, materiał **„Beton”**, zgodne z UI.
Wykryto dwie ściany i celowo odczytano właściwości jednej. Zobacz
[wynik, zakres i oryginalne logi](m4-wall-observation-0.18.2.md).
Zakończonej próby nie trzeba powtarzać; poniżej zachowano poprawiony opis jej
przebiegu. Nie stanowi ona akceptacji filtrowania wszystkich ścian ani zapisu.

## Jedna krótka próba w Allplanie

1. Zachowaj istniejącą kopię MCP_QA_DEMO, rysunek **101 foreground**, istniejące
   ściany jednowarstwowe, dziennik napraw i wcześniejsze logi. W obserwacji
   właściciela były ściany **24 cm i 20 cm**; nie usuwaj drugiej ściany,
   aby wymusić wybór próbki.
   Zamknij Allplan i MCP. Rozpakuj pełny ZIP **0.18.2** do nowego folderu;
   uruchom **Setup.cmd** z tym samym katalogiem Local.
2. Otwórz kopię testową, uruchom **StartPythonHost**, następnie
   **Launch Allplan MCP.cmd** z nowego pakietu. Użyj raz
   **M4 Wall Properties.cmd**. Launcher sprawdza wersję/integralność **0.18.2**,
   zapisuje żądanie przed wysłaniem i nie ponawia odczytu automatycznie.
3. Oczekuj `health_before`, jednej odpowiedzi `one_wall_sample` i
   `health_after` w tej samej sesji, `state=observed` i `tier_count=1`.
   Bez podania UUID próbkowana jest pierwsza ściana według UUID modelu,
   nie według grubości. Porównaj grubość i dokładny surowy materiał tej ściany
   z UI: dla **240 mm** oczekuj `matches_assuming_native_mm=false`,
   dla **200 mm** — `true`, bo warunek to ściśle **<240 mm**.
   W tej próbie poprawnie wybrano ścianę 240 mm o materiale „Beton”.
   `matched_model_identities=2` i `sampled_walls=1` oznaczają dwie wykryte
   ściany i jeden odczyt właściwości. Liczba `adapter_resolution.representations` może być
   większa niż jeden; nie oznacza wielu odczytanych ścian.
4. Zgłoś PASS/FAIL/BLOCKED dla odczytu, grubości, materiału, obu health oraz
   braku zmian w modelu. Zachowaj `logs/wall-properties-*.json` i `.txt`,
   `Local/.allplan-mcp/logs/m4-native-probe.jsonl` i `bridge.log`.
   Przy błędzie lub utracie odpowiedzi zakończ próbę bez ponawiania.

Próba nie wymaga Undo. Dla odczytanej próbki potwierdzono zgodność 240 mm
z 24 cm w UI. Nie jest to ogólna weryfikacja jednostek; oryginalny raport
zachowuje `units_runtime_verified=false`, a zapis materiału pozostaje niedostępny.
Przy potrzebie wycofania zamknij Allplan i MCP, użyj **Restore bridge.cmd**,
a potem uruchom ponownie host i poprzedni pakiet. Instalacja i wycofanie
zachowują dziennik napraw oraz logi.
