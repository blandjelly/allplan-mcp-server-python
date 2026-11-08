# Karta testów natywnych: sesja zbiorcza 0.51.1 (bloki A i B) oraz dane do zebrania (C)

**Na podstawie:**

- gałęzi `claude/m4-0511-window-wall-evidence` (`0fdc2a8`),
- `docs/next-model-handoff.md`, `docs/development-plan.md`, `docs/m4-coverage-matrix.md`, `docs/tool-reference.md`,
- surowych dowodów 0.51.0 (`docs/test-results/evidence/0.51.0-2026-11-07/`).

**Projekt:** „Kopia MCP_QA_DEMO”, rysunek **101** jako pierwszoplanowy.

Do każdego testu jest gotowy prompt dla lokalnego agenta (Claude Code lub Codex
podłączony do MCP na Windows). Wpisujesz go do agenta dosłownie. Robisz tylko
kontrolę w UI i UI Undo, a wynik zaznaczasz w tabeli na końcu.

> UUID poniżej pochodzą z odczytów 0.51.0. Widoki mogą się regenerować, więc
> agent zawsze odczytuje je od nowa przed preview. Rozbieżność z kartą nie jest
> błędem. Agent ma ją zgłosić i użyć świeżego ref.

---

## 0. Przygotowanie (raz na sesję)

### Warunki startu

- PR 0.51.1 jest scalony do `develop/m4` z zielonym `ci-required`.
- ZIP z artefaktu `package` jest zainstalowany.
- Allplan 2026.1 jest uruchomiony, rysunek 101 jest pierwszoplanowy, a StartPythonHost działa.
- Folder `logs/evidence/` pakietu jest pusty albo zarchiwizowany. Dzięki temu
  nowy plik JSONL obejmie tylko tę sesję.

### Prompt 0: kontekst sesji i health-check

```text
Pracujemy w natywnej sesji testowej M4 dla wersji 0.51.1 na projekcie „Kopia MCP_QA_DEMO”,
rysunek 101. Przeczytaj docs/next-model-handoff.md (sekcja "Next task") i stosuj zasady:
- każdy zapis: preview → highlight → pokaż mi plan (element, stare/nowe wartości, liczba zmian)
  → czekaj na moje „OK” → apply z acknowledgement "disposable_copy_reviewed_plan" → świeży odczyt;
- jedno Apply na krok, nigdy nie powtarzaj Apply po wyniku `unknown` — tylko read-only `recover`
  z tym samym execution_id; zapisz `preservation.identity_diff` i `preservation.regeneration_residual`;
- po każdym zapisie poproś mnie o kontrolę UI i UI Undo, a potem zrób odczyt po Undo;
- nie powtarzaj zaakceptowanych prób z listy "Do not repeat" w handoffie;
- przy każdym teście zapisz execution_id, outcome, undo_group i wartości przed/po/po Undo.
Teraz wywołaj allplan_health i get_allplan_version. Sprawdź: bridge 0.51.1, source commit
równy scalonemu commitowi 0.51.1, integrity `sha256-verified`, Allplan 2026.1.
Następnie zrób model_query (scope open_drawings, rysunek 101, fields: display_name, type_name,
family, opening_kind, hierarchy, wall.total_thickness_mm, page_size 200, component_kind
model_identity) i wypisz aktualne model/view UUID dla: Ściany 300 z oknem, Ściany 240,
Ściany 200 z drzwiami, Słupa eb88c850…, Podciągu 7cc9ac55…, Stropu (MultiSlab) bf097d95…,
warstwy płyty (Slab) 8a693925… oraz okna (Window_TypeUUID) w Ścianie 300.
```

**Oczekiwane:** health OK. Refy zgodne z tabelą poniżej albo zgłoszone różnice.

| Element | model UUID | widok (ostatnio znany) | Stan wyjściowy (ostatni odczyt) |
| --- | --- | --- | --- |
| Ściana 300 z oknem | `f4da72fe-f82d-416a-9e38-a0975fc83847` | `a76b11f4-f796-4690-8d0c-98dc28b4ff25` | Material `TEST1`, CalculationMode 0, atr. 120 `m3`, 508 nie zapisany |
| Okno w Ścianie 300 | `268dec66-fb59-410b-8710-38d5b2895c1c` | (odczytać) | — |
| Ściana 240 | `06d71e4d-193b-483e-8a32-344ade3d612c` | `2d33e5a6-b4e8-444b-94e8-d4d0ae75d622` | Material `TEST`, 508 `Silikat`, 0/`m` |
| Ściana 200 z drzwiami | `545bb0a2-a054-4c91-ac6c-ec552d5b0c18` | `32cdf5c8-b19f-4e79-8176-bc4c2ecb416c` | Material `TEST1`, 0/`m3` |
| Słup | `eb88c850-0cac-408a-8091-f118872d74c2` | `cc752bda-aa0a-4bd3-a7b9-26f40fab56e1` | CalculationMode 2/`m`, Material do odczytu |
| Podciąg, wieniec (Beam) | `7cc9ac55-6111-4508-bae8-d33918dbe77e` | `6035d406-ad2e-45e2-9bfc-46d28477e607` (bezpośredni) | 0/`m3`, Material `""`, 508 `""` |
| Strop (MultiSlab) | `bf097d95-8275-4229-ac74-27bbea26c211` | `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9` | 508 `TEST1`, 120 `m3` |
| Warstwa płyty (Slab, tier) | `8a693925-ae20-4dda-91d1-3951af3c0a52` | `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94` | 508 `TEST2`, 120 `m2` |

**Zasada sesji:** każdy blok dotyczy innego elementu. UI Undo robisz od razu
po kroku, który go wymaga, zanim zaczniesz następny. Blok B4 (usuwanie) wykonujesz
na samym końcu.

---

