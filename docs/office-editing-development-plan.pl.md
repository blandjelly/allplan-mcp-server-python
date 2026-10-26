# Allplan MCP — plan dalszego rozwoju M4

## Aktualny stan i kolejne zadanie

M4 jest częściowo odebrane. Aktualną wersję, dostawę i konkretne następne
zadanie opisuje [handoff](next-model-handoff.md). Ten plan utrzymuje pozostałe
prace i warunki ich zamknięcia, zgodnie z [polityką dokumentacji](documentation-policy.md).
Kandydat źródłowy 0.38.0 na `fix/m4-material-recovery` dodaje przeglądaną
reconciliation dla nierozstrzygniętego wyniku native material przy zachowaniu
blokad dla brakujących, niezgodnych lub nieczytelnych reprezentacji. 177 focused
unit checks i 11 MCP/HTTP checks przeszło; version consistency potwierdza 0.38.0.
Test Wall/opening potwierdza pojedynczy setter i odblokowane recover po
dodatkowym wrapperze bez własnego opcjonalnego drzewa dzieci (baseline: unknown).
To test fixture, nie walidacja natywna. Run CI
[40331698187](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40331698187)
zakończył się błędem Windows w durable material HTTP (`726` testów, jeden błąd),
a Ubuntu przeszło; package job pominięto, `ci-required` failed. Poprawka
test-only dla durable HTTP flow i 15 testów focused po zmianie przeszły; runtime
pozostaje 0.38.0. Nowe CI, odbiór native i paczki nadal pending. Lokalne pomiary
Linux i limity tego wyniku podaje [handoff](next-model-handoff.md); bieżący
zakres i warunki opisuje [handoff](next-model-handoff.md).

Dowody wcześniejszych prób są w [statusie walidacji](validation-status.md);
ich istotne ograniczenia zachowują poniższe zadania i handoff. Nie powtarzać
odebranych zakresów ani rozszerzać ich na inne rodziny, typy czy wersje bez dowodu.

## Cel i granice produktu

Użytkownik opisuje zamiar zwykłym językiem. Agent rozpoznaje zakres, elementy,
właściciela pola i typ wartości, pokazuje plan, ponownie go waliduje, wykonuje
obsługiwany zapis i świeży odczyt. Atrybut materiału i natywny materiał mają
odrębne powiązania API; ich ewentualne sprzężenie wymaga odczytu w danym
projekcie. Warstwa organizacyjna i wykończenie mają osobne cele zapisu.

Odczyt może obejmować jawnie wskazane otwarte rysunki; obecny Apply jest
ograniczony do jednego aktywnego rysunku i 1–32 rzeczywistych zmian.
Wieloplikowość i cały projekt wymagają osobnego projektu oraz odbioru.

## Pozostałe prace i nierozwiązane błędy

