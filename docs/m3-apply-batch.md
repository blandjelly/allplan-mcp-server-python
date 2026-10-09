# M3 — zapis i Undo na kopii projektu, pakiet 0.8.0

Status: **ready_for_owner_test**. Natywny zapis i Undo nie są jeszcze zaliczone.
Podgląd 0.7.0 jest już zaliczony; nowy test dotyczy zapisu, odczytu wyniku,
powtórzenia żądania i Undo. Nie powtarzaj M1/M2 ani nie przebudowuj modelu.

## Przygotowanie

1. Zachowaj oryginalny projekt referencyjny i sprawdzone archiwa. W Allplanie
   wykonaj **osobną, jednorazową kopię projektu** ze sprawdzonymi sześcioma
   słupami i pięcioma usterkami w pliku 101. Pracuj wyłącznie na tej kopii.
2. Zamknij Allplan i poprzednie okno MCP. Rozpakuj cały ZIP **0.8.0** do nowego
   folderu, uruchom **Setup.cmd**, wskaż rzeczywisty dotychczasowy `Local`.
3. Otwórz kopię w Allplan **2026-1-7**. Plik **101** ma być na pierwszym planie;
   warstwy słupów dostępne do modyfikacji. Uruchom Library → Private →
   PythonHost → StartPythonHost oraz **Launch Allplan MCP.cmd** z folderu 0.8.0.
   Nie wykonuj innych operacji w trakcie testu. Nie trzeba zmieniać połączenia Codex.

## Zapis dwóch zmian

4. Uruchom **M3 Apply.cmd**. Program sprawdzi wersję/integralność, wykona świeży
   podgląd i kontrolę planu. Przed zapisem pokaże dokładne stare i nowe wartości.
   Porównaj w UI:
   - **C05 / S05:** warstwa `SZ_OGÓ02` → `SZ_OGÓ01`;
   - **C06 / S06:** `MCP_QA_STATUS`, `NWE` → `NEW`.
5. Dopiero po sprawdzeniu kopii i obu celów wpisz **NAPRAW KOPIE** w oknie.
   Inna odpowiedź anuluje test bez zapisu. Nie zmieniaj modelu podczas wykonania.
6. Oczekiwane: `ready_for_ui_observation`, dwa wyniki `applied`,
   `audited_fields_match_plan=true`, pełny audyt **3 usterek** i
   `same_execution_replay: OK`. Sprawdź nowe wartości w UI, wygląd/geometrię
   oraz niezmienione pozostałe słupy i ich oznaczenia. Allplan i host nadal działają.
   Program nie deklaruje automatycznej transakcji ani cofania całej operacji.

## Restart, odczyt i Undo

7. Po zakończeniu zapisu zatrzymaj host ESC i uruchom StartPythonHost ponownie
   w tej samej kopii. Uruchom **M3 Recover.cmd**. Oczekiwane: dwa
   `new_value_observed`, audyt 3, `persisted_execution_replay: OK` i działający host.
   Recover jedynie odczytuje; powtórzenie zapisanej operacji nie stosuje jej ponownie.
8. W UI Allplana wykonaj **Undo**. Obserwuj, czy obie zmiany cofają się razem,
   czy wymagają dwóch kroków. Nie cofaj wcześniejszych operacji tworzenia kopii
   ani modelu. Jeżeli Undo jest niedostępne albo rezultat jest niejasny, zakończ
   test jako BLOCKED i zachowaj kopię do diagnostyki; nie naprawiaj jej ręcznie.
9. Gdy oba cele wrócą do `SZ_OGÓ02` i `NWE`, uruchom **M3 Check Undo.cmd**.
   Oczekiwane: dwa `old_value_observed`, pełny audyt **5 usterek**,
   `persisted_execution_replay: OK`. Sam ten skrypt nie wykonuje Undo ani zapisu.
   Potwierdź powrót wartości, wygląd modelu oraz działanie Allplana/hosta.

## Wyniki i przerwanie

Wyślij oryginalne JSON/TXT z `logs`: `m3-apply-*`, `m3-recover-*`,
`m3-check-undo-*`, oraz krótki opis **PASS / FAIL / BLOCKED**, wersję UI,
zgodność obu celów/wartości, niezmienione pozostałe elementy i liczbę kroków Undo.
`logs/m3-last-execution.json` przechowuje identyfikator do odzyskiwania; zachowaj
go, cały folder pakietu i dziennik `Local/.allplan-mcp/repairs`.

Przy błędzie albo utracie odpowiedzi **nie uruchamiaj ponownie M3 Apply**.
Nie wykonuj kolejnych zmian. Jeśli Allplan działa, uruchom M3 Recover; jeśli
trzeba, uruchom ponownie host w tej samej kopii. Zachowaj logi i zgłoś stan.
Brak zapisu w dzienniku może oznaczać odrzucenie przed pierwszym setterem;
nie zgaduj wyniku. Kopii nie włączaj do projektu produkcyjnego.

Natywny konflikt po ręcznej edycji, szersze typy/zapisy, odporność na awarię
zasilania i wspólna grupa Undo pozostają poza zaliczonym zakresem. Kolejny etap
zależy od tego testu. [Kontrakt i granice](m3-execution-contract.md).
