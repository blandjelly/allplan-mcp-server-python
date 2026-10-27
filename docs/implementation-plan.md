# Implementation plan

M4 development uses **develop/m4**; main integration is separate.
Read the [current handoff](next-model-handoff.md) for the version and next task,
the [office editing plan](office-editing-development-plan.pl.md) for the
backlog, and the [testing policy](testing-policy.md) for checks and builds.

## Accepted fixture baseline

| Stage | Accepted scope |
| --- | --- |
| M0 | Installation, update/restore, health/version/box tools and host lifecycle. |
| M1 | Explicit model context, typed query, selection pages, summaries, resource binding and canonical geometry. |
| M2 | Read-only audit profile, coverage, evidence and locatable findings. |
| M3 | Bounded preview/apply/revalidate, layer/status/mark repairs, stale guards, journaling, replay/readback and controlled unknown-result recovery. |

Acceptance is limited to the retained fixture and recorded scopes in
[validation status](validation-status.md). It does not establish arbitrary
multi-file writes, universal project identity or whole-project coverage.
M4 remains partially accepted; its remaining gates are maintained only in
the office editing plan.

## Later scope

Model generation, layouts, issue exports and whole-project documentation are
future work. Specify their inputs, ownership, conflicts, recovery and native
acceptance independently; they do not expand the accepted M4 scope.

## Analiza skalowania develop/m4 i ergonomii MCP

