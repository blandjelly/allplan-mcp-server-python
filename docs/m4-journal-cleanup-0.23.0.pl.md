# 0.23.0 — czyszczenie dziennika po potwierdzeniu

Kandydat dodaje obsługę pełnego śladu diagnostycznego M4 (limit 1 MiB) i
archiwizację rozliczonych wykonań (limit 128 aktywnych rekordów). Czyszczenie
zwalnia aktywny plik/miejsca, zachowując dane w archiwum. Nie usuwa nieznanych
wyników zapisu ani nie ponawia setterów. Archiwa nadal zajmują miejsce na dysku.

1. Zainstaluj 0.23.0 przez `Setup.cmd`, zachowując dzienniki. Uruchom ponownie
   `StartPythonHost` i połączenie MCP. Zachowaj wersję/manifest z `allplan_health`.
2. Poproś agenta: „Sprawdź zapełnienie dziennika M4 i pokaż podgląd czyszczenia”.
   Agent używa `fix_model_issues` → `inspect_journal`, a następnie
   `preview_journal_cleanup` dla właściwego celu (`native_trace` lub
   `repair_records`). Ma pokazać rozmiar/liczbę, zakres archiwizacji i chronione
   wpisy oraz zapytać, czy wyczyścić dziennik. Bez odpowiedzi nic nie archiwizuje.
3. Potwierdź wybrany zakres. Agent wysyła `cleanup_journal` z dokładnym hashem
   podglądu i `confirmed_journal_cleanup`. Nowe wpisy powstałe między podglądem
   a potwierdzeniem wymagają nowego podglądu i potwierdzenia. Sprawdź wynik
   archiwizacji i stan aktywnego dziennika. Nierozliczone wykonania pozostają.
4. Wykonaj jeden nowy podgląd zwykłej zmiany. Do sprawdzenia czyszczenia nie
   potrzeba ponownie zapisywać zaakceptowanych atrybutów słupów/stropów ani
   powtarzać wyszukiwania warstw, podświetlenia i klasy ogniowej.

Jeśli dziennik jest pusty, wynik „nothing_to_archive” jest prawidłowy — nie
zapełniaj go sztucznie w projekcie. Granice rozmiaru/liczby, przerwania, blokady
plików i replay po archiwizacji sprawdzają testy automatyczne. Nowy przepływ
z rzeczywistym hostem wymaga tylko tej krótkiej próby; UI nie powinno się zmienić.

[Raport: co pozostaje do ukończenia M4](m4-completion-status-2026-10-20.pl.md).
