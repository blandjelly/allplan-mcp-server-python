# Polityka dokumentacji

Na początku każdej pracy przeczytaj ten plik, [politykę testów](testing-policy.md),
[handoff](next-model-handoff.md) i [plan rozwoju](office-editing-development-plan.pl.md).
Przed zakończeniem pracy zaktualizuj istniejące opisy stanu, jeśli zmieniły się
zadania, wersja, wyniki weryfikacji lub blokady.

## Dwa miejsca z kluczowymi informacjami

- **Handoff** przekazuje następnemu modelowi konkretny kolejny krok i aktualny
  stan. Musi wystarczyć do wznowienia pracy bez czytania historii rozmów.
- **Plan rozwoju** zawiera aktualne zadania, zależności, nierozwiązane błędy
  i kryteria zamknięcia. Jest jednym backlogiem, nie kroniką wydań.
- Nie kopiuj obszernych opisów między plikami. W handoffie podaj krótkie
  podsumowanie i link do właściwego zadania w planie. Dowody mogą być podlinkowane,
  ale istotny wynik, jego ograniczenia i wpływ na dalszą pracę muszą być w tych
  dwóch plikach; nie przenoś ich wyłącznie do osobnego raportu.

## Jak aktualizować handoff

Utrzymuj następującą kolejność:

1. **Następne zadanie:** cel, dokładny zakres, warunki rozpoczęcia, konkretne
   działanie i kryterium zakończenia. Wskaż blokady oraz próby już odebrane,
   których nie należy powtarzać. Gdy zadanie zakończono, zastąp je kolejnym.
2. **Ostatnia wersja:** aktualny kandydat lub wersja, najważniejsze zachowanie,
   branch/rewizja i link do istniejącej dostawy, jeśli potrzebny. Krótko rozdziel
   focused checks, pełne CI, weryfikację pakietu i wynik natywny. Nie utożsamiaj
   implementacji ani testów automatycznych z odbiorem w Allplanie.
3. **Kluczowe błędy i niezbędny wcześniejszy kontekst:** zachowaj tylko informacje
   potrzebne do kolejnego kroku, ochrony nierozliczonego stanu lub uniknięcia
   powtórzenia odebranych prób. Podaj objaw/diagnostykę, status i link do zadania
   lub dowodu; zachowaj potrzebne identyfikatory wykonania i ograniczenia wyniku.

Po nowej wersji zastąp opis poprzedniej. Starsze wersje sprowadź do krótkiego
podsumowania tylko tam, gdzie nadal wpływają na pracę. Usuń nieaktualne zalecenia,
powielone wyniki, szczegóły dawnych buildów i rozwiązane blokady. Historia zmian
pozostaje w Git. Nie usuwaj informacji o nieznanym wyniku ani zabezpieczeń
zapisu tylko po to, by skrócić tekst.

## Jak aktualizować plan rozwoju

Aktualizuj istniejące zadania i ich status zamiast dopisywać sekcje kolejnych
wersji. Dla otwartej pracy podaj: co zostało, aktualną blokadę/zależność i dowód
lub warunek zamknięcia. Odróżniaj błąd, brak kontraktu API, brak fixture
i oczekiwanie na próbę natywną. Potwierdzone rozwiązanie usuwa zadanie albo
pozostawia jednozdaniowy wynik, jeśli jest nadal potrzebny.
Opis aktualnej wersji i najbliższego kroku skróć do odnośnika do handoffu;
nie kopiuj historii dostaw, testów ani chronologii napraw.

## Kiedy tworzyć osobny plik

Domyślnie aktualizuj handoff i plan. Nie twórz osobnych handoffów, changelogów,
opisów wersji, planów pojedynczych prób, podsumowań sesji ani raportów statusu.
Krótką procedurę następnego zadania i jego wynik zapisz w istniejących plikach.
Istniejące instrukcje instalacji i testów aktualizuj w ich właściwym miejscu.

Wyjątkiem są **opisy działania API i odkrycia dotyczące API**. Najpierw rozszerz
pasujący dokument; nowy utwórz tylko dla odrębnego tematu. Podaj źródła,
zakres API/builda, ustalone kontrakty, ograniczenia i nierozstrzygnięte pytania.
Oddziel dokumentację SDK, hipotezę i obserwację natywną. Nie dodawaj do notatki
API drugiej historii wydań ani backlogu; wynik istotny dla dalszej pracy streść
w handoffie i zaktualizuj zadanie w planie.

Surowe dowody i maszynowe artefakty wymagane przez politykę testów lub diagnozę
zachowuj bez zmian w istniejących miejscach. Linkuj je zamiast przepisywać logi,
hashy i pełne wyniki do dokumentacji; nie dodawaj im zbędnych opisowych raportów.

## Kontrola przed zakończeniem

Sprawdź zgodność handoffu z planem, usuń sprzeczne lub zduplikowane informacje,
zweryfikuj odnośniki i przejrzyj diff. Dla zmian wyłącznie dokumentacyjnych
stosuj [politykę testów](testing-policy.md): bez testów runtime i buildów.