## Blok A: Ściana 300 z oknem (blokujący, plan pkt 2a, 5, 8)

Cel: oba zapisy parowane na ścianie z oknem kończą się `applied`, z pełnymi
dowodami i jednym UI Undo.

### A1: preview tylko do odczytu

```text
Test A1 (read-only). Zrób preview (bez apply) dla prośby: „zmień calculation mode dla ściany
300 mm na m”. Użyj paired_property calculation_mode, native_types Wall_TypeUUID i wyklucz
pozostałe ściany (exclude_model_uuids: Ściana 240 i Ściana 200 z drzwiami). Pokaż mi:
liczbę zmian, element, stare/nowe wartości (native i atrybut 120), oraz z
resource.native_property_state: czy występuje `partial_preservation` i czy
tier_hierarchy zawiera `shared_children` z WindowTier (parent: Window 268dec66…).
Nie wykonuj apply.
```

**PASS, gdy:**

- 2 zmiany: native 0→2 i atr. 120 `m3`→`m`,
- **brak** `partial_preservation`,
- `shared_children` zawiera WindowTier z rodzicem Window.

**Jeśli FAIL:** przerwij blok A. Zapisz odpowiedź i przejdź do bloku B.

### A2: zapis parowany: calculation mode → `m`

```text
Test A2. Prośba: „zmień calculation mode dla ściany 300 mm na m”. Zrób preview jak w A1,
potem highlight, pokaż mi plan i poczekaj na moje OK. Po OK zrób apply. Raportuj: outcome
dla native i atrybutu 120, accepted (oczekiwane `identities_regenerated_evidence_otherwise_equal`),
listę przemianowanych typów (oczekiwane: Window, Sill, 2 × AttributeContainer), undo_group
(status, setters_in_step) i świeży material_comparison z attribute_ids [120]
(508 nie jest zapisany, więc evidence_complete=false jest oczekiwane).
Jeśli którykolwiek outcome = unknown: NIE powtarzaj apply; podaj identity_diff i
regeneration_residual i poczekaj na moją decyzję o read-only recover.
```

**Oczekiwane:**

- native 0→2 `applied`,
- atr. 120 `m3`→`m` `applied`,
- `undo_group` `created`, `setters_in_step=2`.

**Kontrola UI:**

- dialog elementu: „Obmiar” = `m`,
- paleta atrybutów: „Rodzaj rozliczenia” = `m`.

Potem **jedno** UI Undo.

```text
Zrobiłem jedno UI Undo. Odczytaj material_comparison (attribute_ids [120]) dla Ściany 300
i potwierdź powrót do native 0 / atrybut 120 `m3`. Czy UI pokazuje jeszcze krok Undo
związany z tym Apply? (zapytaj mnie)
```

**PASS, gdy:** obie wartości są `applied`, UI pokazuje `m` w obu miejscach,
a 1 UI Undo przywraca 0/`m3`.

### A3: zapis parowany: materiał → `Cegła`

```text
Test A3. Prośba: „zmień materiał ściany 300 mm na Cegła”. Preview (paired_property material,
wyklucz Ścianę 240 i Ścianę 200 z drzwiami), highlight, pokaż plan, czekaj na OK, apply.
Oczekuję, że 508 nie jest zapisany, więc plan ma tylko zmianę native i listuje ścianę w
paired_property.attribute_follows_native. Raportuj outcome, accepted, przemianowane typy,
undo_group i świeży material_comparison z attribute_ids [120, 508].
Przy unknown — jak w A2: bez powtórki, identity_diff + regeneration_residual, czekaj.
```

**Oczekiwane:**

- `TEST1`→`Cegła` `applied`,
- przemianowane typy jak w A2,
- `attribute_follows_native`.

**Kontrola UI:**

- dialog elementu: materiał `Cegła`,
- paleta atrybutów: „Materiał” `Cegła`.

Potem **jedno** UI Undo i odczyt (oczekiwane `TEST1`):

```text
Zrobiłem jedno UI Undo. Odczytaj material_comparison [120, 508] dla Ściany 300 i potwierdź
Material `TEST1`.
```

### A4: tylko gdy A2 lub A3 = `unknown`

```text
Execution <ID> zakończyło się unknown. Po moim UI Undo wykonaj read-only recover z tym samym
execution_id (bez acknowledgement). Pokaż wynik, identity_diff i regeneration_residual
(do 8 ścieżek). Nie uruchamiaj żadnego settera.
```

### A5 (opcjonalnie, tylko odczyt): `component_identity` na WallTier

```text
Test A5 (read-only). Znajdź WallTier Ściany 300 (model_query, hierarchy) i wywołaj
model_property_probe phase component_identity dla jego model/view. Potwierdź, że raport
zawiera `shared_children` z WindowTier (parent: Window) i nie zwraca probe_scope_unavailable.
```

---

## Blok B1: warstwa płyty w trybie „Warstwa bieżąca” (plan pkt 3)

Cel: jeden zapis warstwy płyty (tier), sprawdzony w UI, z UI Undo, przez
trasę exact.

> W prompcie piszę „warstwa płyty”, a nie „warstwa”, żeby agent nie pomylił
> jej z warstwą organizacyjną (layer).

```text
Test B1. Prośba: „zmień materiał warstwy płyty stropu (tryb Warstwa bieżąca, nie Cały obiekt)
na TEST4”. Najpierw read-only: model_property_probe material_comparison dla Slab 8a693925…
(view a0fcd7b3…) z attribute_ids [508], parent_ref MultiSlab bf097d95… / b4a59b5b…,
include_parent=true — pokaż wartość warstwy (oczekiwane TEST2) i MultiSlab (TEST1).
Potem model_edit preview z exact_target (drawing_file 101, model/view Slab, parent_ref MultiSlab),
native_types ["Slab_TypeUUID"], scope drawing_files [101] include_passive false
visibility api_select_all, jedna zmiana: target attribute 508 z property_owner
"selected_element", replace, value "TEST4". Highlight, pokaż plan, czekaj na OK, apply.
Raportuj outcome, exact_inventory (accepted?), zgodność wszystkich wrapperów warstwy
i świeży odczyt warstwy oraz MultiSlab.
```

