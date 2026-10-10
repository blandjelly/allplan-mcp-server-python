# M3 — podgląd dwóch oznaczeń i kontrola kolizji, pakiet 0.10.0

Status **ready_for_owner_test**. Test standardów 0.9.0 jest
[zaliczony](test-results/m3-standards-acceptance-0.9.0.md); nie powtarzaj go.
Nowy test tylko odczytuje model i pokazuje propozycje. Nie zapisuje oznaczeń.
[Pakiet i suma kontrolna](../evaluation-packages/0.10.0/README.md).

1. Zachowaj tę samą naprawioną kopię z sześcioma słupami, plik **101**:
   **S05 — SZ_OGÓ01 (Ogólne 1), S06 — NEW**. Pozostaw brakujące oznaczenie
   słupa C03 oraz dwie wartości S02 w C02/C04. Nie odbudowuj modelu i nie używaj Undo.
2. Zamknij Allplan i poprzednie okno MCP. Rozpakuj cały **0.10.0** do nowego
   folderu, uruchom **Setup.cmd** i wskaż ten sam rzeczywisty `Local`.
   Zachowaj starsze pakiety, logi i dziennik wykonanych napraw.
3. Otwórz tę kopię, ustaw **101** na pierwszym planie, uruchom
   Library → Private → PythonHost → StartPythonHost oraz
   **Launch Allplan MCP.cmd** z folderu 0.10.0.
4. Uruchom **M3 Marks Preview.cmd**. Nie edytuj modelu podczas odczytu.
   Program sam odczyta aktualne UUID i wykona trzy podglądy:
   - C03, środek około **(12000, 0, 1500) mm**: `<niezdefiniowany>` → **S03**;
     C04, środek około **(0, 6000, 1500) mm**: **S02 → S04**. Dwie propozycje,
     brak kolizji w hipotetycznym wyniku. Drugi słup z S02 pozostaje bez propozycji.
   - Te same wybory z wyjątkiem C04: tylko **jedna propozycja S03**;
     duplikat S02 pozostaje w hipotetycznym wyniku.
   - Celowa propozycja **S06 na C03**, z istniejącym S06 poza wyborem:
     **conflict**, jedna grupa kolizji wskazująca oba dokładne UUID.
     To oczekiwany poprawny wynik tego kroku.
5. Oczekuj **ready_for_ui_observation** i wszystkich **10 kroków OK**.
   Każdy plan rewaliduje się jako `unchanged` — także plan z wykrytą kolizją,
   bo porównywany jest niezmieniony model. Pełny audyt przed/po nadal ma
   **3 usterki oznaczeń**, a sesja hosta pozostaje ta sama.
6. Po zakończeniu sprawdź w UI, że oznaczenia nie zmieniły się na S03/S04,
   S05 nadal jest na Ogólne 1, S06 nadal ma status NEW, a wygląd pozostałych
   słupów jest taki sam. Prześlij `logs/m3-marks-preview-*.json` i `.txt`
   oraz potwierdź brak zmian i ciągłość hosta.

Nie uruchamiaj Apply, Recover ani Undo na potrzeby tego testu. Przy BLOCKED
lub przerwaniu hosta zachowaj logi i zgłoś wynik bez automatycznego powtarzania.
[Zakres podglądu i kontroli kolizji](m3-marks-contract.md).
