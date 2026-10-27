# M4 — analiza API natywnej selekcji Allplan

Analiza z 2026-10-27 dla `develop/m4`, rewizja
`4315d177d27a4af70524dc4dd0fb64e95e8d2ac1`, produkt 0.39.0.
Dotyczy części **selekcja** punktu 5 [planu rozwoju](office-editing-development-plan.pl.md).
Nie zmienia zakresu odebranego delete ani nie zamyka całego punktu 5.
Źródła zewnętrzne dotyczą PythonParts API **2026**; raportowany przez właściciela
runtime to Allplan **2026.1**, bez ustalenia dokładnego hotfixa w ostatnim logu.
Poniżej oddzielono fakty z kodu/dokumentacji, projekt implementacji i wymagane
obserwacje natywne. W tej pracy nie uruchamiano Allplana ani nie zmieniano runtime.

## 1. Wniosek i rekomendacja

**Publiczne API dokumentuje interaktywną selekcję użytkownika, ale w sprawdzonych
źródłach nie znaleziono kompletnego kontraktu programowego ustawienia dowolnej
listy adapterów jako bieżącej selekcji UI, wyczyszczenia jej i niezależnego
odczytu całego zaznaczenia.** Nie jest to dowód, że taka możliwość nie istnieje
w innych interfejsach lub wersjach SDK.

Wymaganie M4 oznacza przepływ `wynik query → dokładne zaznaczenie w Allplanie`.
`StartElementSelect` realizuje inny przepływ: `wybór użytkownika w Allplanie →
lista adapterów`. Można zaprojektować i wdrożyć ten drugi jako osobną funkcję,
lecz nie zastępuje on wymaganego `select` i nie zamyka punktu 5.

Rekomendowane postępowanie:

1. Ustalić kontrakt **replace / clear / read-current** dla zainstalowanego SDK;
   najpierw dokumentacja i wąski eksperyment opisany w sekcji 7. Brakujące
   odpowiedzi skierować do producenta, bez zgadywania setterów.
2. Po potwierdzeniu kontraktu podłączyć mały backend natywny do istniejącego
   `model_selection`, zachowując pełną rewalidację query i wątek UI.
3. Osobno rozważyć `begin_pick` lub import preselekcji, jeśli potrzebny jest
   wybór zakresu przez użytkownika. Nazwy i wyniki muszą jasno odróżniać tę
   funkcję od programowego ustawiania selekcji.

Do czasu potwierdzenia backendu obecne `action=select` powinno nadal jawnie
zwracać `unsupported`, bez automatycznej zamiany na highlight. To techniczny
stan otwartej pracy, nie decyzja o usunięciu wymagania z produktu.

## 2. Co istnieje w M4

| Miejsce | Stan i znaczenie dla implementacji |
| --- | --- |
| [Modele MCP](../src/allplan_mcp/property_models.py), `HighlightInput`, `SelectionRequest` | `highlight` i `select` przyjmują `selection_id` oraz wyjątki UUID; osobno jest `clear_highlight`. Nie ma `clear_selection` ani odczytu natywnego stanu. |
| [Tool MCP](../src/allplan_mcp/server.py), `model_selection` | Przekazuje `m4-selection-1` na `/model-selection`; opis rozdziela highlight i selection, nie nadaje prawa do zapisu. |
| [Walidator hosta](../python_host/PythonPartsScripts/PythonHost/property_contracts.py), `validate_selection` | Druga, niezależna walidacja payloadu przed SDK. Nowe akcje trzeba dodać po obu stronach. |
| [Prezentacja](../python_host/PythonPartsScripts/PythonHost/model_selection.py), `present_selection` | `select` kończy się przed skanem i wywołaniami UI. Highlight skanuje ponownie pełne query, sprawdza fingerprint, TTL, adaptery i budżet, następnie czyści highlight i podświetla wynik. |
| [Query](../python_host/PythonPartsScripts/PythonHost/model_query.py), `ModelQueryService` | Cache JSON, bez trwałych adapterów: TTL 300 s, maks. 8 wpisów, skan 5 s. `selection_id` identyfikuje wynik zapytania w sesji hosta, nie natywny selection set. |
| [Handler](../python_host/PythonPartsScripts/PythonHost/PythonHostHandler.py) | Wspólny punkt dostępu do serwisów. Dziś `select` omija unieważnienie prezentacji planów, ponieważ nic nie wykonuje; przy implementacji trzeba ponownie ustalić tę regułę. |
| [Interactor](../python_host/PythonPartsScripts/PythonHost/StartPythonHost.py) i [dispatcher](../python_host/PythonPartsScripts/PythonHost/transport.py) | `DispatcherTimer` co 50 ms uruchamia pracę natywną na UI. HTTP tylko kolejkuje żądania. `process_mouse_msg` jest pusty; ESC zatrzymuje cały host. |
| [Testy prezentacji](../tests/test_model_properties.py) | Sprawdzają pełne query mimo paginacji, stale/TTL przed UI, `unsupported` bez wywołań, `unknown` po awarii UI. To mocki, nie dowód działania zaznaczenia w Allplanie. |