Analiza kodu z **2026-10-27 (Europe/Warsaw)**, baza `develop/m4`:
[`6cab354c437c8d08c9b8370164733e6ef13eecd7`](https://github.com/blandjelly/allplan-mcp-server-python/commit/6cab354c437c8d08c9b8370164733e6ef13eecd7),
wersja 0.39.0. Poniżej oddzielono stan zaimplementowany od propozycji.
Nie wykonano pomiarów natywnych ani nowych prób Allplana; wnioski o kosztach
wynikają z przepływu kodu, a oczekiwane przyspieszenie wymaga benchmarku.
To projekt optymalizacji, nie rozszerzenie odebranego zakresu produktu.
Priorytety produktu pozostają w [planie rozwoju](office-editing-development-plan.pl.md).

### Wniosek i znaczenie limitów

**Obsługa większych modeli jest możliwa, ale samo zwiększenie 32 i 200 nie
rozwiąże problemu.** 200 oznacza rozmiar strony odczytu, a nie maksymalną
liczbę znalezionych elementów. 32 ogranicza rozwinięte zmiany jednego Apply.
Należy osobno skalować: liczbę przeglądanych adapterów, ilość danych zwracanych
agentowi i liczbę zmian całego zlecenia. Duży model z jednym trafieniem także
może przekroczyć budżet enumeracji.

| Warstwa | Obecny kontrakt i źródło | Konsekwencja |
| --- | --- | --- |
| Strona query | Domyślnie 100, maks. 200; `QueryInput`, `PageInput` w [query_models.py](../src/allplan_mcp/query_models.py), walidacja w [query_contracts.py](../python_host/PythonPartsScripts/PythonHost/query_contracts.py). | `selection_id` i `page.next_cursor` pozwalają już pobrać ponad 200 wyników, jeśli cały scan mieści się w pozostałych budżetach. |
| Enumeracja | Domyślnie 5000, maks. 10000 **surowych adapterów**, 5 s na scan; `ModelQueryService._scan` w [model_query.py](../python_host/PythonPartsScripts/PythonHost/model_query.py). | Adaptery nie są liczbą elementów biznesowych. Licznik rośnie przed odrzuceniem plików spoza scope; samo zawężenie predicate/scope nie gwarantuje mniejszej enumeracji `SelectAllElements`. |
| Pamięć odczytu | 4 MiB sumy serializowanych rekordów `source` podczas skanu; 8 selekcji, TTL 300 s (`ModelQueryService`). | To nie jest ścisły limit RAM ani 4 MiB odpowiedzi. `source`, grupy, wyniki, hashowanie i kopie zwiększają szczyt pamięci. Cache selekcji nie ma osobnego łącznego limitu bajtów. |
| Pola i zakres | Maks. 32 atrybuty, jawny scope do 100 plików, `max_adapters` jak wyżej. | Limit atrybutów jest niezależny od limitu zmian; niezaładowane pliki nie stają się dostępne przez zwiększenie scope. |
| Plan M4 | Do 16 deklaracji `changes` w [model_edit_models.py](../src/allplan_mcp/model_edit_models.py); `preview` rozwija je na elementy i pola w [model_edit.py](../python_host/PythonPartsScripts/PythonHost/model_edit.py). | 20 elementów × 2 zmieniane pola daje 40 zmian i przekracza 32. No-op nie dodaje zmiany. Liczba zmian nie musi odpowiadać liczbie wywołań SDK, np. delete ma grupowy setter. |
| Apply | `RepairExecutor.MAX_CHANGES = 32`; limit także w kwalifikacji planu i walidacji zapisanych rekordów, [repair_execution.py](../python_host/PythonPartsScripts/PythonHost/repair_execution.py). Jeden aktywny foreground drawing. | Zmiana jednej stałej wymaga przeglądu kompatybilności dziennika, recovery i wszystkich tras M3/M4, a nie tylko większej listy requestu. |
| Cache planów | TTL 300 s, do 8 planów, 4 MiB/plan, 8 MiB łącznie, [model_repair.py](../python_host/PythonPartsScripts/PythonHost/model_repair.py). | Duże preview może nie zmieścić się w cache. Apply unieważnia pozostałe plany i czyści selekcje. |
| Dziennik i trace | 512 aktywnych rekordów, 1 MiB/rekord (`RepairExecutor`); trace 8 MiB i trwałe granice wywołań w [property_probe.py](../python_host/PythonPartsScripts/PythonHost/property_probe.py). | Partie zwiększają zużycie miejsca; pełny dziennik/trace zatrzymuje workflow. Nie wolno usuwać nierozliczonych danych, żeby zwolnić miejsce. |
| Czas i transport | Kontrole budżetu Apply 20 s; evidence materiału 10 s, bazowy scan 5 s. [transport.py](../python_host/PythonPartsScripts/PythonHost/transport.py): kolejka 32 requestów, 3 s na start UI, body requestu 1 MiB. [allplan_client.py](../src/allplan_mcp/allplan_client.py): domyślny timeout 30 s. | Są to różne ograniczenia. Kontrola czasu nie przerywa trwającego wywołania natywnego. Utrata odpowiedzi Apply może oznaczać wykonany zapis. Kolejka 32 nie jest limitem zmian modelu. |

Budżet odczytu po przekroczeniu kończy się błędem bez kompletnej selekcji.
Nie można prezentować takich wyników jako „znaleziono 0”. Również
`page.complete` oznacza koniec stronicowania, nie pełne pokrycie projektu:
obowiązują osobne `coverage`, `omissions`, konflikty reprezentacji i
`not_checked`. Dotyczy to szczególnie nadal otwartego discovery Beam/SkeletonBeam.

### Gdzie obecnie powstaje koszt

1. **Ponowny pełny scan każdej strony i summary.** `ModelQueryService.handle`
   ponownie wywołuje `_scan` i porównuje `source_fingerprint`, zanim odczyta
   stronę z cache. Dla N adapterów i P stron to P enumeracji, plus ewentualne
   summary. Sam scan obejmuje odczyty natywne, grupowanie, sortowanie i hash;
   jego koszt nie ogranicza się do liczby zwróconych trafień.
2. **Odczyt pól przed oceną predicate.** `_scan` odczytuje potrzebne pola,
   geometrię i hierarchię przed końcowym filtrowaniem grup. Rekordy odrzucone
   pozostają częścią fingerprintu, aby wykryć nowe trafienia. To zabezpieczenie
   trzeba zachować, ale drogich pól prezentacyjnych nie zawsze trzeba czytać
   dla wykluczonych kandydatów. Ścieżka native material ma już takie częściowe
   zawężenie w `model_edit.observe`; nie należy opisywać go jako nowej funkcji.
3. **Wielokrotna obserwacja przy highlight.** `model_edit.highlight` uruchamia
   revalidate, kolejne observe, osobny `_scan`, a następnie
   [model_selection.present_selection](../python_host/PythonPartsScripts/PythonHost/model_selection.py)
   wykonuje jeszcze scan. W typowej ścieżce M4 daje to cztery skany w jednym
   highlight. Każdy jest uzasadniony aktualnymi granicami usług, ale ich
   współdzielenie w jednej operacji UI jest konkretnym kandydatem do refaktoryzacji.
4. **Resolve każdego celu od początku.**
   [native_model_edit.resolve](../python_host/PythonPartsScripts/PythonHost/native_model_edit.py)
   ponownie wykonuje `SelectAllElements`. Zwykły Apply robi resolve dla każdego
   targetu przy preflight, przed setterem i przy świeżym readbacku, dodatkowo
   obserwując cały zakres przed/po wykonaniu. Część enumeracyjna rośnie więc
   jak N × K dla K zmian. Delete ma odrębną ścieżkę grupową; trzeba mierzyć go
   osobno, podobnie jak koszt preservation materiałów.
5. **Trwały zapis i serializacja.** `RepairExecutor.save` serializuje i hashuje
   cały rekord, zapisuje plik tymczasowy, wykonuje fsync i replace. Przy zapisie
   każdej kolejnej zmiany pełny rekord jest ponownie zapisywany przed setterem
   i po odczycie. Duży monolityczny plan powiększa ten koszt. Trace także
   utrwala granice wywołań; optymalizacja nie może polegać na usunięciu fsync.
6. **Koszt interakcji agenta.** [server.py](../src/allplan_mcp/server.py) ma
   rozbudowane opisy wieloakcyjnych narzędzi, a wyniki zawierają powtarzane
   metadane. `model_edit` już zwraca `write_blockers`, `required_steps` i
   `next_action`; warto ujednolicić ten wzorzec zamiast budować drugi workflow.
   Klient rozpoznaje read-only według endpointu, więc timeout nawet preview
   na `/model-edit` jest klasyfikowany jako `execution_unknown`.

Nie ma podstaw do obietnicy określonego przyspieszenia. W szczególności
równoległe requesty MCP nie przyspieszą Allplan API: dispatcher uruchamia jeden
callback na tick UI, a nadmiar requestów zużyje kolejkę i budżet startu.

### Docelowy odczyt: duży zbiór, małe odpowiedzi

**Najpierw udostępnić istniejące możliwości bardziej czytelnie.** Dodać gotowy
`next_action` dla kolejnej strony, jednoznaczne `matched_total` versus
`returned`, oraz podsumowanie typów/plików z już utworzonego snapshotu.
Nie wymagać dodatkowego summary ani pobrania wszystkich stron, gdy użytkownik
pyta o liczbę elementów lub zamierza wykonać edycję według kryterium.
`model_edit.preview` już przyjmuje predicate i nie wymaga uprzedniego query.

**Oddzielić dwa jawne tryby spójności odczytu (propozycja API):**

- Zachować dotychczasowy domyślny tryb `live_verified`: strona wymaga świeżego
  porównania źródła. Możliwy ograniczony `collect` pobierający większą porcję
  po jednej rewalidacji, z limitem bajtów i cursorem; nie udawać, że eliminuje scan.
- Dodać opt-in `snapshot`: niezmienny wynik konkretnego zakończonego skanu;
  dane kolejnych stron pochodzą z JSON, bez pełnego skanu natywnego.
  Każda strona sprawdza tylko bieżącą tożsamość sesji/projektu/dokumentu
  lekkim odczytem kontekstu, bez enumeracji elementów.
  Zwracać identyfikator snapshotu, czas obserwacji, sesję/projekt/dokument,
  `freshness=not_revalidated` i `usable_for_write=false`. Restart/zmiana
  kontekstu/expiry unieważnia handle; czytanie starego snapshotu nie może
  sugerować aktualności modelu. Preview, highlight i Apply nadal wykonują
  wymagane świeże sprawdzenia. To jawna nowa semantyka, nie ciche usunięcie
  obecnej ochrony stale.

W obu trybach wprowadzić projekcje `summary|compact|full`, stronicowane
szczegóły i `max_response_bytes`. Pole niezamówione oznaczać jako pominięte
przez projekcję, nie `null` ani brak atrybutu. Zawsze zachować coverage,
liczniki konfliktów/omissions i drogę do pełnych dowodów. Jeśli nawet jeden
rekord przekracza budżet, zwrócić identyfikator szczegółów lub jawny błąd;
cursor musi postępować, bez pętli pustych stron. Rozmiar w bajtach jest
egzekwowalny; tokeny zależą od klienta i należy je mierzyć oddzielnie.

**To jeszcze nie usuwa granic 10000 adapterów / 5 s / 4 MiB.** Kolejny etap:

- Utrzymywać indeks JSON po `(session, project, document, file, model, view)`
  i wspólne metadane zamiast powielać cały kontekst w każdym elemencie.
  Wprowadzić jawny budżet bajtów całego cache, TTL i kontrolowane eviction.
  Rozważyć snapshot na dysku po pomiarach RAM; osobne limity/cleanup dla
  odtwarzalnego cache i dla nieusuwalnego nierozliczonego journalu.
- Podzielić query na tani odczyt tożsamości/warunków i drogie pola wynikowe.
  Pushdown musi zachować trójwartościowe predicates, consensus reprezentacji
  i wykrywanie elementów wchodzących w wynik. Cache geometrii/metadanych
  wymaga klucza kontekstu i sprawdzonego sygnału invalidacji; TTL nie dowodzi
  braku zmian wykonanych ręcznie w Allplanie.
- Zbadać API filtrowania/enumeracji według pliku i stabilne identyfikatory
  zmian dokumentu. Repo nie dowodzi dostępności wystarczającego revision tokenu
  ani bezpiecznego iteratora kontynuowanego między callbackami. Bez takiego
  dowodu nie deklarować taniej, kompletnej rewalidacji przyrostowej.
- Długie read joby porcjować na UI tylko po ustaleniu żywotności adapterów
  i semantyki zmian w trakcie skanu. Do cache trafia JSON; live adapters nie
  mogą przechodzić do wątków roboczych ani być używane po mutacji. Jeśli nie
  da się udowodnić spójnego skanu, wynik ma być incomplete/stale, a nie pełny.

### Ponad 32 zmiany: trwałe zlecenie z małymi partiami

Preferowany kierunek to **nowy koordynator zleceń**, początkowo dla jednego
aktywnego rysunku i operacji z odpowiednimi dowodami natywnymi. Pozostawić
do 32 rozwiniętych zmian w pojedynczej partii; całe zlecenie może mieć więcej.
Wieloplikowość i cały projekt są późniejszymi, osobnymi etapami.

Nie wystarczy pętla nad istniejącym Apply: pierwszy zapis unieważnia wszystkie
plany i selekcje, a kolejne odtworzenie predicate może objąć inny zbiór.
Proponowany cykl życia:

1. **Prepare/preview:** kompletny odczyt i trwały manifest zawierający wersję
   schematu, scope, kryterium, dokładne targety/owner/view, stare i nowe wartości,
   zależności, wyłączenia, no-op, blokady oraz hash. Pełne szczegóły są dostępne
   stronami; podsumowanie nie może ukrywać części zakresu podlegającego review.
   Najpierw rozwiązać globalne reguły, np. unikalność numeracji i overlap
   parent/child. Bez kompletnego odczytu nie tworzyć wykonywalnego manifestu.
2. **Review:** autoryzacja obejmuje dokładny manifest i jawny model częściowego
   wykonania. Nie przenosić automatycznie akceptacji z dowolnej wcześniejszej
   selekcji. Zachować wymagany highlight dokładnych celów; dla dużych zbiorów
   podgląd stron nie może udawać przedstawienia całego manifestu.
3. **Partition:** deterministyczne jednostki według pliku, elementu i zależności.
   Nie rozdzielać zmian jednego ownera ani poddrzewa delete w sposób niszczący
   ich kontrakt. Budżet partii uwzględnia liczbę zmian, bytes, przewidywany czas
   i miejsce w journalu; 32 jest sufitem, nie obowiązkowym rozmiarem.
4. **Execute:** dopiero teraz tworzyć świeży child plan dla następnej partii.
   Związać go z manifestem i jego hashem, ponownie sprawdzić zasoby, scope,
   właścicieli, wartości oraz globalne invariants. Koordynator rozpoznaje własne
   wcześniej potwierdzone zmiany; obca zmiana lub nowy pasujący element
   zatrzymuje zlecenie do ponownego review, zamiast rozszerzać zakres.
   Dla każdej partii trwale zapisać dokładny request i niezmienne execution ID
   przed wysłaniem, wykonać serializowany Apply i świeży readback.
5. **Stop/recover/resume:** `unknown`, conflict, niepełny readback, pełny dysk
   lub zmiana kontekstu wstrzymują następne partie. Po utracie odpowiedzi
   tylko inspect/recover tego samego ID; timeout nie upoważnia do nowego ID
   ani ponowienia settera. Restart odtwarza journal/manifest, lecz stare refs
   wymagają ponownego związania i walidacji; ich trwałość nie jest dziś dowiedziona.
   Niepotwierdzony wynik pozostaje unknown. Cancel zatrzymuje przyszłe partie,
   nie przerywa trwającego native call i nie wykonuje domniemanego rollbacku.
6. **Finish:** raport `applied/failed/conflict/unknown/not_attempted/no_op`,
   liczby elementów oraz zmian i zakres walidacji końcowej. Globalne reguły
   sprawdzić również na końcu. Nie obiecywać atomowości, jednego Undo ani
   automatycznego cofania całego zlecenia bez osobnego dowodu API/builda.

Manifest/job store musi przeżyć unieważnienie cache planów. Jego wersjonowanie,
blokada wykonania, walidacja integralności, limity i odtwarzanie stanowią nowy
kontrakt, współpracujący z istniejącym journalem; nie należy przepisywać starych
rekordów tylko po to, by pasowały do większego limitu. Rezerwować pojemność
przed startem partii, uwzględniając wzrost danych readback. Archiwizacja zachowuje
replay guard i nierozliczone rekordy zgodnie z obecną procedurą.

**Najważniejsza optymalizacja wnętrza partii:** wspólny resolver wielu dokładnych
targetów podczas preflight i indeks identyfikatorów dla dalszego lookup. Najpierw
usunąć redundantne skany w obrębie jednego niemutującego callbacku. Ponowne
użycie adapterów po setterze jest niedopuszczalne bez dowodu poprawności;
readback musi pochodzić z nowego odczytu i nadal obejmować wszystkie wymagane
reprezentacje. Ukierunkowane wyszukanie UUID jest osobnym spike API, nie
zakładaną dostępną funkcją. Optymalizacja final audit nie może pominąć nowych
trafień, driftu sąsiadów ani preservation.

### Szybsze i bardziej intuicyjne narzędzia MCP

| Zmiana proponowana | Konkretna korzyść i warunek |
| --- | --- |
| Wspólny status/capabilities | Jedno lekkie źródło informacji o scope, limitach, sesji, dostępnych operacjach i blokadach journalu. Oddzielić obsługę w kodzie, experimental Apply i native acceptance; nie przedstawiać flag jako dowodu odbioru. |
| Jednolite odpowiedzi | `state`, `summary`, `counts`, `coverage`, `blockers`, `next_action`, odnośnik do szczegółów i identyfikatory. Reuse obecnego `write_availability`; błędy stale/expired/limit mają zwracać konkretne dalsze requesty lub jawny brak bezpiecznej akcji. |
| Krótsze opisy i gotowe przykłady | W opisie narzędzia zostawić intencję, poprawny minimalny request i krytyczne zasady zapisu; obszerną referencję udostępnić jako zasób MCP z istniejącego [tool-reference](tool-reference.md). Przykłady: ściany poniżej grubości, brak atrybutu, zmiana warstwy, native material versus attribute. Nie wymagać pamiętania UUID typów; rozważyć jawne aliasy rodzin z ujawnionym mapowaniem i bez automatycznego rozszerzania scope. |
| Prostszą ścieżkę edycji | Dla znanej intencji używać obecnego `model_edit.preview(predicate, changes)` → highlight → Apply. Odrębne query/summary/revalidate tylko gdy potrzebne do decyzji; Apply już rewaliduje. Opcjonalne prepare+highlight może później łączyć niemutujące etapy, zachowując dokładny hash, review i jawny wpływ na highlight UI. |
| Rozdzielenie efektów narzędzi | Dodać poprawne MCP annotations i ewentualne cienkie read/write fasady nad wspólnymi usługami. Nie oznaczać całego wieloakcyjnego `model_edit` jako read-only/idempotent. Uporządkować wybór między `model_edit`, `column_layer`, `rule_based_edit` i presetami bez tworzenia równoległych implementacji. |
| Timeout według operacji | Klasyfikować `(endpoint, action)` i fazę: preview/query to odczyt modelu, highlight zmienia prezentację, Apply może zmieniać model. Rozróżnić `not_started` od utraconego wyniku i dołączać execution ID/recovery request. Nie dodawać automatycznych retry zapisów. |
| Przygotowany request wykonania | Zwracać kompletny szablon Apply i pole do trwałego execution ID; docelowo koordynator utrwala ID oraz payload przed wysłaniem. Agent nie powinien ręcznie rekonstruować hashy ani generować nowego ID po błędzie. |
| Ograniczone, kierowane discovery | Reuse konkretnego bindingu nazwa↔ID/typ z kluczem projektu, fresh verify przed zapisem. Zachować fazy probe i durable trace po wcześniejszych crashach; nie łączyć broad discovery ani nie kontynuować następnej fazy bez oceny wyniku. Native selection nadal unsupported; highlight nie jest jego zamiennikiem. |
| Długie zadania | Jeśli pomiary uzasadnią: job ID, status/progress i bounded polling, z cancel pomiędzy partiami. HTTP/MCP może odpowiadać szybko, ale natywne czynności nadal wykonuje wyłącznie UI. Sam wrapper async nie usuwa zawieszania UI przez długi native call. |

### Kolejność realizacji i kryteria zamknięcia

Poniższe identyfikatory są technicznym rozwinięciem zadania skalowania w
głównym backlogu. Odczyt, pomiary i ergonomię można rozwijać niezależnie od
otwartych Beam/Slab. Włączenie większych zapisów zależy od dowodów dla danej
operacji; nie dziedziczy akceptacji niezweryfikowanego native material.

| Etap | Zakres / główne pliki | Kryterium i zależność |
| --- | --- | --- |
| S0 — pomiary i kontrakt, pierwszy | `transport.py`, query/edit/repair services, istniejące diagnostics. | Baseline etapów i macierz limitów; osobne czasy UI/API/JSON/IO. Żadnego podnoszenia timeoutów przed profilem. |
| S1 — ergonomia, mały zakres | `server.py`, publiczne schemas, host contracts, `tool-reference.md`. | Każdy ważny stan ma parsowalny następny krok, counts odróżniają total/page, brak zbędnego query przed preview; zgodne kontrakty public/host i obsługa starszego klienta. |
| S2 — odczyt snapshot/projekcje | `model_query.py`, `query_models.py`, `query_contracts.py`, cache. | Ponad 200 wyników bez utraty/duplikacji; tryb snapshot wykonuje zero pełnych skanów na następnych stronach, live zachowuje stale guard. Limit bytes, RAM i TTL testowany. Nie deklarować jeszcze obsługi >10000 adapterów. |
| S3 — redukcja skanów i duże odczyty | `model_edit.py`, `model_selection.py`, `native_model_edit.py`, native readers. | Licznik skanów highlight/preflight maleje przy identycznych wynikach i guardach. Spike enumeracji/revision/lookup rozstrzyga dalszą architekturę; większy scan budget dopiero z pomiarem UI i pamięci. |
| S4 — manifest i wykonanie partiami | Nowy coordinator/store oraz `model_repair.py`, `repair_execution.py`, kontrakty M4. | Zlecenie >32 zmian w jednym rysunku, rozliczone partial/unknown, trwałe ID, awaria/restart bez powtórzonych setterów, globalne invariants i pełny końcowy raport. Zależność: S0/S3 i odpowiednie odbiory operacji. |
| S5 — wiele rysunków, później | Resolver scope/context, koordynator plików i ich aktywacji. | Osobny manifest per-file, wykrycie zmiany active file, kontrolowane przełączenie/przywrócenie kontekstu i jawne omissions. Niezaładowany cały projekt wymaga osobnej enumeracji i odbioru. |

Samo podniesienie page size można rozważyć jako ustawienie wydajnościowe po S0,
ale nie zastępuje S2/S3. Zwiększenie jednostkowego Apply ponad 32 pozostawić
na później: wymaga dowodów czasu, readback/recovery, journal size i Undo dla
konkretnej rodziny. Nie ma obecnie uzasadnienia dla uniwersalnego nowego limitu.

### Plan weryfikacji przyszłej implementacji

**Scenariusze pomiarowe:** oddzielnie 200/201 i 1000 wyników;
1000/5000/10000/50000 surowych adapterów (50000 to cel badania, obecnie poza
kontraktem); 1/32/33/100/1000 rozwiniętych zmian. Zmienna liczba reprezentacji,
udział trafień, liczba pól, geometria, hierarchia, jeden/wiele otwartych plików.
Mierzyć zimny/ciepły odczyt, preview, highlight, Apply/recover i pełną sesję
agenta. Utrzymywać te same dane wejściowe przed i po optymalizacji.

Zapisać p50/p95 czasu, najdłuższą blokadę UI, liczbę enumeracji i natywnych
odczytów, requestów MCP/HTTP, bytes/tokeny odpowiedzi, szczyt RAM/cache,
bytes/czas journalu i liczbę fsync. Osobno modelować bezpośredni koszt K zmian
i wpływ N adapterów. Wynik na fake-host/Linux nie zastępuje Windows/Allplan.
Cele strukturalne: jedna enumeracja dla wielu targetów preflight zamiast K
(jeśli spike na to pozwala), brak pełnego skanu dla strony snapshot oraz
stały limit odpowiedzi niezależny od rozmiaru zlecenia. Cele czasowe ustalić
po baseline; nie wpisywać niezmierzonego „10× szybciej”.

Minimalne testy regresji przyszłych zmian:

- Granice public/host schema; 200/201 wyników, 32/33 zmian; zero trafień,
  no-op i incomplete odróżnione. Pamiętać, że 201 wyników obecnie powinno
  działać przez paging, a 33 zmiany w jednym Apply powinny zostać odrzucone.
- Powtórzenie cursor zwraca tę samą stronę tego samego snapshotu; dotychczasowy
  live replay nadal najpierw rewaliduje źródło. Inna selekcja/sesja, expiry,
  eviction, byte budget oraz
  kompletne stronicowanie bez duplikatów. Live wykrywa ręczną zmianę/dodanie
  pasującego elementu; snapshot jawnie nie twierdzi, że został rewalidowany.
- Redukcja scan nie zmienia consensus, owner/view, kolejności i fingerprintów
  wymaganych przez kontrakt; nie ukrywa rejected peers, missing ani unknown.
- Awaria przed journalem, po write-ahead, po setterze/przed readbackiem,
  utrata odpowiedzi, restart, pełny dysk, uszkodzony rekord, trace full;
  wszystkie wykonania mają trwałą tożsamość, recovery nie uruchamia setterów.
- Partie: zewnętrzna zmiana/nowy match pomiędzy partiami, zmiana active file,
  parent/child overlap, dwie zmiany jednego ownera, numeracja/unikalność
  globalna, cancel i unknown w środku. Nie pomijać niezrealizowanych celów
  ani nie dodawać nowych bez review manifestu.
- MCP/HTTP: minimalne requesty i schematy next_action, poprawna klasyfikacja
  timeoutu odczytu/prezentacji/zapisu, zgodność starszych klientów oraz brak
  sugerowanego retry Apply. Dla ergonomii porównać liczbę wywołań, błędnych
  requestów i bytes w tych samych zadaniach użytkownika.

Próba natywna dotyczy wyłącznie nowego większego zakresu i zmienionej ścieżki:
responsywność UI, dokładne targety, świeży readback, preservation i rzeczywisty
zakres Undo na disposable fixture. Nie powtarzać już odebranych małych zapisów
dla odtworzenia historii. Szczegóły CI/dostawy określa [testing policy](testing-policy.md).

**Weryfikacja tej analizy:** wyłącznie przegląd źródeł, diff i odnośników.
Brak zmian runtime, benchmarków, testów produktu, buildów i nowej akceptacji
natywnej; limity obecnej wersji pozostają bez zmian.
