# M4 — status odbioru na 2026-10-20; kandydat 0.23.0

## Werdykt

Najnowsza próba potwierdza użyteczne, natywne przepływy edycji atrybutów w
Allplanie: ustawienie dwóch atrybutów na wynikach zapytania stropów, zmianę
atrybutu `Priorytet` na dwóch wynikach oraz przypisanie wartości
`MCP_QA_MARK` sześciu słupom w żądanej kolejności. Właściciel potwierdza, że
wyniki agenta zgadzają się z Allplanem. To potwierdza te konkretne wyniki w
testowanej instalacji; brak manifestu dokładnie zainstalowanego pakietu oraz
brak części wcześniejszych odpowiedzi nie pozwalają przypisać ich do
konkretnego artefaktu lub rewizji.

M4 pozostaje częściowo odebrane. Dowody nie zamykają pełnej ścieżki natywnej
dla wszystkich rodzin, materialnych właściwości natywnych, selekcji UI,
bezpiecznej obsługi pełnego dziennika ani pracy wieloplikowej. Kandydat 0.23.0
dodaje archiwizację dziennika sterowaną przez agenta; jej CI i akceptacja
natywna pozostają pending; brak końcowych wyników CI, liczników testów i
hasha źródła kandydata. Niedawny zapis
`Materiał = beton zbrojony` jest zapisem atrybutu; nie dowodzi zmiany natywnego
materiału konstrukcyjnego.

Szczegóły potwierdzonych wyników i ograniczeń dowodów znajdują się w
[obserwacji właściciela z 2026-10-20](test-results/m4-agent-observation-2026-10-20.md).
Skrót nie zastępuje wcześniejszych, ograniczonych obserwacji natywnych z
handoffu i nie wnioskuje zbieżności wersji na podstawie samej nazwy „najnowsza”.

## Stan względem etapów pierwotnego planu

Plan rozdziela etapy K1–K7; implementacja API i testy atrap same nie stanowią
odbioru natywnego. Poniższy status dotyczy wyłącznie dostępnych dowodów.

| Etap | Status na podstawie dostępnych dowodów |
| --- | --- |
| K1 — katalog właściwości i rodzin | Częściowo. Celowane rozwiązywanie atrybutów i typowane zapisy wykonały konkretne przykłady. Brak kompletnego, zaakceptowanego katalogu obsługi dla rodzin, właściwości i wersji Allplana. |
| K2 — filtrowanie i widoczny wynik | Częściowo. Wcześniejsze ograniczone obserwacje zapytania/podświetlenia pozostają w handoffie. Ostatni log nie dowodzi natywnej selekcji Allplana; podświetlenie i selekcja są osobnymi zachowaniami. |
| K3 — edycja niezależna od audytu; słupy i W1 | Edycja atrybutu słupa potwierdzona dla sześciu celów. Połączona ścieżka „brak odporności ogniowej → F120 oraz W1” i natywny zapis warstwy nie są potwierdzone przez tę próbę. |
| K4 — typowane atrybuty i natywny materiał | Konkretne zapisy atrybutów potwierdzone. Próba nie dotyczy natywnego materiału ściany ani odrębnego potwierdzenia właściwości natywnej. |
| K5 — sześć rodzin | Nieodebrane jako całość. Log obejmuje słupy oraz wyniki zapytania stropów. Nie potwierdza rodziny ścian, belek, drzwi i okien ani wszystkich wariantów i właścicieli pól. |
| K6 — wiele rysunków i praca biurowa | Nieodebrane. Ograniczenia jednego aktywnego rysunku, limitów zmian, braku gwarancji atomowości i cyklu życia dziennika pozostają. Kandydat 0.23.0 implementuje jawne archiwizowanie; CI i próba akceptacyjna są pending. |
| K7 — cały projekt | Poza odbiorem; brak dowodu enumeracji i bezpiecznej obsługi niezaładowanych plików. |

Zbieżne współrzędne i granice przestrzenne wyników `Slab_TypeUUID` oraz
`MultiSlab_TypeUUID`, przy widocznej w UI jednej płycie/stropie, nie dowodzą,
że adaptery oznaczają ten sam obiekt ani że są niezależnymi obiektami.
Potrzebne są identyfikatory model/view i dowód relacji właściciel–reprezentacja.
Do czasu wyjaśnienia nie należy scalać tych wyników ani wyciągać wniosku o
unikalności fizycznych celów.