Obecny highlight przesyła wszystkie rozpoznane reprezentacje widokowe modelu.
`requested_adapters` może być większe niż liczba modeli. Wynik pozostawia
`selected` i `highlighted` jako `null`: samo wywołanie SDK nie dowodzi stanu UI.
`clear_highlight` czyści wszystkie podświetlenia bieżącego dokumentu, także
pochodzące z innych źródeł. Tych semantyk nie wolno automatycznie przenosić na
native selection.

## 3. Co faktycznie zapewnia API 2026

### Ustawianie i wybór interaktywny

[`InputFunctionStarter`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/InputFunctionStarter/)
udostępnia:

```python
StartElementSelect(text, selectSetting, postSel, markSelectedElements,
                   selectionMode=SelectionMode.eSelectGeometry)
RemoveFunction()
```

Pierwsze wywołanie rozpoczyna interaktywny wybór; argumenty opisują filtr,
odbiornik wyniku i tryb. Nie ma argumentu wejściowego `BaseElementAdapterList`.
`markSelectedElements=True` nie jest udokumentowanym sposobem wstrzyknięcia
istniejącej listy ani gwarancją trwałej selekcji po zakończeniu funkcji.
`RemoveFunction` usuwa funkcję wejścia, nie stanowi udokumentowanego
`clear_selection`.

[`SelectionMode`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectionMode/)
rozróżnia `eSelectGeometry` (wybrany element), `eSelectObject` (również elementy
powiązane i dzieci) i `eSelectSubObject` (część powiązań). Dla M4 ważne jest
ryzyko rozszerzenia ściany o oś, etykiety, kontener atrybutów lub dzieci.
Na początek należy jawnie wybrać `eSelectGeometry` i sprawdzić rzeczywiste
tożsamości; nazwa trybu sama nie dowodzi zgodności z semantycznym modelem query.

