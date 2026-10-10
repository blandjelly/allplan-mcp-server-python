# Nowy test Allplana — oznaczenia i numeracja 0.12.0

Status: **PASS — wykonano 2026-10-10**; [wynik](m3-numbering-acceptance-0.12.0.md).
Nie powtarzaj zakończonej partii. Zostaw i zapisz jednorazową kopię po dwóch Undo:
C03 niezdefiniowany, C04=S02; bez Redo. Poniższe kroki opisują wykonaną partię.

Pierwotny zakres: Wykonaj tylko tę nową partię na Allplanie
2026-1-7, w lokalnym środowisku Windows. Nie powtarzaj zaakceptowanych testów
warstwy/statusu. Test zapisze dane oznaczeń dwóch słupów na jednorazowej kopii.

## Przygotowanie

1. Zachowaj dotychczasowe paczki, logi i Local/.allplan-mcp/repairs. Zamknij
   Allplan i konsolę MCP. Rozpakuj całą nową paczkę 0.12.0 do osobnego folderu.
2. Uruchom Setup.cmd i wskaż ten sam właściwy folder Local. Otwórz oryginalną
   jednorazową kopię projektu testowego, z plikiem 101 na pierwszym planie.
   Nie przenoś dziennika ani identyfikatorów wykonania do innej kopii projektu.
3. Uruchom StartPythonHost z biblioteki Private → PythonHost, a następnie
   Launch Allplan MCP.cmd. Używaj lokalnego Windows Codex, jeśli potrzebna jest pomoc.
4. W modelu C03 ma brakujące oznaczenie, a C02/C04 mają S02. Warstwa C05 i status
   C06 mogą być naprawione albo cofnięte — program odczyta bieżący stan.
   Jeśli oznaczenia są już inne, program zatrzyma się bez zapisu. Nie resetuj
   modelu na podstawie domysłów; przekaż raport.

## Nowy test

1. Uruchom **M3 Numbering.cmd**. Program sprawdzi wersje/integralność, wykona
   pełny audyt, dwa podglądy deterministycznej numeracji i audyt potwierdzający
   brak zmian po podglądzie. Nie używa wcześniejszych wyników jako autoryzacji.
2. Przeczytaj wyświetlony plan. Oczekiwane cele: C03 przy (12000,0) mm,
   `<niezdefiniowany>` → S03; C04 przy (0,6000) mm, S02 → S04. C02 zachowuje S02.
   Jeśli plan i jednorazowa kopia są właściwe, wpisz **NUMERUJ KOPIE** w konsoli.
   Inny tekst anuluje zapis. Nie edytuj modelu podczas planowania/wykonania.
3. Program ponownie sprawdzi plan, zapisze nowy identyfikator przed Apply,
   wykona dwa zapisy z odczytem, sprawdzi cały audytowany zakres, odczyta zapisany
   wynik tym samym identyfikatorem bez ponownych setterów i sprawdzi pusty
   kolejny plan numeracji. Oczekiwany stan: **ready_for_ui_observation**.
   Audyt usuwa dokładnie trzy ustalenia QA-001/QA-002/QA-002. Pozostaje 0–2
   ustaleń warstwy/statusu, zależnie od stanu początkowego.
4. Sprawdź w UI dane oznaczeń C03=S03 i C04=S04, zachowane C02=S02,
   pozostałe oznaczenia, warstwy/statusy, geometrię i brak dodatkowych elementów.
   Zapisz, czy host działał do końca. Ten test zmienia atrybut danych;
   nie wymaga generowania ani przebudowy graficznych etykiet.
5. W tej jednorazowej kopii sprawdź **dwa osobne kroki Undo** dla nowych oznaczeń.
   Zapisz wartości po każdym kroku. Polecenie UI może zakończyć host — to znana
   granica cyklu życia. Wtedy uruchom ponownie StartPythonHost, bez ponownego Apply.
6. Uruchom **M3 Numbering Recover.cmd** w tym samym folderze i projekcie.
   Recover tylko odczytuje bieżące dane. Po pełnym cofnięciu oczekujemy dwóch
   old_value_observed; historyczne applied nie zmienia się w nowe wykonanie.

## Raport i zatrzymanie

Przekaż wynik PASS/FAIL/BLOCKED, obserwacje obu zapisów/Undo, bieżący końcowy
stan modelu i pliki JSON/TXT z folderu logs. Zachowaj również
m3-last-numbering-execution.json oraz m3-numbering-execution-<ID>.json.
Nie trzeba edytować Python/JSON ani wyszukiwać identyfikatorów API.

Po timeout/unknown/stopped przerwij partię, zachowaj logi i użyj wyłącznie
**M3 Numbering Recover.cmd**. Nie uruchamiaj ponownie M3 Numbering.cmd i nie
twórz nowego identyfikatora, żeby powtórzyć niepewny zapis. Nie wykonuj automatycznego
rollbacku. Po rejected z native_setters_started=false ten wniosek nie wymaga Undo.
Po blocked/cancelled bez wysłanego Apply nie wykonano zapisu.
