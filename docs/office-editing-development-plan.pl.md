# Allplan MCP — plan dalszego rozwoju M4

## Aktualny stan i kolejne zadanie

M4 jest częściowo odebrane. Aktualną wersję, dostawę i konkretne następne
zadanie opisuje [handoff](next-model-handoff.md). Ten plan utrzymuje pozostałe
prace i warunki ich zamknięcia, zgodnie z [polityką dokumentacji](documentation-policy.md).

Dowody wcześniejszych prób są w [statusie walidacji](validation-status.md);
ich istotne ograniczenia zachowują poniższe zadania i handoff. Nie powtarzać
odebranych zakresów ani rozszerzać ich na inne rodziny, typy czy wersje bez dowodu.

## Cel i granice produktu

Użytkownik opisuje zamiar zwykłym językiem. Agent rozpoznaje zakres, elementy,
właściciela pola i typ wartości, pokazuje plan, ponownie go waliduje, wykonuje
obsługiwany zapis i świeży odczyt. Atrybut materiału i natywny materiał mają
odrębne powiązania API; ich ewentualne sprzężenie wymaga odczytu w danym
projekcie. Warstwa organizacyjna i wykończenie mają osobne cele zapisu.

Odczyt może obejmować jawnie wskazane otwarte rysunki; obecny Apply jest
ograniczony do jednego aktywnego rysunku i 1–32 rzeczywistych zmian.
Wieloplikowość i cały projekt wymagają osobnego projektu oraz odbioru.

## Pozostałe prace i nierozwiązane błędy

