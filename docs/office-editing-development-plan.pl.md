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

1. **Czyszczenie dziennika 0.23.0 — ograniczony PASS właściciela.** Zapisano
   podgląd i potwierdzoną archiwizację obu zakresów; nie powtarzać tej próby.
   Zmiana migawki i replay po restarcie mają testy automatyczne, ale nie są
   widoczne w dostarczonym wyniku natywnym.
   Nie usuwać, nie archiwizować ani nie zmieniać nierozliczonego, uszkodzonego
   lub zbyt dużego rekordu. Incydent właściciela nie zawiera dokładnego błędu,
   więc osobno rozróżnić limit 1 MiB śladu, 128 aktywnych rekordów i limit 1 MiB
   na rekord; nie przypisywać przyczyny bez dowodu.
2. **Tożsamość celów stropów — odczyt i blokady wdrożone, wynik natywny
   nierozstrzygnięty.** Odczyt `model_identity` ograniczono do `file_state` i
   wymaganej tożsamości type; różne `layer_id` lub nazwy w wrapperach nie
   blokują już strukturalnego wyniku. Regresja obejmuje taką rozbieżność, ale
   nie ustala przyczyny ani nie rozstrzyga natywnego błędu właściciela z 0.24.0.
   Log 0.24.0 opisuje dwa wyniki `Slab_TypeUUID` i
   `MultiSlab_TypeUUID`; dokładny probe pierwszego zwrócił
   `probe_scope_unavailable`, a view UUID płyty potomnej w drugim różnił się
   od view UUID pierwszego wyniku. Zachować typ adaptera, model/view UUID,
   rodzica/dziecko i reprezentację natywną. Nie scalać wyników na podstawie
   bounds ani nie zapisywać do nich przed wyjaśnieniem relacji celu.
3. **Pojedynczy rysunek — rozszerzone testy automatyczne, brak natywnego W1
   no-op/Undo.** Log 0.24.0 potwierdza readback warstwy W1 (ID 65535) dla
   słupa `(12000, 6000 mm)`, ale nie no-op ani Undo. Użyć krótkiej próby 0.25.0
   wyłącznie dla niezaobserwowanych no-op/Undo na jawnych, odrębnych celach.
   Nie powtarzać poprzedniego readbacku ani zaakceptowanych zapisów atrybutów.
4. **Selekcja, usuwanie i materiał — oddzielne stany implementacji i odbioru.**
   Log 0.24.0 stwierdza, że selekcja programowa jest nieobsługiwana;
   podświetlenie ma tylko stan `submitted`, bez potwierdzenia widoczności.
   Usunięcie słupa `MCP_QA_MARK=6` w UI i późniejszy odczyt zera wyników
   potwierdzają przepływ UI, nie API MCP. Kandydat 0.25.0 dodaje typowane
   usunięcie dokładnego root z weryfikacją całego poddrzewa; jego obsługa
   kaskady nie jest zakładana. Dodaje też eksperymentalny setter natywnego
   materiału dla jednowarstwowej ściany, oparty na udokumentowanych metodach
   SDK i jawnych dowodach niezmienników. Obie ścieżki wymagają ograniczonej
   próby właściciela. Selekcja nadal jest nieobsługiwana.
5. **Macierz rodzin i typów — uzupełniona, odbiór natywny nadal częściowy.**
   [Macierz 0.24.0](m4-single-drawing-coverage-0.24.0.md) rozdziela adaptery,
   właścicieli, testy i nieobsługiwane kodeki. Obecne celowane zapisy obejmują
   tekst, Integer, Double, Boolean, SDK Integer/CheckBox i etykiety Enum.
   Daty, wektory i inne obiekty SDK pozostają zablokowane: brak zaakceptowanego
   payloadu/settera istniejącego adaptera i dokładnego readbacku w tym
   kontrakcie. Samo `AttributeDate`, `AttributeDoubleVec` lub
   `Polyhedron3D.WriteToStream` tego nie ustanawia.
   Sprawdzić osobno ściany, belki, stropy, słupy, drzwi i okna, w tym właściciela
   pola, warianty natywne, otwory i elementy wstawione. API ani atrapowe testy
   nie zastępują krótkiej próby w konkretnym buildzie Allplana. Log 0.24.0
   dodaje ograniczone obserwacje atrybutu ściany REI120 i usuwania słupa przez
   UI; nie odbiera to pełnej macierzy rodzin ani natywnego materiału.
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
