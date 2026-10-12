# 0.15.0 — marka C04 z wykluczonym C02 i inspekcja dziennika

Status: **ready_for_owner_test**, bez akceptacji natywnej tego nowego zakresu.
To jeden nowy test `rule_based_edit`, nie powtórzenie zakończonego testu
numerowania ani kontrolowanego przerwania. M3/UAT-05/UAT-06 pozostają otwarte.

## Przygotowanie

Użyj tej samej zachowanej kopii projektu po Undo z zaakceptowanego testu 0.14.1:
C02=S02, C03=`<niezdefiniowany>`, C04=S02; C05 na warstwie konstrukcji,
C06 ze statusem NEW. Plik 101 na pierwszym planie, komplet sześciu kolumn,
audyt: dokładnie 3 uwagi QA-001/QA-002/QA-002. Nie twórz kolejnej kopii,
nie wykonuj Redo i nie uruchamiaj starych testów zapisu.

1. Zachowaj dotychczasowe logi oraz Local/.allplan-mcp/repairs. Zamknij Allplan
   i konsolę MCP. Rozpakuj pełny ZIP 0.15.0 do nowego katalogu.
2. Uruchom Setup.cmd, wskazując ten sam folder Local. Otwórz tę samą kopię
   projektu, ustaw plik 101 i uruchom StartPythonHost.
3. Uruchom Launch Allplan MCP.cmd z nowego pakietu. Korzystaj z lokalnego
   Codex na Windows. Setup nie usuwa dziennika wcześniejszych operacji.

## A — jedna selektywna zmiana

Uruchom **M3 Selected Mark.cmd**. Skrypt sprawdza wersję/integralność, dziennik,
audyt i pełny odczyt kolumn. Plan ma dokładnie jeden cel:
**C04 (0,6000,1500 mm): marka S02 → S04**. Predykat wybiera marki S02,
a C02 (6000,0,1500 mm) jest jawnym wyjątkiem. C03 pozostaje niezdefiniowany.
Pełny model nadal uczestniczy w kontroli kolizji i niezmienności.

Po sprawdzeniu planu wpisz **ZMIEN C04**. Skrypt zapisze nowy identyfikator
przed Apply. Oczekiwany wynik: **ready_for_ui_observation, 13/13 OK**,
jeden applied/readback S04, poprawna pełna weryfikacja, odczytowy replay,
zweryfikowany wpis dziennika, audyt **3 → 1** i tylko C04 zmieniony.
Jedyna pozostająca uwaga to brak marki C03.

W UI potwierdź C04=S04, C02=S02, C03 niezdefiniowany; pozostałe elementy,
warstwy, statusy i geometria bez zmian. Potwierdź dalszą pracę Allplana/hosta.
Nie uruchamiaj ponownie tego testu po zapisaniu identyfikatora.

## B — jedno Undo i końcowy odczyt

Po poprawnym wyniku A wykonaj **jedno Undo w Allplanie**. Jeżeli UI zakończy
hosta, uruchom ponownie StartPythonHost. Uruchom
**M3 Selected Mark Undo Check.cmd** z tego samego katalogu pakietu.
Oczekiwane **ready_for_ui_observation, 6/6 OK**: Recover widzi starą markę S02,
audyt ma ponownie 3 uwagi, cały odczyt sześciu kolumn zgadza się z początkiem,
a historyczny wpis dziennika pozostaje zachowany. Ten krok nie wysyła Apply.
Pozostaw i zapisz tę samą kopię po Undo; zachowaj dziennik i logi.

## Wynik lub blokada

Prześlij JSON/TXT raportów A i B oraz potwierdzenie UI: C04, wykluczony C02,
pozostałe elementy, jedno Undo, działanie hosta i wersja Allplana. Podaj
PASS/FAIL/BLOCKED. Nie edytuj Python/JSON ani identyfikatorów ręcznie.

Jeżeli **nie wysłano Apply**, raport podaje No Apply sent. Zachowaj raport;
nie wykonuj Undo. Jeżeli Apply został rejected przed setterami, raport podaje
native_setters_started=false; również nie wykonuj Undo dla tego żądania.
Dziennik pełny/uszkodzony/nieuzgodniony blokuje nowy zapis; nie usuwaj wpisów.
**M3 Journal.cmd** można uruchomić odczytowo dla diagnozy.

Przy utraconej odpowiedzi, unknown lub błędzie po wysłaniu Apply nie ponawiaj
zapisu i nie twórz nowego ID. Uruchom **M3 Selected Mark Recover.cmd**;
zachowuje oryginalny ID i porównuje pełny stan. Dopiero po poprawnej inspekcji
nowej wartości oraz potwierdzeniu UI wykonaj jedno Undo i część B. Gdy inspekcja
widzi już pełny stan początkowy, nie wykonuj dodatkowego Undo. Przy conflict,
niekompletnym odczycie lub innej zmianie zachowaj model/logi i zgłoś BLOCKED.

Ten test nie potwierdza dowolnych planów 1–32 zmian, innego pliku/projektu,
identyfikacji kopii, grupowego Undo ani odporności na awarię/zanik zasilania.
