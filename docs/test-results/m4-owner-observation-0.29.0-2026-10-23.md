# Ograniczona obserwacja właściciela 0.29.0 — zbiorowe usunięcie Column

**Data:** 2026-10-23  
**Środowisko zgłoszone w logu:** Allplan 2026.1, aktywny rysunek 101  
**Źródło:** [log testu właściciela](evidence/allplan-test-log-0.29.0-2026-10-23.md)

Właściciel zgłosił **PASS wszystkich kroków próby**: host był osiągalny i
integralność bridge nie wykazała rozbieżności; odczyt wykazał trzy
`Column_TypeUUID` na W1 (ID 65535); przygotowano i potwierdzono plan ich
usunięcia; `DeleteElements` zakończyło się statusem `completed`; świeży skan
potwierdził nieobecność trzech słupów i ich kontenerów atrybutów; jedno Undo w
interfejsie Allplan przywróciło wszystkie trzy słupy. To spełnia cel poprawki
0.29.0: grupowe usunięcie zostało zgłoszone jako jedna operacja cofania.

Log nie zawiera surowych odpowiedzi MCP, UUID celów ani manifestu
zainstalowanego ZIP-a. Undo zgłosił właściciel; narzędzie pozostawiło
`undo: not_checked` i nie wykonało automatycznego readbacku po cofnięciu.
`runtime_verified` i `allplan_acceptance` pozostały niepotwierdzone. Zachowujemy
te granice dowodu bez podważania zgłoszonego PASS próby.

Wynik dotyczy trzech Column w aktywnym rysunku 101 na kopii roboczej. Nie
obejmuje innych rysunków ani nie ustanawia grupowego Undo dla innych typów
operacji. Szczegóły są w dołączonym [logu](evidence/allplan-test-log-0.29.0-2026-10-23.md).
