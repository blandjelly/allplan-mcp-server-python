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
| 1 — dostawa i recovery: częściowo potwierdzone | Dla źródła 0.41.0 `f775168aaf8fdb043c269ff09d6ffda9fcea17c9`, merged PR #47 / `dd741fa`, GitHub run `40550057327` potwierdza sukces configuration, Windows/Ubuntu Python 3.12, package i `ci-required`; wcześniejszy run `40549970082` był nieudany. Raport odnotowuje potwierdzenie poprawności CI/ZIP przez właściciela, ale dokładny zainstalowany ZIP i upgrade/restore nie są niezależnie zweryfikowane. Health wiąże bridge z `f775168aaf8fdb043c269ff09d6ffda9fcea17c9`, integrity verified. Zachować historię `87a…` (`stopped/reconciled`, `requires_recovery=false`, bez dowodu applied/preservation) i `4388…` (brak w 31 rekordach nie ustala archiwum); nie powtarzać inspekcji bez nowej przesłanki ani setterów. [Status i następny krok](next-model-handoff.md). |
| 2 — native Material Beam/Slab/MultiSlab: exact-target binding otwarte | Getter-only PASS 0.41.0: exact Slab child i osobny immediate MultiSlab parent zwróciły Material `" "` oraz ID 508 `TEST1` w obu trybach. Próba była complete dla żądanego scope, `usable_for_write=false`, zero setterów; nie dowodzi writable ownera, wspólnego storage, persistence ani równoważności child/parent. `target_in_direct_scan=false` dotyczy tylko dokładnego view sondy; nie dowodzi utraty modelu przez semantic scan ani przyczyny SelectAll. Kod material edit już obsługuje selected Slab properties, bez blokady `slab_write_blocker`; brakującym kontraktem jest jawny exact target child+parent przez preview→revalidation→Apply. Zaprojektować bounded resolution/checks na każdym etapie, zachować identyczność view/lineage, overlap, replay i read-only unknown recovery. Po negative/stale checks, wymaganym CI i exact ZIP dopiero jeden natywny trial na disposable fixture z exact-owner preview/Apply/readback, preservation i Undo. Nie powtarzać historycznych setterów. [Szczegóły](next-model-handoff.md). |
| 3 — atrybuty Slab/MultiSlab: zgłoszony PASS wartości, owner niepełny | Raportowany Apply/readback PASS z 0.39.0 pozostaje, ale historyczne payloady i exact owner binding brakują. Getter 0.41.0 ID 508 `TEST1` na child i parent nie przypisuje właściciela historycznego zapisu ani nie dowodzi sprzężenia z native Material. Zachować `target.property_owner="selected_element"`, lineage/children i overlap guard; nie utożsamiać atrybutu z native Material. Nie ponawiać accepted writes dla odtworzenia dowodu. |
| 4 — warstwa i no-op: częściowo odebrane | Zachować W1 read/write, pojedyncze Undo i zgłoszony no-op w ich dotychczasowym zakresie. Pozostałe pary rodzina/właściciel oraz grupowe Undo wymagają dowodu; poniżej kryteria zamknięcia. No-op nie ma drogi Apply. |
| 5 — delete i selekcja: częściowo odebrane / brak funkcji | Zachować grouped Column delete/Undo i obserwację Wall subtree. Inne deklarowane rodziny/poddrzewa wymagają dowodu. [Analiza API selekcji](m4-native-selection-api.md) rozdziela programowe set/clear/readback od interactive pick i preselekcji. Brak potwierdzonego kompletnego kontraktu; native selection nadal unsupported, highlight nie zamyka selekcji. |
| 6 — typy i rodziny | Domknąć owner-specific roundtrip oraz macierz rodzin/typów. Column Enum `Status` ID 49 pozostaje BLOCKED (`<niezdefiniowany>`, brak potwierdzonej etykiety). Wall CheckBox ID 1371 nie ma surowego Apply; fixture SDK Boolean brak. Inne typed attribute gaps rodzin wymagają osobnych dowodów. Date/vector/object wymagają dokładnych kontraktów setter payload i typed readback; sam symbol lub konstruktor SDK nie wystarcza. |

