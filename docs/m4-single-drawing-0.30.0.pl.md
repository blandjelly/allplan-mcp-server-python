# Wspólna próba natywna M4 0.30.0 — priorytety 1–5

To jest plan jednej wspólnej sesji, nie raport wyniku. Kandydat 0.30.0 ma
częściowo rozszerzyć dowody odczytu i no-op. Nie implementuje nieustalonych
setterów dat/wektorów, wyboru natywnego ani właściciela pól Slab/MultiSlab.
Cel pełnego domknięcia priorytetów 1–5 pozostaje aktualny, ale jest
zablokowany przez brak kontraktów właściciela pól, payloadów date/vector i
set/readback selekcji natywnej. Kandydat 0.30.0 zbiera dane potrzebne do
ustalenia tych kontraktów; nie zastępuje ich dokumentacją.

Właściciel wykonuje próbę na kopii projektu, po ustaleniu konkretnego kandydata
i jego dostawy. Przed próbą zapisać manifest instalacji, build Allplana,
`allplan_health`, surowe request/response MCP, log wykonania i świeże skany.
Nie deklarować CI, pakietu ani native PASS, dopóki odpowiednie etapy nie
zostaną wykonane. Zgłoszony PASS grupowego delete/Undo trzech Column w 0.29.0
pozostaje zaakceptowany dla tego zakresu; **nie powtarzać usunięcia ani Undo**.

Sesja powinna przejść przez wszystkie pięć priorytetów i kontynuować po
pojedynczym statusie BLOCKED, zapisując wynik oraz powód dla tego etapu.
Zatrzymać tylko zależne działania, gdy ich konkretne targety lub bezpieczne
warunki nie są dostępne. Nie zmieniać BLOCKED ani `fixture_missing` na PASS.

## Zakres sesji

1. **Dziennik, podgląd, archiwizacja i restart/replay.** Odczytaj podgląd
   dziennika/śladu. Użyj istniejącego rozliczonego execution ID do
   bezsetterowego replay/recovery i — jeśli stan oraz limity na to pozwalają —
   przetestuj potwierdzoną archiwizację. Wykonaj restart hosta i ponowny odczyt
   tylko wtedy, gdy jest częścią sprawdzanego kandydata i można zachować
   ciągłość logu. Nie twórz nowego zapisu w celu przetestowania replay i nigdy
   nie ponawiaj setterów. Rekordy unknown/running, uszkodzone lub
   niezweryfikowane muszą pozostać chronione.
2. **Slab i MultiSlab — dokładne odczyty.** Na każdym dostępnym konkretnym
   celu wykonaj kompletny `drawing_identity`, następnie
   `model_property_probe phase=attribute_evidence` z dokładnymi
   `drawing_file`, `model_uuid`, `view_uuid` i 1–16 unikalnymi, rzeczywistymi
   `attribute_ids`. Włącz `include_parent=true`, jeśli potrzebna jest
   bezpośrednia relacja rodzic–dziecko. Zapisz osobno tożsamość, ancestry,
   pełne children observations, `ReadAll`, `ReadAllAndComputable`, metadane i
   konsensus wrapperów. Niezależny błąd enumeracji children nie usuwa
   obserwacji ancestry. Nie wnioskuj właściciela pola ani nie zapisuj do Slab,
   MultiSlab lub ich dzieci na podstawie samej struktury.
3. **W1 no-op.** Wykonaj świeży odczyt dokładnego aktywnego rysunku i wybierz
   co najmniej jeden istniejący Column już na potwierdzonej warstwie W1.
   Można użyć wcześniej zaakceptowanego Column do tego read-only no-op; zakaz
   dotyczy ponawiania setterów lub Undo, nie odczytu. Główna asercja to
   `state=no_op`, `setter_calls_started=0`,
   `no_op_evidence.reason=already_at_requested_values`,
   `matched_targets>=1` oraz świeża obserwacja `layer_id` równa potwierdzonemu
   ID W1. Następnie wykonaj `model_edit.revalidate` i potwierdź tę samą
   przyczynę, co najmniej jeden cel, świeży W1 odczyt i zero setterów.
   `no_matching_targets` zapisz oddzielnie jako brak dopasowanego celu; nie
   zastępuje dowodu W1 no-op. **Nie wywołuj Apply** dla no-op. Konflikt
   unieważnia plan.
