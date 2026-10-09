# Diagnostyka istniejących danych awarii Allplan 0.6.0 — 2026-10-09

Awaria jest potwierdzona przez log Allplana i trzy zdarzenia WER APPCRASH. Nastąpiła w czasie zarejestrowanego drugiego wywołania model_audit. Dostępne dane nie ustalają, czy audyt ją spowodował. Sam status narzędzia „read_only” nie wyklucza awarii aplikacji podczas odczytu.

Wszystkie godziny lokalne poniżej: Europe/Warsaw, CEST, UTC+02:00.

| Dane | Wartość i źródło |
| --- | --- |
| Początek obsługi wyjątku | 2026-10-09 12:50:12.730+02:00, Allplan.log:1118 |
| Zapis wyjątku | 2026-10-09 12:50:12.737+02:00, Allplan.log:1119–1121 |
| Aplikacja | Allplan 2026, D:\Programy\Allplan\Prg\allplan_2026.exe |
| Wersja | Plik 16.1617.8659.814; CrashAnalysisTrace.out: „Allplan 2026-1-7 39.1617.8659.814” |
| Kod wyjątku | 0xE0434352, zapisany bezpośrednio w Allplan.log |
| Adres wyjątku | 0x00007FFE90A941CA — adres bezwzględny, nie offset modułu |
| Moduł / wersja modułu / offset | Nieustalone: brak tych pól w dostępnych WER; zrzut incydentu niedostępny |
| Identyfikator raportu WER | a35dfec4-b6eb-4017-84fa-c7f7817f32f7 |
| WER 1001 / RecordID 71756 | 2026-10-09 12:50:49.7516877+02:00; raport w kolejce |
| WER 1001 / RecordID 71757 | 2026-10-09 12:50:49.7563833+02:00; wskazanie CrashDump.dmp |
| WER 1001 / RecordID 71765 | 2026-10-09 12:50:51.4689025+02:00; raport zarchiwizowany, bucket 1321673411613697263 |

To trzy etapy tego samego raportu WER, nie dowód trzech odrębnych awarii. Zdarzenia zachowano z pełnym XML i treścią w diagnostics-crash-20261009.json.

## Kolejność zdarzeń

1. Pierwszy raport: captured_at 12:48:09.367986+02:00, zapis plików około 12:48:13.316+02:00. Żądanie f8b09464-39a2-4ffe-9c23-87450ea6208f, sesja 7273e304-ddd3-4f89-bbc4-5a46020bd6d5. Profil demo, tylko 101, include_passive=false. Pełny wynik: 6 elementów, 5 usterek na 5 elementach, 0 kontroli nieustalonych. „fail” w raporcie oznacza wykryte usterki QA; odpowiedź została zapisana poprawnie.
2. Drugie wywołanie z czatu „Locate allplan_health”: zarejestrowany przedział 12:50:07.761–12:50:15.195+02:00, wraz z narzutem wywołania i przeglądu zgody. Osobno raportowany czas narzędzia: 2.803423200 s; nie ma bezpośredniego znacznika wejścia do odczytu hosta.
3. Allplan.log rejestruje wyjątek o 12:50:12.737+02:00, a następnie zakończenie logów i Stop SDS2Server.exe o 12:50:14.829+02:00.
4. Odpowiedź narzędzia: execution_unknown, request ID 101efe01-58e9-4296-aa93-e1a2c18b60b4. Zachowany output wrappera o 12:50:15.203+02:00; odpowiedź czatu o 12:50:16.701+02:00. WER publikuje raport o 12:50:49–12:50:51.

Dokładne argumenty drugiego narzędzia, z zachowanego zapisu sesji:

```json
{
  "request": {
    "profile_id": "native-model-qa-demo",
    "scope": {
      "drawing_files": [
        101,
        102
      ],
      "include_passive": true,
      "visibility": "api_select_all"
    }
  }
}
```

Dokładny komunikat:

```text
Error calling tool 'model_audit': The host response was lost or unreadable. Inspect the model before retrying a write. [code=execution_unknown, request_id=101efe01-58e9-4296-aa93-e1a2c18b60b4]
```

