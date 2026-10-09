# M3 — konflikt po ręcznej edycji, pakiet 0.8.1

Status: **ready_for_owner_test**. Zapis dwóch zmian, odczyt, dwa osobne kroki
Undo i Recover po Redo są [zaliczone](test-results/m3-execution-acceptance-0.8.1.md).
Nie powtarzaj Apply, M1/M2 ani instalacji. Ten krótki test sprawdza, czy plan
wykryje późniejszą ręczną edycję w Allplanie. MCP wykonuje tylko odczyty.

## Bieżąca kopia i podgląd

1. Użyj tej samej jednorazowej kopii projektu oraz zainstalowanego **0.8.1**.
   Plik **101** na pierwszym planie. Po ostatnim Redo/Recover oczekiwane:
   **S05 = SZ_OGÓ01**, **S06 MCP_QA_STATUS = NEW**, audyt 3 usterek oznaczeń.
   Sprawdź oba cele i wygląd pozostałych słupów. Jeśli stan jest inny, zgłoś go;
   nie uruchamiaj ponownie Apply ani kolejnych kroków Undo.
2. W lokalnym Codex na Windows, połączonym z tym Allplanem, wklej:

   > W pakiecie 0.8.1 wykonaj wyłącznie odczytowy fix_model_issues action=preview,
   > audit profile_id=native-model-qa-demo, scope drawing_files=[101],
   > include_passive=false, visibility=api_select_all. Wybory repairs:
   > QA-003 wartość structure, QA-004 wartość NEW. Zachowaj dokładne plan_id,
   > plan_hash i host_session_id oraz pełną odpowiedź. Wykonaj od razu revalidate
   > tego planu i sprawdź unchanged. Zapisz oryginalne odpowiedzi i host health
   > jako JSON oraz krótkie podsumowanie TXT w logs. Nie wywołuj apply, recover,
   > żadnego settera ani nowego podglądu po ręcznej zmianie. Zatrzymaj się przed
   > ręczną edycją i pokaż wynik.

   Na naprawionej kopii plan może mieć **0 proponowanych zmian** — to poprawne.
   Nie wymuszaj odtworzenia dwóch usterek. Test dotyczy niezmienności danych
   audytu, a nie ponownego zapisu. Od utworzenia planu masz pięć minut.

## Ręczna edycja i kontrola poprzedniego planu

3. W UI zmień **tylko MCP_QA_STATUS słupa S06 z NEW na EXISTING**.
   Nie zmieniaj warstwy, oznaczeń, geometrii ani pozostałych elementów.
   Zaobserwuj, czy polecenie UI zakończyło StartPythonHost.
4. Jeśli **ten sam host nadal działa**, wklej w ten sam lokalny czat:

   > Ręcznie zmieniłem S06 MCP_QA_STATUS z NEW na EXISTING. Sprawdź dokładnie
   > poprzedni plan przez fix_model_issues action=revalidate z zachowanymi
   > plan_id i plan_hash. Nie twórz nowego podglądu i niczego nie stosuj.
   > Oczekuję conflict, source_unchanged=false i read_only=true. Odczytaj health,
   > porównaj host_session_id z poprzednią sesją. Zachowaj oryginalne odpowiedzi
   > JSON i podsumowanie TXT w logs oraz wskaż, czy sesja była ta sama.

5. Oczekiwane **PASS**: `conflict`, `source_unchanged=false`, odczytowy wynik
   w tej samej sesji, S06 nadal `EXISTING`, S05 nadal `SZ_OGÓ01`, działający host.
   Nawet gdy `EXISTING` spełnia regułę statusu, zmieniła się wartość źródłowa;
   poprzedni plan musi wykryć zmianę.
6. Jeżeli UI zakończyło hosta albo plan wygasł, zakończ jako **BLOCKED dla
   konfliktu w tej samej sesji**. Możesz uruchomić host ponownie i odczytać
   stary plan: oczekiwane `plan_expired`. To zabezpieczenie po restarcie;
   nie zastępuje dowodu `conflict`. Nie odnawiaj planu jako rzekomej kontynuacji
   ani nie ponawiaj automatycznie testu.
7. Przywróć ręcznie **S06 = NEW**, sprawdź oba cele i pozostałe słupy.
   Nie używaj Apply do przywrócenia. Wyślij zapisane JSON/TXT i krótki opis:
   wynik, czy host przetrwał edycję, zgodność wartości i wyglądu modelu.

Ten test nie uruchamia zapisu ze starego planu. Natywne odrzucenie Apply po
konflikcie, szersze naprawy i M3.3 zachowują osobne granice akceptacji.
Nie zamyka samodzielnie całego M3/UAT-05/UAT-06.
