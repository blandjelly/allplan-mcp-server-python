# Obserwacja właściciela — Allplan 2026.1, 0.24.0, 21 października 2026

Właściciel potwierdza, że działania opisane w zachowanym
[logu rozmowy](evidence/log_rozmowy-2026-10-21.md) odpowiadały zachowaniu
Allplana podczas pracy z wersją 0.24.0. Log jest źródłem obserwacji; nie
zawiera manifestu instalacji ani surowych odpowiedzi narzędzi dla wszystkich
operacji.

## Obserwacje

- `model_query` znalazł warstwę `Slab_TypeUUID` i agregat
  `MultiSlab_TypeUUID`. Odczyt `component_identity` dla pierwszego wyniku
  zwrócił `probe_scope_unavailable`. Odczyt drugiego pokazał płytę potomną i
  natywną reprezentację `SlabElement`; view UUID płyty potomnej różnił się od
  view UUID warstwy zwróconej przez zapytanie. Nie rozstrzygnięto, czy są to
  odrębne cele, ani nie wykonano zapisu do nich.
- Prośba o zaznaczenie stropów zakończyła się jawną informacją, że dostępne
  narzędzie Allplan nie obsługuje programowego zaznaczania. Polecenie
  podświetlenia zostało wysłane ze stanem `submitted`; widocznego efektu nie
  potwierdzono. To nie jest odbiór natywnej selekcji ani podświetlenia.
- Zapis warstwy W1 dla słupa w punkcie `(12000, 6000 mm)` został odczytany jako
  warstwa ID `65535`. Log nie dokumentuje próby no-op ani Undo; te części W1
  pozostają nieobserwowane.
- Zapis atrybutu `Klasa odporności ogniowej = REI120` na ścianie został
  potwierdzony odczytem. To jest zapis atrybutu, nie zmiana natywnego
  materiału.
- Słup z `MCP_QA_MARK=6` usunięto w interfejsie rozmowy/Allplana po
  potwierdzeniu właściciela. Kolejny odczyt wykazał zero pasujących słupów.
  Dowodzi to, że obiekt był usuwalny w tej sesji przez użyty przepływ UI;
  log nie wykazuje istnienia typowanego narzędzia MCP do usuwania ani jego
  semantyki, rewalidacji, dziennika czy Undo.

Nie wykonano próby natywnej zmiany materiału, kompletnej próby wszystkich
rodzin, no-op/Undo dla W1 ani zapisu do wyników Slab/MultiSlab. Nie rozszerzać
zakresu PASS poza wymienione obserwacje.
