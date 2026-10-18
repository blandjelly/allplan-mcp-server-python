# M4 0.21.0 — krótka próba Wartości U, atrybutu Materiał i warstwy ściany

[Zweryfikowana paczka 0.21.0, CI i instalacja](../evaluation-packages/0.21.0/README.md).

Nowa ścieżka `model_edit` i faza `element_attributes` wymagają ograniczonej
próby właściciela w kopii projektu. Natywna akceptacja pozostaje `not_run`.
Log agenta z 2026-10-18 opisuje podglądy Wartości U i atrybutu Materiał oraz
zablokowaną próbę warstwy ściany, ale nie zawiera surowych żądań/odpowiedzi,
wersji zainstalowanej paczki ani planów. Ustala zakres do sprawdzenia, nie
potwierdza zachowania konkretnego buildu. Nie powtarzaj historycznych prób
odporności ogniowej, query, podświetlania ani zaakceptowanych odczytów.

## Przygotowanie

Użyj dostarczonego kandydata 0.21.0 w tej samej kopii testowej i jednym aktywnym
rysunku foreground. Zapisz wersję/build, `health` przed i po, surowe odpowiedzi
MCP, plany, wyniki Apply/recover oraz obserwacje UI. Każdy zapis wymaga
potwierdzonego `plan_id`/`plan_hash`, podświetlenia, świeżej rewalidacji,
`disposable_copy_reviewed_plan` i nowego UUID4 hex `execution_id`, zapisanego
przed wysłaniem. Utraconej odpowiedzi nie ponawiaj: użyj read-only recover z tym
samym ID.

W odpowiedzi `model_edit` kieruj się `apply_available` i zwróconym
`next_action`. `evaluation_apply_available` jest aliasem; produkcyjny zapis
pozostaje niedostępny, a brak natywnej akceptacji sam w sobie nie blokuje
kwalifikującego się Apply w tej ścieżce ewaluacyjnej. Nie przedstawiaj wyniku
eksperymentalnego jako natywnie zaakceptowanego. Jeśli odpowiedź podaje
`write_blockers` albo wymagane kroki nie są spełnione, zatrzymaj się i zapisz
konkretny powód.

## Ograniczone scenariusze

1. **Odczyt atrybutów.** Dla jednej ściany uzyskaj dokładne `drawing_file`,
   `model_uuid` i `view_uuid` z bieżącego rysunku. Uruchom
   `model_property_probe` z fazą `element_attributes`, `name_contains` równym
   `Wartość U` lub `Materiał` i domyślną stroną. Sprawdź wartości, dokładne
   nazwy/ID, roundtrip i `supported_scalar_value_types`. Zapisz też
   `metadata_complete`, `listing_complete`, `total_matches_status` oraz
   `writable`. Jeśli metadane są niepełne, nie traktuj listy jako pełnej; brak
   z `ReadAll` nie dowodzi nieobecności ani prawa zapisu.
2. **Wartość U.** Wybierz jedną ścianę z odczytaną dokładną nazwą *Wartość U*.
   Przygotuj `model_edit` ustawiający liczbę `0.2`; domyślne
   `value_type=auto` ma rozpoznać typ związanego atrybutu. Dla dokładnej starej
   wartości `<niezdefiniowany>` plan powinien zachować surowy tekst i oznaczyć
   stan jako undefined; nie konwertuj tekstu `0,2` ani innych wartości. Zastosuj
   wyłącznie plan kwalifikujący się do Apply i sprawdź UI oraz świeży readback.
   Jeśli wartość już wynosi `0.2`, nie wymuszaj zapisu.
3. **Jawny atrybut Materiał.** Na tej samej lub drugiej wskazanej ścianie ustaw
   dokładny atrybut projektu *Materiał* na tekst `bloczki gazobetonowe`.
   Weryfikuj nazwę i typ; użyj `upsert` z `all_and_computable`, jeśli trzeba
   udowodnić brak przed dodaniem. To atrybut użytkownika, nie natywny
   `WallTierProperties.Material` ani warstwa. Nie zastępuj go podobnym polem;
   jeśli dokładne wiązanie lub typ nie są potwierdzone, nie zapisuj.
4. **Warstwa ściany.** Użyj kryterium `wall.total_thickness_mm < 240` i
   istniejącej warstwy `W1`, bez ręcznego przekazywania UUID z osobnego
   wyszukiwania. Potwierdź, że ściana 200 mm i jej bezpośrednie części są
   celami, ściana 240 mm nie jest celem, a części odczytują `W1` po zapisie.
   Sprawdź UI, zakres Undo i zdrowie hosta.

Jeśli kopia testowa ma już znany atrybut wyliczeniowy, którego dokładna etykieta
jest widoczna w UI, można dodatkowo sprawdzić jawny `value_type=enum` na jednym
elemencie. Agent rozwiązuje nazwę z bieżącego dokumentu; używa istniejącej
etykiety. Nie prosi operatora o zgadywanie ID/nazwy ani nie generuje katalogu
wartości. Sprawdź
roundtrip etykiety, zastosowanie, UI i readback. Jeśli takiego pola nie ma,
pomiń tę próbę bez zastępowania jej innym typem.

Każdy zapis jest osobną próbą; nie łącz ich w niejawny batch.
Zachowaj raport nawet po blokadzie albo konflikcie. Wyniki przenośnych testów i
sam opis API nie ustanawiają natywnej akceptacji. W raporcie końcowym podaj
status natywny `PASS`, `BLOCKED` albo `FAIL` dla dokładnego builda i wymienionej
próby; pozostałe scenariusze pozostają `not_run`.
