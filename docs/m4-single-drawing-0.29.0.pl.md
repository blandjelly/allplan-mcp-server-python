# Krótka próba natywna 0.29.0 — zbiorowe usunięcie Column i jedno Undo

Ta próba dotyczy wyłącznie zbiorczego usunięcia trzech dokładnie wskazanych
Column na W1 i sprawdzenia, czy pojedyncze Undo przywraca wszystkie trzy oraz
wszystkich związanych potomków. Kandydat 0.29.0 ma wykonać jeden natywny
`DeleteElements(doc, full_reviewed_adapter_list)` dla kompletnej grupy
związanej z jednym delete-only planem. Plan zawiera jeden szablon zmiany
rozwinięty na trzy cele. Nie zakładać, że pojedyncze wywołanie API daje jedno
Undo w interfejsie; to właśnie sprawdza próba.
Oficjalny przykład pokazuje przekazanie listy adapterów do jednego wywołania,
ale nie dokumentuje grupowania Undo; zobacz
[dowody API 0.29.0](m4-editing-api-0.29.0.md).

W tym środowisku nie ma natywnego Allplana; próbę wykonuje właściciel na kopii
projektu, używając dokładnego kandydata 0.29.0 po przejściu jego CI i
weryfikacji ZIP-a. Zachować manifest instalacji, build Allplana,
`allplan_health`, surowe odpowiedzi MCP, log wykonania i świeże odczyty.
Właściciel zgłosił dla próby 0.29.0 PASS wszystkich kroków, w tym grupowego
usunięcia i jednego Undo przywracającego wszystkie trzy Column. Historyczny
FAIL z 0.28.0 — jedno Undo przywróciło tylko jeden Column — pozostaje zapisany
w obserwacji tej wersji. Wynik 0.29.0 i jego ograniczenia opisuje
[obserwacja właściciela](test-results/m4-owner-observation-0.29.0-2026-10-23.md)
wraz z [logiem](test-results/evidence/allplan-test-log-0.29.0-2026-10-23.md).

## Zakres

1. **Ustal dokładny zestaw trzech celów.** Wykonaj świeży odczyt w aktywnym
   rysunku i zapisz dla każdego Column rysunek, model UUID, view UUID, typ,
   warstwę oraz identyfikatory potomków. Potwierdź, że cele są trzema Column na
   W1 i nie zawierają innych elementów. Nie utożsamiaj ich z celami z logu
   0.28.0 na podstawie samej liczby lub bounds. Zatrzymaj się, jeśli zestaw
   jest niejednoznaczny albo niekompletny.
2. **Preview jednego delete-only planu.** Zwiąż dokładnie te trzy Column i
   pełne poddrzewa, z zachowaniem `target`, `descendants`,
   `child_parent_edges`, `descendant_parent_edges`, UUID, typu, kompletności,
   hashy i wykluczeń dla każdego celu. Potwierdź, że odpowiedź obejmuje
   dokładnie trzy korzenie oraz oczekiwanych potomków, bez obcego celu,
   konfliktu własności ani nieznanej krawędzi. Przerwij przy uciętym odczycie,
   brakującej krawędzi lub zmianie zestawu.
3. **Jedno wykonanie natywne.** Po sprawdzeniu planu i wymaganym
   potwierdzeniu wykonaj Apply raz. Zachowaj pełny wynik i potwierdź w logu,
   że backend wywołał `DeleteElements` dokładnie raz z trzema związanymi
   adapterami. Wynik `unknown`, wyjątek albo częściowy rezultat wymaga
   odzyskania pod tym samym execution ID; nigdy nie ponawiaj settera.
4. **Odczyt po usunięciu.** Wykonaj świeży kompletny skan wszystkich trzech
   celów i ich związanych potomków. Każdy z nich ma być nieobecny, a niezależne
   elementy mają pozostać. Zapisz wynik osobno dla każdego celu i potomka.
5. **Jedno UI Undo.** Wykonaj dokładnie jedno Undo. Wykonaj świeży kompletny
   odczyt tożsamości i potomków dla całej grupy. PASS wymaga, by ten jeden krok
   przywrócił wszystkie trzy Column i wszystkie związane potomki oraz by
   niezależne elementy nadal pozostały. Jeśli choć jeden element nie wróci,
   wynik jest FAIL; nie wykonuj dalszego Undo w ramach tej próby.

## Wynik 0.29.0 i granice

Właściciel zgłosił PASS etapów 1–5: aktywny rysunek 101 zawierał trzy
`Column_TypeUUID` na W1; potwierdzono plan; usunięcie zakończyło się
`completed`, a świeży skan wykazał brak trzech słupów i kontenerów atrybutów;
jedno UI Undo przywróciło wszystkie trzy słupy. To spełnia cel naprawy
grupowego Undo w 0.29.0.

Log nie zawiera surowych odpowiedzi MCP, UUID celów ani manifestu ZIP-a.
Przywrócenie zaobserwował właściciel; narzędzie zgłosiło `undo: not_checked` i
nie wykonało automatycznego readbacku po Undo. `runtime_verified` i
`allplan_acceptance` pozostały niepotwierdzone. Nie przypisujemy wyniku do
dokładnego artefaktu ani nie rozszerzamy go na inne typy operacji.

Kolejna praca obejmie priorytety 1–5 wspólnie; ten zapis nie wyznacza jeszcze
zakresu nowego kandydata.

## Pierwotne kryteria próby

Pierwotny plan wymagał oznaczyć każdy etap PASS, BLOCKED, FAIL albo NOT RUN i zachować exact target set,
manifest, build, odpowiedzi, execution ID oraz świeże skany. Próba nie obejmuje
zapisu atrybutów ani warstw, no-op, zapisu materiału, selekcji natywnej,
Slab/MultiSlab setterów, date/vector codec ani innych rodzin. Jej powodzenie
może zamknąć wyłącznie ten konkretny grupowy delete/Undo dla Column i nie
ustanawia ogólnej atomowości wielu operacji ani rodzin.
