# Allplan MCP — plan rozwoju edycji modelu biurowego

## Aktualny stan

M4 jest częściowo odebrane. Właściciel potwierdził, że ostatnie wyniki agenta
odpowiadają Allplanowi: zapis dwóch atrybutów na wynikach zapytania stropów,
zmianę atrybutu `Priorytet` na dwóch wynikach oraz przypisanie `MCP_QA_MARK`
sześciu słupom w żądanej kolejności. Brak dokładnego manifestu instalacji i
części odpowiedzi MCP nie pozwala przypisać tych wyników do konkretnego
artefaktu ani rewizji. Zapis `Materiał = beton zbrojony` jest zmianą atrybutu;
nie potwierdza zmiany natywnego materiału konstrukcyjnego.

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

## Aktualny kandydat 0.28.0 — CI i dokładny ZIP zweryfikowane

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
pozostają. Próby natywnej 0.28.0 nie wykonano; priorytety 1–5 pozostają
częściowo otwarte. Kolejna ograniczona próba dotyczy tylko wskazanych Column
na W1, potomków i Undo: [plan próby](m4-single-drawing-0.28.0.pl.md).
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

1. **Implementacja:** zaakceptowany zakres 0.23.0 obejmuje podgląd i
   potwierdzoną archiwizację. Kandydat 0.28.0 zwiększa limity do 512 aktywnych
   rekordów, 1 MiB na rekord, 8 MiB aktywnego śladu, 32 MiB inspekcji śladu i
   inwentarza archiwizacji 1 GiB / 1024 plików. Focused checks, pełne CI i
   dokładna weryfikacja ZIP-a przeszły. Natywny restart/replay nie ma dowodu.
   Nie archiwizować rekordów running/unknown, uszkodzonych ani
   niezweryfikowanych.
2. **Implementacja:** bounded identity inventory oraz fail-closed blokady
   zapisu istnieją. **Pozostaje:** lineage `Slab_TypeUUID` pod
   `MultiSlab_TypeUUID` zgłoszone w logu 0.27.0 jest nierozstrzygnięte;
   strukturalna tożsamość nie ustanawia właściciela pola. Nie scalać wyników
   ani nie zapisywać do nich przed wyjaśnieniem relacji i właściciela.
3. **Implementacja:** obsługa layer 0 i reviewed W1 plan/apply. **Ograniczony
   dowód native:** właściciel zgłosił W1 read/write i jeden element na krok UI
   Undo. **Pozostaje:** jawny no-op z potwierdzeniem zera setterów nie został
   zgłoszony. Nie powtarzać przyjętego Undo/readback i nie wnioskować o Undo
   całej grupy.
4. **Implementacja:** guarded typed delete, zachowane krawędzie tożsamości
   rodzic–potomek w kandydacie 0.28.0 oraz diagnostyka eligibility materiału.
   **Dowody native:** oddzielny Wall 240 mm subtree delete z pięcioma dziećmi
   i dwa Beam W1 readbacki zgłoszono jako wykonane; nie są to akceptacje Column.
   Preview trzech Column W1 zablokował `component_child_owner_mismatch` i nie
   usunął celów. Kandydat 0.28.0 (focused checks, CI i dokładna weryfikacja ZIP-a przeszły)
   dopasowuje krawędzie po rysunku, model UUID i typie, zachowując rzeczywiste
   view UUID rodziców oraz dokładny view UUID wybranego targetu, związane z
   preview i ponowną walidacją. **Pozostaje:** natywna
   próba dokładnych Column W1, pełnego poddrzewa i Undo. Selekcja pozostaje
   nieobsługiwana, a diagnostyka materiału nie akceptuje ani nie włącza zapisu
   natywnego materiału.
5. **Implementacja:** kontrakty scalar/Enum, inwentarz rodzin/wartości oraz
   bounded resolver nazw. W próbie 0.27.0 zgłoszono PASS lowercase lookup i
   diagnostyki materiału. **Pozostaje:** pełna native macierz rodzin, właściciel
   pola i roundtrip dla konkretnego adaptera; daty, wektory i inne wartości
   nieskalarne pozostają zablokowane do czasu dokładnego setter/readback
   kontraktu oraz osobnej próby z Undo.
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
