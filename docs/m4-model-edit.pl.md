# M4 — typowana edycja modelu: przewodnik operatora

Stan dokumentu: 2026-10-17. Ten przewodnik opisuje nową, eksperymentalną
ścieżkę `model_edit` i nie oznacza jej akceptacji w Allplanie. Przeczytaj też
[evidence API Allplan 2026](m4-attribute-api-evidence.md) oraz
[kontrakt narzędzi](tool-reference.md).

## Polecenia dla agenta

Użytkownik opisuje zamiar zwykłym językiem; nie musi tworzyć JSON ani znać
identyfikatorów. Agent ma najpierw rozpoznać żądane dokładne pole przez
pojedynczy `model_property_probe` w fazie `attribute_name`, a następnie użyć
zwróconego ID i potwierdzić roundtrip nazwa–ID. Nie wolno zgadywać ID ani
wybierać podobnie brzmiącego pola. Jeśli dokładne pole, jego typ lub właściciel
nie zostaną potwierdzone, agent ma zatrzymać plan bez zapisu.

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

## Cele i rozdzielenie pól

`model_edit` zapisuje tylko jawnie związany atrybut przez
`ElementsAttributeService.ChangeAttributes` albo nazwę warstwy organizacyjnej
przez `ElementsLayerService.ChangeLayer`. Nazwa atrybutu jest rozwiązywana w
bieżącym dokumencie i sprawdzana w obie strony; warstwa `W1` również wymaga
roundtrip nazwa–ID. Narzędzie nie tworzy definicji atrybutów ani warstw;
może dodać już istniejącą definicję atrybutu do elementu.

Przykład `Beton C37` w tym narzędziu oznacza dokładnie wskazany atrybut tekstowy.
To oddzielne od natywnego `WallTierProperties.Material`, powierzchni
wizualnej i warstwy organizacyjnej. Natywny materiał ściany pozostaje
`unsupported` w `model_edit`. Odczyt ściany przez `model_property_probe` jest
tylko odczytem i nie zezwala na jego zapis.

Wartość ma jawny typ `text`, `integer`, `real` albo `boolean`. Adapter pyta
`GetAttributeType` o dokładnie związany ID i porównuje zwrócony enum z
rzeczywistym członkiem SDK (`String`, `Integer`, `Double` albo `Boolean`);
nie używa zgadywanych kodów liczbowych. Enumy, daty i inne formaty nie są
obecnie obsługiwane. Zgodny typ nadal nie potwierdza, że Allplan dopuszcza
zapis. Nie traktuj metadanych kontrolki palety jako uprawnienia do zapisu;
nieznany albo sprzeczny typ ma zatrzymać plan.

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

Zapis jest ograniczony do jednej aktywnej, foregroundowej tablicy rysunkowej.
Przy wielu otwartych plikach odczyt może objąć więcej plików, lecz wieloplikowy
Apply jest zablokowany przed setterami. Nie ma ukrytych częściowych zapisów
ani automatycznych partii. Dozwolone jest tylko `preview_ready` z 1–32 zmianami.
K6 — rozliczanie operacji wieloplikowych, partii i wyników powyżej 32 zmian —
nie jest ukończone.

## Krótka próba operatora w kopii testowej

Nowa ścieżka nie ma jeszcze akceptacji natywnej. Po dostarczeniu kandydata
owner powinien wykonać jeden krótki, ograniczony scenariusz w kopii projektu:

1. Sprawdź `health`, zapisz identyfikator i hash dostarczonego kandydata oraz
   potwierdź aktywny foregroundowy plik testowy.
2. Użyj dokładnej nazwy istniejącego, tekstowego atrybutu na jednym prostym
   elemencie; obejmij jedną zmianę `replace` i jedną `add` po jawnym
   `all_and_computable`, jeśli kopia ma odpowiedni brakujący atrybut. Sprawdź
   nazwę, wartość i typ w UI po każdej zmianie.
3. Na jednym słupie w tym samym aktywnym pliku sprawdź połączony zapis atrybutu
   odporności `F120` i istniejącej warstwy `W1`; potwierdź dokładny zakres,
   odczyt po zapisie i brak zmian w polach poza planem.
4. Sprawdź ponowne preview jako no-op i rzeczywisty zakres Undo w Allplanie.
   Nie zakładaj jednego wspólnego Undo dla kilku setterów. Zapisz
   odpowiedzi `health_before`/`health_after`, plan, wynik Apply i obserwację UI.

Otwór `WindowDoor_TypeUUID` nie jest częścią próby odróżniania drzwi od okien;
brakuje zaakceptowanego natywnego dyskryminatora i potwierdzonego właściciela
atrybutu dla tych dwóch podtypów.

Próba jest ograniczona do nowych typowanych setterów i połączonej zmiany
atrybutu/warstwy. Nie powtarza zaakceptowanych odczytów, podświetlenia Column
ani filtra dwóch ścian. Wynik ma status `not_run` do czasu tej obserwacji;
testy przenośne i opisane API nie ustanawiają wsparcia natywnego.

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

