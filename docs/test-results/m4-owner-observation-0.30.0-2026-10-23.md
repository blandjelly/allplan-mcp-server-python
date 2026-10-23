# Ograniczona obserwacja właściciela 0.30.0 — priorytety 1–5

Właściciel zgłasza wyniki próby kandydata 0.30.0: próby 1, 2, 3 i 5 —
**PASS**; próba 4 ścieżki native material — **FAIL przed Apply**. Szczegółowy
log próby 5 jest zachowany poniżej. Surowe odpowiedzi prób 1–3 nie zostały
udostępnione; dla próby 4 właściciel podał blokery opisane niżej, ale bez raw
response MCP. Wyniki pozostają ograniczone do zgłoszonego zakresu.

Szczegółowa próba 5 objęła projekt `Kopia MCP_QA_DEMO`, wyłącznie aktywny
rysunek 101, Allplan 2026.1 i bridge/MCP 0.30.0 z potwierdzoną integralnością.
Wszystkie cztery jawnie dozwolone próby scalar zakończyły się Apply z
`readback_matches`, a po pojedynczym Undo każda świeża obserwacja potwierdziła
wartość początkową:

- Column: `MCP_QA_MARK` (ID 5001), tekst `"5" → "QA-TEST-01" → "5"`;
- Column: `Priorytet` (ID 110), integer `100 → 101 → 100`;
- Column: `Współczynnik` (ID 230), real `1 → 1.05 → 1`;
- Wall: `Nazwa` (ID 507), tekst `"" → "QA-TEST-WALL" → ""`.

Każdy przebieg miał preview, highlight, revalidation bez zmian, jeden Apply,
świeży typed read oraz jedno potwierdzone przez właściciela UI Undo i świeży
odczyt odtworzenia. Apply był dostępny w trybie ewaluacyjnym
(`production_apply_available=false`); nie stanowi to akceptacji produkcyjnej.
Po jednym odczycie realnej wartości zwrócił `host_absent`; po udanym health
checku kolejny odczyt potwierdził odtworzenie. Nie ponowiono zapisu. Log nie
podaje manifestu zainstalowanego ZIP-a ani builda Allplana, więc wyniku nie
wiążę z dokładnym artefaktem ani rewizją źródła.

Nie wykonano zapisu Enum: `Status` (ID 49, SDK type 69) miał wartość
`<niezdefiniowany>`, bez potwierdzonej etykiety. Brakowało fikstury Boolean i
samodzielnego Slab. Odczyty Beam (`probe_scope_unavailable`) i opening
(nieudany odczyt listy atrybutów) zostały zablokowane; żaden z nich nie był
zapisywany. Nie tworzono elementów, atrybutów ani warstw. Zaakceptowanych
wcześniej zapisów Beam W1 i Column W1 no-op nie powtórzono.

Zachowane [szczegółowy log próby 5](evidence/0.30.0-2026-10-23/allplan-attribute-trials-log.md)
i [zapisane requesty Apply](evidence/0.30.0-2026-10-23/allplan-attribute-trial-apply-requests.jsonl)
to kopie dostarczonych plików, zachowane bez zmian.

### Próba 4 — diagnostyka native material

Według relacji właściciela, pierwszy dokładny preview Wall z żądanym
materiałem `Żelbet` zwrócił `native_material_preservation_unavailable`, a
szczegółowy blocker `wall_material_tier_hierarchy_unsupported`; wynik miał
`changes=0`, `usable_for_write=false` i `setter_calls_started=0`. Apply nie
wykonano, a materiał pozostał bez zmian. Drugi Wall z opening, model UUID
`545bb0a2-a054-4c91-ac6c-ec552d5b0c18`, zwrócił
`component_child_owner_mismatch` i ten sam brak zmian/setterów/Apply. To
podsumowanie relacji właściciela, nie cytat z raw response.

To jest FAIL zaplanowanego sprawdzenia dostępności/zmiany native material,
nie zapis nieprawidłowego materiału: oba preview zakończyły się przed Apply i
nie zmieniły modelu. Obserwacja nie zawiera raw response MCP ani UUID pierwszego
Wall, więc nie przypisuje wyniku do dokładnego ZIP-a ani źródłowej rewizji.

PASS prób 1–3 odnosi się wyłącznie do zgłoszonych etapów tej sesji; brak ich
surowych odpowiedzi uniemożliwia rozszerzenie zakresu odbioru. Próba 4
pozostaje niezaliczona dla wymaganej ścieżki native material. Oddzielna native
selection nadal nie ma obsługi set/clear/readback. Próba 5 wspiera tylko cztery
konkretne scalar pary rodzina/typ z readbackiem i Undo; nie zamyka macierzy
rodzin, nie ustanawia ownera Slab/MultiSlab ani nie dostarcza kodeków
date/vector. Priorytety 1–5 i pełna bramka odbioru pojedynczego rysunku
pozostają częściowo otwarte.