| Priorytet | Co pozostało / warunek dalszej pracy |
| --- | --- |
| 1 — dostawa i recovery: częściowo potwierdzone | 0.39.0 jest scalone; owner zgłasza uzgodnienie bieżących Wall/Column/Slab i PASS wartości Wall/Wall z otworem/Column. Końcowe CI Windows/Ubuntu 3.12, build i `ci-required` dla 0.39.0 są potwierdzone w [statusie dostawy](validation-status.md#delivery-and-ci-evidence). Brak powiązania instalacji z exact ZIP/upgrade/restore oraz pełnego journalu z ID. Pozostało ustalić rzeczywiście nierozliczone rekordy i zachować unknown/preservation; nie powtarzać odebranych zapisów. |
| 2 — natywny materiał Beam/Slab/MultiSlab: otwarte | Wcześniejsze zapytanie o materiał natywny nie znalazło belek i zgłosiło dwa konflikty reprezentacji. Odczytowe porównanie z 2026-10-27 później znalazło obie SkeletonBeam i MultiSlab, ale ujawniło rozbieżność view dla pierwszej belki: zapytanie i krawędź do rodzica wskazują różne UUID. Klasy runtime to `StructuralBeamElement`/`SlabElement`; w tym porównaniu nie odczytano materiału natywnego ani nie ustalono właściciela zapisu. Wcześniejsza próba zapisu dla Slab zakończyła się pustym odczytem materiału natywnego; właściciel pozostał nieustalony. Próba identyfikacji dziecka Slab nie zwróciła kompletnego komponentu semantycznego. Kandydat dodaje fazę odczytu wyłącznie przez gettery, by uzyskać brakujące porównanie; nie potwierdza trwałości zapisu ani nie zezwala na modyfikacje. Zachować dokładne referencje, konflikty dla każdego wrappera i wartości puste. [Porównanie API](m4-editing-api-0.32.0.md#native-material-material-attribute-and-surface). |
| 3 — atrybuty Slab/MultiSlab: zgłoszony PASS wartości | Log 0.39.0 potwierdza raportowaną wartość atrybutu na MultiSlab i jego Slab; brak surowych payloadów z ID/typem/ref/owner i readbackiem. Zachować `target.property_owner="selected_element"`, pełne lineage/children i blokadę overlap, bez redirectu. Nie traktować sukcesu atrybutu jako sukcesu materiału natywnego. |
| 4 — warstwa i no-op: częściowo odebrane | Zachować W1 read/write, pojedyncze Undo i zgłoszony no-op w ich dotychczasowym zakresie. Pozostałe pary rodzina/właściciel oraz grupowe Undo wymagają dowodu; poniżej kryteria zamknięcia. No-op nie ma drogi Apply. |
| 5 — delete i selekcja: częściowo odebrane / brak funkcji | Zachować grouped Column delete/Undo i obserwację Wall subtree. Inne deklarowane rodziny/poddrzewa wymagają dowodu. [Analiza API selekcji](m4-native-selection-api.md) rozdziela programowe set/clear/readback od interactive pick i preselekcji. Brak potwierdzonego kompletnego kontraktu; native selection nadal unsupported, highlight nie zamyka selekcji. |
| 6 — typy i rodziny | Domknąć owner-specific roundtrip oraz macierz rodzin/typów. Column Enum `Status` ID 49 pozostaje BLOCKED (`<niezdefiniowany>`, brak potwierdzonej etykiety). Wall CheckBox ID 1371 nie ma surowego Apply; fixture SDK Boolean brak. Inne typed attribute gaps rodzin wymagają osobnych dowodów. Date/vector/object wymagają dokładnych kontraktów setter payload i typed readback; sam symbol lub konstruktor SDK nie wystarcza. |

### Dowody potrzebne do zamknięcia punktów 1–5

Punkty odnoszą się do pojedynczego aktywnego rysunku i istniejącego limitu
1–32 zmian. Podsumowanie nowego logu jest w [statusie walidacji](validation-status.md#latest-owner-observations),
a [pełny załącznik](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md)
oraz [porównanie 2026-10-27](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md)
zostały umieszczone w repozytorium bez zmian, za zgodą właściciela.
Zachować zgłoszone PASS, uzupełniać wyłącznie brakujący dowód lub zmieniony
przepływ; nie powtarzać zakończonych Apply dla samego odtworzenia logu.

1. **Dostawa i recovery:** powiązać instalację 0.39.0 z konkretnym source,
   potwierdzonym CI dla końcowego head PR, dokładnym ZIP/manifestem i buildem Allplana oraz
   wymaganym upgrade/restore. Odczytać bieżący `inspect_journal`; dla każdego
   nadal unknown zachować ID, pierwotny wynik, materiał/owner, zmienione sekcje
   i wynik read-only recovery/reconciliation. Zamknięcie: znany stan wszystkich
   blokujących rekordów bieżącego workflow i rozliczone bramki dostawy.
   Reconciliation nie zmienia unknown w applied ani nie dowodzi preservation;
   otwarte różnice pozostają przypisane do konkretnego elementu.
2. **Natywny materiał Beam/Slab:** kandydat dodaje fazę odczytu tylko do
   getterów `material_comparison`. Dla dokładnego drawing/model/view, jawnej
   listy 1–16 identyfikatorów atrybutów i opcjonalnego `include_parent` ma
   zestawiać dla każdego wrappera łańcuch przodków i listę potomków, klasę natywną, ReadAll i
   ReadAllAndComputable, nazwę↔ID/typ oraz natywny materiał rodzin
   Beam/SkeletonBeam/Slab/MultiSlab. Zachować pusty materiał natywny jako zaobserwowaną
   wartość; brak w ReadAll nie dowodzi braku atrybutu, a zgodność wartości nie
   dowodzi wspólnego przechowywania. Ten odczyt nie ustala właściciela zapisu
   i nie zmienia wcześniejszych PASS. Po wdrożeniu użyć go na dokładnych
   ref/view z porównania 2026-10-27, zachowując konflikty per wrapper.
   Najpierw sprawdzić istniejące journal/trace prób Slab, by ustalić ich cel
   i wynik; nigdy nie ponawiać setterów dla unknown.
   Ordinary Beam wymaga własnego fixture, jeśli ma wejść do odbioru; obecny
   log nie dowodzi jego obecności (`fixture_missing`). Zamknięcie: wyjaśnione
   discovery dwóch SkeletonBeam, poprawiona i odebrana każda deklarowana
   ścieżka native owner → właściwy setter → świeży readback/UI, z dowodem
   zachowania geometrii, poziomów, połączeń i składników oraz odpowiednim
   Undo/odtworzeniem dla nowego przepływu. No-op, drift i replay nie mogą
   uruchamiać dodatkowych setterów. Jeśli konkretna modyfikacja SDK okaże się
   unsupported, udokumentować dokładny typ/build i uzgodnić zakres produktu;
   nie zastępować jej po cichu atrybutem. Wall/Column PASS wartości zachować;
   ich preservation/Undo nadal nie są potwierdzone przez ten log.
3. **Atrybuty Slab/MultiSlab:** uzupełnić z istniejących zapisów dokładne
   payloady i typed readback: nazwa↔ID, typ, file/model/view, wybrany owner,
   lineage/children, plan i execution. Oddzielić dowód dla aggregate od child
   i wykazać, że nie były nakładającymi się celami jednego planu. Zamknięcie:
   owner-specific roundtrip i właściwy Undo/restoration dla deklarowanego
   zakresu oraz zachowane blokady overlap, stale i replay. Po wykonanym
   zapisie atrybutu wystarczy odczytać obie ścieżki materiału, by zbadać ich
   sprzężenie; nie trzeba ponawiać odebranego zapisu. Brak payloadu w logu
   nie unieważnia owner PASS wartości ani nie dowodzi obejścia blokady.
4. **Warstwa i no-op:** macierz istniejących odczytów i braków jest w
   [statusie walidacji](validation-status.md#declared-family-and-owner-evidence-for-layer-and-delete).
   Zachować jedynie wykazane zakresy i wskazać brakujące zadeklarowane
   pary rodzina/właściciel. Dla nich potrzebne są
   dokładne cele, stara/nowa warstwa, preview/revalidation, świeży readback/UI
   i Undo z odczytem przywrócenia; jeśli wspierana jest grupa, dowód jednego
   grupowego Undo. Zamknięcie: udokumentowane pokrycie deklarowanej macierzy,
   no-op z zerem setterów i bez Apply, działający highlight/clear oraz
   zachowane konflikty po zmianie zakresu/wartości i replay. Nie rozszerzać
   wyniku pojedynczego W1/Undo na pozostałe rodziny ani grupę.
5. **Delete i selekcja:** zachować wskazaną w [macierzy](validation-status.md#declared-family-and-owner-evidence-for-layer-and-delete)
   grupową próbę Column oraz obserwację Wall subtree; dla brakujących
   zadeklarowanych rodzin/poddrzew
   potrzebne są disposable fixture, lista dokładnych ref i zależności,
   preview, usunięcie z readbackiem braku właściwego poddrzewa, zachowanie
   sąsiadów oraz Undo i odczyt odtworzenia. Zachować gotowy grouped Column
   wynik. Selekcja wymaga osobno udokumentowanego kontraktu natywnego
   set/clear/readback, implementacji i próby z porównaniem dokładnego zbioru
   w API/UI, także po clear. Zamknięcie pełnego punktu wymaga obu części;
   pozostawienie selekcji unsupported wymaga jawnej decyzji o ograniczeniu
   zakresu. Highlight, query selection cache i native selection to różne stany.
   Następny krok selekcji: ustalić kontrakt replace/clear/niezależnego readbacku
   w SDK zainstalowanego builda i wykonać [wąski eksperyment](m4-native-selection-api.md#7-minimalny-eksperyment-i-pytania-rozstrzygające).
   `GetPreSelectedElements` wymaga rozstrzygnięcia scope/lifecycle; interaktywny
   `StartElementSelect` sam nie spełnia kierunku query → dokładna selekcja UI.

Historyczne unresolved execution IDs i broad property discovery pozostają
zachowane w [statusie walidacji](validation-status.md#evidence-for-unresolved-cases);
nie kasować ich journalu ani nie wznawiać szerokiego probe.
Brak fixture oznaczać `fixture_missing`, nierozstrzygnięty kontrakt — BLOCKED.

## Skalowanie i dalsze rozszerzenia

1. Skalowanie i ergonomia MCP: [analiza i etapy S0–S5](implementation-plan.md#analiza-skalowania-developm4-i-ergonomii-mcp)
   rozdzielają większy odczyt, wykonanie ponad 32 zmian w jednym rysunku oraz
   późniejszą wieloplikowość. 200 jest limitem strony, nie całej selekcji;
   rzeczywiste bariery obejmują pełne ponowne skany, 10000 adapterów, czas,
   pamięć i dziennik. Pomiary, ergonomię i odczyt można rozwijać wcześniej;
   większe zapisy zależą od odbioru konkretnej operacji. Warunek zamknięcia:
   kompletne wyniki, mniej skanów/roundtripów potwierdzone pomiarem, trwały
   manifest/partie i restart bez powtórzonych setterów. Nie deklarować wspólnego
   Undo ani atomowości bez dowodów.
2. Osobno zaplanować cały projekt: enumerację niezaładowanych plików,
   aktywację, przywrócenie kontekstu i raportowanie niekompletności.
   Brak dostępu nie może oznaczać zera wyników.

## Kryteria zamknięcia

- Każdy nowy odebrany przepływ ma dokładny zakres, powiązanie z instalacją
  i buildem Allplana oraz świeży readback/UI/Undo odpowiedni do operacji.
  Zachować ograniczenia wcześniejszych dowodów; nie powtarzać ich prób.
- Zapytanie jawnie raportuje kompletność, właścicieli, reprezentacje,
  otwory/rodziców oraz osobno selekcję i highlight.
- Preview, revalidation, Apply, replay i recovery zachowują granice planu,
  rozliczają konflikty i nie ponawiają setterów po wyniku unknown.
- Dziennik zachowuje nierozliczone zapisy przy limitach, archiwizacji
  i restarcie. Każdy większy zakres ma odrębny odbiór.

[Polityka dokumentacji](documentation-policy.md) określa aktualizację handoffu i zadań;
[testing policy](testing-policy.md) — kontrole i budowanie.

Zbiorcza bramka CI `ci-required` jest przygotowana; właściciel musi
skonfigurować ją jako wymagany check dla `develop/m4`, zgodnie z [polityką
testów](testing-policy.md#required-github-check). Bramka nie zastępuje odbioru
ZIP ani Allplana.
[Tool reference](tool-reference.md), [API evidence](m4-attribute-api-evidence.md)
i [macierz typów](m4-attribute-type-coverage.md) pozostają źródłami kontraktów API.

