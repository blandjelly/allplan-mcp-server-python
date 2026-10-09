# UAT-04 — audyt M2, paczka 0.6.0

**Status: UAT-04 PASS w zachowanym zakresie odczytu po teście 0.6.1.**
[Akceptacja i logi 0.6.1](test-results/m2-acceptance-0.6.1.md).
[Historyczny wynik i awaria 0.6.0](test-results/m2-audit-runtime-0.6.0.md).
Poniższe kroki opisują wykonany test 0.6.0. Zbieranie danych awarii zakończono;
[poprawka 0.6.1](test-results/m2-dispatch-fix-0.6.1.md) przeszła
[ukierunkowany test stabilności](m2-stability-batch.md). Nie powtarzaj tego zestawu.
Test dotyczy wyłącznie odczytu na Allplan 2026-1-7. M0/M1 pozostają
zaakceptowane. Nie powtarzaj budowy fixture ani zestawu A/B/C z M1.
Nie poprawiaj teraz oznaczeń, warstw ani statusów: audyt ma odczytać istniejące
pięć celowych problemów. M3 naprawy nie są częścią tej paczki.

## Przygotowanie i uruchomienie

1. Zachowaj paczkę 0.5.3. Zamknij Allplan i poprzednią konsolę MCP.
   Rozpakuj cały `allplan-mcp-0.6.0-windows-evaluation.zip` do nowego katalogu.
2. Uruchom **Setup.cmd**, wybierając ten sam faktyczny katalog użytkownika
   Allplan **Local**. Instalator sprawdzi integralność i wykona kopię poprzedniego mostu.
3. Otwórz dotychczasowy projekt testowy lub jego kopię z zachowanym fixture M1.
   Plik **101** powinien być aktywny, **102** pasywny, **103** niewczytany.
   Użyj zachowanego wariantu bazowego z zerowym offsetem. Zasoby MCP_QA_MARK,
   MCP_QA_STATUS i warstwy SZ_OGÓ01/SZ_OGÓ02 są już przygotowane w M1.
4. W Library → Private → PythonHost uruchom **StartPythonHost**.
   Uruchom **Launch Allplan MCP.cmd** z nowej paczki i pozostaw konsolę otwartą.
   Jeśli korzystasz z Codex, użyj lokalnego czatu Windows z połączeniem Allplan;
   uruchom ponownie Codex, jeśli lista narzędzi nie zawiera `model_audit`.
5. Dwukrotnie kliknij **M2 Audit.cmd**. Nie trzeba edytować JSON ani wykonywać kodu.
   Skrypt zapisze pełny raport w `logs/diagnostics-*.json` oraz czytelny `.txt`.
   Stan audytu **fail** jest oczekiwany: oznacza wykrycie celowych problemów,
   a nie błąd uruchomienia testu.

## Oczekiwany wynik i porównanie z UI

Audyt obejmuje **6 kolumn z pliku 101**, a nie wszystkie 10 komponentów.
Oczekiwane jest **5 problemów na 5 kolumnach**, jedna grupa duplikatów,
`coverage.audit_complete=true`, zero kontroli `not_checked`.
C01 ma wszystkie cztery kontrole pass. Brakujące oznaczenie C03 jest pomijane
w kontroli unikalności jako not_applicable i zgłaszane przez QA-001.

| Reguła | Kolumna | Oczekiwany dowód | X/Y środka w mm |
| --- | --- | --- | --- |
| QA-001, error | C03 | Brak oznaczenia według jawnej polityki; surowe `<niezdefiniowany>` zachowane | 12000 / 0 |
| QA-002, error | C02 | S02, duplikat w pliku 101/rodzinie kolumn | 6000 / 0 |
| QA-002, error | C04 | S02, ta sama grupa duplikatów | 0 / 6000 |
| QA-003, warning | C05 | SZ_OGÓ02 zamiast SZ_OGÓ01 | 6000 / 6000 |
| QA-004, warning | C06 | NWE zamiast NEW/EXISTING | 12000 / 6000 |

Dla wszystkich kolumn box ma 400 × 400 × 3000 mm, a środek boxa ma Z=1500 mm.
Są to współrzędne model_local; X/Y wskazują położenie w zaakceptowanym fixture,
a Z jest środkiem, nie poziomem podstawy. Narzędzie nie zaznacza elementów w UI.
Użyj pliku, oznaczenia i współrzędnych do odnalezienia każdej kolumny; współrzędne
rozróżniają obie S02. Kolumna S02 w pasywnym 102 i niewczytanym 103 oraz belki
nie mogą powiększyć grupy duplikatów.

Jeśli zwykła inspekcja w UI zakończy działanie hosta, uruchom ponownie
StartPythonHost przed kolejnym odczytem. Opcjonalnie wykonaj **M2 Audit.cmd**
ponownie bez edycji modelu: nadal powinno być 5 problemów. Nie przełączaj offsetu
ani jednostek i nie powtarzaj testów M1 w tym zestawie.

## Wynik do przekazania

Przekaż pliki JSON i TXT z tego odczytu oraz krótką obserwację, np.:

> UAT-04: 5 problemów na 5 kolumnach; C03 brak oznaczenia, C02/C04 S02,
> C05 warstwa SZ_OGÓ02, C06 NWE. Pliki i położenia zgadzają się z UI.
> Model bez zmian. Allplan 2026-1-7, paczka 0.6.0.

Jeśli wynik odbiega od tabeli, przekaż raport i opis różnicy bez naprawiania fixture.
`profile_unbound`, niepełna coverage lub nieczytelne położenia wymagają korekty
implementacji albo potwierdzenia obecnego stanu fixture; nie oznaczają PASS.
Nie oczekuje się od użytkownika testowania sztucznie uszkodzonych odczytów lub
modyfikowania profili. Te przypadki mają osobne testy automatyczne.

Dopiero zgodność raportu z UI i potwierdzenie braku zmian pozwalają zamknąć
M2.1–M2.3 w ograniczonym zakresie fixture. To nie jest zgoda na naprawy M3.
