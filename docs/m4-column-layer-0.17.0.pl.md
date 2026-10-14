# 0.17.0 — słupy bez odporności ogniowej → podświetlenie → W1

Kandydat do nowej próby natywnej, **nie accepted_on_build**. Użytkownik potwierdził
pełny scenariusz i zaakceptował podświetlenie zamiast natywnego zaznaczenia.
Zakres pierwszej dostawy: natywne Column roots, jeden aktywny rysunek 101 kopii
MCP_QA_DEMO, istniejąca W1, najwyżej 32 zmiany. Nowe narzędzie MCP: `column_layer`.

## Co zmienia ta wersja

0.16.1 była celowo tylko próbą odczytu jednego słupa. Załączony raport z
13.10.2026 21:15 czasu Warszawy zawiera health → column_sample → health,
ten sam host i brak crasha według obserwacji użytkownika. Nie wywołano
rozpoznania nazw, metadanych, podświetlenia ani zapisu.

0.17.0 dodaje osobny przebieg, bez wywołania szerokiego `/model-properties`:

1. Dokładne nazwy pola odporności ogniowej → ID → ta sama nazwa; W1 → ID → W1.
   Brak/niespójność/niejednoznaczność zasobu kończy próbę bez zapisu.
2. Odczyt wszystkich słupów w zadanym rysunku. Puste wartości, null oraz jawne
   teksty `<niezdefiniowany>` / `<undefined>` pasują. R60 i inne wartości nie pasują.
   Nieobecność w ReadAll to **unknown**, ponieważ API pomija pola wyliczane.
   Błąd odczytu, liczbowy/nieobsługiwany typ lub nieznany stan blokuje Apply,
   zamiast zgadywać znaczenie. W raporcie każdy stan pozostaje oddzielny.
3. Plan zmian bez wymyślonych findings audytu. Słupy już na W1 są no-op;
   jawne wyłączenia nie trafiają do podświetlenia ani zapisu.
4. Podświetlenie dokładnie celów planu; ponowny odczyt całego zakresu przed Apply.
5. Wspólny executor M3: kontrole zapisywalności wszystkich celów przed pierwszym
   setterem, write-ahead journal, odczyt po zapisie, porównanie odczytanych pól
   i geometrii obwiedni, brak ponownego zapisu przy replay, tylko odczyt w Recover.

Kontenery natywnej enumeracji pozostają żywe podczas pracy adapterów także
w resolverze zapisu/Recover. Nie są przechowywane w planach JSON.
Nie odczytujemy masowo GetAttributeType/GetAttributeUnit/GetAttributeControlType
ani GetEnumValues. Nowe odczyty nazw mają trwały ślad przed/po wywołaniu;
sprawdzony wcześniej skan M1 jest oznaczony jako jedna granica usługi.

**Przyczyna crasha 0.16.0 nadal nie jest udowodniona**: XML/bridge.log nie zawierały
stosu natywnego ani wyjątku wewnętrznego. Te zmiany usuwają ryzykowną ścieżkę
z nowego scenariusza i poprawiają wykrytą lukę własności adapterów; nie gwarantują
odporności procesu Allplana na błędy natywne. Historyczny FAIL_CRASH pozostaje.

## Krótka próba w Allplanie 2026-1-7

1. Rozpakuj cały pakiet 0.17.0. Zamknij Allplan i stary MCP, uruchom Setup.cmd,
   wybierz rzeczywisty Local. Zachowaj logs i Local/.allplan-mcp/repairs.
2. Otwórz kopię MCP_QA_DEMO zapisaną po Undo, uruchom StartPythonHost i nowy launcher MCP.
3. Uruchom **M4 Columns to W1.cmd**. To nowe zadanie; **M4 Properties.cmd** nadal
   służy wyłącznie do dawnej, pojedynczej próby odczytu.
4. Program pokaże nazwę rozwiązanego pola, ID/nazwę W1 i dokładne cele planu.
   Obserwuj podświetlenie. Wpisanie **ZMIEN** zatwierdza wyświetlony plan na kopii;
   Enter kończy na podglądzie. Nie trzeba pisać JSON ani szukać numerów atrybutów.
   Nie edytuj modelu podczas zatwierdzania aktywnego planu.
5. Sprawdź W1 w UI, brak zmian słupów z ustawioną odpornością, pozostałych pól
   i geometrii. Raport `completed` oznacza zgodność odczytu, nie odbiór UI/Undo.
   Ponowne uruchomienie powinno dać no-op dla już poprawnych słupów.
6. Usuń podświetlenie przez **M4 Clear Highlight.cmd**. Zakończ interaktor ESC,
   wykonaj natywne Undo w liczbie kroków odpowiadającej zmianom, sprawdź stare
   warstwy w UI. Nie zakładamy jednego wspólnego Undo dla całej operacji.
   Po ponownym uruchomieniu hosta użyj **M4 Columns Recover.cmd**, aby odczytać
   pierwotne cele bez zapisów. Zachowaj oryginalną kopię w stanie po Undo.

Jeżeli wynik jest unknown/stopped/verification_failed lub nastąpi crash, nie
uruchamiaj ponownie zadania. Zrestartuj host w tym samym projekcie i użyj Recover.
Launcher zachowuje dokładny execution_id **przed wysłaniem** Apply. Dziennik
blokuje nowy zapis przy nierozliczonej operacji. Historia nie jest kasowana.

Gdy pole ma inną nazwę, lokalny Codex może przekazać w `attribute_names` dokładną
nazwę projektu, po sprawdzeniu znaczenia w UI. Nie podstawiamy innego pola ani
warstwy. Jeżeli W1 nie istnieje, zgłoś to; to wydanie jej nie tworzy.

Zwróć `logs/m4-column-layer-*.json` i TXT, `Local/.allplan-mcp/logs/m4-native-probe.jsonl`
oraz `bridge.log`. Podaj PASS/FAIL/BLOCKED dla: doboru słupów, podświetlenia,
warstwy W1, zachowania innych danych, zdrowia hosta, no-op i Undo.
Ślad JSONL z testu 0.16.1 także pomoże porównać wcześniejsze wywołania.
