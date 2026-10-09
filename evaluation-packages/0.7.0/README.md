# Pakiet testowy 0.7.0

[Pobierz gotowy ZIP dla Windows](https://github.com/blandjelly/allplan-mcp-server-python/raw/refs/heads/codex/m3-repair-preview/evaluation-packages/0.7.0/allplan-mcp-0.7.0-windows-evaluation.zip).
Instrukcja: [test M3 Preview](../../docs/m3-preview-batch.md).

Rozpakuj cały ZIP do nowego folderu. Zamknij Allplan oraz poprzednie okno MCP,
uruchom **Setup.cmd**, następnie Allplan/StartPythonHost i **Launch Allplan MCP.cmd**.
Na dotychczasowym modelu testowym, z aktywnym plikiem 101, uruchom **M3 Preview.cmd**.
Oczekiwany podgląd: warstwa C05 → SZ_OGÓ01 i status C06 NWE → NEW; po teście
model ma pozostać bez zmian i nadal mieć pięć usterek w audycie.
Prześlij najnowsze JSON/TXT z `logs` oraz potwierdzenie zgodności z UI.

ZIP jest dokładnie tym samym archiwum, które przygotowano przed zgodą na push;
nie został przebudowany. Jego manifest wskazuje czyste źródło
`22f18db27faf5e0873de18c1e079d1217da736fb`.
Wbudowany dokument przekazania opisuje wcześniejszą blokadę publikacji;
[aktualny dokument GitHub](../../docs/next-model-handoff.md) zastępuje ten status.

SHA-256 ZIP: `e47a103b8a280bf786877f22bab8faf8bfd183f4de9531d8918305bd87cf56c6`.
Rozmiar: **382353 bajty**. Obok znajdują się plik `.sha256`, zweryfikowane
wheel/sdist i opis dostawy `delivery-0.7.0.json`.

**134 testy lokalne PASS**. Testy Allplan 0.7.0 oczekują na wykonanie.
Pakiet udostępnia wyłącznie podgląd i kontrolę planu dla M3; stosowanie napraw,
odczyt po zapisie i Undo nie są jeszcze wdrożone.
