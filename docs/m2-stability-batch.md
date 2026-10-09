# UAT-04 — sprawdzenie stabilności po poprawce 0.6.1

**Test wykonany: UAT-04 PASS w zakresie zachowanego modelu testowego, 0.6.1.**
[Wynik, oryginalne logi i ograniczenia](test-results/m2-acceptance-0.6.1.md).
Wszystkie sześć kroków zakończyło się OK; użytkownik potwierdził działanie
Allplana i hosta. Dane audytowanych elementów odpowiadają wcześniejszemu raportowi
ze zgodnością UI potwierdzoną przez użytkownika. Poniższa karta zachowuje przepis
wykonanego testu; nie trzeba go powtarzać. Log bridge.log nie został przekazany;
jego zapis i rotacja nie są objęte tym wynikiem natywnym.
Pierwszy audyt 0.6.0 dał poprawny wynik i zgodne wskazania w UI.
Crash z 9 października o 12:50:12 czasu Warszawy wystąpił podczas kolejnego
żądania obejmującego 101 i 102. Profil demo dopuszcza wyłącznie 101:
rozszerzone żądanie powinno zostać odrzucone. Poprawka 0.6.1 zatrzymuje wyjątki
wewnątrz callbacku UI i odrzuca błędny zakres również po stronie MCP.
Bez stosu awarii jej dokładna przyczyna pozostaje hipotezą.

## Uruchomienie

1. Zachowaj oryginalną paczkę 0.6.0 oraz dotychczasowe logi. Zamknij Allplan
   i konsolę MCP. Rozpakuj **allplan-mcp-0.6.1-windows-evaluation.zip**
   do osobnego katalogu i uruchom **Setup.cmd**, wybierając ten sam katalog **Local**.
2. Otwórz zachowany projekt testowy. Pozostaw dotychczasowe celowe problemy:
   **101 aktywny**, **102 pasywny**, **103 niewczytany**. Nie odtwarzaj fixture,
   nie powtarzaj A/B/C i nie poprawiaj teraz modelu.
3. Uruchom **StartPythonHost** z Library → Private → PythonHost oraz
   **Launch Allplan MCP.cmd** z paczki 0.6.1. W czasie testu nie wywołuj
   równolegle narzędzi z innych czatów.
4. Dwukrotnie kliknij **M2 Stability.cmd**. Skrypt najpierw sprawdza wersje MCP
   i hosta, integralność instalacji oraz znacznik poprawki w załadowanym moście.
   Przy starej lub mieszanej instalacji kończy pracę przed odczytami modelu.
   Po tej kontroli wykonuje kolejno:
   dwa audyty pliku 101, odrzucenie niezgodnego zakresu 101/102 po stronie MCP,
   jeden kontrolowany test odrzucenia tego samego zakresu przez host i odczyt
   wersji potwierdzający, że host nadal odpowiada. Nie wykonuje zapisów modelu.
   Przy nieudanym odczycie kończy pracę; nie ponawia automatycznie żądania.
5. Odczytaj zapisane `logs/diagnostics-*.json` i `.txt`.
   Nie uruchamiaj skryptu ponownie, jeśli Allplan się wyłączy lub wynik będzie
   niepełny — zachowaj istniejące raporty do analizy.

## Oczekiwany wynik

| Krok w raporcie | Oczekiwane |
| --- | --- |
| host_boundary_preflight | OK; wersje zgodne z 0.6.1, integralność verified, załadowana poprawka callbacku |
| audit_1 | Pełny raport: 6 kolumn, 5 problemów na 5 kolumnach, pełna coverage |
| audit_2 | Te same 5 problemów; nadal pełny odczyt |
| mcp_scope_rejection | OK; komunikat Requested audit files exceed the explicit profile scope |
| host_scope_rejection | OK; kod invalid_payload i ten sam komunikat, z własnym request ID |
| host_health_after_rejection | OK; wersja Allplana i most 0.6.1 |

Końcowy tekst powinien zawierać **Stability checks complete: True**.
Oba audyty mają oczekiwany stan **fail**, oznaczający pięć problemów fixture.
Żądanie dla 101/102 ma celowo zwrócić błąd walidacji; ten błąd jest oczekiwanym
wynikiem kontroli i nie powinien zamknąć Allplana.

Potwierdź, że po zakończeniu skryptu **Allplan pozostaje otwarty, model jest
bez zmian, a wskazania pięciu problemów nadal zgadzają się z UI**.
Zapisane pole checks_complete dotyczy wykonania odczytów/odrzucenia błędnego
żądania; samo nie zastępuje obserwacji UI ani dłuższej weryfikacji stabilności.

## Dane do przekazania

Przekaż nowe pliki JSON/TXT oraz krótką obserwację:

> 0.6.1: oba audyty dały 5 problemów, oba odrzucenia zakresu są OK,
> host odpowiada, Allplan pozostał otwarty, model bez zmian.

Most zapisuje teraz również trwały, rotowany log w
**Local\.allplan-mcp\logs\bridge.log** (rotacja przy 1 MiB + dwa pliki historii).
Użyj faktycznego katalogu Local wybranego przy Setup.
Przy analizie kolejnego błędu przekaż też ten plik i zachowaj ewentualne `bridge.log.1/.2`.
Log zawiera czas UTC, sesję, request ID, ścieżkę żądania i wynik; dla
nieoczekiwanych wyjątków zapisuje traceback. Nie wymaga edycji kodu ani JSON.
Jeśli katalog logów jest niedostępny, host korzysta z konsoli; zgłoś brak pliku.

Akceptacja pozostaje ograniczona do fixture i odczytów. Test nie włącza napraw M3,
nie rozszerza profilu demo na 102 i nie dowodzi obsługi wszystkich awarii natywnych.
