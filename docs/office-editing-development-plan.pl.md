# Allplan MCP — plan rozwoju edycji modelu biurowego

## Aktualny stan

M4 jest częściowo odebrane. Właściciel potwierdził, że ostatnie wyniki agenta
odpowiadają Allplanowi: zapis dwóch atrybutów na wynikach zapytania stropów,
zmianę atrybutu `Priorytet` na dwóch wynikach oraz przypisanie `MCP_QA_MARK`
sześciu słupom w żądanej kolejności. Brak dokładnego manifestu instalacji i
części odpowiedzi MCP nie pozwala przypisać tych wyników do konkretnego
artefaktu ani rewizji. Zapis `Materiał = beton zbrojony` jest zmianą atrybutu;
nie potwierdza zmiany natywnego materiału konstrukcyjnego.

Kandydat **0.23.0** dodaje kontrolowany podgląd i archiwizację śladu
diagnostycznego oraz rozliczonych rekordów dziennika. Źródło
`8c71de958c47ab4cb418a62fbd2d55ce76cbc4db` przeszło pełne CI: 505 testów na
każdej konfiguracji Windows/Ubuntu, Python 3.12, a następnie jeden build.
Dokładny ZIP z CI przeszedł sprawdzenie payloadu, instalację, aktualizację z
0.22.1 i przywrócenie; zachowano 38 hashy mostka i znaczniki dziennika,
śladu oraz archiwów. Natywna próba nowej obsługi dziennika nadal czeka na
wykonanie. [Pakiet 0.23.0](../evaluation-packages/0.23.0/README.md) ·
[krótka próba](m4-journal-cleanup-0.23.0.pl.md) ·
[obserwacja właściciela](test-results/m4-agent-observation-2026-10-20.md).

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

1. **Odebrać czyszczenie dziennika 0.23.0.** Wykonać wyłącznie krótką próbę z
   przewodnika, na kopii projektu i dokładnym pakiecie. Sprawdzić podgląd,
   wymagane potwierdzenie, zmianę migawki, archiwizację i zachowanie replay.
   Nie usuwać, nie archiwizować ani nie zmieniać nierozliczonego, uszkodzonego
   lub zbyt dużego rekordu. Incydent właściciela nie zawiera dokładnego błędu,
   więc osobno rozróżnić limit 1 MiB śladu, 128 aktywnych rekordów i limit 1 MiB
   na rekord; nie przypisywać przyczyny bez dowodu.
2. **Ustalić tożsamość celów stropów.** W read-only zachować typ adaptera,
   model/view UUID, tożsamość rodzica/dziecka i relację do reprezentanta
   natywnego. Nie scalać wyników na podstawie samych bounds. Sprawdzić, że
   zapytanie i plan nie mnożą zmian ani nie zapisują do niewłaściwego właściciela.
3. **Domknąć brakujące elementy pojedynczego rysunku.** Zbadać tylko
   niepotwierdzony zapis istniejącej warstwy W1, pełne rozliczenie celów i
   wyłączeń, świeży readback, no-op oraz zakres Undo. Nie powtarzać
   zaakceptowanych filtrów, podświetleń i zapisów atrybutów.
4. **Rozdzielnie odebrać natywną selekcję i natywny materiał.** Podświetlenie
   nie jest dowodem selekcji Allplana. Próba materiału musi wskazać właściwy
   obiekt lub warstwę, potwierdzić zmianę w UI i API, zachować geometrię i
   pozostałe warstwy oraz sprawdzić readback i Undo.
5. **Rozszerzać macierz rodzin i typów.** Obecne celowane zapisy obejmują
   tekst, Integer, Double, Boolean, SDK Integer/CheckBox i etykiety Enum.
   Daty, wektory i inne obiekty SDK nie mają pełnych, odebranych kodeków.
   Sprawdzić osobno ściany, belki, stropy, słupy, drzwi i okna, w tym właściciela
   pola, warianty natywne, otwory i elementy wstawione. API ani atrapowe testy
   nie zastępują krótkiej próby w konkretnym buildzie Allplana.
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
