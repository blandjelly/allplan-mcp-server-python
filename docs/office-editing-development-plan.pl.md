# Allplan MCP 2026 — ocena M3 i plan edycji modelu

Stan sprawdzony: 12 października 2026, Europe/Warsaw.
Repozytorium: `blandjelly/allplan-mcp-server-python`.
Gałąź: `codex/m3-repair-preview`, HEAD `bc421959e0e488b38867816ee6ec953f680580db`.
Dokument doradczy: proponuje dalszą pracę; nie oznacza wdrożenia poniższych funkcji.

## 1. Werdykt

M3 jest ukończone w zakresie zawężonego i zaakceptowanego MVP projektu testowego. Nie jest ukończone względem pierwotnego, szerszego kryterium odbioru ani jako uniwersalne narzędzie do edycji projektów biurowych. Integracja z main i wydanie pozostają oddzielnym krokiem.

- Aktualny status zamyka M0–M3/UAT-00–06 dla oryginalnej kopii MCP_QA_DEMO, Allplan 2026-1-7, zapisów na słupach w aktywnym rysunku 101 i udokumentowanych scenariuszy jednej/dwóch zmian.
- PR #2 jest otwarty, nie jest już draftem, nie został scalony. Main pozostaje przy 0.6.1 i opisuje dawny stan M3 0.7.0; miarodajna dla M3 jest dokumentacja jego gałęzi.
- Dostarczona wersja 0.15.0 ma zapisane 219 testów przenośnych PASS. Bezpośrednio sprawdzony run GitHub Actions 38181795091 ma sześć konfiguracji Windows/Ubuntu × Python 3.11–3.13 zakończonych success.
- CI dotyczy commitu `7e3657bc33ecf913376d302da900af386b3b8a23`. Porównanie z HEAD pokazuje cztery późniejsze commity zmieniające dokumentację i materiały dostawy/odbioru; brak zmian kodu wykonawczego i testów.
- Sprawdzony zapis odbioru 0.15.0 odnotowuje 13/13 kroków A i 6/6 B, zmianę C04 z wyłączeniem C02, odczyt po zapisie, brak ponownego zapisu przy replay, dziennik i Undo.
- Pierwotna bramka wymieniała konflikt po ręcznej edycji. Aktualny status wyraźnie wyłącza ręczną edycję UI podczas aktywnego planu z zawężonego odbioru. Tego wymagania nie można oznaczyć jako spełnionego.

To przegląd dokumentacji, wybranych modułów kodu, testów i istniejących dowodów. Nie uruchamiałem Allplana ani ponownie pakietu testowego. Połączenie git w środowisku nie działało z powodu niedostępnego proxy; pliki gałęzi i metadane odczytałem przez konektor GitHub, przypinając odczyty kodu do HEAD.

