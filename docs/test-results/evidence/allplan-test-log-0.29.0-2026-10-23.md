# Log testu Allplan — usuwanie słupów na warstwie W1

**Data:** 2026-10-23  
**Środowisko:** Allplan 2026.1, aktywny rysunek 101  
**Cel testu:** sprawdzić wybór i usunięcie wszystkich słupów na warstwie W1 oraz zachowanie operacji Undo.

## Przebieg

1. Sprawdzono połączenie z hostem Allplan. Host był osiągalny, wersja 2026.1, integralność bridge zweryfikowana bez rozbieżności.
2. Rozpoznano warstwę `W1` (ID 65535; nazwa `W1 (W1)`). W aktywnym rysunku znaleziono 3 elementy typu `Column_TypeUUID` na tej warstwie.
3. Wysłano te elementy do podświetlenia. Interaktor nie obsługuje natywnego zaznaczania programowego; widoczności podświetlenia nie dało się potwierdzić automatycznie.
4. Przygotowano plan usunięcia dokładnie tych 3 słupów. Plan obejmował także należące do nich kontenery atrybutów. Użytkownik potwierdził, że to kopia robocza i zaakceptował plan.
5. Wykonano usunięcie przez `DeleteElements`. Wynik operacji zgłosił stan `completed`; świeży skan potwierdził nieobecność wszystkich 3 słupów i ich kontenerów atrybutów.
6. Użytkownik wykonał jedno Undo w Allplan i zgłosił, że przywróciło ono wszystkie usunięte słupy.

## Wynik

- **Usunięcie:** wszystkie 3 słupy zostały usunięte.
- **Undo:** pojedyncze Undo przywróciło wszystkie 3 słupy.
- **Wniosek z testu:** usunięcie trzech słupów zostało zarejestrowane jako jedna operacja cofania w interfejsie Allplan.

## Uwagi

- Narzędzie raportowało `undo: not_checked` i samo nie wykonywało cofania. Przywrócenie po Undo jest obserwacją użytkownika.
- Operacja dotyczyła aktywnego rysunku 101 w kopii roboczej. Nie sprawdzano innych, niezaładowanych rysunków.
- W odpowiedzi narzędzia `runtime_verified` i `allplan_acceptance` pozostały niepotwierdzone.
