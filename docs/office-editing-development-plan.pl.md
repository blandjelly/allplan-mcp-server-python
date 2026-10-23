# Allplan MCP — plan rozwoju edycji modelu biurowego

## Aktualny stan

M4 jest częściowo odebrane. Właściciel potwierdził, że ostatnie wyniki agenta
odpowiadają Allplanowi: zapis dwóch atrybutów na wynikach zapytania stropów,
zmianę atrybutu `Priorytet` na dwóch wynikach oraz przypisanie `MCP_QA_MARK`
sześciu słupom w żądanej kolejności. Brak dokładnego manifestu instalacji i
części odpowiedzi MCP nie pozwala przypisać tych wyników do konkretnego
artefaktu ani rewizji. Zapis `Materiał = beton zbrojony` jest zmianą atrybutu;
nie potwierdza zmiany natywnego materiału konstrukcyjnego.

| Priorytet | Status zaakceptowanego zakresu | Następny brakujący dowód / blokada |
|---|---|---|
| 1 — dziennik | Ograniczony preview/archive 0.23.0; trial 1 z 0.30.0 zgłoszony jako PASS, bez pełnego raw logu. | Pełny replay/restart i obsługa unknown/corrupt/unverifiable wymagają odrębnego dowodu. Nie powtarzać zaakceptowanych kroków. |
| 2 — właściciel pola | Brak rozstrzygnięcia dla project attributes Slab/MultiSlab. | Ustalić właściciela i zweryfikowany zapis/readback; do tego czasu zapisy pozostają zablokowane. |
| 3 — warstwa/no-op | W1/no-op z 0.30.0 zgłoszony jako PASS w ograniczonym zakresie. | Nie rozszerza to akceptacji zapisu/Undo W1 ani szerszych przypadków. |
| 4 — delete/material/selection | Grouped delete/Undo trzech Column zaakceptowany dla zakresu 0.29.0. Native material jest w kandydacie 0.32.0; native UI selection set/clear/readback pozostaje unsupported. | Wykonać tylko jedną próbę Wall 240 mm 0.32.0. Wall 200 mm/opening owner mismatch pozostaje nierozwiązany. |
| 5 — typy atrybutów | Cztery scalar pary z 0.30.0 oraz Wall Enum ID 120 z Apply/readback/Undo są potwierdzone w ograniczonym zakresie. Boolean/CheckBox ma tylko readback po zgłoszonym Undo, bez raw Apply. | Pełne pokrycie rodzin/typów; date/vector payload i typed readback pozostają BLOCKED. |

Nie ma podstaw do bezpiecznego zamknięcia wszystkich priorytetów 1–5: pozostają
braki API i fikstur opisane w tabeli.

Wersja **0.23.0** dodaje kontrolowany podgląd i archiwizację śladu
diagnostycznego oraz rozliczonych rekordów dziennika. Źródło
`8c71de958c47ab4cb418a62fbd2d55ce76cbc4db` przeszło pełne CI: 505 testów na
każdej konfiguracji Windows/Ubuntu, Python 3.12, a następnie jeden build.
Dokładny ZIP z CI przeszedł sprawdzenie payloadu, instalację, aktualizację z
0.22.1 i przywrócenie; zachowano 38 hashy mostka i znaczniki dziennika,
śladu oraz archiwów. Właściciel zgłosił **PASS** krótkiej próby 0.23.0:
podgląd 614 396 bajtów śladu oraz 32 rozliczonych rekordów (739 786 bajtów),
potwierdzenie obu archiwizacji i ich zakończenie. Brak manifestu/builda oraz
natywnego replay/restartu ogranicza zakres tego potwierdzenia.
[Obserwacja PASS](test-results/m4-journal-cleanup-0.23.0-owner-pass-2026-10-21.md) ·
[pakiet 0.23.0](../evaluation-packages/0.23.0/README.md) ·
[obserwacja właściciela](test-results/m4-agent-observation-2026-10-20.md).

### Bieżący kandydat 0.32.0 — ograniczone preservation atrybutów tieru

Kandydat 0.32.0 rozszerza zachowawczy snapshot ścieżki native material Wall i
dodaje opcjonalne, ograniczone identity evidence do odpowiednich shared owner
diagnostics. Snapshot dopuszcza bezpośrednie liście
`AttributeContainer_TypeUUID` pod tierem po sprawdzeniu pełnej linii
container → tier → Wall, zachowując zaobserwowane view UUID i strukturalnie
porównując ponowne enumeracje dzieci.
Snapshot obejmuje wszystkie zapisane wartości z `ReadAll` przez ograniczone
kodowanie JSON: maksymalnie 64 kontenery, 4096 rekordów na kontener i 256 KiB
zachowanych danych. Nieznany typ dziecka, nested child, nieobsługiwana wartość,
opening albo inny child Wall nadal blokuje zapis. Snapshot służy zachowaniu
stanu; nie ustala ownera pola ani nie dodaje zapisu atrybutów.

