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
| 1 — dostawa i recovery: otwarta blokada | Właściciel potwierdził CI i ZIP 0.42.1; health wiąże instalację z `eecdfeb`, integrity verified. Szczegółowa tożsamość ZIP i upgrade/restore nie są niezależnie zweryfikowane. Wall `3f2a8c9d7b5e4a1c9f8e6d3c2b1a0e9f` rozliczony przez reviewed reconciliation, preservation=false. Slab `a8a31c72975541feb1c36a2e8cbb8f65` pozostaje unknown/recovery_required; nie ponawiać Apply ani usuwać journalu. Zachować starsze historie `87a…` i `4388…` opisane w handoffie. |
| 2 — native Material Beam/Slab/MultiSlab: konflikt exact inventory | Preview 0.42.1 potwierdza właściwy raport native owner; highlight API wysłany. Apply i recovery zatrzymane na konflikcie inventory/parent edge, brak odbioru zapisu/preservation/Undo. Następny krok: diagnoza porównania exact inventory przy fresh_resolve, bez nowego settera i bez osłabiania guardów. [Dowód i ograniczenia](next-model-handoff.md#latest-version-and-native-evidence). |
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
2. **Native Material Beam/Slab:** 0.41.0 getter-only PASS dla wskazanego Slab
   child i osobnego immediate parent pozostaje ograniczony do odczytu; oba
   zwróciły native Material `" "` oraz ID 508 `TEST1`, zero setterów.
   `target_in_direct_scan=false` dotyczy exact child/view sondy i nie diagnozuje
   semantic edit scan ani SelectAll. Kod już obsługuje selected Slab
   `SlabProperties` z bezpośrednim MultiSlab parent; brakującą częścią było
   jawne dokładne targetowanie w edit lifecycle, nie setter ani `slab_write_blocker`.

   Kandydat 0.42.0 dodaje `exact_target={drawing_file,model_uuid,view_uuid,
   parent_ref:{model_uuid,view_uuid}}` wyłącznie dla jednego native Material
   targetu, jednego foreground drawing, `native_types=["Slab_TypeUUID"]`, bez
   predicate, attribute IDs i exclusions. Zachowuje pełny inventory direct
   scan i włącza jawnie odnalezione dziecko tylko w tym opt-in. Plan wiąże exact
   target oraz fingerprint inventory/krawędzi; helper powtarza bounded
   enumerację na preview, revalidation, Apply preflight i final setter boundary.
   Highlight weryfikuje exact target, po czym prezentuje wszystkie
   reprezentacje tego dziecka po model UUID, nigdy parent. Fresh readback i
   recovery wymagają tego samego exact inventory/view; zmieniony lub
   odtworzony w innym view target pozostaje unknown, bez fallbacku. Diagnostic
   resolver nie jest sam write authorization.

   **Próba 0.42.1:** [surowy log](test-results/evidence/0.42.1-2026-10-27/allplan-0421-native-test-evidence.json)
   potwierdza poprawiony raport `native_material_ownership` i dwa wysłania
   highlight po jednym modelu/adapterze; widoczność UI niepotwierdzona.
   Pierwszy Apply blokował starszy Wall unknown, następnie rozliczony przez
   reviewed reconciliation bez dowodu preservation. Drugi Apply Slab,
   `a8a31c72975541feb1c36a2e8cbb8f65`, kończy się unknown/repair_conflict
   na `fresh_resolve`: `Exact child inventory or parent edge changed.`
   Recovery powtarza konflikt na `recovery_resolve` i utrzymuje blokadę zapisu.
   Brak dowodu udanego Apply/readback, preservation i Undo/restoration.
   Zgodność obu odczytów materiału w preflight nie dowodzi zgodności inventory;
   sam komunikat nie rozstrzyga rzeczywistego driftu ani błędu porównania.

   Następne zadanie: ustalić różniące się dane inventory/krawędzi w resolverze,
   zachować exact views/owner, revalidation, trace/journal i unknown recovery.
   Nie ponawiać Apply ani kasować journalu. Warunek dalszego trialu: uzasadniona
   zmiana przepływu, focused regression checks oraz rozliczenie bieżącego unknown;
   wymagane nadal fresh readback/UI, preservation i Undo/restoration dla nowej
   próby. CI/ZIP potwierdzone przez właściciela; zakres dostawy i wcześniejsze
   focused checks w handoffie. Zwykły Beam pozostaje `fixture_missing`.
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

