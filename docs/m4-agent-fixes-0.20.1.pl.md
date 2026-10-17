# M4 0.20.1 — poprawki po próbie z agentem

[Zachowany log i zakres obserwacji](test-results/m4-agent-observation-2026-10-17.md)
potwierdzają udane polecenia odporności ogniowej, query i podświetlania. Tych
prób nie trzeba powtarzać. Log nie zawiera surowych wywołań ani wersji paczki;
obserwacja użytkownika pozostaje oddzielona od odbioru konkretnego buildu.

## Poprawione scenariusze

**Wartość U.** Poprzedni podgląd rozpoznawał liczbowy typ atrybutu z metadanych,
ale blokował jego surową, tekstową wartość `<niezdefiniowany>`. Teraz znacznik
ten, a także dokładne `<undefined>`, mogą być starą wartością atrybutu typu
integer/real/boolean. Plan jawnie zapisuje `old_value_state=undefined` i zachowuje
surowy odczyt w `old_value`; nie zamienia go na zero, null ani brak atrybutu.
Metadane nadal muszą potwierdzać nowy typ. Nieznane teksty, np. `abc` lub surowe
`0,2`, błędy odczytu, pominięcia ReadAll i pola wyłącznie wyliczane pozostają
zablokowane. W poleceniu „ustaw na 0,2” agent przekazuje liczbę JSON `0.2`.
Zmiana kryteriów wyszukiwania nie jest ukryta: `is_unset` nadal nie uznaje
dowolnego tekstu za pustą wartość; jawne znaczniki w filtrach podaje się osobno.

**Warstwa ściany.** Sam odczyt warstwy adaptera `Wall_TypeUUID` nie jest dowodem
odczytu warstwy jego części. Zapis wiąże teraz rzeczywiste, bezpośrednie
`WallTier_TypeUUID`, ich UUID, rodzica, widok, rysunek i stare warstwy. Wysyła
jedno ChangeLayer do tych części i świeżo odczytuje każdą z nich. Nie wysyła osi,
otworów ani adaptera nadrzędnego; nie odtwarza geometrii. Plan obejmuje tylko
ściany, których wszystkie rozpoznane warstwy składowe mają zgodną starą warstwę
organizacyjną. Mieszane warstwy, brak części lub niejednoznaczny właściciel
blokują operację. Wszystkie części muszą przejść kontrolę edytowalności przed
pierwszym setterem operacji. Limit to 32 części na ścianę i 32 zmiany planu.

Nowy jawny odczyt `model_query` z `component_kind=semantic_component` i
`layer_resolution=component` zwraca tak ustaloną warstwę ściany. Domyślne
`layer_resolution=adapter` zachowuje dotychczasowy surowy odczyt adaptera.
`model_edit` wybiera odczyt komponentu automatycznie przy edycji albo filtrowaniu
warstwy. Dlatego wynik nowego odczytu komponentu może różnić się od warstwy
surowego adaptera nadrzędnego; nie jest to samo w sobie błąd zapisu.

Kryterium `wall.total_thickness_mm` odczytuje rzeczywistą natywną grubość
jednowarstwowej ściany w mm. Podgląd edycji z warunkiem `< 240` wiąże także
niematchingujące ściany; zmiana grubości przed Apply powoduje konflikt planu.
Nie trzeba przekazywać UUID z osobnego filtra. Wielowarstwowe lub nierozpoznane
reprezentacje zwracają `not_checked`, bez szacowania grubości z obwiedni.

Oba scenariusze zachowują hash planu, jawny podgląd/podświetlenie, kopię testową,
dziennik przed setterem, świeży readback, replay bez zapisu i read-only recover.
Nowa operacja Wall jest odrębna od dawnych `set_layer`, więc historyczne
wykonania nadal odzyskuje się według ich starej ścieżki, bez ponawiania setterów.

## Zakres, którego poprawka nie rozszerza

„Materiał Stal” nie jest automatycznie tłumaczony na dowolny podobny atrybut.
Natywny materiał i jawny atrybut materiału są odrębnymi celami. Natywny materiał
słupa/ściany nadal wymaga osobnej, sprawdzonej ścieżki modyfikacji. Agent może
wykonać niezależną, obsługiwaną część prośby — query/podświetlenie — i wskazać
niedostępny zapis. [Uzasadnienie API](m4-agent-test-api-evidence.md).

Nie odblokowano szerokiego discovery, zapisu do produkcyjnego projektu ani
automatycznych retry. UUID wykonania jest nadal dokładnym identyfikatorem
32-znakowym, małymi znakami szesnastkowymi bez myślników (`uuid.uuid4().hex`).

## Krótka nowa próba w Allplanie

Po dostarczeniu zweryfikowanej paczki 0.20.1 zamknij Allplan i MCP, zainstaluj
pełny ZIP przez Setup w dotychczasowym folderze Local i uruchom host/MCP ponownie.
W zachowanej kopii testowej użyj lokalnego agenta:

1. „W aktywnym rysunku ustaw atrybut Wartość U wszystkich ścian na 0,2”. Agent
   ma rozwiązać dokładną nazwę, potwierdzić typ Double, pokazać stare surowe
   wartości i nową liczbę oraz zachować exact Apply przed wysłaniem. Sprawdź UI,
   readback i następny preview/no-op. Jeśli wartości są już 0,2, nie wymuszaj
   ponownego zapisu tylko w celu testu.
2. „Przenieś ściany o grubości mniejszej niż 24 cm na istniejącą warstwę W1”.
   Agent ma użyć w `model_edit` kryterium `wall.total_thickness_mm < 240`,
   bez przekazywania samych UUID z osobnego wyszukiwania. Plan ma objąć właściwą
   jednowarstwową ścianę 200 mm i jej części,
   z wyłączeniem ściany 240 mm. Sprawdź warstwę w UI i nowym odczycie komponentu,
   nie tylko na adapterze nadrzędnym. Oś, otwory i wyłączona ściana mają pozostać
   poza celami setterów. Sprawdź faktyczny zakres Undo oraz działanie hosta.

Zachowaj plan, wynik Apply/recover, health przed i po, dziennik i ślad natywny.
Po utracie odpowiedzi użyj recover z tym samym execution ID, bez nowego Apply
i bez usuwania historii. Te dwie zmiany mają **native not_run** do czasu nowej
obserwacji. Testy przenośne z atrapami API nie są dowodem działania setterów
w Allplanie ani rozwiązania natywnego materiału.
