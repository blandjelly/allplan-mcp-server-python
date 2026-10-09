# M3 — test podglądu napraw, pakiet 0.7.0

Status: **ready_for_owner_test**. Pierwszy krok M3.1/M3.2; to jeszcze nie
zamknięcie UAT-05/UAT-06. Test jest tylko do odczytu i nie stosuje napraw.
Nie trzeba powtarzać zaakceptowanych testów M1/M2 ani tworzyć modelu od nowa.
Wymagana jest kontrola w Allplanie: chmura nie może potwierdzić wskazanych
obiektów i wartości w Twoim modelu.

## Instalacja i jeden test

1. Zachowaj sprawdzony ZIP **0.6.1** i dotychczasowy model referencyjny.
   Zamknij Allplan oraz poprzednie okno Launch Allplan MCP.
2. Rozpakuj cały ZIP **allplan-mcp-0.7.0-windows-evaluation.zip** do nowego
   folderu. Uruchom **Setup.cmd** i wybierz ten sam rzeczywisty folder `Local`.
   Instalator sprawdzi pliki i zapisze kopię poprzedniego hosta.
3. Otwórz dotychczasowy projekt testowy w Allplan **2026-1-7**. Plik **101** ma
   być aktywny, a sześć słupów i ich celowe błędy zachowane. Pliki 102/103 nie
   należą do tego testu. Uruchom Library → Private → PythonHost → StartPythonHost.
4. Uruchom **Launch Allplan MCP.cmd** z folderu 0.7.0 i pozostaw okno otwarte.
   Połączenie Codex może pozostać dotychczasowe; test uruchamiasz dwuklikiem
   **M3 Preview.cmd**. Nie wykonuj innych poleceń w Allplanie w trakcie odczytu.
5. Oczekiwany wynik: `M3 preview checks complete: True`, podgląd **2 zmian**,
   kontrola planu `unchanged`, audyt nadal **5 usterek**, ten sam działający host.
   Wyniki JSON i TXT zostaną zapisane w folderze `logs` nowego pakietu.
6. Porównaj wskazane elementy w UI. Podgląd ma dotyczyć wyłącznie:

| Element | Środek X/Y w modelu lokalnym | Wartość obecna | Proponowana wartość |
| --- | --- | --- | --- |
| C05, znacznik S05 | 6000 / 6000 mm | warstwa SZ_OGÓ02 | warstwa SZ_OGÓ01 |
| C06, znacznik S06 | 12000 / 6000 mm | MCP_QA_STATUS = NWE | MCP_QA_STATUS = NEW |

Model ma zachować obecne wartości. Marki C03 i pary C02/C04 pozostają poza
planem. Nie klikaj naprawy i nie poprawiaj celowych błędów podczas tego testu.
Nazwy warstw są ważniejsze niż numery ID, które host odczytuje świeżo.

Wyślij **oba najnowsze pliki JSON i TXT** oraz krótką informację:
„PASS — dwa wskazania i wartości zgadzają się; model bez zmian; Allplan i host
działają” albo „FAIL/BLOCKED — …”. Sam komunikat `True` nie potwierdza UI ani
całego modelu. Brak symbolu API w sekcji capabilities jest materiałem do dalszej
analizy, a nie powodem do samodzielnego włączenia zapisu.

## Opcjonalne sprawdzenie konfliktu w lokalnym Codex

Wykonuj tylko na kopii projektu testowego. Ten krok wymaga chwilowej **ręcznej**
zmiany w UI; narzędzie MCP nadal niczego nie zapisuje. Jeśli nie chcesz zmieniać
modelu referencyjnego, zakończ na poprzednim teście i prześlij jego wyniki.

1. W lokalnym czacie Windows poproś: „W pakiecie 0.7.0 przygotuj tylko podgląd
   napraw QA-003 → structure i QA-004 → NEW dla pliku 101, profile_id
   native-model-qa-demo. Zachowaj plan_id i plan_hash. Niczego nie stosuj.”
2. W ciągu pięciu minut zmień ręcznie **MCP_QA_STATUS C06 z NWE na EXISTING**.
   Polecenie UI może zakończyć StartPythonHost. Jeśli go zakończy, nie uruchamiaj
   nowego hosta jako rzekomej kontynuacji starej sesji — zgłoś ten przebieg.
3. Jeśli ten sam host nadal działa, poproś lokalny Codex: „Sprawdź poprzedni
   plan przez fix_model_issues action=revalidate z zapisanym plan_id i plan_hash.
   Niczego nie stosuj.” Oczekiwany wynik to **conflict**, nigdy automatyczna naprawa.
   `plan_expired` po restarcie/wygaśnięciu jest osobnym poprawnym zabezpieczeniem;
   nie stanowi dowodu konfliktu ręcznej zmiany w tej samej sesji.
4. Przywróć ręcznie status **NWE**, sprawdź stan modelu i prześlij wyniki czatu
   oraz informację, czy sesja hosta przetrwała polecenie UI.

## Błąd lub przywrócenie

Po `FAILED`, utracie odpowiedzi lub zamknięciu Allplana zatrzymaj test i zachowaj
wyniki. Nie uruchamiaj kolejnych prób równolegle. Dołącz dostępny
`Local\.allplan-mcp\logs\bridge.log` i informację o zachowaniu UI.
Test nie ponawia żądań automatycznie i zatrzymuje się po błędzie.

Aby wrócić do 0.6.1, zamknij Allplan i okno MCP, uruchom **Restore bridge.cmd**
z pakietu 0.7.0, a następnie uruchom Allplan i launcher z zachowanego folderu
0.6.1. Przywracanie hosta nie zmienia modelu; ewentualną ręczną zmianę statusu
przywróć osobno.
