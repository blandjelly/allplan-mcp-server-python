# M4 — typowana edycja modelu: przewodnik operatora

Ten przewodnik opisuje kontrakt `model_edit` i jego granice; nie stanowi
akceptacji natywnej. Aktualny stan i priorytety znajdują się w
[handoffie](next-model-handoff.md) oraz [planie rozwoju](office-editing-development-plan.pl.md).
Przeczytaj też
[evidence API Allplan 2026](m4-attribute-api-evidence.md) oraz
[kontrakt narzędzi](tool-reference.md).

## Polecenia dla agenta

Użytkownik opisuje zamiar zwykłym językiem; nie musi tworzyć JSON ani znać
identyfikatorów. Agent ma najpierw rozpoznać żądane dokładne pole przez
pojedynczy `model_property_probe` w fazie `attribute_name`, a następnie użyć
zwróconego ID i potwierdzić roundtrip nazwa–ID. Nie wolno zgadywać ID ani
wybierać podobnie brzmiącego pola. Jeśli dokładne pole, jego typ lub właściciel
nie zostaną potwierdzone, agent ma zatrzymać plan bez zapisu.

Do przeglądu wartości atrybutów na jednym elemencie służy osobna faza
`element_attributes`: wymaga aktywnego rysunku oraz dokładnych, niezerowych
`model_uuid` i `view_uuid`; zwraca stronicowane wartości `ReadAll` i celowane
metadane nazw/typów. To nie jest katalog definicji projektu. Brak atrybutu w
`ReadAll` pozostaje nieznany, a lista nie dowodzi zapisywalności. Szczegóły
stronicowania i odpowiedzi są w [kontrakcie fazy](tool-reference.md#model_property_probe--isolated-read-phases).

Przykładowe polecenia użytkownika:

- „W otwartych rysunkach znajdź słupy bez dokładnego atrybutu *Klasa odporności
  ogniowej*. Zaplanuj wartość `F120` i przypisz warstwę organizacyjną `W1`.”
- „Na elementach z dokładnie nieobecnym atrybutem *Materiał konstrukcyjny*
  dodaj wartość `Beton C37`; nie zmieniaj natywnego materiału ściany.”
- „Zmień istniejącą wartość atrybutu *Materiał* na `Beton C37` wyłącznie tam,
  gdzie obecna wartość została odczytana i filtr pasuje.”
- „Znajdź wyłącznie drzwi, nie okna, i zaplanuj zmianę wskazanego atrybutu.”

W pierwszym przykładzie agent musi rozwiązać nazwę atrybutu zanim zbuduje
kryterium `is_unset`. Predykat atrybutu jest przekazywany jako
`attribute:<ID z bieżącego probe>`, a nie jako tekst nazwy. Dla brakującego
atrybutu agent jawnie wybiera odczyt `all_and_computable`; pozwala on
odróżnić brak od atrybutu pominiętego przez zwykłe `ReadAll`. Odczyt musi być
udany dla pełnego zakresu. Błąd, niepełne pokrycie i nieznany stan zostają
`unknown` i blokują Apply. Odczyt obejmujący atrybuty wyliczane jest nową,
wyraźną opcją tej ścieżki. Dotychczasowe ścieżki `ReadAll` pozostają bez zmian.

`is_unset` obejmuje odczytaną wartość pustą/`null` oraz brak udowodniony przez
`ReadAllAndComputable`; nie utożsamia błędu odczytu z brakiem. Znana wartość
`<niezdefiniowany>` jest tekstem, dopóki jawna reguła nie określi jej inaczej.
Kryterium musi osobno ustalić, czy taka wartość ma znaczyć brak.
`model_query` także udostępnia jawny, tylko-odczytowy
`attribute_read_mode=all_and_computable` dla wskazanych ID. Może zwrócić
`computed_only=true`; taki wynik nie jest zapisywalnym atrybutem. Tryb
`stored` pozostaje domyślny, a tryb odczytu jest częścią fingerprintu źródła.

## Cele i rozdzielenie pól

`model_edit` zapisuje tylko jawnie związany atrybut przez
`ElementsAttributeService.ChangeAttributes` albo nazwę warstwy organizacyjnej
przez `ElementsLayerService.ChangeLayer`. Nazwa atrybutu jest rozwiązywana w
bieżącym dokumencie i sprawdzana w obie strony; warstwa `W1` również wymaga
roundtrip nazwa–ID. Narzędzie nie tworzy definicji atrybutów ani warstw;
może dodać już istniejącą definicję atrybutu do elementu.

Przykład `Beton C37` w tym narzędziu oznacza dokładnie wskazany atrybut tekstowy.
To oddzielne od natywnego `WallTierProperties.Material`, powierzchni
wizualnej i warstwy organizacyjnej. Ścieżka `native_material` pozostaje
eksperymentalna i fail-closed. Odczytana wartość starego materiału jest osobna
od dowodu, że ścianę można bezpiecznie zachować podczas zmiany. Preview może
pokazać starą wartość jako `observed`, a jednocześnie zablokować operację jako
`native_material_preservation_unavailable`; szczegóły są w
`criteria.operation_eligibility_failures` (obecnie wyłącznie blokady
preservation natywnego materiału Wall), a `criteria.required_field_failures`
wykazuje wyłącznie nieodczytane wymagane pola docelowe i może być puste.
Błędy kryterium pozostają w `report.criterion_failures`. Kandydat 0.34.0 nadal
wymaga jednego `WallTier_TypeUUID` z lineage `[tier, Wall root]`, lecz nie
odrzuca samego typu potomka: oś, otwór, makro i zagnieżdżone metadane mogą
wejść do ograniczonego drzewa dowodów zachowania ściany. To nie uprawnia do
osobnej edycji tych potomków. Tożsamość i relacje rodzic–dziecko muszą być
spójne, a wartości `ReadAll` kontenerów atrybutów odczytywalne. Geometria
pomocnicza ma hash strumienia, gdy SDK to umożliwia; w przeciwnym razie
`not_checked` nie blokuje wyłącznie z tego powodu. Nie dowodzi to zachowania
wszystkich ukrytych właściwości potomków. Odczyt po zapisie nadal porównuje
cały zapisany snapshot; sam materiał nie wystarcza. Szczegóły kontraktu są w
[opisie API](m4-editing-api-0.32.0.md), a następna próba z przypadkami brzegowymi
w [handoffie](next-model-handoff.md).

Resolver 0.27.0 dla każdego `model_edit` bind sprawdza ograniczone warianty
nazwy: podaną postać, trim/NFC, pierwszą literę wielką, całość wielkimi i
całość małymi. Każdy znaleziony wynik musi przejść roundtrip rzeczywista
nazwa–ID; zgodność casefold jest akceptowana tylko przy jednym ID. Konflikt
odrzuca wiązanie. Nie ma fuzzy search ani katalogu. Odczytowy probe
`attribute_name` nadal zaczyna od dokładnego lookup i używa wspólnego resolvera
dopiero po `ValueError`/`TypeError` lookup miss.

Wartość ma typ `text`, `integer`, `real` albo `boolean`. Domyślne
`value_type=auto` dobiera go na podstawie typu dokładnie związanego atrybutu i
załadowanego SDK; teksty nie są parsowane ani konwertowane. Ręczny typ również
wiąże się z `GetAttributeType` dla dokładnego ID i rzeczywistym członkiem SDK
(`String`, `Integer`, `Double` albo `Boolean`); nie ma zgadywanych kodów.
Enumy obsługuje wyłącznie jawne `value_type=enum` z dokładną etykietą. SDK musi
potwierdzić typ `Enum`, `Integer` albo `String`; etykieta jest rozwiązywana
wywołaniami `GetEnumIDFromValueString` i `GetEnumValueStringFromID` z powrotnym
sprawdzeniem etykiety i klucza. Nie ma `GetEnumValues` ani enumeracji katalogu;
wartość settera i readback pozostają etykietą, a hash wiąże też klucz i etykietę
enum. `auto` nie wnioskuje enumu z wejściowego tekstu. Daty pozostają
nieobsługiwane. Zgodny typ nie potwierdza zapisywalności w Allplanie.

Tryby atrybutu:

- `replace` wymaga odczytanej istniejącej wartości.
- `add` wymaga udowodnionego braku z `ReadAllAndComputable`.
- `upsert` podmienia odczytaną wartość albo dodaje atrybut tylko przy takim
  samym dowodzie braku.

Jeżeli brak ma być obsłużony, `replace` nie oznacza dodania. Plan pokazuje
osobne operacje `add_attribute` i `set_attribute`; warstwa jest osobną
operacją. Dla wymaganego scenariusza pierwsze polecenie ma więc dwie zmiany:
wartość `F120` w dokładnym atrybucie oraz warstwę `W1`.

## Zakres, plan i zapis

Domyślny odczyt obejmuje `open_drawings`, łącznie z pasywnymi otwartymi
plikami. Obsługiwane grupy semantyczne to Column, Beam (w tym SkeletonBeam),
Wall, Slab (w tym MultiSlab) i opening. Ostatnia grupa używa udokumentowanego
`WindowDoor_TypeUUID`; oznacza otwór, ale nie rozstrzyga, czy są to drzwi czy
okno. Nie używamy zgadywanych `Window_TypeUUID` ani `Door_TypeUUID`.
Opcjonalny predykat `opening_kind=door|window` rozstrzyga podtyp przez
`GetElement(adapter)` i sprawdzenie udokumentowanych klas
`DoorOpeningElement`/`WindowOpeningElement`. Jeśli reprezentacja natywna jest
niedostępna lub nie pasuje do tych klas, wynik ma być `not_checked`, a filtr
nie może zostać uznany za kompletny. Ta ścieżka opiera się na dokumentacji API
i wymaga osobnej próby natywnej; nie jest akceptacją edycji drzwi/okien.
Agent ogranicza typy do `WindowDoor_TypeUUID` i łączy predykat z rodziną
`opening`; nie podmienia ich na niezależne, zgadywane typy adapterów.
Pozostałe typy są poza zakresem. Więcej o rodzinach, statusach i polach kryterium podaje
[kontrakt `model_edit`](tool-reference.md).

Plan jest kompletny wyłącznie przy pełnym pokryciu zakresu i polach
kryterium bez statusu `unknown`. Limity to maksymalnie 32 rzeczywiste zmiany,
16 pól w jednym żądaniu, 32 odczytywane atrybuty, 10 000 adapterów i
5-sekundowy kooperatywny budżet skanu. Dopasowane elementy bez zmian mogą
pozostać celami podświetlenia. Podświetlenie jest prezentacją wyników; nie
jest natywnym zaznaczeniem i nie zmienia modelu.

Preview i revalidate są tylko do odczytu. Przed Apply agent ma pokazać zakres,
liczbę zmian, każde pole, starą i nową wartość, wyjątki i pokrycie. Apply
wymaga wskazania dokładnego `plan_id`/`plan_hash`, nowego `execution_id` oraz
potwierdzenia `disposable_copy_reviewed_plan`. Przed setterami executor
ponownie rozwiązuje każdy cel i sprawdza stare wartości; zapisuje trwały
rekord z wyprzedzeniem, po setterze wykonuje świeży odczyt zwrotny. Replay
tego samego `execution_id` nie ponawia setterów. Niepowodzenie lub utrata
odpowiedzi daje `unknown` do czasu jawnego recovery i odczytu.

Po podglądzie agent ocenia możliwość Apply na podstawie publicznego
`apply_available`. `evaluation_apply_available` jest jego aliasem zgodności;
`production_apply_available=false` osobno informuje, że zapis produkcyjny nie
jest dostępny. Brak natywnej akceptacji nie wyłącza same przez się
kwalifikującego się Apply w tej eksperymentalnej ścieżce. Nie wolno
przedstawiać takiego zapisu jako natywnie zaakceptowanego. Po zgodzie
użytkownika agent kontynuuje, gdy `apply_available=true` oraz spełniono
dokładne powiązanie planu, potwierdzenie `disposable_copy_reviewed_plan`,
świeżą rewalidację, ID wykonania i pozostałe straże Apply. Jeśli któryś
warunek nie jest spełniony, agent wskazuje ten konkretny brak; nie uzasadnia
blokady brakiem zapisu produkcyjnego ani akceptacji natywnej.

Zapis jest ograniczony do jednej aktywnej, foregroundowej tablicy rysunkowej.
Przy wielu otwartych plikach odczyt może objąć więcej plików, lecz wieloplikowy
Apply jest zablokowany przed setterami. Nie ma ukrytych częściowych zapisów
ani automatycznych partii. Dozwolone jest tylko `preview_ready` z 1–32 zmianami.
K6 — rozliczanie operacji wieloplikowych, partii i wyników powyżej 32 zmian —
nie jest ukończone.

## Przykłady argumentów MCP

Użytkownik nie musi wysyłać tych obiektów. Agent tworzy je z naturalnego
polecenia, po uprzednim probe dokładnej nazwy i używa uzyskanego ID bez
hardkodowania. Poniższy fragment pokazuje jedynie dwa jawne cele zapisu:

```json
{
  "schema_version": "m4-model-edit-1",
  "action": "preview",
  "scope": "open_drawings",
  "native_types": ["Column_TypeUUID"],
  "attribute_read_mode": "all_and_computable",
  "predicate": {
    "field": "attribute:<ID_ZWRÓCONE_PRZEZ_PROBE>",
    "op": "is_unset"
  },
  "changes": [
    {
      "target": {"kind": "attribute", "name": "Klasa odporności ogniowej"},
      "value_type": "text",
      "value": "F120",
      "mode": "upsert"
    },
    {"target": {"kind": "layer", "short_name": "W1"}}
  ]
}
```

`<ID_ZWRÓCONE_PRZEZ_PROBE>` jest oznaczeniem miejsca podstawianego przez
agenta, nie literalną wartością JSON ani ID do wpisania przez operatora. MCP
otrzymuje liczbowe ID z dokładnego probe w tym samym dokumencie. Jeśli wiązanie
nie zwróci jednego pewnego wyniku, planu nie tworzy się. Nowy kontrakt ma
ustawiony typ wartości przez agenta; porównanie z metadanymi typu i
zapisywalność muszą być potwierdzone przed natywnym trialem.