Drugie wywołanie rozszerzyło zakres o pasywny plik 102. Jest to różnica względem pierwszego audytu, ale nie dowód przyczyny. Odczyt czatu „Kontynuuj moduł m2 do testów” potwierdza zgłoszenie użytkownika, że crash mógł wystąpić przy tym kolejnym żądaniu; nie zawiera zrzutu ani stosu wyjątku.

## Dostępność źródeł

- Application: odczytano dokładny przedział 12:45–12:51:30+02:00. Zwrócił trzy wpisy Allplan WER 1001, bez pasującego Application Error 1000. Brak 1000 nie oznacza braku awarii. WER ma P1=Allplan 2026, P2=Nemetschek i puste P3–P10; nie zawiera modułu ani offsetu.
- Logi Allplan.log, Allplan.1.log, Allplan.2.log, Associations.log, RuleEngine.log oraz log licencji: odczytane; zapisano metadane, SHA-256 i fragmenty dla badanego czasu. Brak request ID w tych logach. CrashAnalysisTrace.out zachowano w całości jako ponumerowane wiersze; zawiera wersję i ślady interaktora StartPythonHost, bez stosu wyjątku powiązanego z tym request ID.
- Archiwum WER: C:\ProgramData\Microsoft\Windows\WER\ReportArchive\AppCrash_Allplan 2026_9cfde4cf15267735ec9f8463f4c46d61edefcd_00000000_a35dfec4-b6eb-4017-84fa-c7f7817f32f7 — odmowa dostępu także poza sandboxem. Nie zmieniano uprawnień systemowych.
- Wskazany przez WER C:\Users\dawid\AppData\Local\Temp\NemCrash_20261009-1244-000B014269506818\CrashDump.dmp — ścieżka nie istnieje podczas zbierania. Nie utworzono nowego zrzutu.
- WER Temp XML: metadane pliku dostępne (5716 bajtów, mtime 10:50:49.990844 UTC), treść niedostępna z powodu odmowy dostępu. Katalog ReportQueue tego raportu nie istnieje podczas zbierania.
- Dostępne CrashDumps Allplan_2026.exe.24704.dmp i Allplan_2026.exe.27988.dmp: odczytano metadane pliku i nagłówka MDMP; daty 2026-09-29 i 2026-10-08. Nie przypisano ich do obecnego incydentu.
- Pozostałe siedem WER LiveKernelEvent w badanym przedziale wskazuje starsze WATCHDOG dumps ze stycznia–maja 2026. Zachowano wpisy jako kontekst, bez przypisywania im związku przyczynowego z Allplanem.
- Konsola MCP/mostu: brak terminala podłączonego do czatu i brak zachowanego transkryptu konsoli w logs paczki. launch.cmd nie przekierowuje stdout/stderr, a kod mostu używa logging bez własnego FileHandler. Treść natywnej konsoli nie jest dostępna przez włączone narzędzia.
- Istniejąca baza logów Codexa: odczyt tylko do odczytu. Wyszukiwanie request ID w czasie incydentu: 0 wpisów. Zachowano 41 wpisów dla przedziału 12:50:00–12:50:20. Ostrzeżenie o ponawianiu websocket dotyczy automatycznego przeglądu zgody/modelu; nie jest zapisem ponowienia model_audit ani dowodem przyczyny crasha.
- Metadane pliku aplikacji: obecny ProductVersion=2026-1-7, wcześniejsze diagnostics podało ProductVersion=2026.0.1.0. Zachowano oba odczyty z rozróżnieniem źródeł; wspólny FileVersion=16.1617.8659.814. Nie utożsamiano tych różnych pól.

## Wynik

Potwierdzono awarię i czasową zbieżność z drugim model_audit. Nie ustalono konkretnego modułu, wersji modułu, offsetu, typu/treści wyjątku zarządzanego ani przyczyny. Utrata odpowiedzi jest zgodna z zakończeniem procesu hosta, ale sama nie dowodzi, że wywołanie audytu spowodowało awarię.

Wyniki są w nowym diagnostics-crash-20261009.json oraz plikach pomocniczych crash-*.json. Zachowano oryginalne diagnostics-20261009T104813Z.json/.txt i wszystkie pliki źródłowe. W ramach tej diagnostyki nie wywołano model_audit, innych odczytów modelu, reinstalacji, odtwarzania awarii ani nowego zrzutu.
