# Ograniczona obserwacja właściciela 0.28.0 — próba Column i undo

Właściciel zgłosił wyniki krótkiej próby 0.28.0 w pięciu punktach. Dołączony
[log rozmowy Allplan](evidence/allplan-chat-log-0.28.0-2026-10-23.md) zachowuje
przebieg podświetlenia i usunięcia trzech Column. Log nie zawiera surowych
odpowiedzi MCP, manifestu instalacji, dokładnego ZIP-a ani identyfikatora
builda Allplana. Wyniki pozostają obserwacją właściciela przypisaną do
zgłoszonej wersji 0.28.0, bez przypisania do dokładnego artefaktu.

## Wyniki zgłoszone przez właściciela

| Punkt próby | Wynik | Zakres i granica dowodu |
| --- | --- | --- |
| 1. Ustalenie dokładnych celów Column na W1 | **PASS, ograniczony** | Właściciel zgłosił PASS dla identyfikacji trzech Column na W1; log wtórnie zapisuje podświetlenie trzech Column w aktywnym rysunku 101. Nie zachowano model/view UUID ani innych stabilnych identyfikatorów, więc nie można potwierdzić dokładnych celów z logu. Podświetlenie nie potwierdza natywnej selekcji. |
| 2. Preview i kontrola zakresu usunięcia | **PASS** | Log opisuje dokładnie trzy wskazane Column, każdy z jednym podrzędnym kontenerem atrybutów i bez innych wykrytych zależności. Nie zachowano odpowiedzi preview, planu/hash ani UUID. |
| 3. Potwierdzone wykonanie i świeży odczyt | **PASS, ograniczony** | Log zgłasza usunięcie trzech Column W1 oraz kontrolny odczyt potwierdzający brak wszystkich trzech. Nie ma surowego wyniku settera, kompletnego skanu, odpowiedzi dla potomków ani dowodu, że setter wykonano jednokrotnie. |
| 4. Undo całej grupy | **FAIL** | Właściciel zgłosił, że jedno UI Undo przywróciło tylko jeden z trzech usuniętych Column; dalsze Undo nie było dostępne. Oczekiwanie jednego Undo przywracającego wszystkie trzy elementy nie zostało spełnione. Log nie podaje identyfikatora przywróconego elementu ani świeżego odczytu po Undo. Nie wnioskować o przyczynie ani o zachowaniu innych operacji Undo. |
| 5. Opcjonalny read-only probe relacji rodzic–potomek | **PASS, ograniczony** | Właściciel zgłosił PASS. Log nie zawiera probe, identyfikatorów ani surowej odpowiedzi, więc nie da się niezależnie ocenić relacji ani rozszerzyć jej na inne cele. |

## Wpływ na zakres odbioru

- Punkt 4 jest niezaliczony w zakresie oczekiwania jednego Undo dla grupy trzech
  Column. PASS wykonania i odczytu po usunięciu nie zmienia tego wyniku.
- Obserwacja nie dowodzi atomowego usuwania ani atomowego Undo. Nie ustala też,
  czy pojedynczy setter lub mechanizm Allplana grupuje elementy w jednym kroku.
- Wynik nie jest powiązany z dokładnym ZIP-em, manifestem ani buildem Allplana;
  nie zastępuje surowych odpowiedzi i identyfikatorów celu.
- Priorytety 1–3 i 5 pozostają w dotychczasowym ograniczonym zakresie.
  Priorytet 4 ma zgłoszony FAIL dla grupowego Undo; obsługa Column nie uzyskuje
  pełnej akceptacji natywnej. Blokady Slab/MultiSlab, zapisu materiału i
  natywnej selekcji pozostają bez zmian.

To zapis owner-reported, bez nowej próby wykonanej w tym środowisku. Patrz
[handoff](../next-model-handoff.md), [plan rozwoju](../office-editing-development-plan.pl.md)
i [macierz pokrycia](../m4-single-drawing-coverage-0.24.0.md).
