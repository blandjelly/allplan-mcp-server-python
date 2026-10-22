# Obserwacja właściciela — Allplan 2026.1, próba 0.25.0, 22 października 2026

Właściciel potwierdza, że zachowany [log rozmowy](evidence/log_rozmowy-2026-10-22.md)
odpowiada rzeczywistemu zachowaniu Allplana podczas próby z 0.25.0. Log
zawiera odpowiedzi asystenta, ale nie surowe odpowiedzi MCP ani dokładny
manifest instalacji i identyfikator builda Allplana. Nie przypisywać obserwacji
do konkretnego ZIP/builda ani nie traktować ich jako pełnego odbioru.

## Ograniczone obserwacje PASS

- `component_identity` dla wcześniej wskazanej ściany w rysunku 101 zwrócił
  `WallElement` jako root oraz warstwę ściany i kontener atrybutów jako dzieci.
  Właściciel właściwości nadal nieustalony; model nie został zmieniony.
- `component_identity` dla wcześniej wskazanego stropu zwrócił
  `MultiSlab_TypeUUID` jako root, natywną reprezentację `SlabElement` oraz
  warstwę płyty i kontener atrybutów jako bezpośrednie dzieci. Właściciel
  właściwości nadal nieustalony; model nie został zmieniony. Odczyt jest PASS
  dla tego dokładnego probe, nie rozstrzyga tożsamości/własności innych wyników
  Slab/MultiSlab ani nie potwierdza, że wcześniejszy nieudany probe 0.24.0 miał
  tę samą przyczynę.
- Po potwierdzeniu planu na kopii roboczej usunięto jedną pozostałą ścianę w
  rysunku 101 wraz z jej elementami podrzędnymi. Świeży kompletny skan zgłosił
  usunięte elementy jako nieobecne, a ścianę z otworem drzwiowym jako nadal
  obecną. To potwierdza wynik operacji w tej sesji, ale brak manifestu i
  surowej odpowiedzi nie wiąże go z dokładnym artefaktem ani nie potwierdza
  wszystkich kontraktów typowanego delete (np. Undo, replay czy recovery).
- Zmieniono warstwę ściany 200 mm z otworem drzwiowym z ID 3702 na W1 (ID
  65535); odpowiedź odnotowała readback W1 na ścianie i brak zmiany drugiej
  ściany. Zakres dotyczy jednego celu i odczytu po zapisie.
- Read-only query aktywnego rysunku 101 zgłosił kompletny skan 26 identyfikatorów
  bez pominięć. To historyczny odczyt; nie stanowi odbioru kompletności innych
  rysunków ani własności wszystkich adapterów.

## Blokady i zakres nieuruchomiony

- Usunięcie otworu drzwiowego zostało zablokowane, bo dostępna operacja nie
  rozpoznała go jako samodzielnego celu. Osobny plan usunięcia ściany z tym
  otworem został zablokowany przez `delete_ownership_unavailable`; nie
  usuwaj otworu pośrednio przez tę ścianę.
- Próba natywnego materiału i kreskowania nie wprowadziła zmian: odczytano
  „Beton” na ścianie 240 mm, ale plan materiału zablokowano z powodu braku
  wartości wymaganej do bezpiecznej edycji; nie znaleziono obsługiwanego
  atrybutu kreskowania 129.
- Przeniesienie wszystkich ścian na W1 zablokował `repair_conflict` przy
  odczycie obecnej warstwy ściany 240 mm. Tylko wskazana osobno ściana 200 mm
  została przeniesiona.
- W logu nie ma próby no-op ani Undo dla W1; ten zakres pozostaje niezaobserwowany.
  Nie odtwarzać go na wcześniej zmienionej ścianie jako ekwiwalentu testu W1
  dla słupa.
- Programowe zaznaczanie natywne nie jest obsługiwane przez dostępne narzędzie.
  Log nie potwierdza widocznego skutku highlightu.

Log nie dowodzi pełnego odbioru natywnego 0.25.0, bezpiecznego usuwania
niezależnego `WindowDoor_TypeUUID`, natywnego materiału Wall, wszystkich rodzin,
selekcji, warstw 0, no-op/Undo ani priorytetów 1–5. Zachować istniejące blokady
wobec niepewnej własności, nie ponawiać zapisu po wyniku nieznanym i kontynuować
wyłącznie pozostałe, jawnie ograniczone punkty planu.