4. **Selekcja, highlight i diagnostyka materiału.** Osobno pokaż odpowiedź
   `model_selection(action=select)` jako `unsupported`; następnie, jeśli jest
   użyteczny nowy dokładny wynik zapytania, wykonaj osobny highlight i opisz go
   wyłącznie jako zgłoszenie highlight, bez utożsamiania z selekcją UI. Dla
   konkretnego, wcześniej niebadanego Wall wykonaj odczyty
   `component_identity`/`wall_sample` i guarded native-material preview.
   Jeśli pojedynczy tier, brak otworów, pełny preservation snapshot i wszystkie
   Apply guardy dają `apply_available=true`, przejdź standardowy przepływ:
   highlight, revalidate, jawne potwierdzenie disposable copy, Apply raz,
   świeży materiałowy readback i jedno UI Undo/readback. Brak native acceptance
   sam nie blokuje evaluation Apply (`native_acceptance_blocks_evaluation=false`).
   Eligibility preview bez zapisu nie jest readbackiem zmiany.
5. **Macierz rodzin i typów.** Dla rzeczywistych definicji i dokładnych
   targetów sprawdź dostępne, już obsługiwane ścieżki scalar/Enum — także
   wcześniej niezaakceptowane rodziny — o ile konkretna bezpieczna fikstura
   jest obecna. Dla każdego faktycznie wykonanego zapisu użyj preview,
   revalidation, jawnego potwierdzenia, Apply raz, świeżego typed readback i
   jednego UI Undo/readback, nie naruszając wcześniej zaakceptowanych targetów.
   Datę/wektor diagnozuj wyłącznie dla rzeczywiście zaobserwowanego
   `attribute_id` z API notatką albo oznacz `fixture_missing`. Zapisz
   `matching_sdk_members`, `binding_status`, surową wartość i runtime type bez
   coercion; jeśli
   wartość to nieznany obiekt, wynik pozostaje type-only `not_checked`. Date/
   vector pozostają BLOCKED bez dokładnego setter payload i typed readback
   kontraktu. Brak definicji lub bezpiecznej fikstury także zapisuj jako
   `fixture_missing`/BLOCKED, nigdy jako PASS.

## Kontrakt `attribute_evidence`

Nowa faza `model_property_probe` przyjmuje dokładnie jeden foreground
`drawing_file`, kanoniczny `model_uuid` i `view_uuid`, listę 1–16 unikalnych
rzeczywistych dodatnich `attribute_ids` oraz opcjonalne `include_parent`
(domyślnie `false`). Wykonuje kompletny `model_identity` scan i czyta najwyżej
16 wrapperów dla dokładnego view UUID. Dla targetu (i opcjonalnie
bezpośredniego rodzica) raportuje ancestry oraz pełną obserwację children
oddzielnie, reprezentację natywną, osobne wyniki stored `ReadAll` oraz
`ReadAllAndComputable` dla żądanych ID, oraz dopasowane człony
`GetAttributeType` do rzeczywiście załadowanych SDK enum members. Wartości JSON
scalar/sequence i runtime type są raportowane niezależnie, bez konwersji,
`repr` ani odgadywania. Nieznane obiekty mają tylko runtime type i
`not_checked`. Zapisz `matching_sdk_members` i `binding_status` (`matched`,
`ambiguous` albo `unresolved`). `evidence_complete=true` i `state=observed`
wymagają consensus wrapperów oraz kompletnych requested raw rows, metadata,
ancestry, children i native-representation reads. Przy częściowych odczytach
zachowaj dane, `evidence_complete=false` i `state=not_checked`. Limit
odpowiedzi wynosi 512 KiB. Probe jawnie nie ustala właściciela właściwości ani
setter payload; nie włącza zapisu.

## Przykładowe requesty do wypełnienia danymi z bieżącego rysunku

Pola w nawiasach kątowych są placeholderami. Przed wysłaniem zastąp je
rzeczywistym rysunkiem, UUID i ID atrybutu uzyskanymi z tej sesji; nie wysyłaj
placeholderów ani nie zgaduj ID.

```json
{
  "phase": "attribute_evidence",
  "drawing_file": 101,
  "model_uuid": "<KANONICZNY_MODEL_UUID_Z_ODCZYTU>",
  "view_uuid": "<KANONICZNY_VIEW_UUID_Z_ODCZYTU>",
  "attribute_ids": [<RZECZYWISTE_ID_1>, <RZECZYWISTE_ID_2>],
  "include_parent": true
}
```