**Oczekiwane:**

- `applied`,
- wszystkie wrappery warstwy mają `TEST4`,
- inwentarz bez zmian albo `attribute_containers_regenerated`,
- MultiSlab nadal `TEST1`.

**Kontrola UI (paleta właściwości stropu):**

- tryb „Warstwa bieżąca”: Materiał `TEST4`,
- tryb „Cały obiekt”: Materiał `TEST1`.

Potem jedno UI Undo i:

```text
Zrobiłem jedno UI Undo. Powtórz material_comparison z parent_ref (attribute_ids [508])
i potwierdź warstwa TEST2, MultiSlab TEST1.
```

**PASS, gdy:** `applied`, UI pokazuje `TEST4` tylko w „Warstwa bieżąca”, a po
UI Undo jest z powrotem `TEST2`.

---

## Blok B2: typy atrybutów × rodziny (plan pkt 4, komórki CODE/PARTIAL)

Cel: zamknąć wybrane komórki macierzy. Każdy test robimy osobno: zapis,
odczyt typowany, kontrola UI, UI Undo i odczyt po Undo.

Do B2a i B2c najpierw trzeba znaleźć atrybuty, które istnieją w projekcie. Wyszukiwanie ma być tylko do odczytu.

### B2-discovery (tylko odczyt)

```text
Test B2-discovery (read-only). Dla Ściany 240 (06d71e4d…), Podciągu (7cc9ac55…, widok 6035d406…)
i Stropu MultiSlab (bf097d95… / b4a59b5b…) wywołaj model_property_probe element_attributes
(stronicuj do końca). Wypisz w tabeli atrybuty zapisane (ReadAll, nie computed_only) o typie SDK
Integer, Double (Real) i Boolean / Integer+CheckBox, z ID, nazwą, wartością i jednostką.
Zaproponuj po jednym bezpiecznym atrybucie użytkownika na każdą komórkę: Wall Integer, Wall Real,
Beam Integer, Beam Real, MultiSlab Integer, MultiSlab Real (unikaj atrybutów geometrycznych
i obliczanych). Niczego nie zapisuj.
```

Ty wybierasz atrybuty z tej listy. Jeśli któraś komórka nie ma kandydata,
zapisz ją jako `FIXTURE` i nie twórz definicji.

### B2a: Ściana 240, Integer i Real

```text
Test B2a. Na Ścianie 240 zmień atrybut <NAZWA_INT> (ID <ID>) z <stara> na <nowa> (value_type auto),
wyklucz pozostałe ściany. Preview, highlight, plan, czekaj na OK, apply, świeży typowany odczyt.
```

Kontrola UI w palecie atrybutów, potem 1 UI Undo i odczyt starej wartości.
Następnie to samo dla Real:

```text
Test B2a-real. Na Ścianie 240 zmień atrybut <NAZWA_REAL> (ID <ID>) z <stara> na <nowa>
(value_type auto). Jak wyżej.
```

### B2b: Podciąg, Enum: tylko atrybut 120

To jest celowo zapis jednego miejsca. Natywne `CalculationMode` ma zostać bez
zmian.

```text
Test B2b. Prośba nazywa jedno miejsce: „zmień TYLKO atrybut Rodzaj rozliczenia (ID 120) podciągu
na m, bez zmiany natywnego Obmiaru”. Użyj target attribute 120 (value_type enum lub auto,
property_owner selected_element), native_types ["Beam_TypeUUID"]. Preview, highlight, plan,
czekaj na OK, apply. Raportuj enum label/key roundtrip, outcome i świeży material_comparison
(widok 6035d406…, attribute_ids [120]) — natywne CalculationMode ma pozostać 0.
```

**Kontrola UI:**

- paleta atrybutów: `m`,
- dialog elementu („Obmiar”): bez zmian, `m3`.

Potem 1 UI Undo i odczyt `m3`.

### B2c: MultiSlab, Integer i Real

```text
Test B2c. Na Stropie (MultiSlab bf097d95…) zmień atrybut <NAZWA_INT> (ID <ID>) z <stara> na <nowa>,
target attribute z property_owner "selected_element", native_types ["MultiSlab_TypeUUID"].
Preview — pokaż też slab_tier_values; highlight, plan, czekaj na OK, apply, świeży odczyt.
```

Kontrola UI w trybie „Cały obiekt”, potem 1 UI Undo. Następnie to samo dla
Real.

### B2d: Ściana 240, Boolean (Integer + CheckBox, ID 1371)

Komórka ma dziś status PARTIAL i brakuje surowego Apply.

```text
Test B2d. Na Ścianie 240 odczytaj atrybut ID 1371 (materiał palny) przez element_attributes:
wartość, typ SDK i control type (oczekiwane Integer + CheckBox). Jeśli control type = CheckBox,
zmień go na przeciwną wartość boolean (true/false, value_type auto). Preview, highlight, plan,
czekaj na OK, apply, świeży odczyt (oczekiwane 1/0 zgodnie z kodekiem).
Jeśli nie CheckBox — przerwij i raportuj.
```

Kontrola UI (pole wyboru w palecie atrybutów), potem 1 UI Undo i odczyt.

---

## Blok B3: słup, natywny Material (plan pkt 5, CODE 0.51.0)

Cel: reguła przemianowania słupa (AttributeContainer i widok główny) po
setterze Material.

