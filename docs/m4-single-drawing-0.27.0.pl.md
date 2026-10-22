# Krótka próba natywna 0.27.0 — warianty nazwy i diagnostyka materiału

To jest ograniczona próba nowych zachowań, nie odbiór priorytetów 1–5 ani
całego `model_edit`. Użyj dokładnego kandydata 0.27.0 po zakończeniu CI i
builda; zachowaj manifest instalacji, build Allplana, `allplan_health`, surowe
odpowiedzi MCP i ślady. Pracuj na kopii projektu. Nie czyść dzienników. Nie
powtarzaj zaakceptowanych zapisów atrybutów, readbacków ani usunięcia z 0.25.0.
Nie wykonuj zapisu natywnego materiału w tej próbie.

## Zakres

1. **Rozpoznanie `mcp_qa_mark` — tylko odczyt.** Dokładny zapis
   `MCP_QA_MARK` przeszedł wcześniejszą obserwację, więc nie powtarzaj go.
   Wywołaj jeden `model_property_probe phase=attribute_name` z lowercase
   `mcp_qa_mark`. Fast exact lookup pozostaje pierwszym krokiem; tylko
   `ValueError`/`TypeError` lookup miss uruchamia bounded resolver. Zachowaj
   odpowiedź z kanoniczną nazwą `MCP_QA_MARK`, jej ID i roundtrip, jeśli lookup
   zakończy się powodzeniem. Warianty są szczegółem diagnostycznego trace i nie
   należy opisywać ich jako surowych pól odpowiedzi probe. Resolver sprawdza
   ograniczone formy wejścia (podana nazwa, trim/NFC, pierwsza litera wielka,
   całość wielkimi, całość małymi), zbiera poprawne ID i odrzuca rozbieżność.
   Brak wyników nie upoważnia do fuzzy search ani katalogu. Nie wykonuj zapisu.
2. **Materiał Wall — świeże read-only preview dla nowych przypadków.** Dla
   dokładnego, istniejącego celu wykonaj najwyżej jedno preview na obserwację.
   Zachowaj całą odpowiedź, w tym `blocked[].reason`,
   `blocked[].observation.reason` oraz diagnostykę `stage`/`error_type`,
   `criteria.required_field_failures` i
   `criteria.operation_eligibility_failures`. Jeżeli stare `Material` jest
   czytelne, może mieć status `observed` mimo blokady preservation; przy
   `native_material_preservation_unavailable` wymagane pola mogą być kompletne,
   więc lista nieodczytanych wymaganych pól docelowych
   (`required_field_failures`) może być pusta, a blocker materiału ma być
   widoczny w `operation_eligibility_failures`. Błędy predykatu pozostają w
   `report.criterion_failures`; nowa tablica eligibility dotyczy obecnie
   blokad preservation natywnego materiału Wall.

   Sprawdź tylko rozróżnienie: `WindowDoor_TypeUUID` ma dać
   `wall_material_openings_unsupported`; inne typy dzieci, w tym nieznany
   Door/Window/Macro, mają dać `wall_material_child_type_unsupported`.
   Jedyny obsługiwany kształt preservation to dokładnie jeden `WallTier` z
   lineage `[tier, Wall root]` i bez dzieci, przy stabilnej enumeracji. Nie
   wnioskuj z braku diagnostyki, że dziecko jest wspierane, i nie ponawiaj
   preview dla tej samej obserwacji. Odczyt materiału sam w sobie nie spełnia
   warunku preservation ani readbacku po zapisie.

3. **Brakujące odrębne dowody.** Jeśli pozostają niewykonane i są dostępne
   wyznaczone, odrębne cele z bezpiecznej kopii, wykonaj wyłącznie W1 no-op na
   wskazanym niezmienionym celu (potwierdź zero setterów) oraz jeden W1 zapis
   na innym celu, po którym wykonaj dokładnie jedno UI Undo i świeży readback.
   Nie używaj ponownie słupa ani ściany, których wcześniejsze readbacki są już
   przyjęte. Dla nierozstrzygniętej pary Slab/MultiSlab wykonaj wyłącznie
   read-only identity probe dokładnych adapterów, zachowując model/view UUID,
   lineage i typ natywny; nie zapisuj do nich. Te operacje są osobnym brakującym
   zakresem, a nie dowodem nowego kodu materiałowego.

## Wynik i granice

Zapisz każdy wynik jako PASS, BLOCKED albo NOT RUN wraz z dokładnym celem,
manifestem, buildem, odpowiedzią i świeżym odczytem, jeśli dotyczy. Przerwij
dany przypadek przy niejednoznaczności, niekompletności, błędzie odczytu lub
nieznanym wyniku. Nie stosuj setterów do atrybutów ani materiału w punktach 1–2.

Ta próba nie obejmuje journal cleanup, zaakceptowanego usunięcia, ponownych
odczytów ani wcześniejszych zapisów atrybutów; nie zamyka selekcji, pełnego
delete, natywnego materiału, odbioru wszystkich rodzin, dat/wektorów ani
priorytetów 1–5. Daty, wektory i inne obiekty SDK pozostają zablokowane.
