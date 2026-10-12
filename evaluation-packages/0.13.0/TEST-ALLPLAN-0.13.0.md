# Nowy test Allplana — konflikt w jednej sesji, 0.13.0

Status: **ready_for_owner_test**, bez akceptacji natywnej. Wykonaj wyłącznie
tę nową partię w Allplanie 2026-1-7. Nie powtarzaj numeracji 0.12.0 ani
zakończonych testów warstwy/statusu. Test zapisuje tylko oznaczenie C03.

## Przygotowanie

1. Zachowaj oryginalną jednorazową kopię projektu, stare paczki i logi oraz
   `Local/.allplan-mcp/repairs`. Zamknij Allplan i konsolę MCP.
2. Rozpakuj całą paczkę 0.13.0 do osobnego folderu. Uruchom **Setup.cmd**
   i wskaż dotychczasowy właściwy folder Local. Nie przenoś dziennika do innej kopii.
3. Otwórz tę samą jednorazową kopię i plik 101 na pierwszym planie. Po poprzednich
   dwóch Undo oczekujemy: C03 niezdefiniowany, C04/C02=S02; C05 warstwa struktury,
   C06=NEW. Nie wykonuj Redo. Program dopuszcza również istniejące ustalenia
   warstwy/statusu i nie zmienia tych pól.
4. Uruchom **StartPythonHost** z Private → PythonHost oraz **Launch Allplan MCP.cmd**.
   Nie uruchamiaj edycji w UI, Undo ani ESC podczas części konsolowej: takie
   polecenia kończyły hosta. Ten scenariusz zmienia źródło przez osobno zatwierdzony
   zapis w tym samym działającym hoście. Nie wymaga edytowania Python/JSON.

## Jedna nowa partia

1. Uruchom **M3 Conflict.cmd**. Program odczyta health/context i pełny audyt.
   Przy innym stanie oznaczeń zatrzyma się bez zapisu — przekaż raport zamiast
   resetować model na podstawie domysłów.
2. Powstaną dwa podglądy z tego samego pełnego źródła:
   - starszy: wybrany tylko C04 przy (0,6000) mm, S02 → S03;
   - do wykonania: wybrany tylko C03 przy (12000,0) mm,
     `<niezdefiniowany>` → S03.
   Każdy podgląd wyklucza pozostałych pięć słupów z propozycji, ale zachowuje je
   w kontroli źródła i kolizji. Podglądy pozostawiają model bez zmian.
3. Przeczytaj plan **C03** i potwierdź właściwą jednorazową kopię. Wpisz
   **SPRAWDZ KONFLIKT**. Program ponownie sprawdzi ten plan, zapisze nowy
   identyfikator wykonania przed wysłaniem Apply i zmieni wyłącznie C03 na S03.
   Inny tekst anuluje partię przed Apply.
4. Oczekiwany wynik zapisu C03: completed, jeden applied, odczyt S03,
   audited_fields_match_plan=true i pełny audyt z jednym ustaleniem mniej
   (w aktualnym modelu **3 → 2**, pozostają dwa QA-002).
5. Program wysyła próbę Apply starszego planu C04 z osobnym nowym identyfikatorem.
   Oczekujemy **rejected / plan_expired / native_setters_started=false**, ponieważ
   rozpoczęcie wcześniejszego zapisu unieważniło plany. Następnie jednorazowa
   odczytowa rewalidacja jego zachowanych dowodów musi pokazać **conflict**,
   **source_unchanged=false**, **plan_invalidated=true** i różne stare/bieżące
   odciski źródła oraz raportu. To rzeczywista zmiana wykluczonego C03; C04 nadal S02.
6. Końcowy audyt musi być identyczny z audytem po zapisie C03. Health musi
   potwierdzić ten sam host_session_id, wersję 0.13.0 i integralność.
   Oczekiwany stan konsoli: **ready_for_ui_observation**, wszystkie 12 kroków OK.
7. Dopiero teraz sprawdź w UI: C03=S03, C04/C02=S02, pozostałe oznaczenia,
   warstwy, statusy, geometria i liczba elementów bez zmian. Zapisz, czy host
   przetrwał całą część konsolową. Kontrolujemy dane oznaczenia, nie graficzne etykiety.
8. Wykonaj **jeden Undo** dla nowego zapisu C03. Nie cofaj starszych zaakceptowanych
   zmian C05/C06. Jeżeli Undo zakończy hosta, uruchom ponownie StartPythonHost.
   Uruchom **M3 Conflict Recover.cmd** w tym samym folderze i projekcie.
   Oczekujemy jednego old_value_observed i pełnego audytu z trzema ustaleniami
   oznaczeń. Historyczne applied pozostaje historycznym wynikiem; Recover nie
   wysyła Apply, nie wznawia zapisu i nie wykonuje Undo.

## Raport i zatrzymanie

Przekaż PASS/FAIL/BLOCKED, obserwacje UI/Undo, końcowy stan projektu i JSON/TXT
z folderu logs. Zachowaj `m3-last-conflict-execution.json`,
`m3-conflict-execution-<ID>.json` oraz raport zawierający osobny identyfikator
odrzuconej próby C04. Po teście zostaw i zapisz tę samą kopię z C03 niezdefiniowanym,
C04/C02=S02 oraz zachowanymi C05/C06. Bez Redo i bez ponownego uruchomienia partii.

Po timeout/unknown/stopped przerwij i zachowaj logi. Użyj **M3 Conflict Recover.cmd**
wyłącznie do odczytu zapisanego wykonania C03. Jeżeli raport zawiera
uncertain_stale_execution_id, lokalny Windows Codex powinien dodatkowo odczytać
Recover tego osobnego ID i świeży audyt — nie twórz nowego Apply. Brak rekordu
tej próby sam nie zastępuje kontroli modelu. Nie usuwaj dziennika, żeby odblokować zapis.
Po blocked/cancelled przed Apply nie wykonano zapisu. Odrzucenie C04 nie cofa
wcześniejszego zapisu C03: po udanej partii nadal potrzebny jest opisany jeden Undo.

Ta partia sprawdza konflikt źródła po kontrolowanym zapisie w jednej sesji oraz
blokadę starego planu. Nie ustanawia akceptacji edycji ręcznej w UI, natywnych
częściowych/unknown wyników, szerszego zakresu ani trwałości po awarii.
Kontrolowany partial/unknown i jego recovery będą kolejną osobną partią po
ocenie tego wyniku; M3/UAT-05/UAT-06 pozostają otwarte.