Źródła: [aktualny status](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/docs/validation-status.md), [pierwotny plan na main](https://github.com/blandjelly/allplan-mcp-server-python/blob/75e80bd65f678fce0c1a5eeafae07d3f3778883b/docs/implementation-plan.md), [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2), [CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38181795091), [odbiór 0.15.0](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/evaluation-packages/0.15.0/native-acceptance/20261012-owner/inspection.json).

## 2. Uzgodniony cel

- Polecenia w języku naturalnym w lokalnym Codexie połączonym przez MCP z Allplanem 2026.
- Domyślny zakres: otwarte rysunki modelu. Cały projekt wyłącznie na wyraźne polecenie.
- Wyszukiwanie i zaznaczanie ścian, słupów, stropów, belek, drzwi i okien.
- Zmiany zarówno natywnych właściwości, np. materiału, jak i wskazanych atrybutów.
- Pierwsze kompletne polecenia: ściany o grubości <24 cm → materiał beton C35; słupy bez odporności ogniowej → warstwa W1.
- Użytkownik określa intencję i obserwuje rezultat. Codex ustala identyfikatory API, jednostki, słowniki i przygotowuje diagnostykę; użytkownik nie pisze JSON/Pythona.

## 3. Luka między M3 a celem

| Obszar | Stan M3 | Potrzebne rozszerzenie |
| --- | --- | --- |
| Wyszukiwanie | Typowane filtry, AND/OR/NOT, atrybuty po ID, stronicowanie i komplet wyników w zadanym zakresie | Nazwy i aliasy właściwości, natywna grubość, nowe rodziny, czytelny domyślny zakres |
| Zaznaczenie w UI | Query i audit nie zaznaczają ani nie podświetlają | Oddzielna usługa prezentacji wyników i sprawdzenie natywnej selekcji |
| Zapis | Istniejące tekstowe mark/status oraz warstwa, Column roots, jeden foreground file | Typowane atrybuty, dodanie brakującego, inne rodziny, natywne właściwości |
| Planowanie | Propozycje powstają z findings audytu | Edycja dowolnego poprawnego elementu spełniającego filtr, bez sztucznego naruszenia reguły |
| Geometria filtra | Wymiary osiowej obwiedni | Rzeczywiste parametry, np. grubość ściany i warstw, przekrój elementu |
| Skala | Do 32 zmian w executorze, odbiór jednej/dwóch; odczyt 5 s/4 MiB, domyślnie 5000 adapterów | Wieloplikowe partie, pełna informacja o pokryciu, pomiary wydajności |
| Historia | Dziennik do 128 rekordów, replay i kontrolowane recovery | Życie dziennika, tożsamość kopii projektu, dłuższa praca, szersze przypadki przerwania |

Ograniczenia zapisu są jawne w `repair_execution.py:evaluation_scope` i `native_repairs.py:resolve`; `repair_models.py` dopuszcza wybory napraw mark/status/layer. `model_repair.py` buduje zmiany, przechodząc po findings. `native_readers.py` udostępnia geometrię obwiedni i nie deklaruje drzwi/okien w zestawie obsługiwanych rodzin.

Źródła: [kontrakt odczytu](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/docs/tool-reference.md), [kontrakt M3](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/docs/m3-execution-contract.md), [planer](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/python_host/PythonPartsScripts/PythonHost/model_repair.py), [executor](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/python_host/PythonPartsScripts/PythonHost/repair_execution.py).

## 4. Architektura docelowa

Przepływ: polecenie → rozpoznanie zakresu/właściwości → query → zaznaczenie → dokładny plan → ponowna walidacja → zapis → odczyt wyniku i raport.

Zachować istniejący podział: Codex → serwer FastMCP → bridge → dispatcher wątku UI → API Allplana. Cała praca na natywnych adapterach pozostaje w hoście. Model językowy dobiera typowane operacje; nie generuje dowolnego kodu wykonywanego w Allplanie jako normalnej ścieżki użytkowej.

Proponowane kontrakty, do zaprojektowania przed implementacją:

| Narzędzie/usługa | Rola |
| --- | --- |
| `get_model_context` | Jawne otwarte pliki, stany edytowalności, możliwości i braki pokrycia |
| `model_properties` — nowe | Katalog nazw/ID, typów, jednostek, enumów, właścicieli i sprawdzonych możliwości odczytu/zapisu |
| `model_query` — rozszerzenie | Typy semantyczne, właściwości natywne, atrybuty, pełny zbiór i wyłączenia |
| `model_selection` — nowe | Wyświetlenie wyników, zaznaczenie/podświetlenie z jawnym trybem, wyczyszczenie, ewentualny zoom |
| `rule_based_edit` — rozszerzenie | Preview/apply/revalidate/recover na wybranych elementach, niezależnie od findings |
| `fix_model_issues`, `apply_office_standard` | Zachowane specjalizacje korzystające ze wspólnego planera i executora |

Plan musi wiązać zakres, kryterium, dokładne cele i wyłączenia, właściciela właściwości, stare/nowe wartości i wersję obsługującego adaptera. Podświetlenie ani aktualna strona wyników nie uprawniają do zapisu. Zmiana modelu lub zestawu celów wymaga ponownej walidacji; nowe pasujące obiekty nie mogą po cichu wejść do zatwierdzonego planu.

Interakcja: „znajdź i zaznacz” kończy się selekcją. Jawne „następnie zmień” określa intencję zapisu; docelowo może uruchamiać cały łańcuch bez dodatkowych pytań, gdy cel jest jednoznaczny i obsługa zaakceptowana. Sam preview pozostaje zawsze dostępny. Pytanie jest potrzebne przy realnej niejednoznaczności właściwości, materiału albo warstwy ściany. Obecny tryb ewaluacyjny M3 zachowuje swoje wymagania do czasu zaprojektowania i odbioru nowego kontraktu.

## 5. Kolejność prac i kryteria odbioru

### K0 — uporządkowanie podstawy M3

Zachować bounded acceptance i historyczne dowody. Przed scaleniem uruchomić wymagany pełny zestaw i macierz sześciu środowisk na finalnym kandydacie, zgodnie z testing-policy. Ujednolicić informacje po integracji; nie oznaczać pierwotnego szerszego gate jako PASS. Scalanie i publikacja nie są częścią wykonanej analizy.

Odbiór: spójny status wersji/zakresu, finalne CI i lista ograniczeń. Nie powtarzać zakończonych testów natywnych bez zmiany zachowania. Ta praca może być przygotowywana niezależnie od prób API M4.

### K1 / M4.1a — katalog właściwości i rodzin

Zbudować rejestr wsparcia: build Allplana × rodzina/wariant × właściwość × read/replace/add/native-update. Oddzielić dostępność symbolu API od udowodnionej obsługi. Nazwy polskie/angielskie mapować na identyfikatory uzyskane z metadanych projektu. Nie zgadywać ID na podstawie tekstu.

Rozdzielić `native.material`, atrybut materiału/klasy betonu, powierzchnię wizualną oraz warstwę organizacyjną. Dla atrybutów zachować typ, enum, jednostkę, możliwość dodania i właściciela. „C35” rozwiązać przez rzeczywisty katalog/profil; nie zamieniać samowolnie na inną klasę ani tekst w przypadkowym polu.

Odbiór: Codex wyjaśnia jednoznacznie, jakie pole zmieni; potrafi wskazać read-only/unsupported/unknown i nie deklaruje zapisu na podstawie samego odczytu. Pierwsze próby obejmują słup i prostą ścianę.

### K2 / M4.1b — poprawne filtrowanie i widoczne zaznaczanie

Domyślne `open_drawings` rozwiązać do jawnej listy otwartych rysunków oraz ich stanów. Uwzględnić rozróżnienie odczytu i zapisu: otwarty pasywnie plik może być widoczny dla wyszukiwania, ale nie edytowalny. Nigdy nie zgłaszać pełnego pokrycia dla niedostępnych danych.

Dodać semantyczne `wall.total_thickness` oraz oddzielne właściwości warstw. Przeliczać 24 cm na 240 mm, zachować ścisłe `<`; dokładnie 240 mm ma być poza wynikiem. Nie używać `size_x_mm`/`size_y_mm` jako zamiennika grubości. Dla braku atrybutu rozróżniać absent, null, pustą wartość, undefined i błąd odczytu; „nieodczytany” nie znaczy „brak”.

Wczesny eksperyment UI ma oddzielnie sprawdzić podświetlenie i natywną selekcję. API 2026 dokumentuje `HighlightService.HighlightElements`, lecz podświetlenie nie dowodzi stanu natywnego zaznaczenia. Jeżeli interaktor uniemożliwia wymaganą selekcję, zaplanować zmianę współpracy z UI i jawnie oznaczyć wynik; samo podświetlenie nie zamyka wymagania użytkownika.

Odbiór: poprawny pełny zbiór również dla ścian obróconych, wyniki na wielu stronach zaznaczone w całości, brak zmiany danych, poprawne usuwanie zaznaczenia i dalsze działanie MCP. Wynik raportuje `matched`, `selected/highlighted`, `not_visible`, `unreadable`, `not_editable`.

### K3 / M4.2a — edycja z kryterium, pierwszy kompletny scenariusz

Rozdzielić wspólny ChangePlan od obowiązku posiadania findings. Przenieść zachowane kontrole M3 do wspólnej ścieżki edycji; nie obchodzić executora ani nie tworzyć sztucznych błędów audytu.

Pierwszy pionowy przebieg: słupy bez odporności ogniowej → zaznaczenie → przypisanie istniejącej warstwy W1. Odkryć właściwy atrybut, rozwiązać W1 do jednoznacznego zasobu i pokazać elementy nieedytowalne. Nowa warstwa tylko na osobne, jawne polecenie. Zacząć od jednego aktywnego rysunku, następnie rozszerzyć.

Odbiór: zmieniają się dokładnie znalezione i dopuszczone słupy, ich inne pola pozostają bez zmian; wyłączenia zachowane, odczyt po zapisie i Undo sprawdzone w Allplanie. Ponowne polecenie daje no-op tam, gdzie wartość już jest poprawna, a ponowienie tego samego execution ID nie wywołuje setterów.

### K4 / M4.2b — atrybuty i natywny materiał

Dodać typowane zmiany istniejących atrybutów oraz oddzielnie udowodnione dodawanie brakujących. Obsłużyć typy udostępnione i zapisywalne przez API, początkowo tekst, liczby i enumy. Pole wyliczane/systemowe nie staje się zapisywalne tylko dlatego, że daje się je odczytać.

Drugi pionowy przebieg: ściany o całkowitej grubości <240 mm → zaznaczenie → natywny materiał beton C35. Oddzielny wariant tego samego testu dotyczy jawnie wskazanego atrybutu. Zacząć od ścian jednowarstwowych; wielowarstwowe wymagają ustalenia, która warstwa ma otrzymać materiał. Nie nadpisywać izolacji/wykończenia na podstawie domysłu.

Odbiór: właściwe pole w UI oraz API ma nową wartość, geometria, otwory, połączenia, pozostałe warstwy i nieobjęte cele są zachowane; sprawdzone readback, no-op, replay i Undo. Natywna ścieżka modyfikacji wymaga potwierdzenia dla konkretnego typu/builda; opis `SetMaterial` nie dowodzi kompletnej bezpiecznej aktualizacji istniejącego obiektu.

### K5 / M4.2c — wszystkie sześć rodzin

| Rodzina | Szczególne rozróżnienia i testy |
| --- | --- |
| Ściany | Proste/obrócone, wielowarstwowe, właściwości całości i warstwy; krzywoliniowe po osobnej próbie |
| Słupy | Zwykły słup i Structural Framing jako osobne warianty; przekrój zamiast obwiedni |
| Stropy | Jedno-/wielowarstwowe, grubość, poziomy, materiał, właściwość właściwego właściciela |
| Belki | Zwykła belka i Structural Framing osobno; przekrój, materiał, zachowanie powiązań |
| Drzwi | Rozróżnić otwór drzwiowy i wstawiony obiekt/SmartPart/makro; nie przechodzić automatycznie do ściany nadrzędnej |
| Okna | Rozróżnić otwór okienny i wstawione okno; oddzielna tożsamość i właściciel atrybutu |

Odbiór każdej rodziny: wyszukiwanie, selekcja, odczyt atrybutów, sprawdzone zmiany atrybutów i warstwy, potwierdzone wybrane właściwości natywne oraz jawna lista pozostałych ograniczeń. Import IFC/obiekt ogólny sklasyfikowany jako ściana nie otrzymuje automatycznie uprawnień natywnej ściany.

### K6 — wiele rysunków i praca biurowa

Dla otwartych rysunków zaprojektować manifest całej operacji i ograniczone deterministyczne partie. Nie wystarczy podnieść limitu 32: trzeba uwzględnić koszt skanu, ponownych odczytów, timeouty, TTL, wielkość odpowiedzi i pojemność dziennika. Zmiany wcześniejszych partii rozróżniać od edycji zewnętrznej. Zapisywać tożsamość partii przed wysłaniem.

Przed regularnym użyciem: stabilna identyfikacja oryginału/kopii projektu, restart/reopen, kontrolowany konflikt z edycją ręczną, historia pełna/uszkodzona, bezpieczna archiwizacja/migracja dziennika. Usuwanie execution IDs nie może służyć za zwalnianie miejsca. Nie obiecywać atomowości wielu plików ani jednego Undo bez dowodów.

Odbiór: reprezentatywna kopia projektu, oba scenariusze na wielu otwartych plikach, prawidłowe wyjątki i wyniki częściowe, utrata odpowiedzi bez powtórzenia zapisu, mierzalna wydajność. Testować >32 zmian i >200 wyników jako nowe przypadki. Limity docelowe ustalić z pomiarów na projekcie użytkownika.

### K7 — cały projekt na wyraźne polecenie

Osobna próba enumeracji i dostępu do niezaładowanych plików oraz struktury budynku. Ujawnić plan wymaganych aktywacji/załadowań, blokady i niekompletność. Przywrócenie kontekstu pracy i koszt operacji należą do kryteriów odbioru. Brak dostępu nie może być raportowany jako zero dopasowań.

Obsługa całego projektu nie blokuje wydania użytecznej wersji dla otwartych rysunków. W obecnym API pluginu nie jest jeszcze udowodniona.

## 6. Minimalna macierz odbioru

| Test | Oczekiwany rezultat |
| --- | --- |
| Ściany 18, 23.9, 24, 25 cm, również obrócone | `<24 cm` wybiera wyłącznie 18 i 23.9; zmiana jednostek UI nie zmienia wyniku |
| Brak/pusta/undefined/poprawna/nieodczytana odporność ogniowa | Wynik zgodny z jawną polityką braków; nieodczytane osobno |
| Natywny materiał i atrybut materiału | Zmienione dokładnie żądane pole; żadnego podstawienia znaczenia |
| Ściana wielowarstwowa | Jawny wybór zakresu materiału; inne warstwy zachowane |
| Drzwi i okno w ścianie | Poprawny element i właściciel pola; ściana nie staje się przypadkowym celem |
| Element poprawny wg audytu | Może być edytowany przez niezależny filtr |
| Wyłączenie jednego elementu, wiele stron | Dokładny pełny zbiór z zachowanym wyłączeniem |
| Pasywny/zablokowany rysunek lub warstwa | Wyszukiwanie i edytowalność rozliczone oddzielnie |
| Zmiana danych lub nowy pasujący obiekt między preview/apply | Konflikt/ponowny plan, bez rozszerzenia zakresu po cichu |
| Replay, timeout, restart, częściowe wykonanie | Historyczny wynik lub jawne unknown; brak automatycznego ponowienia setterów |
| Undo po zmianie atrybutu/natywnej właściwości | Model i obserwacje zgodne; historia nadal zachowuje tożsamość wykonania |
| Wiele plików, >32 zmian, >200 wyników | Kompletność i partie sprawdzone, raport obejmuje całą operację |

Testy przenośne weryfikują semantykę i granice kontraktów. Testy Windows/Allplan weryfikują natywną selekcję, zapis i Undo. Każdy nowy adapter wymaga krótkiego scenariusza w konkretnej wersji, bez automatycznego powtarzania wcześniejszych zaakceptowanych bramek.

## 7. Rekomendowana najbliższa dostawa

Pierwsza dostawa powinna połączyć K1, K2 i K3: rozpoznanie odporności ogniowej oraz warstwy W1, filtrowanie słupów, widoczne zaznaczenie i zmianę warstwy przez wspólny mechanizm M3 w jednym edytowalnym pliku. To najszybciej sprawdzi cały zamierzony sposób pracy.

Następna: K4 dla prostych ścian i obu sposobów zapisu materiału. Potem K5/K6 dla sześciu rodzin i otwartych rysunków. Generowanie konstrukcji/fundamentów, arkusze i eksporty z dawnej roadmapy odłożyć do czasu osiągnięcia tego celu. Terminy oszacować po próbach natywnej selekcji i materiału; obecne dowody nie uzasadniają stałej daty ukończenia.

## 8. Podstawa API i dalszej dokumentacji

- [Roadmapa biurowa repozytorium](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/docs/office-project-roadmap.md): już priorytetyzuje M4.1–M4.2 przed generacją; ten plan rozwija zakres o konkretne polecenia i wszystkie rodziny użytkownika.
- [Polityka testów](https://github.com/blandjelly/allplan-mcp-server-python/blob/bc421959e0e488b38867816ee6ec953f680580db/docs/testing-policy.md): walidacja proporcjonalna do zmiany i pełna macierz przed integracją/wydaniem.
- [Allplan 2026: właściwości ściany](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/WallProperties/): GetThickness i GetWallTierProperties jako punkty startowe prób właściwości.
- [Allplan 2026: HighlightService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/HighlightService/): udokumentowane podświetlenie; nie jest samo w sobie dowodem natywnej selekcji.
- [Allplan 2026: ElementsAttributeService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/): odczyt i zmiany atrybutów; dodawanie/własność wymagają prób dla danego obiektu.
- [Allplan 2026: modyfikowanie elementów](https://pythonparts.allplan.com/2026/manual/features/model_access/element_modification/): odrębna ścieżka modyfikacji właściwości obiektu; zastosowanie wymaga dostępnego reprezentanta konkretnego typu.
- [Allplan 2026: ArchBaseProperties](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_ArchElements/ArchBaseProperties/): natywny materiał i pozostałe właściwości architektoniczne.
- [Allplan 2026: rodzaje elementów](https://pythonparts.allplan.com/2026/manual/features/allplan_elements/): rozróżnienie podstawowych komponentów i otworów związanych z rodzicem.

Dokumentacja API wskazuje możliwe mechanizmy. Nie zastępuje odbioru natywnego i nie stanowi gwarancji zapisu wszystkich pól dla wszystkich reprezentacji obiektów.