### Dowody potrzebne do zamknięcia punktów 1–5

Punkty odnoszą się do pojedynczego aktywnego rysunku i istniejącego limitu
1–32 zmian. Podsumowanie wyników i ograniczeń jest w [statusie walidacji](validation-status.md#latest-owner-observations).
[Załącznik 0.39.0](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md)
i [porównanie 2026-10-27](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md)
pozostają zachowane; surowe dowody getter-only PASS 0.41.0 są w
[test-results/evidence/0.41.0-2026-10-27](test-results/evidence/0.41.0-2026-10-27/).
Zachować zgłoszone PASS, uzupełniać wyłącznie brakujący dowód lub zmieniony
przepływ; nie powtarzać zakończonych Apply dla samego odtworzenia logu.

1. **Dostawa i recovery:** dla źródła 0.41.0 CI, package i `ci-required`
   potwierdza run `40550057327`; raport odnotowuje potwierdzenie poprawności
   CI/ZIP przez właściciela, ale exact installed ZIP identity i upgrade/restore
   pozostają niezależnie niezweryfikowane. Health wiąże installed bridge z commitem
   `f775168aaf8fdb043c269ff09d6ffda9fcea17c9`, integrity verified. Inspekcja
   31 rekordów już wykonana: `87a…` pozostaje stopped/reconciled bez dowodu
   applied/preservation; brak `4388…` w tych rekordach nie ustala archiwum.
   Nie powtarzać inspekcji bez nowej przesłanki, nie usuwać journalu ani nie
   ponawiać setterów. Zamknięcie wymaga rozliczenia delivery i nierozliczonych
   unknown outcomes.
2. **Native Material Beam/Slab:** getter-only Slab child + osobny bezpośredni
   parent probe 0.41.0 jest PASS tylko dla odczytu wskazanych refs/views
   i wartości z handoffu; raw files zachowuje katalog evidence 0.41.0.
   `target_in_direct_scan=false` dotyczy tego exact child/view probe, nie
   diagnozuje semantic scan ani SelectAll. Kod natywnego materialu już
   obsługuje selected Slab adapter i jego `SlabProperties`; luka nie dotyczy
   `SetMaterial` ani `slab_write_blocker`, lecz braku osobnego jawnego
   exact-target contract w `model_edit` (request obecnie jest predicate-based).
   Zaprojektować i implementować ograniczone wiązanie exact child+parent w
   preview, revalidation, Apply preflight i fresh readback. Każdy etap ponownie
   potwierdza refs/views, bez przekierowania do rodzica ani rozszerzania
   predicate; zachować limity enumeracji, fingerprint, overlap, stale, journal,
   replay i unknown safeguards. Diagnostic resolver nie nadaje write authority.
   Dodać focused negative checks: missing/stale/conflicting parent/child,
   view drift, niepełne lub rozbieżne wrappers, overlap, replay; unknown recovery
   pozostaje read-only dla tego samego execution ID. Przed natywnym zapisem
   wymagane są te kontrole, full CI i exact ZIP verification. Następnie jeden
   reviewed exact-owner trial na disposable fixture: preview, Apply, świeży
   readback/UI, preservation geometrii/poziomów/połączeń/składników oraz Undo
   i odczyt przywrócenia. Nie powtarzać historycznych setterów. Zwykły Beam
   pozostaje `fixture_missing`; nie rozszerzać wyniku na rodzinę Beam.
3. **Atrybuty Slab/MultiSlab:** zachować zgłoszony PASS wartości 0.39.0.
   Brakuje dokładnych historycznych payloadów Apply i powiązania właścicieli,
   kolejności grupowania oraz Undo/odtworzenia. Getter 0.41.0 ID 508 na
   exact child i parent nie ustala ownera wcześniejszego Apply ani sprzężenia
   z native Material. Nie wnioskować o równoważności parent/child ani o
   dopuszczalności overlap. Nie ponawiać zapisów dla odtworzenia dowodu;
   zachować `selected_element`, complete lineage/children i overlap/stale/replay
   guards. Zamknięcie wymaga dokładnych istniejących payloadów lub osobno
   uzasadnionego zmienionego przepływu.
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