```text
Test B3. Najpierw read-only: material_comparison dla Słupa eb88c850… (aktualny widok)
z attribute_ids [508] — podaj native Material i czy 508 jest zapisany.
Potem prośba: „zmień materiał słupa eb88c850 na C35/45” (paired_property material,
native_types ["Column_TypeUUID"], exclude_model_uuids pozostałe słupy albo zawężenie do tego modelu).
Pokaż plan. Jeśli plan jest zablokowany `replace_requires_existing_attribute` (508 nie zapisany
na słupie) — zatrzymaj się i zapytaj mnie, czy zmienić tylko natywny materiał (native_material
tier_index 1). Po OK apply; raportuj outcome, accepted (oczekiwane
identities_regenerated_evidence_otherwise_equal: AttributeContainer + widok główny),
undo_group i świeży odczyt.
```

**Kontrola UI:**

- dialog słupa: materiał `C35/45`,
- paleta atrybutów: „Materiał”, jeśli był w planie.

Potem jedno UI Undo i odczyt starej wartości.

**PASS, gdy:** `applied` i jeden UI Undo przywraca materiał. Widok słupa może
dostać nowy UUID, a agent odczytuje go od nowa.

---

## Blok B3b (opcjonalnie): warstwa organizacyjna (plan pkt 7)

### B3b-1: no-op

Cel: potwierdzić, że zmiana na obecną warstwę daje zero setterów i brak Apply.

```text
Test B3b-1 (no-op). Odczytaj warstwę (layer) Słupa 4f3cc27e-5224-403d-939d-7b4e0cedf9a2.
Zrób preview zmiany warstwy na jego OBECNĄ warstwę (dokładny short_name z odczytu).
Pokaż: liczbę zmian (oczekiwane 0), no-op, brak ścieżki apply. Nie wykonuj apply.
```

### B3b-2: zmiana warstwy na Ścianie 200 z drzwiami

```text
Test B3b-2. Odczytaj warstwę Ściany 200 z drzwiami (545bb0a2…). Zmień ją na istniejącą
warstwę SZ_OGÓ02 (zweryfikuj przez model_property_probe layer_name / layer_catalog i pokaż
mi pełną i krótką nazwę + ID do potwierdzenia). Trasa tier-aware set_wall_layer / model_edit
layer target. Preview, highlight, plan, czekaj na OK, apply, świeży odczyt warstwy.
```

Kontrola UI (warstwa ściany), potem 1 UI Undo i odczyt starej warstwy.

---

## Blok B4 (opcjonalnie, destrukcyjny, ostatni): usunięcie okna (plan pkt 8)

Ten blok wykonujesz tylko wtedy, gdy zgadzasz się na test destrukcyjny i
blok A jest zamknięty.

```text
Test B4. Prośba: „usuń okno ze ściany 300 mm”. model_edit preview z target delete,
native_types ["Window_TypeUUID"], zawężone do okna 268dec66… (lineage dokładnie [okno, Ściana 300]).
Pokaż poddrzewo (WindowTier, Sill, WindowReveal, WindowOpeningSmartPart, AttributeContainery)
i liczbę adapterów. Highlight, czekaj na OK, apply. Raportuj: nieobecność okna i całego
poddrzewa, obecność Ściany 300 (rodzic musi zostać), sąsiednie elementy bez zmian.
Przy unknown — bez powtórki, tylko read-only recover.
```

**Kontrola UI:** okna nie ma, ściana jest. Potem **jedno** UI Undo i:

```text
Zrobiłem jedno UI Undo. Zrób model_query i potwierdź, że okno i całe poddrzewo wróciły
(UUID mogą być nowe — podaj je) oraz że Ściana 300 jest nienaruszona.
```

**PASS, gdy:**

- okno i jego poddrzewo zniknęły, a ściana została,
- jedno UI Undo przywróciło okno,
- odczyt po Undo jest kompletny.

---

## Zakończenie sesji

```text
Koniec sesji. Wypisz zbiorczą tabelę: test, element, execution_id, outcome (native/atrybut),
accepted, undo_group, wartości przed/po/po Undo, moje potwierdzenia UI. Wskaż pliki JSONL
w logs/evidence/ z tej sesji. Nie zmieniaj niczego w modelu.
```

Następnie przekaż agentowi w repo:

- pliki z `logs/evidence/`, do zapisania bez zmian w `docs/test-results/evidence/0.51.1-<data>/`,
- wypełnioną tabelę poniżej.

### Tabela wyników (do wypełnienia)

