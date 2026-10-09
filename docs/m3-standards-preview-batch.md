# M3.3 — podgląd standardu i wybór z wyjątkami, pakiet 0.9.0

Status: **ready_for_owner_test**. Odrzucenie starego Apply w 0.8.1 jest
[zaliczone](test-results/m3-stale-apply-acceptance-0.8.1.md); nie powtarzaj go.
Nowy test sprawdza dwa nowe narzędzia i wybór elementów. Wykonuje tylko odczyty.

1. Użyj tej samej naprawionej, jednorazowej kopii z sześcioma słupami w pliku
   **101**. **S05 = SZ_OGÓ01**, **S06 MCP_QA_STATUS = NEW**. Pozostałe trzy
   usterki oznaczeń pozostają celowo. Nie odbudowuj modelu ani nie przywracaj
   błędnej warstwy/statusu.
2. Zamknij Allplan i poprzednie okno MCP. Rozpakuj cały **0.9.0** do nowego
   folderu, uruchom **Setup.cmd** i wybierz dotychczasowy rzeczywisty `Local`.
   Zachowaj sprawdzony pakiet 0.8.1, jego logi i dziennik napraw.
3. Otwórz tę samą kopię w Allplanie, ustaw plik **101** na pierwszym planie,
   uruchom Library → Private → PythonHost → StartPythonHost oraz
   **Launch Allplan MCP.cmd** z nowego folderu. Nie zmieniaj modelu w UI podczas
   odczytu — poprzedni test pokazał, że taka akcja może przerwać hosta.
4. Uruchom **M3 Standards Preview.cmd**. Program sam odczyta audyt, wskaże
   dokładny model UUID S06 i wykona trzy scenariusze:
   - standard warstwy/statusu w wersji 1.0.0 — **0 proponowanych zmian**;
   - warunek „warstwa 3700” z wyjątkiem S06 — **5 wybranych, 1 wyjątek**;
   - warunek „warstwa inna niż 3700” — **0 wybranych**.
5. Oczekiwane: **ready_for_ui_observation**, wszystkie kroki **OK**, po każdym
   podglądzie `unchanged`, pełny audyt przed/po identyczny i nadal **3 usterki**.
   Każdy plan jest odczytowy; zapis standardu i wybranych planów jest niedostępny.
6. Po zakończeniu sprawdź w UI wartości S05/S06 oraz wygląd pozostałych słupów.
   Wyślij oba pliki `logs/m3-standards-preview-*.json` i `.txt` oraz krótkie
   potwierdzenie, czy model pozostał bez zmian i Allplan/host nadal działają.

Nie uruchamiaj M3 Apply, Recover ani Undo na potrzeby tego testu. Przy BLOCKED
lub przerwaniu hosta zachowaj wynik i zgłoś go, bez automatycznego powtarzania.
[Zakres i granice M3.3](m3-standards-contract.md).