| Priorytet | Co pozostało / warunek dalszej pracy |
| --- | --- |
| 1 — dziennik i recovery | Sprawdzić 0.38.0 na istniejącym execution `87a45065d5e14e3a9ac8c54756e273a0`: najpierw recover bez acknowledgement, potem przeczytać wszystkie targets/meaning/changed sections/hashes i zweryfikować bieżący model. Akceptować wyłącznie przedstawiony niezmieniony `reconciliation_hash` z `acknowledgement=reviewed_material_reconciliation`; recovery ponownie czyta wszystkie dokładne widoki pod lockiem. Rekord otrzymuje reason `reviewed_material_preservation_conflict`, zachowuje `original_outcome`, `reconciliation_evidence`, hash i acknowledgement, ma `preservation_verified=false`; to nie jest applied success ani dowód przyczynowości settera i nie usuwa historii. Brak widoku/ownera, nieczytelność lub rozbieżność zostawia lock. Nie ponawiać settera. [Dowód 0.37](test-results/evidence/0.37.0-2026-10-26/allplan-conversation-log.md), [handoff](next-model-handoff.md). |
| 2 — Slab/MultiSlab | 0.37.0 dodaje jawne `target.property_owner="selected_element"` dla dokładnego ref, przy pełnym lineage i children; parent/child overlap pozostaje zablokowany, a stare requesty bez ownera nadal blokują child/aggregate. Nie ma automatycznego redirectu. Pozostaje natywna walidacja wybranego ownera atrybutu i ścieżki `SlabProperties.Material`; różne view UUID, zbieżne bounds i wcześniejszy `property_owner=not_established` nie dowodzą fizycznej równoważności. |
| 3 — warstwa i no-op | Uzupełnić wyłącznie nieodebrane przypadki. W1 read/write, pojedyncze Undo i zgłoszony no-op nie dowodzą grupowego Undo ani pełnego pokrycia rodzin. No-op nie ma drogi Apply. |
| 4 — natywny materiał | Zachować ograniczenia routingu z 0.37.0: runtime classes i exact owner dla Beam/SkeletonBeam oraz Slab/MultiSlab; Slab child tylko z bezpośrednim MultiSlab parent; Wall single-tier. Nie rozszerzać zakresu rodzin na podstawie API availability. Dla Wall z drzwiami/otworem: po ewentualnej reviewed reconciliation execution `87a45065d5e14e3a9ac8c54756e273a0`, wykonać świeży preview i dopiero rozpatrywać nową próbę; 0.37.0 preview został zablokowany przez `scan_limit_exceeded`, root cause nieustalony. Właściciel zgłosił PASS wartości materiału na Wall 240 mm bez otworów (`Beton1` potwierdzone UI/sondą), ale journal result pozostał unknown. Native Beam PASS nadal nieustalony; Column/Beam/Slab nie były testowane w 0.37.0. [Handoff](next-model-handoff.md), [status](validation-status.md#evidence-for-unresolved-cases). |
| 4 — delete i selekcja | Zachować odebrany grouped Column delete/Undo; pozostałe rodziny/poddrzewa wymagają oddzielnego dowodu. Native selection set/clear/readback nadal unsupported. Highlight nie jest selekcją. |
| 5 — typy i rodziny | Domknąć owner-specific roundtrip oraz macierz rodzin/typów. Column Enum `Status` ID 49 pozostaje BLOCKED (`<niezdefiniowany>`, brak potwierdzonej etykiety). Wall CheckBox ID 1371 nie ma surowego Apply; fixture SDK Boolean brak. Beam/SkeletonBeam material route z 0.37.0 jest opisany w priorytecie 4, ale jego native trial pozostaje pending; inne typed attribute gaps rodzin wymagają osobnych dowodów. Date/vector/object wymagają dokładnych kontraktów setter payload i typed readback; sam symbol lub konstruktor SDK nie wystarcza. |

Dwa dodatkowe nierozwiązane przypadki wymagają zachowania wcześniejszego
stanu i dowodów:

- **Broad property discovery:** native crash, bez ustalonej przyczyny;
  trasa pozostaje `blocked_after_native_crash`. Usunięcie nieuzasadnionych
  odczytów Enum nie dowodzi naprawy awarii. Nie wznawiać szerokiego probe.
- **Retained execution `4388b04e39a14fac811db4f58723d01f`:**
  zgłoszona blokada multiview recovery nie ma potwierdzonego natywnego
  rozwiązania. Consensus recovery i exact-view binding nie zastępują
  obserwacji tego wykonania. Zachować oryginalny dziennik i używać read-only
  recovery pod tym samym ID, bez ponawiania setterów.

Źródłowe dowody i identyfikatory przypadków są w
[statusie walidacji](validation-status.md#evidence-for-unresolved-cases).
Brak fixture oznaczać `fixture_missing`, nierozstrzygnięty kontrakt — BLOCKED.

## Po domknięciu priorytetów 1–5

1. Zaprojektować wykonanie wieloplikowe: manifest, deterministyczne partie,
   jawne wyniki częściowe, timeout/restart i pomiary dla ponad 32 zmian oraz
   ponad 200 wyników. Nie deklarować wspólnego Undo ani atomowości bez dowodów.
2. Osobno zaplanować cały projekt: enumerację niezaładowanych plików,
   aktywację, przywrócenie kontekstu i raportowanie niekompletności.
   Brak dostępu nie może oznaczać zera wyników.

## Kryteria zamknięcia

- Każdy nowy odebrany przepływ ma dokładny zakres, powiązanie z instalacją
  i buildem Allplana oraz świeży readback/UI/Undo odpowiedni do operacji.
  Zachować ograniczenia wcześniejszych dowodów; nie powtarzać ich prób.
- Zapytanie jawnie raportuje kompletność, właścicieli, reprezentacje,
  otwory/rodziców oraz osobno selekcję i highlight.
- Preview, revalidation, Apply, replay i recovery zachowują granice planu,
  rozliczają konflikty i nie ponawiają setterów po wyniku unknown.
- Dziennik zachowuje nierozliczone zapisy przy limitach, archiwizacji
  i restarcie. Każdy większy zakres ma odrębny odbiór.

[Polityka dokumentacji](documentation-policy.md) określa aktualizację handoffu i zadań;
[testing policy](testing-policy.md) — kontrole i budowanie.

Zbiorcza bramka CI `ci-required` jest przygotowana; 49 focused checks PASS,
a run 40228207181 przeszedł wymagany check wraz z pełnym CI i paczką dla
`ee831a0`. Właściciel nadal ustawia wymagany check dla develop/m4 według
[polityki testów](testing-policy.md#required-github-check). Ochrona gałęzi nie
została zmieniona; bramka nie zastępuje odbioru ZIP ani Allplana.
[Tool reference](tool-reference.md), [API evidence](m4-attribute-api-evidence.md)
i [macierz typów](m4-attribute-type-coverage.md) pozostają źródłami kontraktów API.