| Test | execution_id | Outcome | UI OK? | Liczba UI Undo | Odczyt po Undo | Wynik |
| --- | --- | --- | --- | --- | --- | --- |
| A1 (read-only) | — | `preview_ready`, plan `7a76ed98…`: 2 zmiany (native 0→2, atr. 120 `m3`→`m`), brak `partial_preservation`, `shared_children` = WindowTier (parent Window `268dec66…`), `setter_calls_started: 0` | — | — | — | **PASS** |
| A2 calc mode `m` | `c1395fe64f0743fab54e8bbd6d9da3cc` (plan `91c37c58…`) | native `unknown` (`readback_differs_or_unavailable`, odczyt 2), atr. 120 `skipped`; brak `accepted`; `undo_group` `created`, `setters_in_step=1`; przemianowano 6: Window, Sill, WallAxis, 3 × AttributeContainer; residual 8 ścieżek, **obcięte** (hash geometrii WindowTier i WindowReveal + niesparowany AttributeContainer ściany) | **NIE**: właściwości `m`, atrybut `m3` | 1 | native 0, atr. 120 `m3`; recover `reconciled` / `old_value_observed`, `write_blocked=false` | **FAIL** |
| A3 materiał `Cegła` | `3c5df3d971a6427da2748854e2b75114` (plan `5c445b65…`) | native `unknown` (`wall_material_invariants_changed`, odczyt `Cegła`); 508 bez settera (`attribute_follows_native`); brak `accepted`; `undo_group` brak w odpowiedzi; przemianowano 6: Window, Sill, WallAxis, 3 × AttributeContainer; residual 2 ścieżki (tylko hash geometrii WindowTier i WindowReveal) | TAK: `Cegła` w obu miejscach | 1 | `TEST1` (508 `not_returned`, `evidence_complete=false`); recover `reconciled` / `old_value_observed`, `write_blocked=false` | **FAIL** |
| A4 recover po `unknown` (A2, A3) | `c1395fe6…`, `3c5df3d9…` | read-only `recover` bez acknowledgement: oba `reconciled` / `old_value_observed`, `agreed=true`, bez rekoncyliacji, bez setterów | — | — | A2: 0 / `m3`; A3: `TEST1` | **PASS** (recover) |
| A5 component_identity (opc.) | — | WallTier `e6e244c9…` (widok `1a7bfe70…`): `state` `observed`, `shared_children` = WindowTier `360e85e2…` (parent Window `268dec66…`), brak `probe_scope_unavailable`, `read_only` | — | — | — | **PASS** |
| B1 warstwa płyty `TEST4` | `1a0194481b164593a6ed23231cbbb416` (plan `b3318b59…`) | `applied` (`readback_matches`), 1 setter; `exact_inventory` `unchanged` (fingerprint `796cd760…`, hierarchia Slab → MultiSlab bez zmian); wrappery Slab (widoki `a0fcd7b3…`, `4d8810a2…`) zgodne (hash `6369eb8d…` → `e6d175cf…`, `agreed=true`); świeży odczyt: warstwa `TEST4`, MultiSlab `TEST1`; native Material `" "` bez zmian | TAK (ogólne „zgodny z opisem”, bez rozbicia na tryby „Warstwa bieżąca” / „Cały obiekt”) | 1 | warstwa `TEST2`, MultiSlab `TEST1` | **PASS** |
| B2a Wall Integer: 1442 „Wysokość pomieszczenia ściana” 1→0 | `9bf9d05d03a643699d6c0dcc6e75aa3a` (plan `78dbc954…`) | `applied` (`readback_matches`); wrappery ściany (4, widok `2d33e5a6…`) zgodne (hash `80e2609f…` → `d969033f…`); odczyt: Ściana 240 = 0, ściany 200 i 300 = 1; typ SDK Integer (kod 73), w UI checkbox | TAK (checkbox odznaczony) | nie zgłoszono | 1 (z `old_value` następnego preview; osobnego odczytu po Undo nie robiłem) | **PASS** (apply i UI; Undo bez osobnego odczytu) |
| B2a Wall Integer (dod.): 1442 1→2, poza zakresem 0/1 | `360930f8b4ff44098791e287d892060c` (plan `3900fc68…`) | `applied`, odczyt 2 (nie znormalizowany do 1); pozostałe ściany 1; wrappery (4) zgodne (hash `80e2609f…` → `982a67d8…`) | TAK: checkbox zaznaczony (UI nie odróżnia 1 od 2) | 1 | 1 | **PASS** (informacyjnie) |
| B2a Wall Real: 220 „Długość” 4.65→5 | `052283c9fbb047e8ac50c697c3eb3a5d` (plan `d03cdcde…`) | `failed` (`readback_unchanged`), stan `stopped`; readback 4.65; `audited_fields_match_plan=false`; hash wrapperów bez zmian (`3f9710ce…`); read-only `recover`: `old_value_observed`, `write_blocked=false` | — (nic nie zapisano) | 0 | 4.65 (bez zmian) | **FAIL** (220 niezapisywalny; prawdopodobnie obliczany, niepotwierdzone) |
| B2a Wall Real (zamiennik): 230 „Współczynnik” 1→2 | `3be71e58cb87469c80d60f706fafdc45` (plan `727dfee7…`) | `applied`, odczyt 2 (Real, kod 82); 220 i 221 bez zmian; wrappery (4) zgodne (hash `e3d9e528…` → `7590bb16…`) | TAK (zgodne z odczytem, potwierdzone po fakcie) | 1 | 1 | **PASS** |
| B2b Beam Enum 120 | `8cc1e6871aae449dae601a27abab5c2b` (plan `2fe9ecbb…`) | `applied`, atr. 120 `m3` → `m` (enum_id 2, roundtrip `m`); **native CalculationMode 0 → 2 (`m`)**, wbrew założeniu testu; wrappery podciągu (3) zgodne (hash `70e7ddce…` → `253f061d…`) | NIE: w UI `m` w obu miejscach (oczekiwano natywnego bez zmian, `m3`) | 1 | atr. 120 `m3`, native 0 (jedno Undo cofnęło oba pola) | **FAIL** |
| B2c MultiSlab Integer: 110 „Priorytet” 200→201 | `1ca552c6efa8482a8d316217ca561e1a` (plan `43e55005…`) | `applied`, odczyt 201; `slab_tier_values`: warstwa 200 (efekt „none”, bez zmian); native Priority 200 bez zmian (niesprzężone); wrapper MultiSlab (1) zgodny (hash `53c52182…` → `0ba37a54…`) | TAK | 1 | MultiSlab 200, warstwa 200 | **PASS** |
| B2c MultiSlab Real: 981 „Wartość U” `<niezdefiniowany>` → 0.25 | `0a7fc6d5fbdd4c54a2639cf93f0b416f` (plan `f51c76ea…`) | `applied`, odczyt 0.25 (typ wartości z `str` na `float`); warstwa nadal `<niezdefiniowany>`; pola natywne bez zmian; wrapper (1) zgodny (hash `6355a9a0…` → `f1e20ed7…`) | TAK | 1 | `<niezdefiniowany>` (`str`) na MultiSlab i warstwie | **PASS** |
| B2d Wall Boolean 1371 | `56739a3058334c6182269a2fafa95aef` (plan `f21cddff…`) | kontrolka CheckBox potwierdzona w preview (`boolean_binding`, kodek `integer_checkbox_boolean`); `applied`, 0 → 1 (`true`), readback 1; ściany 200 i 300 = 1 (stan wyjściowy); wrappery (4) zgodne (hash `d969033f…` → `80e2609f…`) | TAK | 1 | 0 | **PASS** |
| B3 Column Material `TEST1`→`C35/45` (Słup `eb88c850…`) | `7c1e4a92b5d84f60a3e91d2c8b0f5a47` (plan `397fc26f…`) | Plan nie był zablokowany (508 zapisany: `TEST1`), więc pytanie o samo natywne nie zachodziło. native `applied` (`readback_matches`, `C35/45`); atr. 508 `applied` (`paired_attribute_already_set_by_native_write`, 0 setterów atrybutu); `accepted` = `identities_regenerated_evidence_otherwise_equal`: widok główny `cc752bda…`→`55509cf2…`, AttributeContainer `82c18eca…`→`966e12f9…`, zmiana tylko w `component_tree` i `hierarchy`; `undo_group` `created`, `setters_in_step=1`; świeży odczyt (widok `55509cf2…`): native `C35/45`, 508 `C35/45`, CalculationMode 2, Priority 100, Trade -1 bez zmian | TAK (wartości zgodne w UI, zgłoszone przez właściciela; rozbicia dialog/paleta brak) | 1 (zgłoszone: „wykonałem undo”) | native `TEST1`, 508 `TEST1`, widok z powrotem `cc752bda…`, AttributeContainer z powrotem `82c18eca…` | **PASS** |
| B3b-1 layer no-op (Słup `4f3cc27e…`) | — | `no_op` (`already_at_requested_values`), plan `3fbf6e31…`: `changes: 0`, `apply_available=false`, `write_blockers=["no_op"]`, `setter_calls_started: 0`; warstwa ID 3700 = `SZ_OGÓ01` („SZ_OGÓ01 (Ogólne01)”), nazwa podana przez właściciela i zweryfikowana przez `layer_name` | — | — | — (brak zapisu) | **PASS** |
| B3b-2 Wall layer (Ściana 200 `545bb0a2…`) | `b3e8d1f46a2c4975918c0d7e5f2a6b13` (plan `eb5dd903…`) | `applied` (`readback_matches`), `set_wall_layer` (korzeń + 1 tier `ab2d33d2…`), warstwa 65535 → 3701 (`SZ_OGÓ02`, „SZ_OGÓ02 (Ogólne02)”), 1 setter; zgodność reprezentacji `agreed=true`; tożsamości niezregenerowane (widok `32cdf5c8…` bez zmian); odpowiedź Apply bez pola `undo_group` (jest `undo: not_checked`); świeży odczyt: 3701; pozostałe ściany bez zmian (240: 0, 300: 65535) | TAK (wartość zgodna w UI) | 1 (zgłoszone: „wykonałem undo”) | 65535 (ściany 240: 0, 300: 65535 bez zmian) | **PASS** |
| B4 usunięcie okna (opc.) (okno `268dec66…`) | `d5a79c20e1b64f38a7c4829b0e6f1d35` (plan `a84e136d…`) | `applied` (`readback_matches`), 1 `DeleteElements`; poddrzewo 7 adapterów (okno, WindowTier, Sill, WindowReveal, WindowOpeningSmartPart, 2 × AttributeContainer): kompletny świeży skan `present_model_uuids=[]`; rodzic Ściana 300 `f4da72fe…` zachowany (300 mm, WallTier + AttributeContainer); sąsiedzi bez zmian (Ściana 200 z drzwiami, Ściana 240); adaptery 38→33, duplikaty 20→16 | TAK (okno z poddrzewem zniknęło, ściana bez zmian; patrz uwaga o hoście) | 1 (zgłoszone: „wykonałem undo”) | okno `268dec66…` i WindowTier `360e85e2…` wróciły z oryginalnymi UUID, Ściana 300 nienaruszona, adaptery 38 / duplikaty 20 jak przed; pozostałe 5 elementów poddrzewa nie były wyliczane osobno | **PASS** |