[`MultiElementSelectInteractor`](https://pythonparts.allplan.com/2026/api_reference/ScriptObjectInteractors/MultiElementSelectInteractor/MultiElementSelectInteractor/)
jest wyższą warstwą dla script object. Nadal obsługuje wybór użytkownika;
przepisanie działającego hosta na script object nie dostarcza brakującego settera.

### Odczyty — trzy różne znaczenia „selected”

| API | Udokumentowany wynik | Granica dowodu |
| --- | --- | --- |
| [`PostElementSelection.GetSelectedElements(doc)`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/PostElementSelection/) | `BaseElementAdapterList` pobrana i usunięta z kontenera wyniku interakcji. | Odczyt konsumujący. Drugi pusty wynik nie dowodzi wyczyszczenia zaznaczenia w UI. |
| [`SelectElementsService.GetPreSelectedElements(doc, filter)`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectElementsService/) | Lista elementów preselekcji spełniających `SelectionQuery`. | Kandydat do odczytu preselekcji. Moment odczytu względem startu narzędzia, trwałość, konsumowanie i przydatność jako readback po set/clear nie są ustalone. |
| [`CoordinateInput.GetSelectedElements()`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/CoordinateInput/) | Lista elementów w tej samej odległości od kursora, związana z identyfikacją wejścia. | Nie jest udokumentowanym odczytem całego zaznaczenia UI. Także `GetSelectedElement()` dotyczy identyfikacji elementu w wejściu. |

Preselekcja zasługuje na osobny eksperyment, a nie z góry na odrzucenie.
Nie wolno jednak filtrować potencjalnego readbacku wyłącznie do żądanego zbioru:
ukryłoby to przypadkowo zaznaczone elementy dodatkowe i dało fałszywy PASS.

### Wyszukiwanie, podświetlenie i stan adaptera

- [`SelectElementsService.SelectByPolygon` / `SelectByRect`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectElementsService/)
  zwracają adaptery wyszukane przez geometrię, projekcję i filtr. Nie przyjmują
  listy adapterów do ustawienia. Oficjalny przykład
  [SlopedGeneralOpening.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/Objects/SlopedGeneralOpening.py)
  osobno podświetla wynik. Brak podstaw, by sam wynik query traktować jako
  programowe zastąpienie zaznaczenia.
- [`BaseElements.ElementsSelectService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsSelectService/)
  to inna klasa niż `IFW_Input.SelectElementsService`. Jej `SelectAllElements`
  i `SelectElementsByIfcGuid` służą do pobrania listy elementów. Pierwszej już
  używa skaner M4; nie oznacza to zaznaczenia całego modelu w UI.
- [`HighlightService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/HighlightService/)
  ma `HighlightElements(eleList)` i `CancelAllHighlightedElements(documentID)`.
  [GetObjectByAttributeValue.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ObjectAccessExamples/GetObjectByAttributeValue.py)
  pokazuje query, highlight i redraw. Nie dokumentuje set/clear/readback selekcji.
- [`BaseElementAdapter`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/)
  ma `IsActive()` opisane jako sprawdzenie aktywacji, lecz bez wystarczającego
  kontraktu, aby utożsamić je z bieżącą selekcją UI. Spis metod nie zawiera
  `IsSelected`/`SetSelected`. Ani `IsActive`, ani `SetVisibilityState` nie
  uzasadniają implementacji setterów zaznaczenia.

Przykład [SelectObjectsByAttributeID.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/SelectObjectsByAttributeID.py)
potwierdza drogę `StartElementSelect → callback → PostElementSelection`.
Przykłady przypięto do rewizji `8e2c252477e20bc9afac8918f78a8eeabd473a81`;
nie są dowodem odbioru M4 na aktualnym buildzie. Wcześniejsze ustalenia są w
[notatce 0.25](m4-editing-api-0.25.0.md#native-selection-remains-interactive)
i [notatce 0.28](m4-editing-api-0.28.0.md#selecting-existing-query-results).

## 4. Projekt programowego set/clear/readback — po potwierdzeniu API

Poniższe nazwy są **propozycją kontraktu M4, nie istniejącymi metodami Allplana**.
Minimalny backend powinien rozdzielać `replace_exact`, `clear` i `read_current`,
z deklaracją scope, obsługiwanych buildów, tożsamości oraz synchroniczności.
Brak dowolnej części nie pozwala ogłosić pełnej obsługi punktu 5.

### Kontrakt MCP

| Proponowana akcja | Kontrakt |
| --- | --- |
| `select` | Pełny, świeżo sprawdzony wynik `selection_id` minus jawne wyjątki; semantyka replace, bez cichego add/toggle. Wynik po niezależnym odczycie. |
| `read_selection` | Nowy odczyt bieżącego stanu backendu, bez wymogu żywego query ID. Osobno czas obserwacji, kontekst, kompletność i zakres odczytu. |
| `clear_selection` | Jawnie określony zakres czyszczenia i świeży odczyt pustego zbioru w tym samym zakresie. Niezależne od `clear_highlight`. |

Rozszerzenie wymaga spójnej wersji schematu po obu stronach (np. nowego
`m4-selection-2`) i obsługi starszego hosta przez jawny błąd/unsupported.
Nie zmieniać po cichu znaczenia `clear_highlight` ani utożsamiać identyfikatora
zapytania z identyfikatorem operacji UI.

### Tożsamości i rewalidacja

Pierwszy obsługiwany zakres: jeden jawnie wskazany aktywny rysunek, bez aktywacji
plików i bez zmiany warstw. Liczba zaznaczeń nie jest automatycznie ograniczona
limitem 32 zmian modelu; potrzebny jest osobny budżet i odbiór wydajności.
200 to limit strony query, nie pełnego zbioru do zaznaczenia.

Przed UI odtworzyć całe zapytanie, sprawdzić kontekst, TTL, fingerprint,
kompletność i brak niejednoznacznych reprezentacji. Nie wybierać tylko pierwszej
strony ani próbki. Dla exact selection odrzucić wynik niekompletny lub o nieznanej
tożsamości; ujawnienie omissions bez blokady nie wystarcza do obietnicy „wszystkie”.

Klucz modelu to co najmniej `(drawing_file, model_uuid)` wewnątrz przypisanego
projektu/dokumentu/sesji. Osobno zachować `view_uuid` adaptera i relacje
parent/child. Obecne wyjątki `exclude_model_uuids` i wewnętrzne
`target_model_uuids` nie kwalifikują pliku. Przy rozszerzaniu zakresu trzeba
przejść na pełne ref albo odrzucać niejednoznaczność; nie zakładać globalnej
unikalności UUID między rysunkami.

Nie kopiować automatycznie wszystkich view adapterów z highlightu do native
selection. Najpierw ustalić, czy setter/readback operuje modelem, reprezentacją
czy obiektem z zależnościami. Nie przekierowywać Slab na MultiSlab, otworu na
ścianę ani child na parent. Każde rozszerzenie zbioru musi być widoczne.

### Przebieg operacji

```text
MCP → walidacja payloadu → kolejka UI
    → pełna rewalidacja query → rozstrzygnięcie dokładnych adapterów
    → odczyt zastępowanego zakresu → backend.replace_exact
    → backend.read_current → porównanie zbiorów → wynik JSON
```

To projekt, nie wykonywalny pseudokod SDK. Wszystkie wywołania natywne pozostają
na wątku UI. Adaptery oraz ich właścicieli utrzymywać przy życiu przez wywołanie;
w cache i odpowiedzi przechowywać JSON/ref, nie wskaźniki SDK. Jeśli setter
kończy się asynchronicznie, potrzebny jest callback/automat stanów, a nie
założenie, że wynik jest gotowy przed końcem bieżącego ticka.

Nie wyznaczać sukcesu przez porównanie liczników. Dla żądanego zbioru `E` i
niezależnie odczytanego `A` raportować `missing = E − A`, `unexpected = A − E`,
nierozpoznane adaptery oraz kompletność. `verified` wymaga obu różnic pustych,
pełnego odczytu i zgodnego kontekstu. Porównanie musi obejmować również obiekty
spoza rodzin znanych query, jeśli mogły pozostać zaznaczone. Odczyt filtrowany
tylko do `E` nie może wykryć `unexpected`.

Po clear `A` musi być puste w zadeklarowanym zakresie. Błąd odczytu nie oznacza
pustego zbioru. Przed wywołaniem UI można zwrócić `unsupported`/`blocked` z
`ui_calls_started=false`; po wywołaniu i utracie pewności — `unknown`, a przy
pełnym odczycie rozbieżności — jawny `mismatch`. `submitted` nie jest `verified`.

Selekcja pozostaje `model_data_changed=false`, `usable_for_write=false`.
Nie uruchamia Apply, delete, Undo ani setterów właściwości. Zmiana prezentacji
wymaga przeglądu reguły unieważniania prezentacji planów w handlerze, ale nie
może osłabić istniejących blokad zapisu, journalu czy recovery.

Po utracie odpowiedzi nie ponawiać automatycznie replace/clear: użytkownik
mógł już zmienić zaznaczenie. Identyfikator operacji i status w sesji pozwolą
rozliczyć żądanie; wymagają nowego rejestru/statusu operacji. Obecny bridge
`request_id` służy korelacji logów i sam nie dowodzi wykonania. Readback pozostaje
świeżą obserwacją. Po utracie rejestru wynik nierozliczonej operacji jest nieznany.
Restart unieważnia
sesję i query ID, nie dowodzi wyczyszczenia native selection. Bez kontraktu
odczytu nie obiecywać automatycznego przywrócenia wcześniejszego wyboru.

## 5. Osobna funkcja: interaktywny wybór przez użytkownika

To wykonalny kierunek oparty na udokumentowanym API, wymagający integracji i
próby natywnej. Proponowany kontrakt to `begin_pick → status/result → cancel_pick`,
z osobnym `operation_id`. HTTP ma szybko zwrócić `awaiting_user`; nie wolno
blokować UI ani odpowiedzi HTTP do czasu kliknięcia przez człowieka.

[Podręcznik selekcji](https://pythonparts.allplan.com/2026/manual/features/input/selection/)
opisuje przejęcie obsługi myszy do zakończenia wyboru, możliwość zmiany filtra
przez użytkownika oraz ryzyko awarii przy ponownym starcie aktywnej funkcji
lub usuwaniu funkcji nieaktywnej. Dlatego host potrzebuje automatu stanów
`idle → starting → awaiting_user → completed/cancelled/unknown`, pojedynczego
właściciela funkcji wejścia i odrębnej obsługi ESC podczas wyboru.

W proponowanej integracji wzorzec SDK wykorzystuje wznowione `process_mouse_msg`
do pobrania wyniku po zakończeniu interakcji; obecny host tego nie implementuje.
Callback nie służy do cyklicznego odczytywania wyniku w trakcie wyboru.
`PostElementSelection` pobrać
raz, zamienić na ograniczony snapshot ref i ponownie sprawdzić scope/typy/relacje.
Nie ufać samemu filtrowi. Pusty wynik jest poprawnym zakończeniem, a nie powodem
automatycznego restartu. `RemoveFunction` wywoływać wyłącznie dla nadal aktywnej
funkcji należącej do hosta; po normalnym zakończeniu nie usuwać jej ponownie.

Podczas oczekiwania inne mutacje UI oraz Apply/delete/Undo powinny otrzymywać
`selection_busy`. Zezwolić na status/cancel i tylko sprawdzone odczyty; zachowanie
timera w natywnej pętli wejścia trzeba potwierdzić. ESC, zmiana projektu/rysunku
i zatrzymanie hosta muszą kończyć operację bez podwójnego cleanup i bez
pozostawienia aktywnej funkcji. Stan `starting/unknown` nie uprawnia do ślepego
`RemoveFunction` ani do drugiego startu.

Wynik nazywać `interactive_pick`, z `readback_kind=interaction_result`.
Nie przedstawiać go jako trwałej selekcji UI ani jako wyniku `read_selection`.
Można utworzyć osobny snapshot wejściowego zakresu; nadal nie jest on zgodą
na zapis i musi przejść zwykłe preview/revalidation przed edycją.

## 6. Warianty i koszt techniczny

| Wariant | Co daje | Ocena |
| --- | --- | --- |
| Publiczny backend replace/clear/read-current | Spełnia docelowy kierunek query → native UI, jeżeli kontrakt zostanie potwierdzony. | Preferowany; obecnie BLOCKED brakiem kompletnego kontraktu. |
| `StartElementSelect` + wynik callbacku | Użytkownik wskazuje elementy natywnymi gestami. | Realny odrębny feature; średnia złożoność lifecycle, nie zamyka obecnego wymagania. |
| `GetPreSelectedElements` | Potencjalny import wcześniej zaznaczonego zakresu. | Najmniejszy eksperyment odczytu; semantyka i zakres wymagają sprawdzenia. |
| Inny oficjalny SDK/rozszerzenie producenta | Potencjalnie brakujący setter i readback. | Do rozpoznania z producentem; nie potwierdzono tu konkretnej ścieżki C++/.NET. Dochodzą instalacja, ABI/build i most do hosta. |
| Highlight, geometria prostokąta lub syntetyczne kliknięcia | Prezentacja albo próba odtworzenia gestu. | Nie zapewniają udokumentowanego exact set/clear/readback; nie stanowią zamiennika wymagania. |

Największy koszt nie leży w dodaniu nowej akcji MCP, lecz w ustaleniu
semantyki native selection i w bezpiecznej integracji pętli UI. Bez brakującego
kontraktu nie ma podstaw do wiarygodnej estymacji pełnej implementacji.

## 7. Minimalny eksperyment i pytania rozstrzygające

To projekt przyszłej próby, **nie wykonany test i nie żądanie ponowienia
odebranych operacji modelu**. Działać na małym rysunku testowym; zapisać build
Allplana, SDK/stuby, wersję paczki i dokładne ref elementów. Nie wznawiać
szerokiego property discovery ani historycznych prób prowadzących do crasha.

1. Sprawdzić lokalne stuby tylko wymienionych klas oraz oficjalną odpowiedź
   producenta o setterze, clear i globalnym readbacku. Samo istnienie symbolu
   nie jest dowodem jego semantyki. Nie wywoływać zgadywanych metod.
2. Dla ręcznego wyboru `{A, B}`, następnie `{B}` i pustego zbioru sprawdzić
   `GetPreSelectedElements` przed/w trakcie/po wejściu do hosta oraz powtórny
   odczyt. Odróżnić od wyniku pod kursorem i od samego highlightu. Ustalić,
   czy odczyt konsumuje stan i czy filtr naprawdę obejmuje cały zakres.
   Porównać filtr zawężający z wariantem niezawężającym, po sprawdzeniu jego
   konstrukcji w bindingach 2026. Sam pusty `SelectionQuery` nie dowodzi
   globalnego ani kompletnego readbacku.
3. Dla osobnego pick sprawdzić jedno zakończenie, pusty wynik i anulowanie;
   zapisać kolejność callbacków, działanie timera, zakres `markSelectedElements`
   oraz to, co pozostaje po zakończeniu. Bez celowego podwójnego start/Remove.
4. Dopiero po ustaleniu settera wykonać `{A, B} → {B} → ∅`, z obcym wcześniejszym
   zaznaczeniem `C`, porównując pełne dokładne ref API i UI. Jeśli backend
   nie daje takiego readbacku, odnotować BLOCKED zamiast uznawać podświetlenie
   za sukces. Kontrolować brak zmiany danych modelu i historii Undo.
5. Dopiero dla działającej ścieżki rozszerzyć macierz o Wall z otworami,
   Slab/MultiSlab, reprezentacje widokowe, warstwy pasywne/ukryte, zmianę
   kontekstu, utratę odpowiedzi, ESC i restart. Nie rozszerzać odbioru z jednej
   rodziny na pozostałe; brak przykładu oznaczać `fixture_missing`.

Pytania do producenta: jaka publiczna metoda przyjmuje dokładne istniejące
adaptery jako selekcję, czy replace jest atomowy, jak wyczyścić stan i jaki
getter czyta go niezależnie od kursora/callbacku? Jaki jest scope
(rysunek/dokument/widok/aplikacja), lifetime i zachowanie po końcu interaktora?
Czy są normalizacje do parent/children? Czy `GetPreSelectedElements` konsumuje
preselekcję i działa po programowym set/clear? Co dokładnie oznacza `IsActive()`?
Czy te wywołania są wspierane z callbacku `DispatcherTimer` na UI w 2026.1?
Czy `markSelectedElements` pozostawia selekcję po końcu funkcji i czy jej
zbiór może różnić się od wyniku `PostElementSelection`?

## 8. Weryfikacja przyszłej implementacji i warunek zamknięcia

Testy jednostkowe powinny sprawdzać kontrakty MCP/hosta, pełny zbiór wszystkich
stron, stale/TTL/context przed UI, różnice `missing/unexpected`, duplikaty
reprezentacji, nierozpoznane ref, scope clear i `unknown` po rozpoczęciu UI.
Dla pick: pojedynczy start, konsumpcja wyniku raz, brak podwójnego Remove,
busy/cancel/stop oraz brak automatycznego restartu po pustym wyniku.
Test HTTP ma potwierdzić szybki start/status i brak niejawnego retry; mock backendu
nie jest dowodem dostępności prawdziwego API.

Produktowy kandydat wymaga kontroli z [polityki testów](testing-policy.md),
odpowiedniego CI i dostawy oraz osobnej próby natywnej. Odbiór selekcji wymaga
zgodności **całego dokładnego zbioru w API i UI po replace i po clear**,
kontroli braku edycji modelu oraz zapisania builda i zakresu dowodu. Sam odczyt
wyniku pick albo liczba podświetleń nie wystarcza. Pełny punkt 5 nadal wymaga
także brakujących dowodów delete; istniejący grouped Column delete/Undo PASS
pozostaje zachowany.

Bieżący rezultat tej pracy to analiza dokumentacji i kodu, sprawdzenie diffu
i odnośników. Brak nowego native PASS, implementacji selekcji, testów runtime
lub buildów; ograniczenia 0.39.0 pozostają aktualne.
