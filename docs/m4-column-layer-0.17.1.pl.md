# 0.17.1 — właściwa klasa odporności ogniowej → podświetlenie → W1

Kandydat do próby w Allplanie **2026-1-7**, bez odbioru natywnego.
Wyniki testów źródła, CI i weryfikacji nowego pakietu są zapisane w [pakiecie 0.17.1](../evaluation-packages/0.17.1/README.md).

Wersja 0.17.0 wybrała inne pole: **Odporność ogniowa**, ID **1398**.
Raport użytkownika z **15.10.2026, 19:40 Europe/Warsaw** zawiera sześć stanów
unknown, ponieważ tego ID nie było w odpowiedziach ReadAll słupów. Próba zakończyła
się **BLOCKED**, przed podświetleniem, Apply i setterami. Blokada zapisu zadziałała,
ale rozpoznane pole nie odpowiadało żądanemu kryterium. `health_before` był zdrowy,
dziennik dostępny z siedmioma rekordami i bez blokad. Brak `health_after` nie pozwala
potwierdzić zdrowia hosta przez cały przebieg ani po nim.
[Oryginalny JSON](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.json),
[oryginalny TXT](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.txt).

Użytkownik potwierdził nazwę **Klasa odporności ogniowej** i wartości F30/F60.
0.17.1 sprawdza dokładne nazwy `Klasa odporności ogniowej` /
`Fire resistance classification`, a następnie zgodność ID → nazwa. Nie wraca do
1398 i nie podstawia na sztywno 935. Oficjalna
[lista Allplan 2026-1](https://help.allplan.com/Allplan/2026-1/1034/Allplan/326206.htm)
opisuje 935 jako Fire resistance classification, String, a
[przykład SDK](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/BasisExamples/MacroWithElementGroup.py#L164)
przypisuje mu F30. [Podręcznik API](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
używa 1398 jako Fire risk factor z A1/A2 — to inne pole.

Odczyt pozostaje ReadAll. Pusta wartość, null oraz jawne `<niezdefiniowany>` /
`<undefined>` pasują; F30, F60 i inne ustawione wartości nie pasują. Faktyczny brak
pola w ReadAll nadal oznacza unknown i blokuje Apply, podobnie jak błąd odczytu
lub nieobsługiwany typ. Nie dodajemy odczytów wyliczanych ani masowych metadanych.
Szeroka ścieżka 0.16.0 pozostaje zablokowana po crashu; jego przyczyna nadal nie
jest udowodniona. Przenoszenie na W1 nie jest zapisem klasy odporności ogniowej.

## Krótka próba

1. Rozpakuj cały pakiet **0.17.1**. Zamknij Allplan i stary MCP, uruchom
   **Setup.cmd**, wybierz rzeczywisty Local. Zachowaj logs oraz
   Local/.allplan-mcp/repairs.
2. Otwórz zachowaną kopię **MCP_QA_DEMO** po Undo, z aktywnym rysunkiem **101**
   i istniejącą **W1**. Uruchom **StartPythonHost** i nowy launcher MCP.
3. Uruchom **M4 Columns to W1.cmd**. Sprawdź wyświetloną nazwę i ID pola:
   ma to być **Klasa odporności ogniowej**, nie Odporność ogniowa/1398.
   Słupy z F30/F60 muszą mieć wynik niepasujący i pozostać poza celami zmian.
4. Sprawdź dokładne cele oraz podświetlenie. Dotychczasowy przepływ pozostaje:
   wpisanie **ZMIEN** zatwierdza pokazany plan na kopii; Enter kończy na podglądzie.
   Słupy już na W1 są no-op. Nie edytuj modelu przy aktywnym planie.
5. Sprawdź warstwę W1 w UI, pozostałe dane i geometrię, no-op przy ponownym
   uruchomieniu oraz natywne Undo. **M4 Clear Highlight.cmd** usuwa podświetlenie.
   Po utracie odpowiedzi zachowaj execution_id i użyj **M4 Columns Recover.cmd**
   do odczytu; nie wysyłaj nowego Apply. Nie zakładamy jednego wspólnego Undo.

Jeżeli poprawnej nazwy nie uda się rozwiązać albo pole rzeczywiście nie występuje
w ReadAll, zwróć raport z nazwą, ID i stanami kryterium. Nie podstawiaj innego pola.
Zakres pozostaje ograniczony do natywnych Column roots w jednym aktywnym rysunku,
istniejącej W1 i najwyżej 32 zmian, ze wspólnym executorem/dziennikiem M3.
Nie ma nowego odbioru zapisów, natywnego zaznaczenia ani odporności na crash.

Zwróć `logs/m4-column-layer-*.json` i TXT, `bridge.log` oraz
`Local/.allplan-mcp/logs/m4-native-probe.jsonl`. Podaj PASS/FAIL/BLOCKED dla nazwy
pola, doboru słupów, podświetlenia, W1, zachowania innych danych, zdrowia hosta,
no-op i Undo. Historyczny pakiet i instrukcja 0.17.0 pozostają bez zmian.