**Uwagi do bloku A (sesja 2026-11-08, bridge 0.51.1, source `0fdc2a8e9c4294c6efb867add3f8f07e8493913c`, `sha256-verified`, Allplan 2026.1):**

- Source commit z health (`0fdc2a8e…`) nie został porównany z commitem scalonego PR (handoff go nie podaje). Do potwierdzenia przez właściciela.
- A2 i A3 kończą się `unknown` na ścianie z oknem. Wspólna pozostała przyczyna w A3: zmiana `geometry/stream_sha256` WindowTier `360e85e2…` i WindowReveal `8ad3fe60…` po regeneracji okna. W A2 residual jest obcięty limitem 8 ścieżek (`truncated: true`), więc pełna lista może być większa.
- A2: atrybut 120 nie został zapisany (setter `skipped`), a `undo_group` miał jeden setter zamiast dwóch.
- A3: odpowiedź Apply nie zawierała pola `undo_group`.
- Niewyjaśnione: `counts.matched: 3` w odpowiedzi `highlight` przy jednym zgłoszonym elemencie (`submitted_model_identities: 1`).
- Po każdym UI Undo drzewo okna wróciło do pierwotnych UUID (Window `268dec66…`, Sill `d0c002e4…`, AttributeContainery `0421fa13…`, `8f0e0520…`, `ac7a4495…`).
- Wnioski z danych odpowiedzi, kod bridge'a nie był czytany.

**Uwagi do bloku B (sesja 2026-11-08, bridge 0.51.1, Allplan 2026.1, rysunek 101):**

