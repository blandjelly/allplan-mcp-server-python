# Ograniczona obserwacja właściciela 0.31.0 — materiał Wall i atrybuty

Zachowany log rozmowy opisuje sesję na kopii `Kopia MCP_QA_DEMO`, w aktywnym
rysunku 101, z mostkiem 0.31.0 i Allplan 2026.1. `allplan_health` zgłosił
integralność mostka jako zweryfikowaną, ale zgodność runtime nie była w pełni
zweryfikowana. Nie ma manifestu zainstalowanego ZIP-a ani jego checksumy, więc
nie przypisuję tych obserwacji do dokładnego pakietu ani rewizji źródła.

## Native material Wall — BLOCKED

Dla Wall o grubości 240 mm odczytano model UUID
`06d71e4d-193b-483e-8a32-344ade3d612c`, root view UUID
`2d33e5a6-b4e8-444b-94e8-d4d0ae75d622`, native material `Beton` oraz jeden tier
240 mm. Tier miał model UUID `4db19151-9090-4b1c-bd50-b6fba6873aff` i view UUID
`1bdccbc1-6931-46fd-9f1f-f7b8657ac284`; jego linia wskazała parent view UUID
Wall `2d33e5a6-b4e8-444b-94e8-d4d0ae75d622`. Pozostałe zachowywane właściwości
nie zostały zwrócone w tym odczycie.

Guarded preview dla materiału `Silikat` zatrzymał się na diagnostyce
`wall_material_tier_hierarchy_unsupported`, etap `material_tier_hierarchy`,
`ValueError`. Dokładne dane przekazane w rozmowie to `changes=[]`,
`usable_for_write=false` i `setter_calls_started=0`. Nie wykonano Apply; materiał
pozostał `Beton`. To BLOCKED zaplanowanej ścieżki, a nie udany zapis. Dostępny
jest tylko zapis rozmowy, bez surowej odpowiedzi MCP.

Osobny preview dla Wall 200 mm, model UUID
`545bb0a2-a054-4c91-ac6c-ec552d5b0c18`, którego odczytany materiał to `Cegła`,
również żądał `Silikat`. Zatrzymał się na `component_child_owner_mismatch`, etap
`child_parent_identity`, `ValueError`; rozmowa podaje pustą listę zmian,
`usable_for_write=false` i zero rozpoczętych setterów. Wall 240 mm był
wykluczony. Nie wykonano Apply. Ten przypadek pozostaje odrębną, nierozstrzygniętą
blokadą i nie jest objęty dowodem poprawy parent identity. Również dla niego
brakuje surowej odpowiedzi MCP.

## Enum na Wall — ograniczony PASS Apply/readback/Undo

Surowe requesty i odpowiedzi potwierdzają zapis atrybutu `Rodzaj rozliczenia`
(ID 120, SDK Enum 69) na Wall `06d71e4d-193b-483e-8a32-344ade3d612c` w rysunku
101. Zastosowano jeden zapis z `m3` na `m2`; odpowiedź wykonania podaje
`state=completed`, wynik `applied/readback_matches`, a świeży odczyt po Apply
zwrócił `m2`. Po potwierdzonym przez właściciela UI Undo świeży odczyt zwrócił
`m3`, typ 69 i `adapter_attribute_consistency=consistent` dla czterech
reprezentacji. Jest to ograniczony PASS wyłącznie dla tej pary Wall/Enum i
zaobserwowanego odtworzenia. Metadane wykonania nadal oznaczają
`allplan_acceptance=not_run` i `runtime_verified=false`; brak manifestu
instalacji uniemożliwia przypisanie do dokładnego ZIP-a.

## Boolean/CheckBox na Wall — ograniczony odczyt po zgłoszonym Undo

Rozmowa podaje, że atrybut `Materiał łatwopalny` (ID 1371) jest SDK `Integer`
z kontrolką `CheckBox`, a plan wiązał `true` z wartością native `1`. Dołączony
surowy JSON dokumentuje wyłącznie świeży odczyt po potwierdzonym przez
właściciela Undo: wartość `0`, typ 73 (scalar `integer`) i zgodne cztery
reprezentacje. Wartość `0` odpowiada wcześniejszej wartości odczytanej w
rozmowie. Załączony plik jawnie podaje `write_performed_during_this_turn=false`;
nie ma surowego requestu/response Apply dla Boolean. Zachowuję więc tylko
ograniczoną obserwację odtworzenia po zgłoszonym Undo, bez statusu PASS dla
pełnego cyklu Apply/readback/Undo.

## Slab/MultiSlab i pozostałe typowane przypadki

Read-only log rozmowy podaje aktywny rysunek 101, bridge 0.31.0 i Allplan
2026.1. Slab (`8a693925-ae20-4dda-91d1-3951af3c0a52`) był dzieckiem MultiSlab
(`bf097d95-8275-4229-ac74-27bbea26c211`); reprezentacja dziecka z widoku
MultiSlab miała inny Slab view UUID niż view UUID zwrócony dla osobnej
tożsamości Slab. Zachowuję tę różnicę bez utożsamiania wrapperów. Dołączony
surowy probe ma `evidence_complete=false` dla Slab i `true` dla MultiSlab,
lecz dla obu `property_owner=not_established`,
`physical_target_equivalence=not_established` i brak ustalonej dostępności
zapisu. Żaden zapis Slab/MultiSlab nie został wykonany. Surowe odpowiedzi
obejmują wyłącznie wywołania `attribute_evidence`; pozostałe fazy są opisane w
logu rozmowy.

Enum `Status` na Column (ID 49) pozostał BLOCKED z wartością
`<niezdefiniowany>` i bez potwierdzonej poprawnej etykiety. Boolean SDK typu
`Boolean` ma status `fixture_missing`. Beam i Door pozostały BLOCKED z powodu
niejednoznacznej reprezentacji lub nierozwiązanej tożsamości. Nie przygotowano
preview ani zapisu dla Slab/MultiSlab. Dla dat i wektorów brakowało
potwierdzonego ID i typu SDK; pozostały BLOCKED. Nie wykonano szerokiego skanu
katalogu definicji.

Zachowane kopie wszystkich dostarczonych plików, bez zmian:

- [log rozmowy](evidence/0.31.0-2026-10-24/allplan-conversation-log.md)
- [Enum Apply request i etapy](evidence/0.31.0-2026-10-24/enum-apply-evidence.json)
- [Enum execution i readback po Apply](evidence/0.31.0-2026-10-24/enum-apply-execution-evidence.json)
- [Enum readback po Undo](evidence/0.31.0-2026-10-24/enum-undo-evidence.json)
- [Boolean/CheckBox readback po Undo](evidence/0.31.0-2026-10-24/boolean-checkbox-undo-evidence.json)
- [Slab/MultiSlab attribute evidence](evidence/0.31.0-2026-10-24/slab-multislab-readonly-evidence.json)

Obserwacje nie zamykają priorytetów 1–5 ani pełnej bramki odbioru pojedynczego
rysunku. Nie stanowią też odbioru native material w 0.31.0: oba dostępne
preview materiału były zablokowane przed Apply.
