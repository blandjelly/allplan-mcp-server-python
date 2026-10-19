# M4 0.21.1 — krótka próba odczytu atrybutów i warstwy ściany

Kandydat 0.21.1 adresuje problemy odkrywania i wiązania atrybutów zgłoszone w
logu właściciela z 2026-10-18. Właściciel identyfikuje używaną wersję jako
0.21.0; dokładny build hash i surowe żądania/odpowiedzi MCP nie są dostępne.
Zapisane odmowy i zmiany są więc obserwacjami właściciela dla tej wersji, ale
nie pozwalają odtworzyć konkretnej odpowiedzi ani przyczyny API.
[Zachowany log](test-results/evidence/m4-agent-test-2026-10-18.md) ·
[Obserwacja właściciela](test-results/m4-agent-observation-2026-10-18.md).

## Stan potwierdzony przez właściciela dla 0.21.0

- U słupa ustawiono na 0,2 i potwierdzono odczytem zwrotnym.
- U ściany 200 mm ustawiono na 0,15 i potwierdzono odczytem zwrotnym.
- Zmiana klasy odporności ogniowej słupa F60 → F90 została potwierdzona.
- W tym samym planie `Poziom_Górny` 500 → 300 nie została potwierdzona; odczyt
  pozostał 500, a wykonanie zatrzymało się po częściowym zapisie.
- Dla ściany 200 mm filtr `<240 mm` i W1 zostały rozpoznane, lecz plan zmiany
  warstwy otrzymał blokadę i zapis nie nastąpił. Także wcześniejsze polecenie
  `<24 cm` nie zmieniło warstwy. Zgoda użytkownika nie ominęła blokady.
- Właściciel potwierdził widoczny highlight słupa. Zachowujemy tę obserwację.

Nie powtarzaj zaakceptowanych prób U dla słupa/ściany, klasy ogniochronnej,
query ani highlight. Częściowy zapis F90/poziom górny jest obserwacją, a nie
dowodem rollbacku. Ogólny setter dla `Poziom_Górny` pozostaje nieobsługiwany
lub niezweryfikowany; 0.21.1 nie deklaruje poprawki tej ścieżki.

## Zakres kandydata 0.21.1

- Dla równoważnych wrapperów ściany porównywać odczytane wartości atrybutów,
  zamiast odrzucać odczyt wyłącznie z powodu różnych reprezentacji obiektu.
- Zachowywać surowe atrybuty i stronicowanie także wtedy, gdy odczyt metadanych
  zawiedzie. Niepełne metadane nadal nie dowodzą kompletności ani zapisywalności.
- Rozwiązywać nazwę z małą literą początkową przez roundtrip z nazwą/ID
  projektu. Nie tłumaczyć etykiet i nie zgadywać synonimów.
- Wymagać kompletności kryterium i celu dla elementów pasujących oraz ich
  pełnej rewalidacji źródłowej. Nie blokować planu z powodu nieistotnych,
  niepasujących elementów. Raportować `required_field_failures` oraz
  `criterion_failures`.
- Nie osłabiać zabezpieczeń dla nieznanej hierarchii warstw ściany. Nie twierdzić,
  że log ujawnia dokładną przyczynę odmowy warstwy: brak surowego payloadu.

Ogólna edycja skalarna po identyfikatorze atrybutu pozostaje istniejącą ścieżką
dla Column, Wall, Beam i Slab. Ten kandydat nie dodaje natywnej obsługi tych
rodzin ani zapisu właściwości natywnych/materiału. Obsługa nieznanej hierarchii
warstw i natywny zapis warstwy ściany wymagają osobnego potwierdzenia.

## Ograniczona próba właściciela

Próbę wykonaj na kandydatach 0.21.1 w kopii projektu i aktywnym rysunku
foreground. Zapisz wersję zgłoszoną przez aplikację, `health` przed i po,
surowe odpowiedzi MCP, diagnostykę planu oraz obserwacje UI. Build hash pozostaw
nieznany, jeśli aplikacja go nie podaje. Każdy zapis wymaga planu, świeżej
rewalidacji, właściwego potwierdzenia kopii testowej i nowego execution ID.
Przy blokadzie nie zapisuj; utraconą odpowiedź sprawdź przez read-only recover
z tym samym ID, bez ponawiania Apply.

1. **Nowe listowanie i lookup ściany.** Na jednej ścianie odczytaj atrybuty
   przez nowe rozwiązywanie wrapperów. Sprawdź dokładne ID/nazwę, zachowanie
   surowej wartości, strony wyników i diagnostykę błędów metadanych. Sprawdź
   lookup nazwy `materiał` pisanej małą literą; wymagaj roundtripu do dokładnej
   nazwy/ID projektu. Nie zapisuj atrybutu Materiał i nie zakładaj tłumaczeń.
2. **Opcjonalne odczyty reprezentatywne.** Jeśli są dostępne bez zmiany modelu,
   odczytaj po jednym Beam i Slab, zapisując kompletność i diagnostykę. Nie
   traktuj tego jako nowej natywnej akceptacji rodziny.
3. **Warstwa ściany.** Przygotuj kryterium
   `wall.total_thickness_mm < 240` z jawnym zakresem `native_types=["Wall_TypeUUID"]`
   (lub warunkiem AND `family=wall`) i cel W1. Sprawdź raporty
   `required_field_failures` / `criterion_failures`, wynik dla ściany 200 mm
   oraz wykluczenie 240 mm. Jeśli pełna rewalidacja, plan i odpowiedź wyraźnie
   dopuszczają Apply, wykonaj pojedynczą próbę i sprawdź warstwę w UI, świeży
   readback oraz Undo. Jeśli odpowiedź blokuje zapis, zatrzymaj się i zachowaj
   dokładny powód; nie omijaj zabezpieczeń.

## Walidacja kandydata

- Automatyczne CI 0.21.1: **PASS**, Windows/Ubuntu Python 3.12, po 448 testów,
  dla źródła `41e0cabf1352ffc54b5e35b68adbf3fed498e8d4`.
- Paczka 0.21.1 i weryfikacja instalacji/dostawy: **PASS** — dokładny ZIP,
  36 sum plików mostu, aktualizacja z 0.21.0 i restore, z zachowaniem dziennika
  i logów. [Paczka i dowody](../evaluation-packages/0.21.1/README.md).
- Próba natywna 0.21.1: **not_run** do czasu obserwacji właściciela.

Nie aktualizuj tych statusów na podstawie testów przenośnych ani opisu API.
