# M4 0.16.1 — pojedyncza próba po crashu

Status: **ready_for_owner_test wyłącznie dla izolowanego odczytu słupa**.
Szeroki katalog `model_properties` jest zablokowany. Przyczyna crasha 0.16.0
pozostaje nieustalona; [analiza i dowody](../../docs/m4-native-crash-0.16.0.md).
Nie powtarzaj starego `M4 Properties.cmd` z 0.16.0.

1. Pobierz cały [pakiet 0.16.1](README.md), rozpakuj
   osobno, zamknij Allplan i stary MCP, uruchom **Setup.cmd** w nowej paczce.
   Zachowaj dotychczasowy projekt, logi, execution IDs i Local/.allplan-mcp/repairs.
2. Otwórz oryginalną zachowaną kopię MCP_QA_DEMO, **rysunek 101 jako foreground**,
   uruchom StartPythonHost oraz nowy Launch Allplan MCP.cmd. Nie zmieniaj pól modelu.
3. Uruchom **M4 Properties.cmd z 0.16.1 tylko raz**. Teraz przycisk odczyta
   surowe atrybuty jednego zwykłego słupa. Nie odczyta definicji/enumów, ściany,
   W1 ani materiału i nie podświetli modelu. Sprawdzi zdrowie hosta i zatrzyma się.
4. Zwróć `logs/m4-properties-check-*.json`,
   **Local/.allplan-mcp/logs/m4-native-probe.jsonl** oraz **bridge.log** z tego samego
   katalogu. Dopisz: czy Allplan pozostał otwarty, host odpowiadał, wersję z UI
   i PASS/FAIL/BLOCKED. Nie uruchamiaj następnych faz ani M4 Clear Highlight.

Oczekujemy: poprawna wersja/hashes hosta, jeden odczyt słupa, surowe wartości
atrybutów zachowane, brak setterów/UI oraz zdrowie hosta po próbie. Ślad na dysku
powstaje **przed** nowymi wywołaniami i jest flush/fsync; M1.column_scan jest
jednym wpisem istniejącej usługi, nie śladem każdej jej wewnętrznej metody.
Raport przechodzi przez request_pending → response_received/failed; sukces API
nie oznacza jeszcze odbioru właściwości ani jej właściciela.

Jeżeli nastąpi crash lub utrata odpowiedzi, **nie ponawiaj** przycisku. Zachowaj
oba logi natywne i JSON. Ostatni wpis started bez returned pomoże zawęzić miejsce
awarii. Gdy ślad jest pełny/niezapisywalny, próba blokuje dalsze wywołania;
nie usuwa historii. Powrót do poprzedniej instalacji: Restore bridge.cmd przy
zamkniętym Allplanie oraz poprzedni launcher. Odczyt nie wysyła Apply i nie wymaga Undo.

Po sprawdzeniu tego wyniku przygotuję kolejne, oddzielne fazy: jedna nazwa
atrybutu, jedna definicja, jedna nazwa warstwy. Nie uruchamiamy ich automatycznie.
K1/K2/K3 oraz natywne zaznaczenie pozostają otwarte.
