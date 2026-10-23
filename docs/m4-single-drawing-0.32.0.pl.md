# Krótka próba native material — 0.32.0

Zakres obejmuje wyłącznie ponowną próbę istniejącej ścieżki materiału Wall
240 mm z sesji 0.31.0. Użyj kopii projektu i tego samego żądanego materiału
`Silikat`. Zapisz dokładny manifest i checksumę zainstalowanego kandydata,
build Allplana, `allplan_health`, aktywny rysunek, requesty i surowe odpowiedzi
MCP. Nie przypisuj wyniku do ZIP-a bez potwierdzenia instalacji.

Nie powtarzaj accepted Enum, scalar, journal ani grouped Column delete/Undo
prób. Boolean/CheckBox ma tylko zapisany readback po Undo bez surowego dowodu
Apply; nie powtarzaj tego readu jako accepted trial. Nie testuj Wall 200 mm z opening:
`component_child_owner_mismatch` pozostaje osobnym, nierozwiązanym przypadkiem.

1. Świeżo odczytaj Wall 240 mm, jego dokładny tier, materiał i zachowywane
   właściwości. Zapisz drawing/model/view UUID Wall i tier oraz rzeczywisty
   view UUID parenta tieru.
2. Wykonaj jeden guarded preview. Jeśli jest zablokowany, nie wykonuj Apply.
   Zachowaj pierwszy `reason`, `diagnostic.stage`, `error_type` oraz całe
   obecne `diagnostic.evidence`, target identities, `changes`,
   `usable_for_write` i `setter_calls_started`. Dla Wall i dokładnego tieru
   wykonaj `component_identity`, aby ustalić ich świeżą tożsamość i
   hierarchię. Zapisz `BLOCKED` albo `fixture_missing`.
3. Jeśli preview kwalifikuje się do zapisu, sprawdź dokładny target binding,
   pełny snapshot preservation, `apply_available=true`, highlight i fresh
   revalidation. Potwierdź, że parent-wrapper jest zachowany oraz tier ma tylko
   dozwolone, poprawnie powiązane `AttributeContainer` liście; snapshot
   wartości nie ustanawia właściciela pola ani zapisu atrybutów.
4. Tylko dla niezmienionego, kwalifikującego się planu wykonaj jeden Apply,
   świeży readback materiału i preservation state, jedno UI Undo oraz świeży
   readback przywróconego stanu. Przy wyniku unknown nie ponawiaj Apply; użyj
   tego samego execution ID i recovery.

Kandydat dopuszcza bezpośrednie tier `AttributeContainer` liście wyłącznie jako
bounded preservation evidence. Szczegóły i pozostałe blokady opisuje
[notatka API 0.32.0](m4-editing-api-0.32.0.md). Próba obejmuje tylko tę jedną
Wall material ścieżkę; nie zamyka priorytetów 1–5 ani native acceptance
szerszej rodziny przypadków. Bounded identity evidence może pomóc w osobnym,
read-only sprawdzeniu 200 mm `component_child_owner_mismatch`; nie powtarzaj
dla tego Wall material preview ani żadnego zapisu.
