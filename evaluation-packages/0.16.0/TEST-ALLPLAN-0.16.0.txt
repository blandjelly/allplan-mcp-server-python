# M4 — krótka obserwacja właściwości i podświetlenia, 0.16.0

Status: **ready_for_owner_test**. Docelowa próba: **Allplan 2026-1-7**,
oryginalna kopia **MCP_QA_DEMO** zapisana po Undo. Jest to pierwsza próba K1
i wczesna próba UI K2 z [planu rozwoju](../../docs/office-editing-development-plan.pl.md).
Nie zamyka K1/K2 ani nie włącza nowych zapisów.

## Przygotowanie

1. Pobierz i rozpakuj cały [pakiet 0.16.0](README.md).
   Zachowaj starsze paczki, logi oraz Local/.allplan-mcp/repairs.
2. Zamknij Allplan i starszy serwer MCP, uruchom **Setup.cmd** i wybierz ten sam
   rzeczywisty katalog Local. Setup zachowuje historię napraw; otwórz ponownie Allplan.
3. Otwórz zachowaną kopię MCP_QA_DEMO, uruchom **StartPythonHost** z biblioteki
   i **Launch Allplan MCP.cmd**. Korzystaj z lokalnego Codexa na Windows.
   Nie uruchamiaj starych bramek M3, Redo ani zwykłych poleceń edycji UI podczas próby.

## Obserwacja, bez edycji modelu

1. Uruchom **M4 Properties.cmd**. Program sprawdza wersję/hashes załadowanego hosta,
   odczytuje próbkę właściwości słupów i ściany oraz próbuje rozwiązać dokładne nazwy
   odporności ogniowej i krótką nazwę warstwy W1. Nie tworzy brakujących zasobów.
2. Spójrz na model: wszystkie znalezione słupy/ściany z otwartych plików powinny
   być podświetlone, mimo że pierwsza strona query zawiera tylko jeden element.
   Dla samego rysunku 101 oczekujemy 6 słupów + 1 ściany; dodatkowe otwarte pliki
   mogą rozszerzać wynik i są jawnie wymienione w raporcie. Zgłoś niewidoczne cele osobno.
3. Przekaż lokalnemu Codexowi polecenie: „Przeczytaj najnowszy raport M4 z logs.
   Wskaż odczytane nazwy, typy, jednostki i enumy, właściwe pole odporności ogniowej
   oraz czy W1 ma zgodny odczyt ID/nazwy. Nie zapisuj modelu i nie zgaduj brakujących ID”.
   W razie potrzeby Codex może użyć `model_properties` z dokładną nazwą uzyskaną
   z katalogu. Użytkownik nie wyszukuje numerów atrybutów ani nie pisze JSON/Pythona.
4. Uruchom **M4 Clear Highlight.cmd**. Podświetlenie powinno zniknąć, a MCP dalej
   odpowiadać. Usuwane są wszystkie podświetlenia bieżącego dokumentu, także pochodzące
   z innych źródeł. Wynik API `submitted` wymaga Twojej obserwacji UI.
5. Zwróć oba pliki `logs/m4-properties-check-*.json` i `logs/m4-properties-clear-*.json`
   oraz krótką obserwację według tabeli. Pliki TXT są skrótami; JSON zawiera dowody.

| Obszar | Oczekiwany wynik / sposób raportowania |
| --- | --- |
| Rysunki i zakres | PASS: jawna lista odpowiada otwartym rysunkom; pasywne rozliczone jako odczyt, bez obietnicy edytowalności. |
| Katalog | PASS: próbki słupa/ściany i surowe metadane są czytelne; `not_checked`/ucięcia pozostają jawne. Nie jest to pełny katalog projektu. |
| Odporność ogniowa / W1 | PASS dopiero po jednoznacznym odczycie rzeczywistych zasobów; BLOCKED jeśli nie istnieją, są nieodczytane lub niejednoznaczne. Nie dodawaj ich na potrzeby tej próby. |
| Podświetlenie / usunięcie | PASS: wszystkie widoczne cele z całego wyniku podświetlone i potem wyczyszczone; zgłoś niewidoczne/niepodświetlone oraz FAIL/BLOCKED. |
| Natywne zaznaczenie | **BLOCKED_current_interactor**. Polecenie `select` zwraca unsupported i nie wywołuje UI. Podświetlenie nie oznacza natywnego zaznaczenia ani odbioru tego wymagania. |
| Stan modelu i host | PASS: raporty próbek i geometrii przed/po zgodne, UI bez zmian danych, ten sam host odpowiada po próbie. |

Nazwy „Odporność ogniowa” i „Fire resistance” są wyłącznie kandydatami sprawdzanymi
przez dokładny odczyt nazwy/ID z API. Brak trafienia jednego tłumaczenia nie jest
dowodem braku właściwości w projekcie. Alias semantyczny, rzeczywisty właściciel
i zapisywalność pozostają niepotwierdzone. Brak atrybutu w GetAttributes(ReadAll),
null, pusty tekst, undefined i błąd odczytu nie są automatycznie utożsamiane.

## Zatrzymanie i reset

Jeżeli program zwróci `blocked`/`unknown`, zachowaj raport i obserwuj UI; nie
uruchamia ponownie operacji samodzielnie. Podświetlenie usuń osobnym przyciskiem.
Jeżeli host nie odpowiada, zakończ go ESC i uruchom ponownie z biblioteki;
nowe wyniki query zastępują wygasłe ID. W razie problemu instalacyjnego użyj
**Restore bridge.cmd** przy zamkniętym Allplanie i poprzedniego launchera.
Historia M3 pozostaje w Local. Próba nie wymaga Undo, ponieważ nie wysyła setterów modelu.

Podaj wersję z UI Allplana, listę otwartych rysunków oraz PASS/FAIL/BLOCKED
dla każdego obszaru. `accepted_on_build` można nadać dopiero po sprawdzeniu tych dowodów.