No-op dla warstwy W1 na Column wymaga świeżo potwierdzonego `W1` short name i
ID. Poniższy przykład używa znanego ID 65535, które przed requestem trzeba
potwierdzić świeżym odczytem w tym projekcie. Jawny scope ogranicza query do
jednego foreground drawingu. Predicate zawęża wynik do Column już na W1, więc
plan nie może przypadkowo zawierać rzeczywistych zmian warstwy:

```json
{
  "action": "preview",
  "scope": {"drawing_files": [101], "include_passive": false, "visibility": "api_select_all"},
  "native_types": ["Column_TypeUUID"],
  "predicate": {"field": "layer_id", "op": "eq", "value": 65535},
  "changes": [{"target": {"kind": "layer", "short_name": "W1"}}]
}
```

Po odpowiedzi preview użyj jej dokładnego `plan_id` i `plan_hash`:

```json
{
  "action": "revalidate",
  "plan_id": "<PLAN_ID_Z_ODPOWIEDZI_PREVIEW>",
  "plan_hash": "<PLAN_HASH_Z_ODPOWIEDZI_PREVIEW>"
}
```

Oczekiwane dla no-op: `reason=already_at_requested_values`,
`matched_targets>=1`, `setter_calls_started=0` i świeża obserwacja W1.
Jeśli nie ma dopasowania, zapisz `no_matching_targets` jako osobny wynik.
No-op nie ma Apply.

## Macierz rodzin, typów i dostępności fikstur

| Rodzina / wartość | Działanie w sesji 0.30.0 | Wynik przy braku bezpiecznej fikstury |
| --- | --- | --- |
| Column, Wall, Beam, SkeletonBeam, WindowDoor — istniejący scalar/Enum | Użyj obecnego typowanego kontraktu na nowym, dokładnym celu; pełny guarded write, readback i Undo, jeśli fixture jest dostępny. Nie powtarzaj wcześniej zaakceptowanych zapisów. | `fixture_missing` dla tej pary rodzina/typ. |
| Standalone Slab — istniejący scalar/Enum | Dozwolone tylko dla niezależnie potwierdzonego samodzielnego Slab i istniejącego owner-bound kontraktu; nie używaj nierozstrzygniętego dziecka z konfliktu lineage. | `fixture_missing` albo BLOCKED przy niepewnej lineage. |
| MultiSlab lub Slab child pod MultiSlab — dowolny zapis | Odczyt `attribute_evidence` i identity-only; nie zapisuj, bo właściciel pola nie jest ustalony. | BLOCKED — brak field-owner contract. |
| Wall native material — guarded single-tier target bez otworów | Pełny istniejący eksperymentalny preview/Apply/readback/Undo, tylko gdy wszystkie preservation i Apply guardy są spełnione. | BLOCKED z konkretnym eligibility powodem. |
| Date/vector — dowolna rodzina | Diagnostyka rzeczywistego ID przez `attribute_evidence`; bez setter fallback i bez coercion. | `fixture_missing` jeśli brak definicji/ID; w przeciwnym razie BLOCKED — brak payload/readback contract. |
| Native selection set/clear/readback | Zarejestruj `unsupported`; osobny highlight może być zgłoszony wyłącznie jako highlight. | BLOCKED — setter/readback API contract nieustalony. |

Każdą obecną parę family/type raportuj osobno. Nie twórz atrybutów, warstw,
elementów ani zasobów, aby wypełnić brakującą fiksturę.

## Raportowanie

Oznacz każdy z pięciu priorytetów oraz każdy podkrok jako PASS, BLOCKED, FAIL,
NOT RUN albo `fixture_missing`. Wpisz dokładne targety, rzeczywiste ID
atrybutów, manifest/build, source fingerprint, execution ID (dla replay),
surowe odpowiedzi i readbacki. Nie wpisuj PASS dla samej obecności SDK member,
diagnostyki, highlight, typu runtime lub planu. Próba zbiera evidence, ale sama
nie ustanawia właściciela Slab/MultiSlab, set/clear/readback selekcji UI,
date/vector writability ani atomowości innych operacji; pełny cel priorytetów
1–5 pozostaje zablokowany do czasu ustalenia i zweryfikowania tych kontraktów. Dotychczas
zaakceptowane zakresy pozostają zaakceptowane; żaden wcześniej przyjęty zapis
ani grupowe Undo Column nie są powtarzane.
