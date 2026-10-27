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
| 1 — dostawa i recovery: częściowo potwierdzone | Źródło 0.40.0 `fca3da98` przeszło CI Windows/Ubuntu 3.12, package i `ci-required`; health potwierdza ten commit i integralność zainstalowanego bridge’a. Exact ZIP/upgrade/restore pozostają niepotwierdzone. Inspekcja 31 rekordów już wykonana: `87a…` jest `stopped/reconciled`, verified, `requires_recovery=false`, bez dowodu applied/preservation; `4388…` nie występuje w 31 wynikach, archiwum nieustalone. Nie odtwarzać tej inspekcji bez nowej przesłanki ani odebranych zapisów. [Status i następny krok](next-model-handoff.md). |
| 2 — natywny materiał Beam/Slab/MultiSlab: otwarte | Odczyt 0.40.0 na obu SkeletonBeam i MultiSlab: native Material dokładnie `" "`, atrybut 508 `TEST1` w obu trybach; owner zapisu i trwałość nieustalone. Discovery po konfliktach zapytania i różne view celu/krawędzi rodzica SkeletonBeam 1 pozostają otwarte. Dokładny child Slab jest zablokowany `probe_scope_unavailable`, przyczyna natywna nieustalona. Kandydat 0.41.0 dodaje odczyt przez jawnego rodzica; po CI/exact ZIP tylko zachowany child z `parent_ref`, `include_parent=true`, ID 508 i trace. Nie ponawiać trzech udanych sond ani setterów. [Szczegóły](next-model-handoff.md). |
| 3 — atrybuty Slab/MultiSlab: zgłoszony PASS wartości | Raportowany Apply/readback PASS z 0.39.0 pozostaje, ale historyczne payloady/owner binding brakują. Odczyt 0.40.0 i dalsze ograniczenia są w [handoffie](next-model-handoff.md); child read nadal blocked. Zachować `target.property_owner="selected_element"`, lineage/children i overlap guard; nie utożsamiać atrybutu z native Material. |
| 4 — warstwa i no-op: częściowo odebrane | Zachować W1 read/write, pojedyncze Undo i zgłoszony no-op w ich dotychczasowym zakresie. Pozostałe pary rodzina/właściciel oraz grupowe Undo wymagają dowodu; poniżej kryteria zamknięcia. No-op nie ma drogi Apply. |
| 5 — delete i selekcja: częściowo odebrane / brak funkcji | Zachować grouped Column delete/Undo i obserwację Wall subtree. Inne deklarowane rodziny/poddrzewa wymagają dowodu. [Analiza API selekcji](m4-native-selection-api.md) rozdziela programowe set/clear/readback od interactive pick i preselekcji. Brak potwierdzonego kompletnego kontraktu; native selection nadal unsupported, highlight nie zamyka selekcji. |
| 6 — typy i rodziny | Domknąć owner-specific roundtrip oraz macierz rodzin/typów. Column Enum `Status` ID 49 pozostaje BLOCKED (`<niezdefiniowany>`, brak potwierdzonej etykiety). Wall CheckBox ID 1371 nie ma surowego Apply; fixture SDK Boolean brak. Inne typed attribute gaps rodzin wymagają osobnych dowodów. Date/vector/object wymagają dokładnych kontraktów setter payload i typed readback; sam symbol lub konstruktor SDK nie wystarcza. |

### Dowody potrzebne do zamknięcia punktów 1–5

Punkty odnoszą się do pojedynczego aktywnego rysunku i istniejącego limitu
1–32 zmian. Podsumowanie wyników i ograniczeń jest w [statusie walidacji](validation-status.md#latest-owner-observations).
[Załącznik 0.39.0](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md)
i [porównanie 2026-10-27](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md)
pozostają zachowane; siedem plików dowodowych 0.40.0 skopiowano bez zmian do
[test-results/evidence/0.40.0-2026-10-27](test-results/evidence/0.40.0-2026-10-27/).
Zachować zgłoszone PASS, uzupełniać wyłącznie brakujący dowód lub zmieniony
przepływ; nie powtarzać zakończonych Apply dla samego odtworzenia logu.

1. **Dostawa i recovery:** CI i powiązanie źródła z bridge’em 0.40.0 są
   potwierdzone. Pozostaje wskazać dokładny ZIP/hash i wymagane wyniki instalacji,
   upgrade/restore. `inspect_journal` zwrócił kompletne 31 rekordów bez nowych
   blockerów; nie powtarzać go dla samego odtworzenia dowodu. Zachować pierwotne
   wyniki i późniejsze uzgodnienie `87a…`, bez rozszerzania go na applied lub
   preservation. Nieobecność `4388…` w tej inspekcji nie rozstrzyga archiwum.
   Zamknięcie wymaga rozliczenia dostawy i każdej nadal istotnej sprawy o
   nieznanym wyniku, bez ponawiania setterów.
2. **Natywny materiał Beam/Slab:** odczyty obu ścieżek na SkeletonBeam i
   MultiSlab już wykonano; wartości i ograniczenia są w [handoffie](next-model-handoff.md).
   Osobny odczyt child Slab nadal jest zablokowany; 0.41.0 dodaje wskazaną tam
   ścieżkę przez dokładnego rodzica. Dla zwykłego Beam nie ustalono fixture
   (`fixture_missing`). Następna próba właściciela obejmuje tylko zachowany
   child z `parent_ref`, `include_parent=true` i ID 508, po CI i weryfikacji ZIP.

   Każda zmieniona natywna ścieżka zapisu wymaga świeżego preview, przejrzanego
   Apply na dokładnym właścicielu, świeżego odczytu/UI, dowodu zachowania
   geometrii, poziomów, połączeń i składników oraz Undo/odtworzenia. No-op,
   drift i replay nie mogą uruchamiać dodatkowych setterów. Dla unsupported
   SDK trzeba podać dokładny typ/build i jawny zakres produktu, bez cichego
   zastąpienia atrybutem. Zachować PASS Wall/Column oraz niepotwierdzone
   preservation/Undo.
3. **Atrybuty Slab/MultiSlab:** zachować zgłoszony PASS wartości 0.39.0.
   Brakuje dokładnych historycznych payloadów Apply, powiązania właścicieli,
   kolejności grupowania oraz Undo/odtworzenia. Nie wyciągać wniosków o
   dopuszczalności nakładających się celów parent/child. Odczyt 0.40.0 opisuje
   [handoff](next-model-handoff.md); nie ponawiać udanych zapisów dla odtworzenia
   dowodu. Zamknięcie wymaga istniejących dokładnych payloadów lub osobno
   uzasadnionego zmienionego przepływu, z zachowaniem blokad overlap, stale i replay.
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

