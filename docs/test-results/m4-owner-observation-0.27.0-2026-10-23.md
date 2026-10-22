# Ograniczona obserwacja właściciela 0.27.0 — 23 października 2026

Ta notatka rozdziela bezpośredni raport właściciela o punktach krótkiej próby
0.27.0 od dołączonego logu rozmowy Allplan. Raport i log nie zawierają
manifestu instalacji, surowych odpowiedzi MCP ani identyfikatora builda
Allplana. Wyników nie przypisuję więc do konkretnego ZIP-a ani rewizji źródła.

## Bezpośredni raport o próbie 0.27.0

Właściciel zgłosił:

| Punkt próby | Wynik zgłoszony | Granica dowodu |
| --- | --- | --- |
| 1. Rozpoznanie lowercase `mcp_qa_mark` | **PASS** — resolver rozpoznał nazwę. | Brak zachowanej surowej odpowiedzi, kanonicznego ID i manifestu. Nie powtarzać zaakceptowanego lookupu. |
| 2. Diagnostyka natywnego materiału Wall | **PASS** — diagnostyka próby działała zgodnie z oczekiwaniem. | To PASS diagnostyki, nie zapisu materiału ani akceptacji native material. Brak surowej odpowiedzi i dokładnego celu. Nie powtarzać tej samej obserwacji. |
| 3. Warstwa W1 i Undo | **PASS ograniczony** — właściciel zgłosił, że odczyt/zapis W1 działa, a jedno cofnięcie UI cofa jedną zmianę elementu. | Nie podano dokładnych celów, starego/nowego ID, liczby setterów ani manifestu. Nie zgłoszono jawnego no-op ani potwierdzenia zera setterów. Nie wnioskować o wspólnym lub wieloelementowym Undo. |

Są to raporty właściciela, a nie surowe odpowiedzi narzędzi. Zachować je jako
ograniczone obserwacje i nie przypisywać dokładnej dostawie.

## Istotne wyniki w dołączonym logu Allplan

Oryginalny plik jest zachowany bez zmian w
[evidence/allplan-chat-log-0.27.0-2026-10-23.md](evidence/allplan-chat-log-0.27.0-2026-10-23.md).

- Podgląd usunięcia trzech słupów Column na W1 został zablokowany przez
  `component_child_owner_mismatch`; słupy nie zostały wtedy usunięte.
  Szczegółowego wyniku ponowienia nie ma w zachowanym logu. Nie przypisywać
  tego błędu do potwierdzonej przyczyny bez surowej odpowiedzi.
- Oddzielne, potwierdzone usunięcie pozostałej ściany 240 mm zakończyło się
  świeżym kompletnym odczytem potwierdzającym brak ściany i jej pięciu dzieci.
  To ograniczony Wall subtree PASS; nie dowodzi obsługi Column ani ogólnej
  kaskady dla wszystkich rodzin.
- Dwie belki zostały przeniesione na W1 (ID 65535), a odczyt zwrotny zgłosił
  nowe przypisanie dla obu. To raportowane wykonanie, bez surowych odpowiedzi
  i dokładnego manifestu.
- Read-only probe stropu zgłosił `MultiSlab_TypeUUID` z model UUID
  `bf097d95-8275-4229-ac74-27bbea26c211` i view UUID
  `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`. Warstwa płyty `Slab_TypeUUID` miała
  model UUID `8a693925-ae20-4dda-91d1-3951af3c0a52`; wpis własności podawał
  view UUID `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, a świeży skan adaptera
  `d947addb-95fd-410b-a320-5c9ee0af72eb`. Lineage nie zostało potwierdzone z
  powodu konfliktu własności. Nie zapisywać do tych celów ani nie utożsamiać
  ich na podstawie bounds.

Pozostałe pytania w logu obejmowały wcześniejsze odczyty, podświetlenie i
operacje. Nie rozszerzają powyższych wyników ani nie stanowią dowodu selekcji
natywnej, zmiany materiału, no-op lub Undo dla niewskazanych celów.

## Wpływ na priorytety

- Punkt 1 krótkiej próby (resolver) ma zgłoszony PASS; nie stanowi to kodeka
  wartości ani pokrycia rodzin.
- Punkt 2 krótkiej próby (diagnostyka materiału) ma zgłoszony PASS; setter
  materiału pozostaje bez akceptacji.
- Punkt 3 daje ograniczone W1/Undo: jeden element na krok Undo. No-op nie został
  sprawdzony.
- Tożsamość i własność Slab/MultiSlab pozostają nierozstrzygnięte.
- Usuwanie Column pozostaje zablokowane; wcześniejsze usunięcie Wall i zapis
  W1 dla Beam mają odrębny zakres i nie rozszerzają akceptacji rodzin.

Nie wykonano nowej próby natywnej w bieżącym środowisku. Następny planowany
zakres dotyczy wyłącznie dokładnych celów Column na W1 i brakującego dowodu
usunięcia, potomków oraz Undo; patrz [krótka próba 0.28.0](../m4-single-drawing-0.28.0.pl.md).
