# Allplan MCP — plan dalszego rozwoju M4

## Aktualny stan i kolejne zadanie

M4 jest częściowo odebrane. Aktualną wersję, dostawę i konkretne następne
zadanie opisuje [handoff](next-model-handoff.md). Ten plan utrzymuje pozostałe
prace i warunki ich zamknięcia, zgodnie z [polityką dokumentacji](documentation-policy.md).

Dowody wcześniejszych prób są w [statusie walidacji](validation-status.md);
ich istotne ograniczenia zachowują poniższe zadania i handoff. Nie powtarzać
odebranych zakresów ani rozszerzać ich na inne rodziny, typy czy wersje bez dowodu.

## Cel i granice produktu

Użytkownik opisuje zamiar zwykłym językiem. Agent rozpoznaje zakres, elementy,
właściciela pola i typ wartości, pokazuje plan, ponownie go waliduje, wykonuje
obsługiwany zapis i świeży odczyt. Atrybut materiału, natywny materiał, warstwa
organizacyjna i wykończenie są odrębnymi polami.

Odczyt może obejmować jawnie wskazane otwarte rysunki; obecny Apply jest
ograniczony do jednego aktywnego rysunku i 1–32 rzeczywistych zmian.
Wieloplikowość i cały projekt wymagają osobnego projektu oraz odbioru.

## Pozostałe prace i nierozwiązane błędy

| Priorytet | Co pozostało / warunek dalszej pracy |
| --- | --- |
| 1 — dziennik i recovery | Uzupełnić brakujące dowody restart/replay oraz unknown/corrupt/unverifiable poza już odebranym zakresem. PASS próby dziennika bez pełnego raw logu nie potwierdza osobno każdego podkroku. Chronić nierozliczone rekordy. |
| 2 — Slab/MultiSlab | Rozstrzygnąć lineage i właściciela project attributes. Różne view UUID, zbieżne bounds oraz structural identity nie ustanawiają właściciela ani równoważności fizycznych celów. Najnowszy probe ma `evidence_complete=false` dla Slab i `true` dla MultiSlab, ale `property_owner=not_established` dla obu. Do ustalenia kontraktu zapisy pozostają BLOCKED. |
| 3 — warstwa i no-op | Uzupełnić wyłącznie nieodebrane przypadki. W1 read/write, pojedyncze Undo i zgłoszony no-op nie dowodzą grupowego Undo ani pełnego pokrycia rodzin. No-op nie ma drogi Apply. |
| 4 — materiał Wall | 0.33.0: testy automatyczne i weryfikacja paczki PASS; odbiór natywny pozostaje otwarty. 0.32.0 native preview zablokowany przed zapisem; zgłoszona przyczyna nie zgadza się ze source/ZIP i pozostaje nieustalona. Następny krok i osobny blocker Wall 200 mm/opening: [handoff](next-model-handoff.md). |
| 4 — delete i selekcja | Zachować odebrany grouped Column delete/Undo; pozostałe rodziny/poddrzewa wymagają oddzielnego dowodu. Native selection set/clear/readback nadal unsupported. Highlight nie jest selekcją. |
| 5 — typy i rodziny | Domknąć owner-specific roundtrip oraz macierz rodzin/typów. Column Enum `Status` ID 49 pozostaje BLOCKED (`<niezdefiniowany>`, brak potwierdzonej etykiety). Wall CheckBox ID 1371 nie ma surowego Apply; fixture SDK Boolean brak. Beam i Door blokuje niejednoznaczna reprezentacja/tożsamość. Date/vector/object wymagają dokładnych kontraktów setter payload i typed readback; sam symbol lub konstruktor SDK nie wystarcza. |

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

Zbiorcza bramka CI `ci-required` jest przygotowana; 49 focused checks PASS.
Właściciel sprawdza CI/paczkę kandydata workflow i ustawia wymagany check dla
develop/m4 według [polityki testów](testing-policy.md#required-github-check).
Ochrona gałęzi nie została zmieniona; bramka nie zastępuje odbioru ZIP ani Allplana.
[Tool reference](tool-reference.md), [API evidence](m4-attribute-api-evidence.md)
i [macierz typów](m4-attribute-type-coverage.md) pozostają źródłami kontraktów API.