Pełne M4 według przyjętego planu obejmuje K1–K6. Domknięcie jednego aktywnego
rysunku jest odbiorem częściowym, nie zakończeniem całego M4. K7, czyli praca
na niezaładowanych plikach całego projektu, pozostaje osobnym rozszerzeniem.

## Priorytetowa lista do domknięcia

### 1. Dziennik: odbiór kandydata 0.23.0

To najbliższy praktyczny bloker zgłoszony przez właściciela. Kandydat
implementuje w `fix_model_issues` dwie jawne akcje: `preview_journal_cleanup`
oraz `cleanup_journal`, dla celów `native_trace` i `repair_records`. Preview
pokazuje zakres i wymaga potwierdzenia użytkownika; cleanup wiąże się z dokładnym
`snapshot_hash` oraz `confirmed_journal_cleanup`. Zmiana migawki wymaga nowego
preview i nowego potwierdzenia.

Mechanizmy są różne dla dwóch zasobów. Ślad diagnostyczny
`m4-native-probe.jsonl` dopisuje się do stałej ścieżki i ma limit 1 MiB;
potwierdzona rotacja archiwizuje zrecenzowane bajty i tworzy pusty aktywny plik,
zwalniając limit aktywnego śladu. Dziennik napraw ma oddzielny limit 128
aktywnych rekordów, a pojedynczy rekord ma oddzielny limit 1 MiB. Jego cleanup
przenosi do archiwum tylko poprawne i rozliczone rekordy, zachowując dokładny
execution ID dla replay. Wykonania `running`, `unknown`, uszkodzone i zbyt duże
pozostają chronione. Archiwizacja nie wykonuje wywołań modelu ani setterów.
Globalny współdzielony dziennik można sprzątać bez lookup projektu/dokumentu;
identity projektu/dokumentu nadal obowiązuje przy Apply i Recover.

Status: implementacja w kandydacie 0.23.0; pełne CI i natywna akceptacja
pozostają pending. Nie ma dokładnego błędu, stanu licznika ani rozmiaru pliku
z incydentu właściciela, więc źródło blokady nadal nie jest ustalone. Osobno
diagnozować 1 MiB aktywnego trace, limit 128 aktywnych rekordów i limit 1 MiB
na rekord. Archiwum zachowuje dane, ale nie jest polityką retencji ani
obietnicą nieograniczonego odzyskiwania miejsca na dysku. Zachować istniejące
wykonania i nierozliczony stan.

### 2. Przypiąć zaakceptowane natywne wyniki do dostawy

Zachować manifest/hash `allplan_health`, wersję MCP/hosta, plan i wynik
Apply/readback dla następnego celowanego przebiegu w kopii. Nie powtarzać już
zaakceptowanych prób atrybutów słupów/stropów; uzupełnić brakujące metadane z
zapisanych dowodów, jeśli istnieją. Powiązanie instalacji z artefaktem pozwoli
ustalić, jaki kod rzeczywiście potwierdzono, bez ponownego wykonania tych samych
zmian.

### 3. Rozstrzygnąć tożsamość wyników stropów

Na read-only odczycie zachować dokładne model UUID, view UUID, typ adaptera,
tożsamość rodzica/dziecka i relację do reprezentanta natywnego dla obu wyników.
Potwierdzić, czy są odrębnymi celami, czy różnymi adapterami tej samej
reprezentacji. Sprawdzić, że query i plan nie mnożą tej samej fizycznej zmiany
ani nie zapisują do niezamierzonego właściciela. Identyczne bounds same w sobie
nie są kryterium zlania tożsamości.

### 4. Domknąć brakującą część przepływu słupów bez powtarzania odbioru

Zachować wcześniejsze zaakceptowane odczyty, filtry, podświetlenie i zmiany
klasy ogniowej zgodnie z handoffem; nie uruchamiać ich ponownie. Pozostaje
wykazać wyłącznie brakujący zakres połączonego scenariusza K3, jeśli ma być
częścią kolejnej dostawy: dokładny właściciel i zapis istniejącej warstwy W1,
pełne rozliczenie celów/wyłączeń, odczyt zwrotny, no-op i zakres Undo.
Uwzględnić tylko zachowanie zmienione od już zaakceptowanej próby. Błędy i
utratę odpowiedzi rozliczać bez ponawiania nieznanych setterów.