- Zakres: wykonane B1, B2-discovery, B2a (Integer i Real), B2b, B2c (Integer i Real), B2d. Niewykonane: B3, B3b-1, B3b-2, B4.
- Wszystkie zapisy to jedno Apply z jednym setterem. Odpowiedzi Apply nie zawierały pola `undo_group` (jest tylko `undo: not_checked`), więc kolumny `undo_group` nie wypełniałem. Przed każdym Apply zapisałem request z `execution_id` w pliku w scratchpadzie sesji (`apply_request_<plan>.json`).
- Dziennik wykonania zapisuje każdy Apply jako `applied` i nie zna UI Undo, więc po Undo nie różni się od stanu bieżącego. Nie robiłem `recover` ani ponownych Apply na tych ID. Pliki JSONL z `logs/evidence/` nie były sprawdzane.
- `host_session_id` zmieniał się między krokami (m.in. po UI Undo), czyli most prawdopodobnie restartował się. Wniosek z identyfikatorów, nie z logów.
- B1: UUID w prompcie były skrócone (`8a693925…` itd.). Pełne uzupełniłem z `drawing_identity` rysunku 101. Pierwsza próba odczytu `attribute_evidence` dała `probe_scope_unavailable`, bo ta faza nie widzi widoku dziecka (`target_in_direct_scan=false`). Użyłem `material_comparison` z `parent_ref`.
- B2-discovery: Ściana 240 ma 29 atrybutów, Podciąg 44 (2 strony), MultiSlab 27. Probe nie zwraca jednostek ani etykiet kontrolek. Boolean/CheckBox nie da się odróżnić od Integer po kodzie typu (73); `attribute_definition` dla 1371 i 1442 zwraca control type 67. Etykietę CheckBox potwierdziło dopiero preview z wartością boolean. Odczyt nie oznacza `computed_only`, więc atrybuty geometryczne wykluczałem po nazwie.
- B2a-real: 220 „Długość” się nie zapisał (`readback_unchanged`), a 230 „Współczynnik” tak. To zgadza się z hipotezą, że 220 jest obliczany z geometrii, ale nie została ona potwierdzona. W tym samym odczycie `size_x_mm` i `size_y_mm` Ściany 240 zwróciły `not_checked` (`ValueError`), a dla pozostałych ścian się odczytały.
- B2b: zapis atrybutu 120 przez `ChangeAttributes` zmienił także natywne CalculationMode (0 → 2), a jedno UI Undo cofnęło oba pola. Probe zgłasza `attribute_mirror` i `storage_coupling` jako „not_established”, więc sprzężenia nie rozstrzygam. Preview nie zgłosiło `paired_property_hint`.
- B2c: atrybut 110 nie jest sprzężony z natywnym Priority (200 bez zmian po zapisie). `slab_tier_values` poprawnie zapowiedziało, że warstwa zachowa własną wartość.
- B2d: wcześniej zapowiedziałem odczyt 1 / 0 / 0, a pozostałe ściany miały 1 już w stanie wyjściowym. Ich wartości sprzed zapisu nie czytałem. Zapis ich nie dotykał (były wykluczone z planu).
- Niewyjaśnione: `counts.matched` w odpowiedzi `highlight` pokazuje liczbę wszystkich ścian (3) przed wykluczeniem, przy `submitted_model_identities: 1`. To samo zjawisko co w uwagach do bloku A.
- Stan modelu po Undo: ostatnie odczyty zgodne z wyjściowymi. Ściana 240: 1371 = 0, 1442 = 1, 230 = 1. Ściany 200 i 300: 1371 = 1, 1442 = 1, 230 = 1. Podciąg: 120 `m3`, natywny 0. MultiSlab: 110 = 200, 981 `<niezdefiniowany>`, 508 `TEST1`. Warstwa płyty: 508 `TEST2`. Dla podciągu i MultiSlab to odczyty z wcześniejszych tur, a Długość (220) Ściany 240 = 4.65 z tury, w której zapis się nie powiódł.

**Uwagi do B3, B3b i B4 (sesja 2026-11-08, bridge 0.51.1, Allplan 2026.1, rysunek 101):**

- B3: do `exclude_model_uuids` trafiło tylko 5 słupów znanych z próbki 20 tożsamości, bez pełnego skanu projektu. Kryteria wykazały `matched: 1`, `excluded: 5`, więc nic poza celem nie pasowało. Okno ważności planu (300 s) zdążyło wygasnąć między highlightem a OK właściciela. Apply przeszedł z tym samym planem i wygaśnięcie nie zablokowało go.
- B3: wcześniej zapowiedziana „potencjalna blokada `replace_requires_existing_attribute`” nie wystąpiła, bo 508 miał zapisaną wartość `TEST1`. Po Undo UUID widoku i AttributeContainera wróciły do pierwotnych.
- B3b-1: `layer_catalog` z `candidate_ids: [3700]` zakończył się `host_error` (request_id `110b1ced-501d-49cb-9b53-a52843a4a301`), do zgłoszenia w Diagnostics. Skan stronicowany (offset 3700, limit 1) działa, ale szuka tylko po nazwie, więc z samego ID nie da się odczytać short_name. Atrybuty 141 „Warstwa” i `layer_id` dają tylko numer. Short_name musiał podać właściciel (`layer_short_name` + `layer_name` rozwiązały go do ID 3700).
- B3b-1: preview użył `short_name`, `expected_layer_id` i `expected_name` w jednym wpisie. Odpowiedź zawiera `confirmed_name` zgodny z odczytem.
- B3b-2: odczyt warstwy na poziomie komponentu (`layer_resolution: component`) pokazał dla korzenia i tieru tę samą wartość (65535). Po zapisie nie robiłem osobnego odczytu samego tieru, bo readback Apply obejmował cały komponent.
- B4: `host_session_id` zmieniał się między krokami. Właściciel zgłosił, że okno z poddrzewem zniknęło, gdy zatrzymał hosta, przy ścianie bez zmian. Z danych nie rozstrzygam, czy zatrzymanie hosta miało wpływ na usunięcie, bo odpowiedź Apply zawierała już `completed` z pustym `present_model_uuids`. Brak logu hosta w sesji.
- B4: po Undo odczyt potwierdził okno i WindowTier oraz liczniki 38/20 jak przed usunięciem. Sill, WindowReveal, WindowOpeningSmartPart i dwa AttributeContainery nie były wyliczone osobno (wniosek z liczników).
- B4: skan zgłaszał dwa konflikty reprezentacji (`2dfa6117…`, `7cc9ac55…`) przed i po zapisie, niezwiązane z oknem.
- `counts.matched` w odpowiedzi `highlight` nadal pokazuje liczbę elementów danego typu przed wykluczeniem (B3: 6, B3b-2: 3), przy `submitted_model_identities: 1`. To samo zjawisko co w blokach A i B.
- Odpowiedzi Apply w B3b-2 i B4 nie zawierały pola `undo_group` (tylko `undo: not_checked`). W B3 `undo_group` był `created`.
- Liczbę UI Undo wpisano z wypowiedzi właściciela („wykonałem undo”), bez osobnego potwierdzenia, że krok był jeden. Pliki JSONL z `logs/evidence/` nie były sprawdzane.
- Wnioski z danych odpowiedzi, kod bridge'a nie był czytany. Natywna akceptacja Allplan (`allplan_acceptance`) i trwałość po zapisie projektu nie były sprawdzane (`runtime_verified: false`).

