# Ograniczona obserwacja właściciela — Allplan 2026.1, log z 22 października 2026

Zachowany [log rozmowy](evidence/log_rozmowy-0.26.0-2026-10-22.md) opisuje
interakcje z Allplanem raportowane dla bridge 0.26.0. Zawiera końcowe odpowiedzi
asystenta, nie surowe odpowiedzi MCP. Nie zawiera manifestu instalacji,
identyfikatora builda Allplana, dokładnego artefaktu ZIP ani dziennika
wykonania/builda. Nie wiązać obserwacji natywnych z dostarczonym pakietem
0.26.0 ani nie traktować ich jako pełnego odbioru tej wersji.

## Ograniczone obserwacje

- Read-only `model_property_probe phase=drawing_identity` dla rysunku 101
  zwrócił 16 wpisów przy `offset=0`, a następnie 10 przy `offset=16`;
  obie strony miały ten sam fingerprint źródła. Odpowiedź zgłosiła
  `scan_complete=true`, `requested_scope_complete=true` i 26 z 26 tożsamości.
  Łącznie 7 wpisów miało status `observed`, a 19 `not_checked`, mimo kompletnej
  enumeracji 26/26 członków zakresu. Jest to ograniczony wynik tego skanu,
  nie dowód widoczności ekranowej, własności pól ani kompletności innych rysunków.
- Read-only query rysunku 101 znalazł dwa komponenty `Wall_TypeUUID` z
  odczytanymi warstwami: `06d71e4d-193b-483e-8a32-344ade3d612c` → ID 0 oraz
  `545bb0a2-a054-4c91-ac6c-ec552d5b0c18` → ID 65535. Skan i zakres zgłoszono
  jako kompletne. Odczyt nie jest zapisem ani próbą W1 no-op/Undo.
- Po rozwiązaniu dokładnej nazwy atrybutu `MCP_QA_MARK` znaleziono słup
  `80211557-a3c1-4ccd-84d9-1274ec533776` z wartością `"2"`. Po potwierdzeniu
  planu na kopii roboczej zmieniono jego warstwę z ID 3700 na W1 (ID 65535);
  odpowiedź zgłosiła odczyt kontrolny nowej wartości. Następnie, po osobnym
  podglądzie i potwierdzeniu, zmieniono warstwę tego samego słupa z W1 na ID 0
  (`STANDARD`), również z odczytem kontrolnym `layer_id = 0`. Są to dwa
  ograniczone zapisy i readbacki jednego celu, nie dowód no-op, Undo, replay,
  recovery ani odbioru warstwy 0 dla innych rodzin.
- Na aktywnym rysunku 101 znaleziono jedną ścianę o grubości 200 mm i wysłano
  jej podświetlenie. Odpowiedź podała `ready_for_owner_test` i wymagała
  obserwacji w widoku. Właściciel potwierdza, że log odpowiada zachowaniu
  Allplana, ale sam log nie zawiera wyniku takiej obserwacji ani liczby
  natywnie zaznaczonych elementów; nie dowodzi widoczności highlightu ani
  programowej selekcji.

## Blokada i niezaobserwowany zakres

- Dla tej ściany nie znaleziono tekstowego atrybutu materiałowego do zmiany;
  wskazano atrybut `Materiał łatwopalny = 1` i natywny materiał `Cegła`.
  Asystent zgłosił, że preview dla natywnego materiału zostało zablokowane
  z powodu przypisanego otworu drzwiowego. Materiał nie został zmieniony
  według logu. Późniejszy zapis tego preview zawiera puste `blocked` i brak
  diagnostyki; bez surowej odpowiedzi MCP nie potwierdza on, że otwór był
  faktyczną przyczyną blokady.
- Na późniejsze żądanie zapisania diagnostyki poprzedniego preview odpowiedź
  podała `blocked: []` i `blocked_observations: []`, `change.old_value` jako
  `observed` z wartością `Cegła`, `old_value_unknown=false`, a
  `criteria.required_field_failures` jako nieujęte w zapisanym wyniku. Zatem
  log nie dostarcza `blocked[].observation.reason` ani pól diagnostycznych
  `stage` / `error_type`, ani wartości `criteria.required_field_failures`.
  Asystent nie ponowił preview. Wcześniejsza odpowiedź przypisała blokadę
  wykrytemu dziecku `Door_TypeUUID`, lecz późniejszy zapis tego samego wyniku
  pokazuje puste `blocked` i `blocked_observations`. Bez surowej odpowiedzi MCP
  przyczyna Door jest niespójnie udokumentowaną deklaracją asystenta, a nie
  potwierdzoną diagnostyką. Nie wyciągać brakujących pól z tego opisu.
- Pierwsze dwie próby rozwiązania nazw `mcp_qa-mark` i `mcp_qa_mark` zwróciły
  `attribute_id: not_checked` z `ValueError`; nie doprowadziły do zapisu.
- Żądanie przeniesienia słupa na ID 1 nie ma w logu końcowej obserwacji.
  Następny cel zmieniono na ID 0; nie przypisywać temu brakującemu żądaniu
  wyniku.
- Nie wykonano W1 no-op ani Undo. Nie testowano delete. Nie zmieniono
  natywnego materiału. Programowa selekcja, widoczność highlightu, replay,
  recovery oraz odbiór pozostałych rodzin i typów pozostają niezaobserwowane.

Ten log nie zamyka priorytetów 1–5 ani bramki odbioru pojedynczego rysunku.
Zachować diagnostyczne blokady i wymagania dotyczące ponownej walidacji,
dziennika, wyniku nieznanego i braku ponawiania setterów po niepewnym wyniku.
