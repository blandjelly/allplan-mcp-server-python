# Krótka próba natywna 0.26.0 — inwentarz, warstwa 0 i diagnostyka

Użyj wyłącznie dokładnego pakietu 0.26.0 po CI i zachowaj manifest instalacji,
build Allplana, `allplan_health`, całe odpowiedzi MCP oraz ślady. Pracuj na
kopii projektu. Nie czyść dzienników. Wyniki natywne zapisuj osobno od CI.
Ta próba nie odbiera całych priorytetów 1–5.

## Status priorytetów 1–5

1. **Ograniczony PASS już przyjęty.** Zachowaj wcześniejsze wyniki właściciela
   i nie powtarzaj zaakceptowanych zakresów. Odbiór pozostaje ograniczony do
   konkretnych obserwacji; nie dowodzi kompletności edycji biurowej.
2. **Inwentarz tożsamości, nie właściciel pola.** Nowy odczyt rysunku
   dokumentuje model/view UUID, lineage i typ natywny zaenumerowanych przez API
   adapterów. Widoczność ekranowa pozostaje `not_checked`; odczyt nie ustala
   właściciela właściwości ani równoważności Slab/MultiSlab.
3. **Odczyt warstwy 0 — naprawa automatyczna, bez nowego natywnego PASS.**
   Implementacja powinna poprawnie traktować ID 0 jako legalne (zakres
   0–65535), zachowując W1 jako dodatnie ID. Właściciel wykonuje tu tylko
   brakujący no-op/Undo dla W1; nie powtarza readbacku ściany 200 mm.
4. **Selekcja, delete i materiał pozostają osobnymi stanami.** Selekcja natywna
   jest nieobsługiwana; oficjalne API 2026 opisuje wybór użytkownika, nie
   ustawienie selekcji wyniku query. Usunięcie ma ograniczony PASS dla jednego
   poddrzewa, bez pełnego odbioru typowanego kontraktu.
5. **Daty/wektory/inne obiekty pozostają jawnie nieobsługiwane.** Brakuje
   dokładnego payloadu/settera dla istniejącego adaptera i jego świeżego
   readbacku; sama reprezentacja SDK lub dokumentacja typu nie wystarcza.

## Próba

1. **Inwentarz tożsamości — read-only, dokładny rysunek 101.** Wywołaj
   `model_property_probe` z `phase=drawing_identity`, `drawing_file=101`,
   `offset=0`, `limit=16`. Każda kolejna strona wykonuje nowy scan; zachowaj
   offsety, fingerprint i kompletność, używając kolejnych offsetów do końca
   (maksymalny `limit=32`). Czytający porównuje fingerprinty stron; są one
   wskazówką `membership/type/state`, nie gwarancją atomowej hierarchii. Przy
   różnicy fingerprintów przerwij i zapisz drift.
   Oczekiwane pola to para `(entry.ref.model_uuid, entry.view_uuid)` jako
   dokładna tożsamość, ograniczona lineage i reprezentowany native type każdego
   adaptera zwróconego przez API; samo `ref` nie wystarcza. Widoczność ekranowa
   jest `not_checked`. Bez zmian modelu między stronami. Zapisz pominięcia i błędy;
   inwentarz nie ustala własności właściwości.
2. **Warstwa 0 — read-only.** `model_query` obsługuje
   `component_kind=semantic_component`, `layer_resolution=component`,
   `fields=[layer_id]` i predykat `type_name eq Wall_TypeUUID` dla rysunku 101.
   Żądanie ma postać:

   ```json
   {"action":"query","scope":{"drawing_files":[101],"include_passive":false,"visibility":"api_select_all"},"component_kind":"semantic_component","layer_resolution":"component","fields":["layer_id"],"predicate":{"field":"type_name","op":"eq","value":"Wall_TypeUUID"}}
   ```

   Zachowaj wynik `observed` z `layer_id=0`; potwierdza on odczyt legalnego ID 0
   przez component resolution. Nie zapisuj ID 0. Testy automatyczne pokrywają
   pełny zakres 0–65535.
3. **Brakujące W1 no-op/Undo — jawne, odrębne cele.** Nie powtarzaj W1
   readbacku ściany 200 mm (3702 → 65535) ani wcześniej zaakceptowanych
   atrybutów. Na jawnie wskazanym, niezmienianym słupie sprawdź preview bez
   zmiany i potwierdź `no_op` oraz zero setterów. Na innym, odwracalnym słupie
   z kopii wykonaj jedną zmianę na istniejące W1 przez zwykły
   preview/highlight/revalidate/Apply. Zapisz stare i nowe ID, wykonaj jedno
   UI Undo i świeżym odczytem potwierdź powrót do starego ID. Ogranicz wynik do
   tych celów i operacji.
4. **Nowa diagnostyka — jeden read-only preview na dokładny cel.** Dla
   istniejącego, wcześniej zablokowanego celu opening lub Wall wykonaj jeden
   świeży `model_edit preview`; Apply nie jest wymagany. Zachowaj
   `blocked[].observation.reason` i `blocked[].observation.diagnostic`
   (`stage`, `error_type`). Dla materiału zapisz też
   `criteria.required_field_failures`, zwłaszcza gdy `old_value_unknown`.
   Dla delete zapisz diagnostykę w `blocked[].observation`. Nie zmieniaj celu
   ani nie omijaj blokady; nie ponawiaj preview dla tej samej obserwacji.

Konflikt, niekompletny odczyt, nieznany wynik lub zmiana celu kończy daną
próbę. Nie wykonuj zapisu do dat, wektorów ani innych obiektów SDK. Ta próba
nie zamyka całych priorytetów 1–5, pełnej macierzy rodzin, native selection,
natywnego materiału ani typowanego usuwania.
