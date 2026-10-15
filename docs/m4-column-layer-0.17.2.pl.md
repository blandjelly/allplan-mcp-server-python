# M4 Columns → W1 — krótka próba 0.17.2

Ta próba sprawdza zmianę semantyki podświetlania i przypadek samych no-opów.
Zakres: pakiet **0.17.2**, Allplan **2026-1-7** (API **2026.1**), zachowana
kopia **MCP_QA_DEMO**, aktywny rysunek **101** i istniejąca warstwa **W1**.
Uruchom ją po przejściu kontroli źródła, CI i pakietu opisanych w
[README pakietu 0.17.2](../evaluation-packages/0.17.2/README.md). Nie powtarzaj
zakończonych bramek M3.

## Scenariusz A: wszystkie dopasowania już na W1

1. Zachowaj kopię modelu po wykonaniu pakietu 0.17.1: Słupy **1, 5 i 6** są na
   **W1**, a **2, 3 i 4** mają klasę **F120**. Zainstaluj pakiet 0.17.2 według
   jego README, uruchom Allplan, PythonHost i MCP. Zachowaj logi oraz
   `Local/.allplan-mcp/repairs`.
2. Uruchom **M4 Columns to W1.cmd** i sprawdź podsumowanie. Oczekuj:
   **highlight targets 3** (Słupy 1, 5, 6), **changes 0**, **no_op 3**,
   **nonmatching 3**. Wszystkie dopasowane Słupy mają być podświetlone, choć
   już są na W1.
3. Zatrzymaj się na podglądzie. Nie wpisuj `ZMIEN`; nie powinno być potwierdzenia
   ani Apply. Uruchom **M4 Clear Highlight.cmd**, sprawdź zniknięcie podświetleń
   i odpowiedź `allplan_health`.

Brak dopasowań oznacza wyczyszczenie podświetlenia. Polecenie czyszczenia
usuwa wszystkie podświetlenia w bieżącym dokumencie, również z innych źródeł.

## Scenariusz B: dwie zmiany i jeden no-op (opcjonalnie)

1. Tylko jeśli chcesz sprawdzić również zapis, przed rozpoczęciem nowego
   podglądu przywróć na kopii **wyłącznie Słupy 5 i 6** do ich wcześniejszej
   warstwy. Nie zmieniaj modelu, gdy istnieje aktywny plan. Jeśli operacja UI
   zakończy PythonHost, uruchom go ponownie i sprawdź jego zdrowie.
2. Uruchom świeży **M4 Columns to W1.cmd**. Oczekuj **highlight targets 3**
   (1, 5, 6), **changes 2** (5, 6), **no_op 1** (1) i **nonmatching 3**
   (2, 3, 4). Podświetlenie obejmuje także Słup 1; lista zmian zawiera tylko
   Słupy 5 i 6.
3. Sprawdź pełną listę dopasowań i osobną listę zmian. Wpisz `ZMIEN` tylko gdy
   plan dokładnie odpowiada powyższemu zakresowi. Sprawdź W1 na Słupach 5 i 6,
   brak zmian w pozostałych polach oraz zachowaną geometrię. Po ponownym
   uruchomieniu oczekuj **highlight targets 3, changes 0, no_op 3**; ponownie
   zatrzymaj się bez `ZMIEN`/Apply.
4. Jeśli wykonano zapis, sprawdź też dotychczas niepotwierdzone natywne Undo:
   po zakończeniu polecenia przywróć Słupy 5 i 6 do poprzednich warstw, zgodnie
   z liczbą kroków Undo pokazaną przez Allplan. Słup 1 pozostaje na W1, a klasy
   F120 na 2, 3 i 4 pozostają bez zmian. Nie zakładamy jednego wspólnego Undo.
   Jeżeli UI zakończy host, uruchom go ponownie; użyj Recover zapisanego
   execution_id wyłącznie do odczytu, bez ponownego Apply.

Natywne Undo dla tej operacji M4 pozostaje niepotwierdzone; wyniki Undo ze
starszych bramek M3 tego nie rozstrzygają. Po utracie odpowiedzi zachowaj
`execution_id` i użyj **M4 Columns Recover.cmd** do odczytu. Nie wysyłaj nowego
Apply. Zwróć `logs/m4-column-layer-*.json` i TXT, `bridge.log` oraz
`Local/.allplan-mcp/logs/m4-native-probe.jsonl`. Podaj PASS/FAIL/BLOCKED dla
podświetlenia 1/5/6, braku zapisów w A, wyczyszczenia i zdrowia hosta; jeśli
wykonano B, również dla listy zmian 5/6, pozostałych danych/geometrii, no-op
i Undo. Ta ograniczona próba nie oznacza akceptacji całego M4.
