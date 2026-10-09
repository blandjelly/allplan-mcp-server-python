# M2 — zebranie danych po crashu Allplana

**Zbieranie danych wykonano.** [Wynik i poprawka 0.6.1](test-results/m2-dispatch-fix-0.6.1.md).
Późniejszy [test 0.6.1 zaliczono; UAT-04 PASS w zachowanym zakresie odczytu](test-results/m2-acceptance-0.6.1.md).
Poniższe polecenie zachowujemy jako opis wykonanej diagnostyki; nie trzeba go powtarzać.

Pierwszy audyt z paczki 0.6.0 zakończył się poprawnie; raport
`diagnostics-20261009T104813Z` zawiera 5 oczekiwanych problemów.
Użytkownik potwierdził zgodność z UI i brak zmian modelu.
Późniejsze wywołanie `model_audit` w innym czacie utraciło odpowiedź hosta:
`execution_unknown`, ID **101efe01-58e9-4296-aa93-e1a2c18b60b4**.
Zgłoszono również crash Allplana, prawdopodobnie przy tym drugim wywołaniu;
dokładna kolejność i przyczyna wymagają danych systemowych.

Historyczny stan przed zebraniem danych: UAT-04 pozostawał otwarty. Zadaniem było zebranie istniejących danych,
bez kolejnej instalacji, odtwarzania fixture ani ponawiania audytu.
Chmurowy czat z katalogiem `/workspace` nie ma dostępu do zdarzeń Windows
na komputerze z Allplanem.

## Polecenie do lokalnego czatu Codex na Windows

Wklej poniższy tekst w lokalnym czacie Windows, który używał narzędzia:

> Zdiagnozuj zgłoszony crash Allplana po odczycie model_audit z paczki 0.6.0.
> Pierwszy raport diagnostics-20261009T104813Z został zapisany poprawnie
> 2026-10-09 około 12:48 czasu Europe/Warsaw. Późniejsze żądanie
> 101efe01-58e9-4296-aa93-e1a2c18b60b4 utraciło odpowiedź hosta
> (execution_unknown), prawdopodobnie przy wyłączeniu Allplana.
>
> Zbierz tylko istniejące dane. Nie ponawiaj model_audit ani innych odczytów
> modelu, nie zmieniaj modelu, nie reinstaluj mostu i nie kasuj logów.
> Odczytaj zdarzenia Windows Application Error / Windows Error Reporting
> dotyczące Allplana od około 12:45 tego dnia do zgłoszonej awarii
> (typowo zdarzenia 1000/1001; szukaj też po nazwie programu).
> Podaj dokładny czas ze strefą, nazwę i wersję aplikacji oraz modułu powodującego
> awarię, kod wyjątku, offset błędu i identyfikator raportu.
> Sprawdź dostępne istniejące logi Allplana, konsoli MCP/mostu i odpowiedź
> drugiego czatu dla tego request ID. Zapisz dokładne argumenty drugiego
> model_audit i błędy, jeśli zostały zachowane. Odczytaj metadane dostępnego
> raportu WER/minidumpu; nie włączaj nowego zrzutu ani odtwarzania crasha.
> Zapisz zebrane zdarzenia i krótkie podsumowanie w nowym pliku diagnostycznym
> w katalogu logs paczki. Jeśli źródło nie jest dostępne, zapisz tę informację
> zamiast wnioskować, że awarii nie było. Zachowaj wszystkie oryginalne pliki.

Przekaż wynik tego odczytu w tym czacie. Moduł/kod wyjątku oraz kolejność zdarzeń
pozwolą wybrać ukierunkowany dalszy test lub poprawkę. Sam `execution_unknown`
potwierdza utratę odpowiedzi, a nie źródło crasha. Nie zakładamy ani sprawności
drugiego audytu, ani związku przyczynowego bez tych danych.