Źródło
[`c7783cc05f00b032ead10f49e54092b9504a35c6`](https://github.com/blandjelly/allplan-mcp-server-python/commit/c7783cc05f00b032ead10f49e54092b9504a35c6)
jest na `fix/m4-material-metadata-0.32.0`; [PR #30](https://github.com/blandjelly/allplan-mcp-server-python/pull/30)
celuje w `develop/m4`. **161 unique focused checks przeszły** ([rekord](../evaluation-packages/0.32.0/focused-verification.json)).
Pierwszy full CI [run 40032392662](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40032392662)
zakończył się jednym niepowodzeniem `test_model_delete`: assertion oczekiwał
wcześniejszego exact diagnostic shape po dodaniu `diagnostic.evidence`.
Ubuntu wykonał 635 testów, Windows został anulowany przez fail-fast, a package
job został pominięty. Aktualizacja assertion i focused delete checks oraz
rerun CI dla poprawionego source są w toku. Build pakietu, ZIP verification i
native acceptance pozostają pending.

Focused fake-adapter checks odtwarzają wcześniejsze blanket odrzucenie dzieci
tieru i sprawdzają nowy bounded flow, lecz nie dowodzą, że była to dokładna
przyczyna native diagnostyki 0.31.0. `component_child_owner_mismatch` dla Wall
200 mm z opening pozostaje nierozstrzygnięty i poza tą poprawką. Corrected-source
CI, build/verification pakietu i native acceptance pozostają pending.
Próba właściciela ogranicza się do pierwotnej ścieżki materiału
Wall 240 mm: przy blokadzie zachować pierwszy reason/stage oraz świeże
`component_identity` Wall i dokładnego tieru; przy kwalifikacji jeden
Apply/readback/UI Undo. [Notatka API 0.32.0](m4-editing-api-0.32.0.md) ·
[krótka próba](m4-single-drawing-0.32.0.pl.md).

Priorytety 1–5 pozostają otwarte poza wcześniej zaakceptowanymi zakresami.
Konkretnie nadal brakuje project-attribute ownership/writable contract dla
Slab/MultiSlab, date/vector setter payloadów i typed readback, native UI
selection set/clear/readback oraz szerszego family/type coverage. Nierozwiązany
pozostaje też wynik `component_child_owner_mismatch` dla Wall z opening.

Kandydat **0.24.0** dodaje odczyt dokładnej tożsamości adaptera, pełnego łańcucha
rodziców, dzieci i typu reprezentacji natywnej. Blokuje zapis do dzieci Slab
i agregatów MultiSlab bez ustalonego właściciela pola; samodzielny Slab
wiąże własność z planem i ponownie sprawdza ją przed zapisem i readback.
Testy automatyczne rozszerzają W1, wyłączenia, replay/no-op oraz odmowę
nieobsługiwanych typów. [Macierz i luki API](m4-single-drawing-coverage-0.24.0.md) ·
[krótka próba](m4-single-drawing-0.24.0.pl.md).
Punkty 2–5 nie mają pełnego odbioru natywnego. Selekcja pozostaje
nieobsługiwana, a daty/wektory wymagają osobnych kodeków.
Właściciel potwierdził, że najnowszy log odpowiada zachowaniu Allplana przy
wersji 0.24.0. [Ograniczona obserwacja](test-results/m4-owner-observation-0.24.0-2026-10-21.md)
zachowuje jej zakres: readback W1 bez próby no-op/Undo, nieudany dokładny
probe view stropu, odmowę selekcji natywnej i usunięcie przez interfejs
rozmowy. Nie potwierdza to istnienia typowanego narzędzia MCP delete.
Pełne CI finalnego źródła przeszło 529 testów na każdym systemie
Windows/Ubuntu (Python 3.12), po nim wykonano jeden build. Dokładny ZIP z CI
przeszedł weryfikację i aktualizację/przywrócenie z 0.23.0, zachowując 40 hashy
mostka oraz znaczniki dzienników i archiwów.
[Dostawa i wyniki 0.24.0](../evaluation-packages/0.24.0/README.md).

Kandydat **0.25.0** dodaje do `model_edit` dwa odrębne kontrakty: usunięcie
dokładnego terminalnego root komponentu z pełnym, ograniczonym poddrzewem
(maks. 256 adapterów łącznie z celem) oraz wyjątek dla `WindowDoor_TypeUUID`
o dokładnej linii `[opening, Wall root]` bez makro-przodków; nie usuwa to Wall.
Slab child pozostaje zablokowany, chyba że obejmuje go wybrany pełny root
MultiSlab. Kandydat dodaje też eksperymentalny zapis natywnego
materiału tier 1 samodzielnej, jednowarstwowej ściany. Usunięcie wysyła tylko
target do natywnego API; brak targetu i potomków oraz pozostanie Wall w wyjątku
otwarcia muszą potwierdzić świeże pełne skany.
Materiał przyjmuje dokładny tekst bez sprawdzania katalogu i wiąże dowody
niezmienników geometrii, hierarchii i pozostałych właściwości. Te ścieżki nie
mają jeszcze odbioru natywnego. Finalne źródło
`574ef06ca97fced289b414faa3ba91b78b5b91ef` przeszło pełne CI: **557 testów
na Windows i 557 na Ubuntu (Python 3.12)**, a następnie jeden build.
Dokładny ZIP z CI przeszedł weryfikację payloadu/hashów, instalację,
aktualizację z 0.24.0, frozen sync/import i przywrócenie. Zachowano 42 hashe
mostka oraz znaczniki aktywnych dzienników, śladów i archiwów.
[Dostawa i wyniki 0.25.0](../evaluation-packages/0.25.0/README.md).
[Krótka próba](m4-single-drawing-0.25.0.pl.md) obejmuje wyłącznie te dwie
ścieżki oraz niezaobserwowane wcześniej W1 no-op/Undo.
[Podstawa i granice API](m4-editing-api-0.25.0.md) nie odbiera selekcji,
materiału, rodzin ani kodeków. Kandydat nie zamyka priorytetów 1–5.

Właściciel potwierdza, że [log z 22 października](test-results/evidence/log_rozmowy-2026-10-22.md)
odpowiada rzeczywistemu zachowaniu Allplana. [Ograniczona obserwacja 0.25.0](test-results/m4-owner-observation-0.25.0-2026-10-22.md)
zapisuje PASS odczytu `component_identity` dla jednego wskazanego Wall i
jednego wyniku MultiSlab oraz usunięcia jednej pozostałej ściany z dziećmi po
potwierdzeniu i świeżym kompletnym skanie. Zapisuje też readback W1 dla ściany
200 mm (ID 3702 → 65535). Log nie zawiera dokładnego manifestu instalacji,
surowych odpowiedzi MCP ani builda Allplana, więc wyniki nie są przypisane do
konkretnego ZIP-a i nie stanowią pełnego odbioru typowanego usuwania. Usunięcie
otworu i jego ściany nadrzędnej, zmiana natywnego materiału/kreskowania 129 oraz
zbiorcza zmiana warstw na W1 zostały zablokowane. No-op/Undo W1 nie wykonano.
Punkty 1–5 i bramka odbioru pojedynczego rysunku pozostają otwarte.

Kandydat **0.26.0** ze źródła `48e64b1a06bef005c26a143860d9257038cccde3`
(PR #24 do `develop/m4`, merge `40f71b737616b9dde4b3f6804b774c0e5f76ac40`)
przeszedł [CI 39822585188](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39822585188):
580 testów na Windows i 580 na Ubuntu (Python 3.12) oraz job pakietu. Transfer
oryginalnego artefaktu CI (ID 12445232990) zablokował proxy CONNECT 403; zgodnie
z polityką wykonano jeden fallback build z czystego detached worktree tego
samego źródła (`source_modified=false`). Dostarczany ZIP ma SHA-256
`4c0dd3ed9c9c038320fe08032a26ef61d8be7a57ed4169d5cdd3bc5952b292a9`. Dokładny
ZIP przeszedł weryfikację: checksum/payload, rejestrację, frozen sync/import,
schemat `drawing_identity`, upgrade z 0.25.0 i restore, 42 hashe mostka oraz
zachowanie markerów dziennika/śladu/logu i archiwów. Oryginalny artifact CI nie
został dostarczony; zweryfikowany pakiet jest pojedynczym local fallback
buildem. Szczegóły są w [rekordzie 0.26.0](../evaluation-packages/0.26.0/README.md),
[source CI](../evaluation-packages/0.26.0/source-ci.json),
[focused checks](../evaluation-packages/0.26.0/focused-verification.json),
[build logu](../evaluation-packages/0.26.0/build.log) i
[weryfikacji ZIP](../evaluation-packages/0.26.0/package-verification.json).

Ówczesna [krótka próba właściciela](m4-single-drawing-0.26.0.pl.md) obejmowała
stronicowany read-only inwentarz tożsamości rysunku 101, odczyt warstwy 0,
brakujące W1 no-op/Undo oraz jedną diagnostykę read-only dokładnego celu.
Focused testy pokrywają odczyt ID 0 oraz reviewed W1 plan/apply od starej
wartości 0, ale nie natywne Undo ani przyczynę historycznego `repair_conflict`.
Diagnostyka delete/materialu nie naprawia blokad ani nie włącza setterów.
W chwili dostawy nie było natywnej próby 0.26.0; późniejsza obserwacja
potwierdza tylko jej ograniczony zakres, a pełny odbiór natywny pozostaje
nieukończony. Nie powtarzać ograniczonego PASS usunięcia, odczytów identity ani
readbacku W1 ściany 200 mm z 0.25.0. Statusy priorytetów są w
[macierzy pokrycia](m4-single-drawing-coverage-0.24.0.md); pełne priorytety
1–5 pozostają otwarte.

Ograniczona [obserwacja 0.26.0](test-results/m4-owner-observation-0.26.0-2026-10-22.md)
zachowuje log właściciela bez surowych odpowiedzi MCP, manifestu, dokładnego
ZIP-a ani builda Allplana. Skan `drawing_identity` zgłosił kompletne 26/26
członków zakresu przy 7 `observed` i 19 `not_checked`. Na tym samym słupie
potwierdzono readbacki po zmianie warstwy 3700 → W1 → 0. Podświetlenie jednej
ściany 200 mm zostało wysłane; status wymagał obserwacji widoku, a log nie
podaje jej wyniku ani natywnej liczby selekcji. Asystent zgłosił blokadę
materiału z powodu otworu, lecz późniejsza odpowiedź zawiera puste `blocked`
i brak diagnostyki, więc rzeczywista przyczyna nie jest potwierdzona. Materiału
nie zmieniono; nie wykonano delete ani W1 no-op/Undo.

Status zaktualizowano 23 października 2026 (Europe/Warsaw). Kandydat **0.27.0**
ze źródła `e62a50c9c6c6b51978b6f1a55f9d9978eee5b1c3` na PR #25 do `develop/m4`
scalono jako `23b8b2591d7be0721fe7a5651379408e7a2f5e76`. Przeszedł pełne CI
39841530841: 593 testy na Windows i 593 na Ubuntu (Python 3.12) oraz job
pakietu. Pojedynczy fallback ZIP z czystego źródła (`source_modified=false`)
przeszedł dokładną weryfikację za pierwszym razem: 183 pliki payload, checksum
i payload, rejestrację, frozen sync/import, schemat `drawing_identity`, upgrade
i restore 0.26.0, 42 hashe mostka oraz markery dziennika/śladu/logu i archiwum.
SHA-256 ZIP-a: `eab80cd2c907e7fd90ba733f4f8d1335f097986b938c74ccdda6bf3382cdaa30`.
Oryginalny artifact CI nie został dostarczony; zweryfikowany pakiet to fallback.
W chwili dostawy nie było próby natywnej. Historyczny log CI zachowuje datę
22 października. Szczegóły: [rekord pakietu](../evaluation-packages/0.27.0/README.md)
i [weryfikacja ZIP](../evaluation-packages/0.27.0/package-verification.json).
Kandydat obejmuje bounded resolver nazw
atrybutów bez fuzzy/catalog, fail-closed inwentaryzację potomków Wall dla
preservation materiału oraz rozdzielenie starej wartości materiału od
kwalifikacji operacji. Diagnostyka nie dodaje nowych zapisów i nie umożliwia
materiału bez pełnego snapshotu preservation, również przy świeżym odczycie po
zapisie. Właściciel zgłosił ograniczony PASS próby lowercase resolvera i
diagnostyki materiału oraz W1 read/write z jednym elementem na krok Undo.
Szczegóły i granice są w [obserwacji 0.27.0](test-results/m4-owner-observation-0.27.0-2026-10-23.md)
i jej [oryginalnym logu](test-results/evidence/allplan-chat-log-0.27.0-2026-10-23.md).
Nie zgłoszono jawnego no-op ani zera setterów. Log potwierdza osobny Wall
subtree delete i dwie zmiany Beam na W1, ale trzy Columns na W1 pozostały
zablokowane przez `component_child_owner_mismatch`; relacja Slab/MultiSlab
nadal jest nierozstrzygnięta. Nie przypisano wyników do dokładnego ZIP-a ani
builda Allplana. Punkty 1–5 pozostają częściowo otwarte zgodnie z
[handoffem](next-model-handoff.md); kolejny zakres opisuje
[krótka próba 0.28.0](m4-single-drawing-0.28.0.pl.md).

## Zachowany kandydat 0.29.0 — plural delete i grupowe Undo

Źródło `df050afc71b9e0c2303594d6acbd3da463df3e89` na gałęzi
`fix/m4-batch-undo-0.29.0` ma [PR #27 do `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/27).
Przeszedł full CI 39971389774: 607 testów na Windows i 607 na Ubuntu (Python
3.12) oraz job pakietu; przeszło też 99 unique focused checks. Artefakt CI
12510270932 (digest
`3d509667620fb3a23fc7a1daf0c9303f68e2ede98cccac1c4ee08d7b00e615da`) nie został
przesłany przez connector: pojedynczy transfer zwykłym proxy zakończył się
`URLError` przed odpowiedzią HTTP. Zgodnie z polityką wykonano jeden fallback
build z czystego detached checkoutu dokładnego źródła (`source_modified=false`).
ZIP z 191 plikami payload przeszedł dokładną weryfikację raz; SHA-256
`0e4211b7a28f69a0b0400c13e2a90efeca9c230d34e42599adc6e8a2932d5aa5`.
Szczegóły zawiera [rekord pakietu 0.29.0](../evaluation-packages/0.29.0/README.md).

Kandydat obejmuje jeden plan usunięcia rozwinięty na dokładny zestaw Column,
jedno wywołanie `DeleteElements` z pełną listą adapterów, dziennik nieznanych
wyników dla całego zestawu przed wywołaniem i świeży odczyt każdego celu oraz
potomka. Częściowe/nieznane wyniki odzyskuje się pod tym samym execution ID bez
powtarzania settera. Właściciel zgłosił **PASS wszystkich kroków próby 0.29.0**:
trzy Column na W1 w aktywnym rysunku 101 zostały usunięte, świeży skan
potwierdził brak słupów i kontenerów atrybutów, a jedno UI Undo przywróciło
wszystkie trzy. To spełnia cel poprawki grupowego Undo dla tej operacji Column.
Log nie zawiera surowych odpowiedzi MCP, UUID celów ani manifestu ZIP-a; Undo
zaobserwował właściciel, narzędzie zgłosiło `undo: not_checked` i nie wykonało
automatycznego odczytu po Undo. Zobacz
[obserwację 0.29.0](test-results/m4-owner-observation-0.29.0-2026-10-23.md)
i [log próby](test-results/evidence/allplan-test-log-0.29.0-2026-10-23.md).
FAIL z 0.28.0 pozostaje historyczny. Priorytety 1–5 pozostają częściowe poza
tym odebranym zakresem; następna praca ma objąć je wspólnie w zakresie
opisywanym poniżej dla 0.30.0. Granice SDK opisuje
[notatka API 0.29.0](m4-editing-api-0.29.0.md).

## Zachowany kandydat 0.31.0 — poprawka owner identity materiału Wall

Praca odbywa się na gałęzi `fix/m4-material-owner-0.31.0`, opartej na
`develop/m4`. Przeszło 86 affected/dependent focused checks w zestawach
`wall_material_edit`, `wall_material_http`, `model_edit`, `native_model_edit`
i `edit_ownership`, w tym trzy regresje parent-wrapper. Przeszedł też jeden
package version/lock check; 25 nakładających się checks nie liczono drugi raz.
Łącznie 87 unique focused checks. [Rekord focused verification](../evaluation-packages/0.31.0/focused-verification.json).
Oba full CI unittest jobs przeszły na Windows i Ubuntu Python 3.12 w
[run 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481).
Run 40012042481 przeszedł: 625 testów Ubuntu Python 3.12.15, 625 testów
Windows Python 3.12.10 i package job. Oryginalny CI artifact 12527730616 był
niedostępny, więc jeden fallback ZIP z czystego detached exact source
(`source_modified=false`) przeszedł weryfikację: 201 payload files, 43 bridge
hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`.
Zobacz [rekord package](../evaluation-packages/0.31.0/README.md),
[weryfikację ZIP](../evaluation-packages/0.31.0/package-verification.json) i
[zweryfikowany ZIP](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip).
Pozostaje native acceptance. Zmiana porównuje
parent edge tieru przez `same_model_identity` (drawing, model UUID i type),
zachowując rzeczywiście zaobserwowany wrapper w `tier_hierarchy`. Target Wall
nadal ma związany dokładny view UUID.

Focused regression potwierdził, że stary exact view UUID comparison blokował
alternatywny parent wrapper tego samego modelu. Pierwszy native diagnostic z
0.30.0 jest z tym defektem zgodny, ale bez raw lineage/children response nie
ustalono dokładnej przyczyny wyniku Allplana. Guardy pozostają: standalone Wall root, dokładnie jeden
bezpośredni `WallTier_TypeUUID`, brak tier children, opening i innych Wall
children, poprawna geometria i pełny istniejący preservation snapshot.
Drugi 0.30.0 wynik `component_child_owner_mismatch` dla Wall z opening jest
nierozstrzygnięty i nie jest objęty poprawką.

Właściciel później dostarczył log z Allplan 2026.1 i mostka 0.31.0. Dla Wall
240 mm preview żądanego `Silikat` zakończył się
`wall_material_tier_hierarchy_unsupported` przed Apply (`changes=[]`,
`usable_for_write=false`, zero setterów). Dla Wall 200 mm z materiałem `Cegła`
preview `Silikat` zakończył się `component_child_owner_mismatch`, również bez
Apply i setterów. Nie ma surowych odpowiedzi MCP ani manifestu/checksumy
instalacji; nie przypisuję tych wyników dokładnemu ZIP-owi. Natywny zapis
materiału w 0.31.0 pozostaje BLOCKED. Pełna obserwacja wraz z ograniczonymi
dowodami Enum, Boolean/CheckBox oraz Slab/MultiSlab jest w
[obserwacji 0.31.0](test-results/m4-owner-observation-0.31.0-2026-10-24.md),
a kopie dostarczonych plików są w
[archiwum dowodów](test-results/evidence/0.31.0-2026-10-24/). Enum Wall ma
udokumentowany Apply/readback/Undo w zakresie ID 120; Boolean/CheckBox ma tylko
surowy readback po zgłoszonym Undo, bez surowego Apply. Slab/MultiSlab nadal nie
ustala właściciela pola; Slab nie ma kompletnego evidence. Obserwacje nie
zamykają priorytetów 1–5.

Obie obserwacje z 0.30.0 opisuje [notatka API 0.31.0](m4-editing-api-0.31.0.md);
wąski plan i kryteria próby są w [planie 0.31.0](m4-single-drawing-0.31.0.pl.md).
Nie powtarzać zaakceptowanych etapów 0.30.0 1–3 i 5 ani grouped delete/Undo
Column 0.29.0.

## Zachowany kandydat 0.30.0 — jedna sesja priorytetów 1–5

Źródło `9966c31fc1b79b0ed7c2061d671dafa3f1f2e8d6` na gałęzi
`feat/m4-combined-evidence-0.30.0` ma [PR #28 do `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/28).
Przeszło full [CI 39993048110](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39993048110):
622 testy na Windows i 622 na Ubuntu (Python 3.12) oraz job pakietu; przeszło
też 142 unique focused checks. Oryginalny artifact CI 12518373563 nie został
dostarczony przez connector: jedyny transfer zwykłym proxy zakończył się
`URLError` przed odpowiedzią HTTP. Wykonano jeden fallback build z czystego
detached worktree dokładnego źródła (`source_modified=false`). Exact ZIP
verification przeszło za pierwszym razem: 196 plików payload, 43 hashe mostka,
checksum/payload, rejestrację, frozen sync/import, schematy `drawing_identity`
i `attribute_evidence`, limity bezpieczeństwa, upgrade i restore 0.29.0 oraz
markery journal/trace/log. SHA-256 ZIP-a:
`78b7b24c98749ebbd28814f84d70a2fc9cbeab80b477b9fd1585e5c10e63af8e`.
Właściciel wykonał później zaplanowane próby natywne; ograniczone wyniki są
opisane poniżej. Szczegóły dostawy są w
[rekordzie dostawy](../evaluation-packages/0.30.0/README.md),
[source-ci.json](../evaluation-packages/0.30.0/source-ci.json),
[weryfikacji ZIP](../evaluation-packages/0.30.0/package-verification.json),
[logu weryfikacji](../evaluation-packages/0.30.0/package-verification.log),
[hashach artefaktów](../evaluation-packages/0.30.0/artifact-hashes.json),
[build.log](../evaluation-packages/0.30.0/build.log) i
[zweryfikowanym ZIP](../evaluation-packages/0.30.0/allplan-mcp-0.30.0-windows-evaluation.zip).
Nowy
[`attribute_evidence`](tool-reference.md#model_property_probe--isolated-read-phases)
czyta exact foreground model/view oraz 1–16 rzeczywistych ID; oddziela
ancestry, children, stored/computable wartości i runtime type. `evidence_complete`
wymaga konsensusu wrapperów i kompletności wszystkich żądanych odczytów; część
niekompletna zachowuje dane ze stanem `not_checked`. Probe nie ustala ownera ani
setter payload. `model_edit.preview`/`revalidate` dodają świeży no-op evidence i
zero-setter accounting; no-op nie ma Apply.

Właściciel zgłosił PASS prób 1, 2, 3 i 5 oraz FAIL próby 4 ścieżki
natywnego materiału. Szczegółowy zachowany log obejmuje wyłącznie próbę
5; raw response prób 1–3 nie udostępniono, a próba 4 ma tylko objawy opisane
w obserwacji. Próba 5 potwierdza cztery
konkretne scalar zapisy z readbackiem i UI Undo: tekst i integer na Column,
real na Column oraz tekst na Wall. Enum, Boolean, Beam, samodzielny Slab i
opening nie zostały zapisane z powodów opisanych w obserwacji.
[Ograniczona obserwacja 0.30.0](test-results/m4-owner-observation-0.30.0-2026-10-23.md)
i [szczegółowy log próby 5](test-results/evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md).

Plan [próby 0.30.0](m4-single-drawing-0.30.0.pl.md) łączy journal
inspect/archive/restart/replay bez powtórnego settera, Slab/MultiSlab identity
i attribute evidence, W1 no-op, osobny wynik selection versus highlight,
material eligibility oraz dostępne scalar/Enum writes na bezpiecznych nowych
fixture'ach. Próba 4 native material zakończyła się FAIL przed Apply:
preview `Żelbet` zgłosił `native_material_preservation_unavailable` i
`wall_material_tier_hierarchy_unsupported`, a drugi Wall z opening został
zablokowany przez `component_child_owner_mismatch`. Oba przypadki miały zero
zmian, setterów i Apply; materiał pozostał bez zmian.
[Ograniczona obserwacja](test-results/m4-owner-observation-0.30.0-2026-10-23.md).
Natywna selekcja pozostaje unsupported. Data/vector i nierozstrzygnięte field-owner/selection
kontrakty pozostają BLOCKED; brak fixture to `fixture_missing`. Nie powtarzać
zaakceptowanego Column delete/Undo 0.29.0. Szczegóły API i granic:
[evidence 0.30.0](m4-editing-api-0.30.0.md). Cel pełnego domknięcia
priorytetów 1–5 pozostaje aktualny, ale jest zablokowany przez nierozstrzygnięty
field owner Slab/MultiSlab, brak setter/readback payloadów date/vector i brak
kontraktu native selection set/clear/readback. Kandydat zbierał dane do ustalenia
tych kontraktów; dokumentacja i probe ich nie zastępują.

## Zachowany kandydat 0.28.0 — CI i dokładny ZIP zweryfikowane

Źródło `b59ef15d9bfd4dfb42476b240e31b5b300268d2d` na gałęzi
`fix/m4-owner-views-0.28.0` ma [PR #26 do `develop/m4`](https://github.com/blandjelly/allplan-mcp-server-python/pull/26);
CI 39871551499 zakończyło się powodzeniem: 601 testów na
Windows i 601 na Ubuntu, Python 3.12, oraz job pakietu. Przeszło też 170
unikalnych focused checks.

Oryginalny artifact CI 12466447229 (digest
`52f5a8533673c7347de2a9fe6d3e12f49a24ecc460585cf4acd8687f25922649`) nie został
dostarczony: transfer referencji pliku przez zwykły proxy zakończył się
`URLError` przed odpowiedzią HTTP. Zgodnie z polityką utworzono jeden fallback
build z czystego checkoutu dokładnego źródła (`source_modified=false`). ZIP z
186 plikami payload przeszedł dokładną weryfikację za pierwszym razem; SHA-256
`74099ec341cdf8b2bc87def42487fafbbbcdb963ec6f4b8859a412f7b6d064ed`.
Przeszły checksum/payload, rejestracja, frozen sync/import, schemat
`drawing_identity`, limity źródła, upgrade z i restore do 0.27.0, 42 hashe
mostka oraz markery aktywnego/archiwalnego dziennika, śladu i logu. Szczegóły:
[rekord pakietu](../evaluation-packages/0.28.0/README.md),
[weryfikacja](../evaluation-packages/0.28.0/package-verification.json),
[build](../evaluation-packages/0.28.0/build.log) i
[hashe artefaktów](../evaluation-packages/0.28.0/artifact-hashes.json).

Kandydat wiąże krawędzie własności rodzic–potomek usuwania po rysunku, model
UUID i typie pomiędzy wrapperami widoku; zachowuje rzeczywisty view UUID
rodzica w krawędziach podglądu/ponownej walidacji, a dokładny view UUID
wybranego targetu nadal jest związany z planem. Limity dziennika wynoszą teraz
512 aktywnych rekordów, 1 MiB na rekord, 8 MiB śladu, 32 MiB inspekcji śladu
oraz 1 GiB / 1024 pliki inwentarza archiwizacji. Blokady zapisu Slab/MultiSlab
pozostają. Właściciel zgłosił później ograniczony PASS punktów 1, 2, 3 i 5
próby Column oraz FAIL punktu 4: jedno UI Undo przywróciło tylko jeden z trzech
usuniętych Column, a dalsze Undo nie było dostępne. Brak UUID, surowych
odpowiedzi, manifestu i builda Allplana ogranicza przypisanie wyniku. Zobacz
[obserwację 0.28.0](test-results/m4-owner-observation-0.28.0-2026-10-23.md)
i [oryginalny log](test-results/evidence/allplan-chat-log-0.28.0-2026-10-23.md).
Priorytety 1–3 i 5 pozostają częściowo otwarte; priorytet 4 nie spełnia
oczekiwania grupowego Undo ani pełnej akceptacji natywnej. [Plan próby 0.28.0](m4-single-drawing-0.28.0.pl.md)
zachowuje jej zakres i wynik.
[Macierz pokrycia](m4-single-drawing-coverage-0.24.0.md) nie zastępuje odbioru
natywnego.

Nie powtarzać zaakceptowanych odczytów, zapytań, podświetleń ani zapisów
atrybutów słupów i stropów. Identyczne granice przestrzenne wyników
`Slab_TypeUUID` i `MultiSlab_TypeUUID` nie dowodzą, że reprezentują ten sam
obiekt ani dwa fizycznie odrębne cele. Przed kolejnym zapisem trzeba rozstrzygnąć
ich model/view UUID i relację właściciel–reprezentacja. Zachować blokadę dla
nierozliczonych zapisów, ponownej walidacji, replay i odzyskiwania; nigdy nie
ponawiać setterów przy wyniku `unknown`.

## Cel produktu

Użytkownik opisuje zamiar zwykłym językiem. Agent ustala zakres, elementy,
właściciela pola i typ wartości, pokazuje zakres zmian, a następnie wykonuje
wyłącznie operacje obsługiwane przez sprawdzony adapter. Domyślny zakres to
jawnie wskazane otwarte rysunki; cały projekt wymaga osobnego polecenia i
osobnego odbioru. Planowany przepływ obejmuje wyszukiwanie, widoczny wynik,
podgląd, ponowną walidację, zapis, świeży odczyt, replay, odzyskiwanie i Undo.

Przykładowe cele nadal obejmują: ściany o grubości całkowitej <240 mm z
wybranym natywnym materiałem, słupy bez odporności ogniowej z przypisaną
istniejącą warstwą W1 oraz typowane zmiany wskazanych atrybutów. Nie wolno
utożsamiać materiału natywnego, atrybutu materiału, warstwy organizacyjnej i
wykończenia. Właściciel właściwości oraz dokładny cel muszą być jawne.

## Priorytety dalszej pracy

Szczegółowy aktualny status i działanie dla priorytetów 1–5 podaje tabela na
początku tej sekcji. Wcześniejszy trial 0.30.0 zgłosił PASS prób 1–3 i 5 oraz
FAIL próby 4; jego szczegółowy log potwierdza cztery scalar zapisy z readbackiem
i Undo. Nowsze ograniczone dowody 0.31.0 potwierdzają również Wall Enum ID 120
z Apply/readback/Undo. Nie uogólniają one wyniku na Column Enum ID 49, którego
wartość pozostała niezdefiniowana, ani na Boolean/CheckBox: dla ID 1371
dostępny jest post-Undo readback bez raw Apply. Właściciel pola Slab/MultiSlab,
date/vector payloady i native selection nadal nie mają wymaganych kontraktów.
Kandydat 0.32.0 dodaje tylko bounded preservation evidence dla tieru Wall;
nie zamyka tych braków ani priorytetów 1–5.

1. **Implementacja:** zaakceptowany zakres 0.23.0 obejmuje podgląd i
   potwierdzoną archiwizację. Kandydat 0.28.0 zwiększa limity do 512 aktywnych
   rekordów, 1 MiB na rekord, 8 MiB aktywnego śladu, 32 MiB inspekcji śladu i
   inwentarza archiwizacji 1 GiB / 1024 plików. Focused checks, pełne CI i
   dokładna weryfikacja ZIP-a przeszły. Właściciel zgłosił PASS próby 1 z
   planu 0.30.0, którego zakres obejmował podgląd, archiwizację i restart/replay
   bez nowego settera; szczegółowy log tej próby nie jest dostępny, więc nie
   przypisuję PASS do poszczególnych podkroków. Nie archiwizować rekordów
   running/unknown, uszkodzonych ani niezweryfikowanych.
2. **Implementacja:** bounded identity inventory oraz fail-closed blokady
   zapisu istnieją. **Pozostaje:** lineage `Slab_TypeUUID` pod
   `MultiSlab_TypeUUID` zgłoszone w logu 0.27.0 jest nierozstrzygnięte;
   strukturalna tożsamość nie ustanawia właściciela pola. Właściciel zgłosił
   PASS próby 2 (odczyty identity/evidence), lecz brak szczegółowego logu nie
   rozstrzyga konfliktu lineage ani field owner. Nie scalać wyników ani nie
   zapisywać do nich przed wyjaśnieniem relacji i właściciela.
3. **Implementacja:** obsługa layer 0 i reviewed W1 plan/apply. **Ograniczony
   dowód native:** właściciel zgłosił W1 read/write i jeden element na krok UI
   Undo. Właściciel zgłosił PASS próby 3 no-op w 0.30.0, ale jej surowy log
   nie jest dostępny; zero setterów traktuję jako zgłoszenie na poziomie próby,
   bez niezależnego potwierdzenia odpowiedzi. Nie powtarzać przyjętego
   Undo/readback i nie wnioskować o Undo całej grupy.
4. **Implementacja:** guarded typed delete, zachowane krawędzie tożsamości
   rodzic–potomek oraz diagnostyka eligibility materiału. Kandydat 0.29.0
   rozwija jeden plan na trzy cele i wykonuje jeden plural `DeleteElements`.
   **Dowód native:** właściciel zgłosił PASS wszystkich kroków próby: świeży
   skan potwierdził brak trzech Column i kontenerów atrybutów po usunięciu;
   jedno UI Undo przywróciło wszystkie trzy. To spełnia cel naprawy grupowego
   Undo dla testowanej operacji. Log nie zawiera surowych odpowiedzi MCP, UUID
   ani manifestu ZIP-a; narzędzie nie wykonało automatycznego readbacku po Undo
   (`undo: not_checked`). [Ograniczona obserwacja](test-results/m4-owner-observation-0.29.0-2026-10-23.md).
   FAIL próby 0.28.0, w której Undo przywróciło jeden z trzech, pozostaje
   historyczny. Osobny Wall 240 mm subtree delete i dwa Beam W1 readbacki nie
   są akceptacjami Column. Selekcja pozostaje nieobsługiwana. Próba native
   material w 0.30.0 zakończyła się FAIL przed Apply: Wall z `Żelbet` zgłosił
   `native_material_preservation_unavailable` →
   `wall_material_tier_hierarchy_unsupported`, a Wall z opening zgłosił
   `component_child_owner_mismatch`; oba miały zero zmian, setterów i Apply.
   Testy focused odtworzyły błąd porównania wrapperów, ale dokładna przyczyna
   native diagnozy nie została wykazana. Kandydat 0.31.0 zmienia porównanie
   parent identity, a 0.32.0 dodaje bounded preservation evidence dla
   bezpośrednich AttributeContainer leaves. Próba native 0.32.0 jest w toku;
   nie przypisywać jej jeszcze wyniku. Native selection set/clear/readback
   nadal unsupported.
5. **Implementacja:** kontrakty scalar/Enum, inwentarz rodzin/wartości,
   bounded resolver nazw i read-only probe `attribute_evidence`. Zachowany log
   0.30.0 potwierdza cztery scalar pary (Column tekst/integer/real i Wall
   tekst), każdą z `readback_matches`, UI Undo i odczytem odtworzenia. Ograniczony
   dowód 0.31.0 potwierdza Wall Enum `Rodzaj rozliczenia` ID 120: Apply z `m3`
   na `m2`, świeży readback, jedno UI Undo i readback przywrócenia `m3`.
   **Pozostaje:** nie uogólniać Enum na inne obiekty — Column `Status` ID 49
   pozostał `<niezdefiniowany>` i BLOCKED. Wall Boolean/CheckBox ID 1371 ma
   tylko readback wartości `0` po zgłoszonym Undo; brak raw Apply dowodu, więc
   pełny cykl nie jest zaakceptowany. Pełne family/type coverage, właściciel
   pola Slab/MultiSlab i dokładne date/vector setter/readback kontrakty nadal
   wymagają dowodu. Nie uogólniać PASS na inne pary rodzina/typ.
6. **Dopiero potem zaprojektować pracę wieloplikową.** Potrzebne są manifest,
   deterministyczne partie, jawne wyniki częściowe, obsługa timeout/restart i
   pomiary dla ponad 32 zmian oraz ponad 200 wyników. Nie deklarować atomowości
   wielu rysunków ani wspólnego Undo bez dowodów.
7. **Cały projekt pozostawić osobnym rozszerzeniem.** Enumeracja niezaładowanych
   plików, ich aktywacja, przywrócenie kontekstu i niekompletność wymagają
   osobnego planu oraz odbioru. Brak dostępu nie może oznaczać zera wyników.

## Kryteria zamknięcia

- Każdy odebrany przepływ ma obserwację właściciela powiązaną z dokładną
  dostawą i buildem Allplana; zachowane wcześniej zaakceptowane obserwacje nie
  są powtarzane.
- Zapytanie raportuje kompletność i rozróżnia adaptery, właścicieli, warstwy,
  otwory i ich rodziców. Selekcja i podświetlenie mają osobne wyniki.
- Każdy typowany zapis, dodanie atrybutu, zmiana warstwy i właściwości natywnej
  ma dowód dla właściwego właściciela, UI/readback oraz Undo.
- Preview, ponowna walidacja, Apply, replay i recovery zachowują granice planu,
  rozliczają konflikt i nie ponawiają setterów po nieznanym wyniku.
- Dziennik obsługuje limity bajtów i rekordów, archiwizację, odtworzenie i
  niepewny stan bez utraty nierozliczonych zapisów.
- Limity pojedynczego rysunku, rodzin, ponad 32 zmian, wielu plików oraz całego
  projektu są raportowane jawnie i mają oddzielny odbiór.

Automatyczne testy sprawdzają przenośne kontrakty; CI i próby natywne pozostają
oddzielnymi wynikami. Wybór testów i budowy opisuje [polityka testów](testing-policy.md).
Kontrakty obecnych narzędzi są w [tool-reference](tool-reference.md), a
szczegóły bezpiecznych typów w [macierzy pokrycia](m4-attribute-type-coverage.md).
