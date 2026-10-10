# M3 — zapis standardu i reguły z wyjątkami, pakiet 0.11.0

Status **ograniczony odbiór natywny PASS**, 2026-10-10 Europe/Warsaw.
[Wynik i cztery oryginalne pliki](test-results/m3-workflow-acceptance-0.11.0.md):
10/10 kroków, obie naprawy, odczyty po zapisie, odczytowy replay, audyty 5 → 4 → 3
i ta sama sesja hosta. Użytkownik potwierdza zmiany w modelu, nieprzerwany host,
pozostałe elementy bez zmian i dwa kroki Undo. Nie powtarzaj tej próby.
Poniżej zachowano wykonaną procedurę; surowych flag/logów nie zmieniono.
To następny krok po audycie kompletności: dwa osobno zatwierdzone plany po jednej
zmianie przez apply_office_standard i rule_based_edit. Nie powtarzaj starego
M3 Apply.cmd, testu Undo ani ręcznej edycji podczas działania hosta.
[Kontrakt i ograniczenia](m3-workflow-execution-contract.md).
[Pakiet i sumy kontrolne](../evaluation-packages/0.11.0/README.md).

## Przygotowanie tej samej jednorazowej kopii

1. Zachowaj poprzednie pakiety, logi i cały dziennik
   Local\.allplan-mcp\repairs. Nie usuwaj go. Zamknij poprzednie okno MCP
   i Allplan, rozpakuj cały ZIP **0.11.0** do nowego folderu i uruchom
   **Setup.cmd**, wybierając ten sam faktyczny katalog Local.
2. Otwórz tę samą jednorazową kopię projektu z sześcioma słupami w aktywnym
   pliku **101**. Przed uruchomieniem StartPythonHost przywróć w UI wyłącznie:
   **S05** w środku (6000, 6000, 1500) mm → warstwa **SZ_OGÓ02 / Ogólne2**;
   **S06** w środku (12000, 6000, 1500) mm → istniejący status
   **MCP_QA_STATUS = NWE**. Oznaczeń i pozostałych pól nie zmieniaj.
   Przywrócenie tych dwóch usterek jest potrzebne, bo poprzedni test zostawił
   je naprawione. Nowa próba sprawdza dwa wcześniej niedostępne wejścia zapisu.
3. Uruchom Library → Private → PythonHost → **StartPythonHost**, a następnie
   **Launch Allplan MCP.cmd** z nowego pakietu. Nie wykonuj równoległych
   poleceń/edycji modelu. UI może zakończyć interaktywny host, dlatego
   przygotowanie danych musi nastąpić przed jego startem.

## Dwa osobno sprawdzane zapisy

1. Uruchom **M3 Workflow Apply.cmd**. Program sprawdzi zgodną wersję/integralność
   MCP i hosta oraz pełny audyt: 6 słupów, 5 usterek, 0 not_checked.
   Przy innej kopii/stanie zatrzyma się przed zapisem. Nie omijaj blokady.
2. Pierwszy podgląd musi pokazać **jedną** zmianę: S05, QA-003,
   warstwa SZ_OGÓ02 → SZ_OGÓ01. Standard 1.0.0 obejmuje warstwę/status,
   ale jawny wyjątek S06 chroni jego NWE w tym kroku.
   Po sprawdzeniu celu i jednorazowej kopii wpisz **NAPRAW STANDARD**.
   Program zapisze, odczyta i ponownie zaudytuje model: **4 usterki**.
3. Drugi świeży podgląd musi pokazać **jedną** zmianę: S06, QA-004,
   status NWE → NEW. Selekcja szuka statusu NWE i zawiera jawny wyjątek S05.
   Po sprawdzeniu wpisz **NAPRAW REGULE**. Wynik: **3 usterki oznaczeń**.
4. Każdy krok ma inny execution_id zapisany na dysku przed wysłaniem Apply.
   Program powtórzy dokładnie to samo ID/żądanie i sprawdzi odczytowy replay,
   następnie końcowy audyt i zdrowie w tej samej sesji. Oczekiwane **10/10
   kroków**, state=ready_for_ui_observation. Nie wykonuje Undo.

Po ukończeniu obejrzyj model: S05 ma warstwę struktury SZ_OGÓ01, S06 ma NEW,
oznaczenia/geometria i inne elementy pozostały bez zmian. Zapisz, czy host
działał bez przerwania do końca testu. Nie trzeba otwierać właściwości elementu
w trakcie pracy programu.

Wyślij oryginalną parę **logs\m3-workflow-apply-<czas>.json/.txt** i obserwację UI.
Raport zawiera oba plany, żądania/identyfikatory, wyniki, audyty i oryginalny tekst
MCP. Zachowaj również m3-workflow-execution-<id>.json/.txt oraz
m3-last-workflow-execution.json/.txt do ewentualnego odzyskiwania.

## Przerwanie lub brak odpowiedzi

Nie uruchamiaj Apply ponownie z nowymi identyfikatorami po częściowym wyniku,
utracie odpowiedzi lub niezgodnej weryfikacji. Zachowaj model/dziennik/logi.
Jeśli pierwszy zapis się skończył, a drugi został anulowany, pierwszy pozostaje
wykonany; program nie cofa modelu.

**M3 Workflow Recover.cmd** odczytuje zapisany identyfikator ostatniego kroku
i wywołuje wyłącznie Recover na tej samej kopii. Nie powtarza Apply, nie kończy
pominiętych zmian i nie wywołuje Undo. Dla jawnego rejected przed setterami
nie wysyła nawet Recover. Przy niepewnym wyniku zbierz również JSON/TXT recovery
i zgłoś obserwację, zanim powstanie następny plan.

Nie przywracaj ani nie usuwaj dziennika w celu obejścia blokady. Ten test nie
potwierdza natywnego odzyskiwania nieznanego wyniku, jeśli wszystkie odpowiedzi
dotrą prawidłowo. M3 pozostaje otwarty także po pozytywnym wyniku.
