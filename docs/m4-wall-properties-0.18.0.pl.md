# M4 Wall Properties — krótka próba 0.18.0

Ta próba odczytuje jedną istniejącą natywną ścianę jednowarstwową. Zakres:
pakiet **0.18.0**, Allplan **2026-1-7** (API **2026.1**), zachowana kopia
**MCP_QA_DEMO** i rysunek **101 foreground**. Pakiet 0.18.0 zawiera niezmieniony
runtime Columns z 0.17.2 oraz nowy launcher **M4 Wall Properties.cmd**.
Najpierw wykonaj kontrole źródła, CI i instalacji opisane w
[README pakietu 0.18.0](../evaluation-packages/0.18.0/README.md).

## Przygotowanie

1. Zachowaj istniejącą kopię testową z natywną ścianą jednowarstwową
   **200 × 4000 × 3000 mm**. Zgodnie z [przewodnikiem fixture](fixture-guide.md)
   spodziewana próbka ma jedną warstwę o grubości 200 mm. Nie twórz nowej ściany
   na potrzeby tej próby.
2. Możesz najpierw zainstalować 0.17.2 i wykonać jego sprawdzenie Columns
   (Słupy 1, 5 i 6). Nie jest to zależność kodowa ani warunek uruchomienia próby
   ściany; obie wersje możesz sprawdzić później. Zachowaj logi i
   `Local/.allplan-mcp/repairs`.
3. Przed przejściem do 0.18.0 zamknij Allplan i MCP. Uruchom `Setup.cmd` z
   pakietu 0.18.0, wybierz ten sam rzeczywisty katalog `Local`, a następnie
   ponownie otwórz Allplan, zachowaną kopię MCP_QA_DEMO i uruchom MCP. Przygotuj
   model przed startem PythonHost; jeśli polecenia UI zakończą host, uruchom go
   ponownie z biblioteki. Zachowaj też natywny trace.

## Jedna próba odczytu

1. Użyj **M4 Wall Properties.cmd**. Launcher wykonuje `health_before`, zapisuje
   lokalnie żądanie oczekujące **przed wysłaniem** pojedynczego wywołania
   `model_property_probe` z fazą `wall_sample` w pliku 101,
   a po odpowiedzi wykonuje `health_after` w tej samej sesji hosta. Nie wysyłaj
   ręcznie kolejnego żądania.
2. Faza enumeruje zaakceptowane korzenie M1, wybiera jeden jednoznaczny
   korzeń `Wall_TypeUUID` (pierwszy według UUID modelu) i odczytuje jego natywne `GetElement`, `.Properties`
   i `.TierCount`. Jeśli `TierCount != 1`, kończy się jako nieobsługiwane przed
   odczytem warstw. Dla warstwy o indeksie 1 odczytuje `.Thickness` i `.Material`.
   Nie wywołuje broad discovery, `GetEnumValues`, filtrów po całym modelu,
   podświetlania ani zapisów.
3. Oczekuj jednej próbki ściany, `TierCount = 1`, wartości grubości
   odpowiadającej **200 mm** przy założeniu jednostek API w mm oraz
   `sample.criterion.matches_assuming_native_mm = true`, bo 200 < 240. Jednostka mm jest założeniem do
   potwierdzenia natywnym odczytem; fixture i oczekiwanie nie dowodzą jej
   samodzielnie. Porównaj surową wartość materiału z dokładną wartością
   pokazywaną przez UI Allplana. Nie przeliczaj jej na arbitralny atrybut,
   powierzchnię ani klasę C35.
4. Brakujące lub nieprawidłowe pola raportuj jako `not_checked` i zakończ próbę
   bez fallbacku i ponowienia. Utrata odpowiedzi również nie uruchamia nowej
   próby. Jeśli Allplan ulegnie awarii, nie uruchamiaj odczytu ponownie;
   zachowaj trace i logi. Trwałe granice zapisu trace nie stanowią gwarancji
   izolacji ani przechwycenia native crash.

Próba jest wyłącznie do odczytu i nie wymaga Undo. Odczyt natywnych właściwości nie włącza zapisu materiału;
przed jakimikolwiek zapisami materiału wymagany jest osobny natywny test
odczytu/zapisu i odczytu zwrotnego.

Zachowaj `logs/wall-properties-*.json` i `.txt`, `bridge.log`,
`Local/.allplan-mcp/logs/m4-native-probe.jsonl` oraz
`Local/.allplan-mcp/repairs`. Zgłoś PASS/FAIL/BLOCKED dla odczytu jednej
ściany, `TierCount`, grubości/jednostki, materiału, obu odpowiedzi health i
braku zmian w modelu. Podaj wszelkie pola `not_checked` bez interpretowania ich
jako wartości pustych lub domyślnych.

Przykład modyfikacji ściany w oficjalnych skryptach Allplan pokazuje odczyt
`WallElement.Properties`, `TierCount` i właściwości warstw przez
`GetWallTierProperties(iCnt+1)`; jest to punkt odniesienia dla rodziny API,
nie dowód akceptacji natywnej próby: [ModifyWall.py, przykłady przypięte do
8e2c252477e20bc9afac8918f78a8eeabd473a81](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/ModifyObjects/ModifyWall.py).
Przykład [WallInteractor.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/InteractorExamples/WallInteractor.py#L436)
ustawia materiał warstwy; getter `WallTierProperties.Material` w tej próbie
wymaga osobnego potwierdzenia i przy braku obsługi kończy się `not_checked`.
Żaden setter z przykładów SDK nie jest wywoływany przez diagnostykę.
