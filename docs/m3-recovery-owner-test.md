# Nowy test Allplana — odzyskiwanie po przerwanym zapisie, 0.14.1

Status: **ready_for_owner_test**, bez akceptacji natywnej. Wykonaj tylko tę
nową partię na zachowanej kopii w Allplanie 2026-1-7. Poprzednich testów
konfliktu, numeracji i warstwy/statusu nie trzeba powtarzać.

Test zapisze **tylko C03: niezdefiniowany → S03** i celowo zatrzyma dalszą
część wykonania. **C04 pozostanie S02**. Potem sprawdzimy odzyskiwanie po
restarcie hosta oraz jedno Undo. Program nie wywołuje awarii Allplana.
Nie edytujesz Python/JSON ani dziennika.

## Ponowienie po blokadzie 0.14.0

Raport z 2026-10-11T21:57:26Z zakończył się na `numbering_preview`, przed
wysłaniem Apply i przed utworzeniem ID wykonania. Przyczyną była kolejność
C04/C03 zależna od UUID, mimo poprawnych propozycji S04/S03. **W tej próbie
nie wykonano zapisu; nie używaj Undo.** Zachowaj te logi. Zainstaluj nową
paczkę 0.14.1 zgodnie z punktami 1–3 i wykonaj część A od początku na tej
samej niezmienionej kopii. Nie przenoś starych logów do nowego folderu paczki.
Dziennik Local pozostaje w tym samym miejscu. Nie czyść żadnego dziennika
ani zapisanych ID. To ponowienie dotyczy wyłącznie potwierdzonej blokady
przed Apply; dla `unknown` lub istniejącego ID obowiązuje inspekcja.

## Przygotowanie

1. Zostaw tę samą jednorazową kopię po ostatnim Undo i zapisz ją.
   C03 ma być niezdefiniowany, C04/C02=S02; C05 warstwa struktury, C06=NEW.
   Zachowaj starsze paczki, logi i `Local/.allplan-mcp/repairs`. Bez Redo.
2. Zamknij Allplan i konsolę MCP. Rozpakuj całą paczkę **0.14.1** do nowego
   folderu. Uruchom **Setup.cmd**, wskazując ten sam właściwy folder Local.
   Nie usuwaj ani nie przenoś dziennika do innej kopii projektu.
3. Otwórz tę samą kopię i plik **101** na pierwszym planie. Uruchom
   **StartPythonHost** z Private → PythonHost oraz **Launch Allplan MCP.cmd**.
   Konsolę MCP zostaw otwartą przez wszystkie trzy części.

## Część A — jeden zapis i kontrolowane zatrzymanie

4. Uruchom **M3 Recovery Test.cmd**. Program sprawdza wersję, integralność,
   audyt trzech usterek oznaczeń i pełny odczyt sześciu słupów.
5. Zobaczysz plan C03 → S03 oraz C04 → S04. To plan służący sprawdzeniu
   przerwania: **ten test wykona tylko pierwszy zapis C03**, a C04 pominie.
   Jeśli cele i kopia się zgadzają, wpisz **SPRAWDZ ODZYSKIWANIE**.
   Inny tekst anuluje test przed zapisem.
6. Oczekujemy **awaiting_host_restart**, **13/13 OK**. C03=S03,
   C04/C02=S02, dwie pozostałe usterki oznaczeń. Nie wykonuj jeszcze Undo.
   Nie edytuj modelu ani nie uruchamiaj innych napraw podczas części konsolowej.

## Część B — restart hosta i inspekcja

7. Dopiero po zakończeniu części A zakończ StartPythonHost przez **ESC**,
   a następnie uruchom go ponownie z Library w tym samym projekcie/pliku.
   Nie zamykaj projektu i nie wykonuj Undo. Oczekujemy nowej sesji hosta.
8. Uruchom **M3 Recovery Inspect.cmd**. Nie uruchamiaj ponownie Test.cmd.
   Oczekujemy **ready_for_ui_observation**, **6/6 OK**: odzyskany zapis C03,
   C04 nadal pominięty, dwie usterki; inspekcja nie zmienia modelu.
9. Sprawdź UI: C03=S03, C04/C02=S02; pozostałe oznaczenia, statusy, warstwy,
   geometria i inne elementy bez zmian. Potwierdź, że Allplan działa i host
   działał bez przerwania w każdej części konsolowej. Restart w punkcie 7 był
   zamierzony.

## Część C — jedno Undo i końcowy odczyt

10. Wykonaj **jedno natywne Undo**. Ma przywrócić C03 do niezdefiniowanego;
    C04/C02 pozostają S02, naprawy C05/C06 pozostają zachowane.
    Jeśli Undo zakończyło hosta, uruchom StartPythonHost ponownie.
11. Uruchom **M3 Recovery Undo Check.cmd**. Oczekujemy
    **ready_for_ui_observation**, **6/6 OK**: obie stare wartości, trzy usterki
    i pełny odczyt zgodny ze stanem początkowym. Program nie ponawia zapisu.
12. Zostaw i zapisz tę samą kopię **po Undo**. Bez Redo i kolejnego Apply.

Prześlij JSON/TXT z trzech części (`logs/m3-recovery-check-*`,
`logs/m3-recovery-recover-*`, `logs/m3-recovery-undo-check-*`),
`logs/m3-last-recovery-execution.json/.txt` i
`logs/m3-recovery-execution-<ID>.json/.txt`. Dopisz wynik UI, brak innych zmian,
przebieg restartu i Undo. Przy błędzie dołącz wszystkie zapisane raporty.

## Zatrzymanie lub utracona odpowiedź

Jeśli część A ma **unknown**, nie uruchamiaj jej ponownie. Zachowaj stan
projektu, logi i dziennik; bez Undo do czasu inspekcji. Po restarcie hosta użyj
**M3 Recovery Inspect.cmd** z tej samej paczki. Nie zmieniaj ID i nie wysyłaj
nowego Apply. Jeżeli inspekcja zgłasza osobną nierozstrzygniętą próbę blokady,
prześlij raporty do lokalnego Codexa; zachowano dwa różne ID.

Jeśli wynik to **rejected**, żądanie odrzucono przed zapisem. Zachowaj raport;
inspekcja nie wyśle wtedy Recover, bo nie powstał zapis.

Jeśli wynik to **blocked**, kontrola wstępna lub dane nie spełniają warunków,
zatrzymaj się i prześlij raporty. Komunikat **No Apply sent** i
`native_setters_started=false` oznaczają blokadę przed wysłaniem zapisu.
Po usunięciu przyczyny taką próbę można powtórzyć, jeśli nie utworzono ID
wykonania; potwierdzony przypadek 0.14.0 opisano wyżej. Nie czyść dziennika ani nie
naprawiaj ręcznie fixture, żeby wymusić PASS. Inspekcję można powtórzyć po
rozwiązaniu problemu połączenia. Po utworzeniu ID wykonania zapisującego
Test.cmd nie powtarzamy.

Test dotyczy kontrolowanego przerwania po jednym zapisie. Nie potwierdza
odporności na awarię procesu/zasilania ani grupowego Undo wielu zapisów.
M3/UAT-05/UAT-06 pozostają otwarte do zarejestrowania dalszej akceptacji.
