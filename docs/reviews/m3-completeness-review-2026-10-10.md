# Ocena kompletności M3 — 10.10.2026

**Werdykt: M3 jest częściowo zrealizowany i zgodny z architekturą planu, ale nie realizuje jeszcze całej planowanej funkcjonalności. UAT-05/UAT-06 oraz pierwszego MVP nie należy zamykać.**

Sprawdzono repozytorium `blandjelly/allplan-mcp-server-python`, aktualny [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2), wersję **0.10.0**, commit **ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f**. PR jest otwarty jako draft i bazuje na `codex/m2-audit-accepted`. `main` zawiera zaakceptowane M0–M2, wersję 0.6.1; jego informacja o M3 0.7.0 nie opisuje aktualnego stanu gałęzi M3.

Podstawą oceny są [plan M3 i warunki zakończenia](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/docs/implementation-plan.md#L122), [zakres narzędzi](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/docs/features.md#L24), kod, testy oraz zapisane raporty odbiorów Allplana. Nie wykonywano nowej sesji natywnego Allplana.

## Pokrycie planu

| Zadanie | Co istnieje i ma pokrycie testami | Co pozostaje otwarte | Ocena |
| --- | --- | --- | --- |
| M3.1 — wspólny cykl preview/apply | Dokładny plan i hash, stare/nowe wartości, TTL, unieważnianie, świeża walidacja pełnego źródła, blokada zapisów, identyfikator wykonania, odczyt po zapisie, zatrzymanie po błędzie, częściowe/nieznane wyniki. Zapis i dwa kroki Undo potwierdzone dla dwóch napraw demo. | Wykonanie planów standardów/selekcji; natywne potwierdzenie konfliktu ręcznej zmiany w tej samej sesji; natywne scenariusze częściowego/nieznanego wyniku. | Częściowo wykonane, z ograniczonym odbiorem. |
| M3.2 — fix_model_issues | Podgląd napraw warstwy/statusu; jawne propozycje oznaczeń z kontrolą kolizji; natywny zapis warstwy S05 i statusu S06 w pliku 101. | Obsługiwany zakres zapisu jest zakodowany pod konkretny scenariusz demo; brak zapisu oznaczeń i szerszego zakresu atrybutów. | Częściowo wykonane. |
| M3.3 — standardy i rule_based_edit | Wspólny planer, jeden wersjonowany standard warstwy/statusu, selekcja i wyjątki, pełny audyt i ponowna walidacja, podgląd oznaczeń. | Oba narzędzia przyjmują tylko preview; brak zastosowania zmian. Standard nie obejmuje zapisu oznaczeń ani numeracji, które są wymienione w planowanym zakresie. | Podglądy wykonane; operacje edycyjne nieukończone. |
| M3.4 — trwałe wykonania i recovery | Dziennik z hashem, atomowy zapis i znacznik przed setterem, deduplikacja exact-ID, blokowanie nowych operacji przy nierozliczonym wyniku, recovery bez ponownego zapisu. Powtórzenie po restarcie hosta i obserwacja po Undo/Redo są udokumentowane. | Native unknown-outcome recovery nieodebrane; trwałość po awarii aplikacji/systemu i utracie zasilania niepotwierdzona. Tożsamość kopii projektu i szerszy cykl życia rejestru mają jawne ograniczenia. | Zaimplementowana podstawa; odbiór częściowy. |

## Najważniejsze luki

1. **Brak rzeczywistego apply dla M3.3.** `OfficeStandardPreview.action` oraz odziedziczony kontrakt `RuleBasedPreview` dopuszczają tylko `preview`. Executor odrzuca każdy plan z metadanymi `selection`, `workflow` lub `mark_validation`, nawet jeżeli pozostałe zmiany są identyczne jak w zaakceptowanym demo. Nie wystarczy więc podać takiego planu do `fix_model_issues`. To zamierzona granica bezpieczeństwa, ale także brak funkcjonalności wymaganej do zamknięcia M3.3. [Kontrakty wejścia](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/src/allplan_mcp/standard_models.py#L10), [blokada executora](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/python_host/PythonPartsScripts/PythonHost/repair_execution.py#L88).

2. **Zapis napraw jest ograniczony do konkretnej pary testowej.** Wymagane są dokładnie dwie zmiany, trzy wykluczenia, pięć usterek, aktywny plik 101 i typ Column. Jedna zmiana dotyczy S05 i warstwy SZ_OGÓ01, druga S06 oraz istniejącego MCP_QA_STATUS: NWE → NEW. Poprawny plan jednej naprawy lub innego wspieranego przez odczyt elementu nie staje się wykonywalny. To działający pionowy fragment funkcji, a nie pełny zakres planowanego narzędzia napraw. [Warunki dopuszczenia](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/python_host/PythonPartsScripts/PythonHost/repair_execution.py#L89).

3. **Oznaczenia są symulowane, numeracja nie jest zaimplementowana.** Wersja 0.10.0 poprawnie planuje jawne oznaczenia konkretnych UUID i sprawdza kolizje także z wykluczonymi elementami. Nie zapisuje tych oznaczeń. Jedyny standard zawiera dwie reguły warstwy/statusu i jawnie odkłada oznaczenia oraz numerację. Numeracja widnieje natomiast w planowanym zakresie `apply_office_standard`. [Standard](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/src/allplan_mcp/office_standard.py#L6). Etykiety graficzne, przenoszenie plików i dowolne właściwości natywne są osobno odroczone — ich brak nie powinien automatycznie powiększać obowiązkowego zakresu M3.

4. **Niepełny odbiór konfliktów i odzyskiwania nieznanego wyniku.** Testy na atrapach pokrywają zmianę źródła, błędy dysku, przerwanie po znaczniku zapisu i recovery. Natywny odbiór wykazał odrzucenie planu po restarcie, ale nie konflikt ręcznej zmiany przy zachowaniu tego samego planu w sesji: czynność UI zatrzymała hosta. Odczyt zakończonego wykonania po Redo nie dowodzi recovery po utraconej odpowiedzi ani po częściowym zapisie. [Odbiór wykonania i ograniczenia](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/docs/test-results/m3-execution-acceptance-0.8.1.md), [odrzucenie starego Apply](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/docs/test-results/m3-stale-apply-acceptance-0.8.1.md). Nie należy powtarzać znanego zablokowanego scenariusza UI bez rozwiązania problemu cyklu życia hosta.

5. **Dokumentacja statusu wymaga uzgodnienia.** Aktualny [kontrakt oznaczeń](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/docs/m3-marks-contract.md#L3) nadal mówi `ready_for_owner_test` i `not_run`, mimo [zapisanego odbioru PASS 0.10.0](https://github.com/blandjelly/allplan-mcp-server-python/blob/ad146f69ecd5c5bab6b1bf5c2dd1218ec7a6558f/docs/test-results/m3-marks-acceptance-0.10.0.md#L1). Dodatkowo kontrakt wykonania nadal wskazuje stale-Apply jako następny test, choć ten odbiór jest zakończony. Należy aktualizować bieżące kontrakty/odnośniki, zachowując oryginalne logi i historyczne flagi bez zmian. Integracja z `main` pozostaje osobną pracą; draft PR nie dostarcza jeszcze M3 użytkownikom tej gałęzi.

## Kryteria UAT-05/UAT-06

| Kryterium | Dostępny dowód | Wniosek |
| --- | --- | --- |
| Preview nie zmienia modelu | Odbiory 0.7.0, 0.9.0 i 0.10.0; zgodne audyty i obserwacje właściciela. | PASS w zapisanym zakresie. |
| Zmieniają się wyłącznie autoryzowane, zapisywalne cele | Preflight, dwa settery, odczyt po zapisie, porównanie audytowanych pól i obserwacje UI w 0.8.1. | PASS dla dwóch celów i sprawdzanych pól. |
| Naprawy demo zostawiają trzy usterki | Odbiór 0.8.1: warstwa/status naprawione, trzy usterki oznaczeń pozostają. | PASS. Nie należy mylić tego z brakiem napraw demo. |
| Stare plany/ręczne edycje powodują konflikt | Restart i stale Apply odebrane; zmiana danych w tej samej sesji testowana przenośnie, natywnie zablokowana cyklem hosta. | Częściowo potwierdzone. |
| Powtórzone żądanie nie powtarza zapisu | Exact execution-ID replay, także po restarcie hosta i Undo. | PASS dla istniejącego dziennika i testowego zakresu. |
| Ponowny audyt/odczyt odpowiada modelowi | 0.8.1: dwa odczyty, pełny audyt sześciu słupów i weryfikacja ich audytowanych pól. | PASS w zakresie fixture. |
| Recovery nieznanego wyniku zgodnie z M3.4 | Testy atrap przechodzą; zapisany native recovery dotyczy zakończonego wykonania. | Odbiór natywny nadal otwarty. |

**Undo:** dwa osobne kroki są udokumentowanym, przetestowanym ograniczeniem. Sam brak grupowego Undo nie jest automatycznie naruszeniem punktu M3.1, który wymaga przetestowanych ograniczeń Undo; nie wolno jednak deklarować jednej atomowej transakcji ani automatycznego rollbacku.

**Zakres 0.9.0:** trzy natywne podglądy standardu/selekcji miały zero zmian. Potwierdzają ścieżkę odczytu, wyjątki i no-op. Dodatnie propozycje oznaczeń i kolizja zostały następnie odebrane w 0.10.0, co nadal nie potwierdza wykonywania standardów/selekcji.

## Przeprowadzona weryfikacja

- Odtworzono źródła aktualnego commita przez konektor GitHub w `/workspace/m3-review`; 154 pliki źródłowe/dokumentacyjne poza archiwami dostaw i katalogami surowych dowodów mają zgodne identyfikatory Git blob. Zwykły `git fetch` był niedostępny z powodu nieosiągalnego proxy środowiska.
- Lokalnie **35/35 testów logiki M3 PASS**: `test_model_repair`, `test_repair_execution`, `test_standard_preview`, `test_mark_preview`. [Log](/tmp/m3-focused-tests.log).
- Próba pełnego lokalnego zestawu: 165 testów, 138 zakończonych poprawnie, 25 błędów uprawnień do gniazd sieciowych oraz 2 błędy braku metadanych Git w odtworzonej kopii używanej do testów pakowania. Nie są to potwierdzone błędy produktu. [Log próby](/tmp/m3-unittest.log).
- Automatyczna kontrola uprawnień odrzuciła uruchomienie całego zestawu z siecią, wskazując ryzyko niezamierzonych połączeń wychodzących/ujawnienia danych przez kod repozytorium. Nie obchodzono blokady. Ocenę uzupełniono testami bez sieci i istniejącym CI.
- Zweryfikowano [CI aktualnego commita](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38059799006): **6/6 zadań PASS**, Windows/Ubuntu, Python 3.11–3.13. Workflow wykonuje pełny zestaw unittest, build wheel/sdist i pakiet Windows.
- Przeczytano zapisane decyzje natywnego odbioru 0.8.1/0.9.0/0.10.0 i ich pliki `verification.json`. To istniejące dowody projektu; w tej ocenie nie wykonywano nowych operacji w Allplanie ani ponownej pełnej weryfikacji binarnych ZIP-ów i wszystkich surowych logów.
- Repozytorium robocze `/workspace/allplan-mcp-server-python` pozostało bez zmian. Raport nie zmienia statusów odbioru ani PR.

## Kolejność domknięcia

1. Rozszerzyć wspólny executor o jawnie wspierane naprawy atrybutów/warstw poza zakodowaną parą demo; następnie podłączyć zatwierdzone plany standardów i selekcji. Zachować hash, kontrolę źródła, wyjątki, deduplikację i odczyt po zapisie.
2. Zaimplementować przewidziane dla M3 oznaczenia/numerację w standardzie albo jawnie zatwierdzić zmianę bazowego zakresu. Samo umieszczenie funkcji jako „deferred” w opisie kolejnego przyrostu nie zamyka pierwotnego wymagania.
3. Zaprojektować natywne sprawdzenie konfliktu danych w obsługiwanym cyklu życia hosta oraz kontrolowanego partial/unknown outcome i read-only recovery. Nie powtarzać już zaakceptowanych prób bez istotnej zmiany.
4. Ujednolicić bieżącą dokumentację, udokumentować obsługę limitu dziennika 128 rekordów i jego zachowania podczas aktualizacji/kopii/odtwarzania, a następnie przeprowadzić integrację z `main` i końcowy odbiór zadeklarowanego zakresu.

Nie podano procentu ukończenia: plan nie definiuje wag, a liczba testów lub zakończonych przyrostów nie mierzy kompletności funkcji. Najtrafniejszy status to **„zaawansowana implementacja częściowa: zaakceptowane podglądy i ograniczone naprawy, M3/MVP nadal otwarte”**.
