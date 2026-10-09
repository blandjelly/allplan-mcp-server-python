# M3 — odrzucenie starego Apply po restarcie, pakiet 0.8.1

Status: **ready_for_owner_test**. [Poprzedni test](test-results/m3-plan-restart-acceptance-0.8.1.md)
potwierdził odrzucenie starego podglądu przez `plan_expired` po restarcie.
Kliknięcie w UI zakończyło hosta, dlatego nie powtarzamy testu konfliktu w tej
samej sesji. Teraz sprawdzamy odrzucenie przez wejście **Apply**, z audytem
przed i po. Oczekiwane jest odrzucenie przed pierwszym zapisem.

Użyj **tej samej jednorazowej kopii i zainstalowanego 0.8.1**. Nie przeinstalowuj,
nie odbudowuj słupów i nie uruchamiaj **M3 Apply.cmd**, który utworzyłby nowy plan.
Nie zmieniaj modelu w UI podczas testu. Jeśli S06 pozostał `EXISTING` po ręcznej
edycji, zachowaj ten stan na czas porównania — test nie wymaga przywracania NEW.

## Jedno polecenie w lokalnym Codex na Windows

Wklej do czatu połączonego z tym Allplanem:

> Wykonaj test odrzucenia starego planu w pakiecie 0.8.1 na tej samej kopii
> testowej. Najpierw odczytaj allplan_health: MCP i host muszą mieć wersję 0.8.1,
> source_commit 8074905536ff5c95e20de4a59a70d513f8694314 i zweryfikowaną
> integralność. Bieżący host_session_id musi różnić się od
> fdca1b5c-b147-4ac4-9c9e-4019eda2203b. Jeśli warunki nie są spełnione, zatrzymaj
> test i zapisz diagnostykę.
>
> Odczytaj pełny model_audit, profile_id native-model-qa-demo, scope
> drawing_files=[101], include_passive=false, visibility=api_select_all.
> Wymagana jest kompletna kontrola sześciu słupów. Zachowaj cały wynik,
> source_fingerprint, report_fingerprint oraz wartości warstwy S05 i statusu S06.
> Nie twórz nowego podglądu.
>
> Wygeneruj jeden nowy execution_id w formacie 32 małych znaków hex. Zapisz go
> i dokładne poniższe żądanie do osobnego pliku w logs **przed wysłaniem**.
> Nie nadpisuj m3-last-execution.json z zaliczonego zapisu dwóch zmian.
> Wywołaj fix_model_issues dokładnie raz z request:
> action=apply, plan_id=500b57e169df4a6d99e982d413282542,
> plan_hash=8687e394b90923fd99ca666fdc3f3ee588fe92dec7b5effdd483e16268dfa420,
> execution_id=<wygenerowany identyfikator>,
> acknowledgement=disposable_copy_reviewed_two_repairs.
> To stary plan z poprzedniej sesji; nie zastępuj go świeżym planem.
>
> Oczekiwane: state=rejected, native_setters_started=false, read_only=true,
> error.code=plan_expired. Zachowaj pełną oryginalną odpowiedź. Nie ponawiaj
> wywołania, nie stosuj nowego planu, nie wykonuj Recover ani Undo automatycznie.
> Jeśli nie otrzymasz jawnego odrzucenia przed zapisem, zatrzymaj test i zapisz
> wynik do diagnostyki.
>
> Po oczekiwanym odrzuceniu powtórz ten sam odczytowy model_audit i health.
> Sprawdź kompletność, tę samą sesję hosta i identyczne source_fingerprint oraz
> report_fingerprint audytu przed/po. Warstwa S05 i status S06 muszą być takie
> same jak przed żądaniem. Zapisz oryginalne odpowiedzi, żądanie i porównanie
> jako allplan_stale_apply_rejection.json oraz krótkie TXT w logs.

Wyślij oba pliki oraz informację, czy wartości i wygląd słupów pozostały bez
zmian. **PASS** wymaga jawnego odrzucenia, zgodnych audytów i działającego hosta.
W tym wyniku Undo nie jest potrzebne. To osobny test zabezpieczenia starego
żądania, nie powtórzenie zaliczonego zapisu dwóch napraw. M3.3 i szerszy zakres
pozostają kolejnymi etapami; nie zamykamy całego M3 na podstawie tego testu.
