# 0.24.0 — tożsamość komponentów i brakujące rozliczenie W1

To krótka próba nowych zachowań na kopii projektu. Nie powtarza testu
dziennika 0.23.0 ani odebranych zapisów atrybutów słupów i stropów. Nie odbiera
selekcji natywnej ani materiału: oba zapisy pozostają nieobsługiwane.

Zainstaluj dokładny pakiet 0.24.0 przez `Setup.cmd`, uruchom ponownie host i
połączenie MCP. Zachowaj `allplan_health`, manifest i numer buildu Allplana
razem z odpowiedziami poniżej. Nie kasuj dzienników ani archiwów.

1. **Dwa wyniki stropów, wyłącznie odczyt.** W jednym aktywnym rysunku wykonaj
   `model_query` z `component_kind=model_identity`, filtrem `type_name in
   [Slab_TypeUUID, MultiSlab_TypeUUID]` i polami `display_name`, `type_name`,
   `layer_id`. Zachowaj model UUID, wszystkie view UUID i type UUID każdego
   wyniku. Dla każdego z tych dokładnych model/view UUID wywołaj
   `model_property_probe` z `phase=component_identity`, `drawing_file`,
   `model_uuid`, `view_uuid`. Porównaj `ownership.target`, `lineage`,
   `terminal_root`, `children` i `native_representation`. Identyczne bounds
   nie rozstrzygają tożsamości; próba nie zmienia modelu i nie nadaje
   uprawnienia do zapisu do rodzica ani dziecka. Jeśli odczyt się nie uda,
   zachowaj błąd i ślad; nie ponawiaj natywnych eksperymentów automatycznie.
2. **W1 — najpierw odczyt/no-op.** Użyj znanych, jawnie wskazanych słupów i
   zachowanego powiązania istniejącej warstwy W1 (ID, pełna i krótka nazwa).
   Nie wyszukuj ponownie odebranej warstwy. Zrób pełne zapytanie słupów w tym
   jednym rysunku. `model_edit preview` nie ma dodatniej listy UUID celów:
   przy tym samym `native_types`/kryterium wyłącz przez `exclude_model_uuids`
   wszystkie pozostałe pasujące UUID. Limit wyłączeń wynosi 100; niepełny
   wynik lub przekroczenie limitu oznacza `not_run`, bez Apply. Preview ma
   zawierać wyłącznie zmianę warstwy i dokładne oczekiwane cele po wyłączeniach.
   Jeśli cel już ma W1, oczekiwane są brak zmiany i `no_op`; nie zapisuj go
   ponownie. Zachowaj pełne liczby dopasowań, wyłączeń, zmian i blokad.
3. **Tylko brakujący przypadek W1.** Jeśli pozostaje wcześniej nieodebrany cel
   o innej warstwie, sprawdź dokładny model/view UUID, stary ID i powiązanie
   docelowej W1. Przejrzyj plan, użyj wymaganego `highlight` i `revalidate`,
   potem jednego Apply z zapisanym nowym execution ID. Oczekiwane są
   `completed`, świeży `readback.value` równy ID W1 i
   `audited_fields_match_plan=true`; sprawdź UI i nienaruszone wyłączenia.
   Identyczny execution ID ma zwrócić replay bez drugiego zapisu. Ponowny
   preview tej samej zmiany ma być `no_op`.
4. **Undo tylko tego nowego przypadku.** Wykonaj w UI Undo i świeży odczyt
   warstwy dokładnego model/view UUID; porównaj ze starym ID. Zachowaj liczbę
   kroków Undo i zaobserwowany zakres. Nie wnioskuj o wspólnym Undo wielu
   zmian. Przy wyniku `unknown` najpierw Recover oryginalnego execution ID,
   bez ponownego Apply i bez ręcznego usuwania wpisu.

Wystarczy raport odpowiedzi i krótki wynik UI. Brak osobnego celu do kroku 3
oznacza `not_run`, nie konieczność tworzenia kolejnej zmiany. Pozostałe rodziny,
kodeki, selekcja i materiał mają osobne statusy w
[macierzy](m4-single-drawing-coverage-0.24.0.md).
