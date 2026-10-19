# 0.22.1 — krótka próba odzyskiwania zapisu

W [ostatnim logu](test-results/m4-agent-followup-2026-10-19.md) odzyskiwanie
pierwszej belki zatrzymuje się na wielu widokach tego samego elementu. Kandydat
odczytuje je wszystkie i rozlicza wynik tylko przy zgodnych wartościach. Nie
ponawia zapisu. Nowy podgląd wiąże konkretny widok do wykonania zmiany.
Testy automatyczne używają atrap API; wynik natywny wymaga poniższej próby.

1. Zainstaluj 0.22.1 przez `Setup.cmd`, zachowując oryginalny dziennik. Otwórz
   ten sam projekt i dokument 101. Uruchom ponownie `StartPythonHost` i połączenie
   MCP, aby załadować nowe moduły. Sprawdź `allplan_health` i zachowaj informację
   o wersji/paczce 0.22.1 razem z wynikiem próby.
2. Poproś agenta: „Odzyskaj wykonanie 4388b04e39a14fac811db4f58723d01f bez
   ponawiania zapisów. Pokaż wynik oraz pozostałe blokery”. Zachowaj pełny JSON.
3. Jeżeli blokada została rozliczona, wydaj jedno z oczekujących poleceń, np.
   zmianę samych atrybutów obu belek: Nazwa przekroju na 450X450 i Długość na
   5 m. Agent sprawdza bieżące typy/jednostki, tworzy świeży podgląd i wykonuje
   dozwolony zapis. Sprawdź wartości w UI i odczyt kontrolny.
4. Jeśli odzyskiwanie nadal blokuje, zachowaj odpowiedź z etapem, przyczyną i
   `representation_consensus`, dziennik oraz natywny trace. Nie usuwaj dziennika.

Nie trzeba powtarzać działającego wyszukiwania warstw, filtrów, podświetlania
ani zaakceptowanych zmian U i klasy ogniowej. Zakres tej próby obejmuje wyłącznie
odzyskanie starego wykonania oraz jeden kolejny zapis. Zmiana atrybutów belki
nie zmienia jej geometrii. Pozostają kontrola projektu/dokumentu, jednego
aktywnego rysunku, świeżego podglądu, limit 32 setterów i blokada nieznanych wyników.