---

## C. Dane do zebrania od właściciela (bez testów zapisu)

Te dane możesz zebrać w dowolnym momencie, także poza sesją testową: zrzut
ekranu, eksport albo odpowiedź tekstowa. Każda pozycja odblokowuje konkretną
pracę w kodzie.

| # | Co jest potrzebne | Skąd / jak | Co odblokowuje | Komentarz właściciela |
| --- | --- | --- | --- |
| C1 | **Pełna lista `Trade` („Typ robót”) kod ↔ etykieta**, np. 12 = „Roboty murarskie”, 0 = puste. Wszystkie pozycje listy rozwijanej, z numerami, jeśli Allplan je pokazuje | Dialog ściany → „Typ robót”: zrzut całej listy. Albo katalog typów robót w ustawieniach projektu lub biura. Jeśli numerów nie widać, wystarczy kolejność listy i agent ją potwierdzi odczytem | Plan pkt 5: zapis natywnego `Trade`, który dziś jest zablokowany przez brak etykiet | zrzuty w załączonych plikach |
| C2 | **Etykieta atrybutu Column Enum `Status` (ID 49)**: jakie wartości pokazuje UI dla słupów i czy `<niezdefiniowany>` to pusta wartość | Paleta atrybutów słupa: zrzut listy rozwijanej `Status` | Plan pkt 4: komórka Column Enum, dziś BLOCKED | zrzuty w załączonych plikach |
| C3 | **Atrybuty Integer, Real i Boolean na ścianie, belce i stropie**, jeśli B2-discovery nie znajdzie kandydatów: czy w projekcie są atrybuty użytkownika tych typów, które można bezpiecznie zmieniać | Paleta atrybutów: nazwy i typy. Ewentualnie decyzja, że komórka zostaje `FIXTURE` | Plan pkt 4: zamknięcie komórek CODE | przetestowaliśmy część z nich w tej karcie testów, możemy wykonać więcej testów jeśli są konieczne |
| C4 | **Przykład atrybutu typu Data**: nazwa, ID (jeśli widać), format wyświetlania w UI, np. `07.11.2026`, oraz czy ma godzinę | Paleta atrybutów dowolnego elementu z atrybutem daty | Plan pkt 4: projekt kodeka Date, dziś NONE | nie znalazłem tego typu atrybutu |
| C5 | **Decyzja o zaznaczaniu natywnym (selection)**: rozwijamy dalej (eksperyment z `m4-native-selection-api.md` §7) czy zamykamy jako świadomie nieobsługiwane | Decyzja właściciela | Plan pkt 8: zamknięcie albo zaplanowanie eksperymentu | eksperyment po skończeniu wcześniejszej części |
| C6 | **Zgoda na destrukcyjne testy usuwania** (okno, ewentualnie jednorazowy słup, ściana lub belka) i czy możesz dodać jednorazowe elementy: SkeletonBeam, samodzielna płyta (Slab bez MultiSlab), MultiSlab | Decyzja i ewentualne dodanie elementów w kopii projektu | Plan pkt 7–8: komórki `FIXTURE` w macierzy (layer i delete) | wyrażam zgodę na destrukcyjne testy |
| C7 | **Zmiana warstwy płyty `TEST1`→`TEST2` po 0.47.0**: czy to była Twoja ręczna zmiana | Odpowiedź tak / nie / nie wiem | Usunięcie otwartej niejasności z handoffu | nie wiem |
| C8 | **Sprawdzenie aktualizacji i przywracania pakietu na końcowej wersji M4**: robimy je czy zamykamy M4 z adnotacją | Decyzja właściciela | Kryteria zamknięcia M4 | zrobimy po skończeniu wczesniejszych etapów |
| C9 | **Kolejność kandydatów do natywnego zapisu po `CalculationMode`**: czy `Thickness` (grubość warstwy ściany) ma być następny, czy inna właściwość, np. `Priority` | Decyzja właściciela | Plan pkt 5: następna wersja (0.52.0) | "Priority" było przetestowane i działa, zmiana parametrów geometrycznych (grubość, długość, wysokość prawdopodobnie jest niemożliwa, test zmiany atrybutu długości ściany się nie powiódł)
