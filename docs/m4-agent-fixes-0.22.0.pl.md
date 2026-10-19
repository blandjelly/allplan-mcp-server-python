# 0.22.0 — zapis atrybutów i nazwy warstw

Kandydat obejmuje źródła testowanej wersji 0.21.1 i poprawki po
[teście właściciela z 19 października](test-results/m4-agent-observation-0.21.1-2026-10-19.md).
Testy automatyczne używają atrap API. Działanie nowego kodu w natywnym Allplanie
wymaga poniższej krótkiej próby na zachowanej kopii roboczej.

## Co zmienia kandydat

- Odzyskiwanie M4 sprawdza tożsamość oryginalnego projektu i dokumentu, a potem
  odczytuje dokładne elementy z dziennika. Nie wymaga ponownego wykonania całego
  kryterium wyszukiwania. Potwierdzenie starej albo nowej wartości rozlicza
  nieznany wynik; nieznany odczyt nadal blokuje zapis. Odzyskiwanie nie ponawia
  ani nie cofa setterów.
- Wyszukiwanie elementów pomija wyłącznie adaptery potwierdzone jako null lub
  usunięte. Świeży odczyt pozostaje wymagany. Dla atrybutu potwierdzonego przez
  SDK jako Double wartości liczbowe `5` i `5.0` są równoważne; surowy odczyt
  pozostaje w dzienniku. Boolean i Integer pozostają różnymi typami.
- `true`/`false` może zostać zakodowane jako `1`/`0` dla atrybutu Integer tylko
  po potwierdzeniu kontrolki CheckBox w bieżącym SDK. Podgląd wiąże tę informację
  i sprawdza ją ponownie przed zapisem. Typ Enum w trybie auto rozwiązuje
  dokładną etykietę przez API; nie zgaduje kodów ani nie pobiera całego słownika.
- Warstwy można wyszukiwać po nazwie pełnej i skróconej. Allplan 2026 udostępnia
  stronicowany, odczytowy `model_property_probe` z fazą `layer_catalog`.
  Agent kontynuuje po `next_action`; po znalezieniu niepewnego dopasowania pokazuje
  pełną nazwę, skrót i ID do potwierdzenia. W podglądzie zmiany używa następnie
  potwierdzonego skrótu. Nazw nie tłumaczy i nie usuwa polskich znaków.

## Krótka próba w Allplanie

1. Zainstaluj 0.22.0 przez `Setup.cmd`, zachowując dotychczasowy dziennik.
   Otwórz oryginalną kopię projektu i dokument 101. Sprawdź `allplan_health`.
2. Poproś agenta o odzyskiwanie wykonania
   `4388b04e39a14fac811db4f58723d01f`. Zachowaj pełną odpowiedź JSON.
   Przy rozliczonym wyniku agent przygotowuje nowy podgląd. Przy nadal nieznanym
   wyniku zwraca etap, przyczynę i blokery; nie usuwaj dziennika.
3. Powtórz polecenie zmiany **samych atrybutów** obu belek: Nazwa przekroju na
   450X450 i Długość na 5 m, a potem Element nośny na true. Agent odczytuje
   identyfikatory i typy z projektu, sprawdza jednostkę długości, pokazuje zakres
   i wykonuje dozwolony zapis. Sprawdź wartości w UI i odczyt kontrolny.
4. Poleć przeniesienie pozostałej ściany na pełną nazwę „ogólne03”. Agent ma
   wyszukać zarówno pełną nazwę, jak skrót i w razie wątpliwości poprosić
   o potwierdzenie pary nazw. Następnie sprawdź przeniesienie wybranej belki
   oraz stropu na SZ_OGÓ01. Nie powtarzaj już zaakceptowanego filtra grubości,
   podświetlania ani wcześniejszych zmian U/klasy ogniowej.
5. Zachowaj odpowiedzi podglądu, Apply, recovery i health oraz natywny trace.
   Sprawdź UI i w razie potrzeby natywne Undo na kopii roboczej.

## Granice obsługi

Nie ma listy dozwolonych nazw atrybutów: istniejące definicje projektu typu
tekst, Integer, Double, Boolean i Enum korzystają ze wspólnej ścieżki zapisu.
Sama obecność atrybutu w API nie dowodzi edytowalności. Pola obliczane i odmowa
natywnego zapisu muszą dawać konkretny wynik, bez pozorowania sukcesu. Daty
i obiekty wektorowe wymagają dalszych kodeków; ten kandydat nie deklaruje
pełnej obsługi wszystkich typów API. Zmiana atrybutu długości lub nazwy przekroju
nie jest zmianą geometrii belki. Pozostają limity jednego aktywnego rysunku
i 32 setterów na operację; dziennik, świeża rewalidacja i kontrola wyniku obowiązują.