### 5. Oddzielnie odebrać selekcję, native material oraz pozostałe rodziny

Sprawdzić natywną selekcję w UI osobno od już obserwowanego podświetlenia.
Osobna próba natywnego materiału musi wykazać właściwy obiekt/warstwę, zmianę
właściwości w UI i API, zachowanie geometrii i pozostałych warstw, readback oraz
Undo. Następnie rozszerzać rodzinami według K5: ściany, belki, stropy, słupy,
drzwi i okna, z odrębną tożsamością otworu i elementu wstawionego. Udokumentowane
API i wyniki atrap nie zastępują prób w konkretnym buildzie Allplana.

Uzupełnić też macierz typów zapisywalnych atrybutów projektu. Obecna wspólna
ścieżka obejmuje tekst, Integer, Double, Boolean, powiązany z SDK Integer/CheckBox
i etykiety Enum; nie ma listy dozwolonych nazw. Daty, wektory i inne obiekty SDK
nadal nie mają pełnych kodeków wejścia, zapisu i odczytu zwrotnego. Dla każdego
rzeczywiście zapisywalnego typu potrzebne są jawny kontrakt API oraz celowany
odbiór; typów nie wolno zgadywać z nazwy lub tekstu w UI. Pola obliczane i odmowy
natywnego API muszą pozostać konkretnym wynikiem read-only/unsupported, zamiast
pozornego sukcesu. [Aktualne pokrycie typów](m4-attribute-type-coverage.md).

### 6. K6 dopiero po ustaleniu granic operacji

Zaprojektować i odebrać manifest dla wielu otwartych rysunków, deterministyczne
partie, częściowe wyniki, timeout/restart oraz operacje przekraczające 32
zmiany i 200 wyników. Nie obiecywać atomowości wieloplikowej ani wspólnego Undo
bez dowodów. K7 (cały projekt) pozostaje odrębnym, opcjonalnym zakresem.

## Zakres odbioru a opcjonalne rozszerzenia

Najbliższy sensowny cel zgodny z planem to odebrać kandydata 0.23.0 w zakresie
kontrolowanej archiwizacji, a następnie domknąć brakującą część bezpiecznego
cyklu pojedynczego aktywnego rysunku: rozstrzygniętą tożsamość celu, brakującą
ścieżkę warstwy W1 oraz jawny wynik selekcji/highlight. Zachować już
zaakceptowane przepływy atrybutów bez ich ponawiania. K4 dla natywnego materiału
i K5 dla pozostałych rodzin są kolejnymi etapami.

Praca wieloplikowa, partie >32 zmian, komplet sześciu rodzin i przeszukiwanie
całego projektu mają pozostać jawnie szerszym zakresem K5–K7. Nie należy
opisywać M4 jako ukończonego na podstawie ostatnich trzech przepływów atrybutów.

## Kryteria zamknięcia M4

- Dla każdego zaakceptowanego przepływu istnieje obserwacja właściciela
  powiązana z dokładną dostawą i buildem Allplana, bez utraty wcześniejszych
  zaakceptowanych wyników.
- Zapytanie wykazuje pełne pokrycie, a identity/ownership rozróżnia adaptery,
  warstwy, otwory i ich rodziców; selekcja oraz highlight mają osobne wyniki.
- Typowane zapisy atrybutów, dodawanie, warstwy i natywne właściwości mają
  niezależny dowód dla właściwego właściciela, UI/readback i Undo.
- Preview/revalidate/Apply/recovery/replay/restart zachowują granice planu,
  nie ponawiają nieznanych setterów i rozliczają konflikt ręcznej edycji.
- Dziennik obsługuje limity rekordów i bajtów, kopię/archiwizację, odzyskanie
  oraz kontrolowane czyszczenie bez utraty nierozliczonego stanu.
- Ograniczenia jednego rysunku, >32 zmian, wielu plików, rodzin i zakresu całego
  projektu są jawne; rozszerzenia dostają osobny odbiór przed deklaracją obsługi.

Automatyczne testy i CI weryfikują przenośne kontrakty. Nie zastępują natywnego
odbioru. Zgodnie z polityką testów zmiany dokumentacji wymagają przeglądu diffu
i linków; nie wymagają testów runtime ani budowania pakietu.
