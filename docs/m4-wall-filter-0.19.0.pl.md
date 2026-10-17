# M4 — filtr ścian według grubości, 0.19.0

Ta próba sprawdza odczyt wszystkich ścian w jednym jawnym rysunku i ich
podświetlenie według kryterium **grubość < 24 cm**. Uruchom ją na lokalnym
Windowsie z Allplan 2026. Użyj istniejącego projektu `MCP_QA_DEMO` i
rysunku pierwszoplanowego **101**, w którym są ściany 20 cm i 24 cm. Nie
zmieniaj geometrii ani nie zamykaj innych otwartych rysunków; żądanie obejmuje
wyłącznie rysunek 101.

## Próba

1. Zamknij Allplan i MCP, a następnie rozpakuj kompletny, zweryfikowany pakiet
   0.19.0 do nowego folderu. W tym folderze uruchom **Setup.cmd**, wskazując
   ten sam katalog Local co wcześniej. Zachowaj istniejącą historię, logi,
   dziennik napraw i ślad natywny; nie usuwaj ich.
   [README dostawy 0.19.0](../evaluation-packages/0.19.0/README.md).
2. Otwórz projekt w Allplan, uruchom Library → Private → PythonHost →
   **StartPythonHost**, a następnie **Launch Allplan MCP.cmd** z nowego folderu
   pakietu. Pozostaw host uruchomiony.
3. Uruchom **M4 Thin Walls.cmd**. Launcher sprawdza host przez `health_before`,
   wysyła jedno żądanie `model_wall_filter` i po odpowiedzi sprawdza
   `health_after` w tej samej sesji. Raport zapisuje się w
   `logs/wall-filter-*.json` oraz `.txt`; ślad natywny pozostaje w
   `Local/.allplan-mcp/logs/m4-native-probe.jsonl`.
4. Raport powinien zawierać oba odczyty: `thickness_mm=200`, `match=true` oraz
   `thickness_mm=240`, `match=false`, z kompletnym kryterium i liczbą wykluczeń.
   `units_runtime_verified=false` jest informacją o nadal niezweryfikowanej
   jednostce API. Sprawdź w Allplan, że widoczna jest tylko ściana 20 cm.
   To podświetlenie zastępuje wszystkie wcześniejsze podświetlenia w bieżącym
   dokumencie. Liczby `submitted_*` opisują wysłane cele; widoczności nie
   potwierdza odpowiedź MCP.
5. Uruchom **M4 Clear Highlight.cmd** i sprawdź, że podświetlenie zniknęło.
   Host powinien pozostać responsywny.

Przekaż modelowi JSON i TXT z `logs`, odpowiedni
`m4-native-probe.jsonl` oraz `bridge.log`, a także krótką ocenę PASS/FAIL:
stan zdrowia przed/po, wartości obu ścian, wynik widoczny w UI, wyczyszczenie
podświetlenia i to, że model nie uległ zmianie.

Jeśli odpowiedź na `model_wall_filter` zaginie, zachowaj raport i identyfikator
żądania. Nie uruchamiaj ponownie próby ani kolejnego natywnego żądania. Raport
`request_pending` jest zapisywany i fsync przed każdym wywołaniem.

## Zakres i ograniczenia

`model_wall_filter` wymaga jednego jawnego aktywnego rysunku pierwszoplanowego,
skanuje świeży kompletny zbiór M1 i przyjmuje do **100** ścian. `max_walls`
domyślnie wynosi **20** i można go podnieść najwyżej do 100. Próg domyślnie
wynosi 24 cm; jednostka wejściowa może być mm, cm lub m, a odpowiedź podaje mm.
Porównanie jest ścisłe `<`.

Obsługiwana jest wyłącznie natywna ściana `Wall` z dokładnie jedną warstwą;
czytana jest właściwość `Thickness`. Każdy UUID wykluczenia musi należeć do
pełnego zbioru ścian tego rysunku. Wykluczone ściany nie są odczytywane. Brak
pełnego pokrycia, przekroczenie limitu, nieobsługiwany typ/warstwowość lub
pierwszy błąd odczytu zatrzymuje operację przed podświetleniem. Nie ma częściowego
podświetlenia. Jeden skan i pojedyncza dyspozycja UI są wykonywane w ramach
żądania; nie powstaje buforowany plan zapisu.

Operacja jest tylko do odczytu: nie wywołuje setterów, nie czyta materiałów,
atrybutów ani metadanych i nie zmienia danych modelu. `native_selection` jest
nieobsługiwane. `units_runtime_verified=false`; jednostka natywna nie została
zweryfikowana w Allplan. Liczby zgłoszone jako wysłane nie potwierdzają liczby
widocznych podświetleń. Zero dopasowań czyści dotychczasowe podświetlenia.
Pełna akceptacja M4 i obsługa zapisów/materiałów pozostają poza tą próbą.

Status 0.19.0: **ready_for_owner_test**. Źródło `e455f35` przeszło 356 testów
w każdej z sześciu konfiguracji Windows/Ubuntu; dokładny dostarczany ZIP
przeszedł instalację, aktualizację z 0.18.2 i wycofanie, kontrolę 31 plików bridge
oraz zachowania dziennika i logów. [Dowody i sumy kontrolne](../evaluation-packages/0.19.0/README.md).
Pobranie artefaktu CI do środowiska zablokowało proxy, więc zgodnie z polityką
wykonano jedną lokalną budowę z czystego checkoutu tego samego commitu.
Próba natywna pozostaje **not_run**. Zawartość zamrożonego ZIP powstała przed
uzupełnieniem tych wyników; dołączone tam wzmianki PENDING dotyczą chwili budowy.
