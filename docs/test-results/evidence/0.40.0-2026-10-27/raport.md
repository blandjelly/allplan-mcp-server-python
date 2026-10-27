# Diagnostyka Allplan MCP 0.40.0 — 2026-10-27

Zakres: wyłącznie odczyt. Nie wykonano Apply, setterów, Undo, usuwania, zmiany warstwy ani konserwacji journalu. Surowe argumenty i pełne odpowiedzi narzędzi znajdują się w plikach JSON w tym katalogu.

## Środowisko i journal

Allplan 2026.1, MCP 0.40.0, bridge 0.40.0, zainstalowany bridge zweryfikowany bez rozbieżności SHA-256. `runtime_verified=false`; hotfix nie sprawdzono. Projekt „Kopia MCP_QA_DEMO”, rysunek 101 aktywny na pierwszym planie. Health request `701ad697-988e-4109-b954-49cf260dad7e`; context request `f727b1e3-4cc0-4600-863f-bea05af12d37`.

Inspect journal request `10bc99c7-33d1-48c8-bc93-624b22a65265`: complete, 31 rekordów, 481 wolnych miejsc, brak `new_execution_blockers` i brak rekordów `requires_recovery=true`. Historyczne `87a45065d5e14e3a9ac8c54756e273a0` jest obecne: `stopped`, integralność verified, wynik `reconciled: 1`, recovery false. `4388b04e39a14fac811db4f58723d01f` nie występuje w zwróconych 31 rekordach; nie dowodzi to jego nieistnienia w archiwum. Inspekcja nie sprawdza bieżących wartości modelu ani nie dowodzi tożsamości kopii. Trace przed sondami: 130170 / 8388608 bajtów; SHA-256 `9cbbfa7bcdf8b85b437ab0afec65041eff8437e78bcd13de6569da3097ebca1b`.

Lokalne podsumowanie `docs/validation-status.md` wersji 0.40.0 opisuje dwie wcześniejsze próby natywnego materiału Slab z pustym readbackiem i zmianą komponentów; dokładny execution_id, właściciel i liczba setterów nie wynikają z podsumowania. Ten sam dokument podaje zgłoszony odczyt atrybutu na MultiSlab i Slab, ale bez surowych payloadów i powiązania właściciela. Nie przypisujemy tych prób do ID z journalu bez dowodu. Lokalny `allplan-conversation-log-2026-10-26.md` opisuje starszy recover `87a...` jako stopped/unknown; obecna inspekcja pokazuje późniejszy status reconciled. `allplan-log-rozmowy.md` łączy `4388...` z atrybutami belek, nie dowodzi próby Slab.

## Wyniki sond

We wszystkich trzech udanych sondach metadane potwierdzają `508 ↔ Materiał`, SDK `String` (wartość Python `str`), `representation_count=1`, `representation_consensus=true`. Jeden wrapper nie dowodzi zgodności między różnymi widokami. Zakres 101: scan i requested scope complete, returned fields complete, zero returned fields not_checked; poza zakresem są unloaded files, cały projekt, widoczność ekranowa/zasłonięcie, native component counts i jednostki/offset geometrii. Property owner, writable owner, storage coupling i physical equivalence nieustalone; persistence not_checked. `not_requested` dla odczytu rodzica pierwszych trzech sond wynika z braku `include_parent`. Nie rozszerzano discovery.

| Cel | Natywna klasa i hierarchia | native_material (observed; owner_ref = dokładny cel) | 508 ReadAll | 508 ReadAllAndComputable |
|---|---|---|---|---|
| SkeletonBeam 1 `2dfa6117-d481-4588-8647-d24049d61d29` / `d9f3d9b1-a005-4789-b929-c39b291d1cd0` | StructuralBeamElement; root, pełny łańcuch rodziców; dzieci AttributeContainer `9a86b9d7-d1fa-4cb1-b06f-5ab043cb6004` / ten sam view i SkeletonAxis `1ae5ed7b-6eb2-46c7-a336-0bef55d0d78a` / `1b43e246-c34a-4037-a68e-11ec73de9a59` | `" "` (jedna spacja); `StructuralBeamElement.StructuralBeamProperties.Material` | `"TEST1"` | `"TEST1"` |
| SkeletonBeam 2 `8f13565b-abfc-4ce2-8b1d-7d133fe1a10d` / `5f6e4603-6282-4ae0-9d02-ad089e73b859` | StructuralBeamElement; root; dzieci AttributeContainer `2f91fb33-5e4d-481f-a775-2522adfbce42` / ten sam view i SkeletonAxis `26007d81-ecfc-4702-b8aa-1d1fb3aec2a7` / `d6e727cd-31a6-44e4-92c6-a2346758be8b` | `" "` (jedna spacja); `StructuralBeamElement.StructuralBeamProperties.Material` | `"TEST1"` | `"TEST1"` |
| MultiSlab `bf097d95-8275-4229-ac74-27bbea26c211` / `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9` | SlabElement; root; dzieci Slab `8a693925-ae20-4dda-91d1-3951af3c0a52` / `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94` i AttributeContainer `f0b54fce-8fdb-4f4e-86b2-9a59d6d499d7` / ten sam view | `" "` (jedna spacja); `SlabElement.Properties.Material` | `"TEST1"` | `"TEST1"` |
| Slab child `8a693925-ae20-4dda-91d1-3951af3c0a52` / `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94` | BLOCKED: `probe_scope_unavailable`; odrębny odczyt wrappera i rodzica nie nastąpił. Relacja powyżej to obserwacja sondy MultiSlab. | nie odczytano | nie odczytano | nie odczytano |

Dla SkeletonBeam 1 obie krawędzie child-parent zwracają ten sam model rodzica, lecz view rodzica `efb18c61-fab3-42f4-b79b-9f41d05da940`, różny od view celu `d9f3d9b1-a005-4789-b929-c39b291d1cd0`. Nie ustalono równoważności tych widoków. Dla MultiSlab native owner_ref wskazuje wyłącznie jego wrapper; nie jest dowodem wartości dziecka.

Identyfikatory: Beam 1 probe `3d2ae565171c4ba7a2e357058119cca3`, request `64e9b644-c7cb-4eab-909e-5bd068e4fa54`; Beam 2 probe `a822050593f445f0bb3c3095d69826db`, request `d2d85e7f-9d4c-4e19-9deb-144eff427680`; MultiSlab probe `c105c234f79f4378bf2491f22ec4f638`, request `87c34b3d-e323-4ea8-9154-14d09597255a`; Slab request `e8e7078e-2723-4ff9-91f6-40cd83811409`, probe_id nie zwrócono. Ścieżka trace według odpowiedzi: `Local/.allplan-mcp/logs/m4-native-probe.jsonl`.

Pełnego pliku trace nie udało się zlokalizować w sprawdzonych lokalizacjach systemowych; nie jest dołączony do tego pakietu. Zachowano ścieżkę, stan i hash sprzed sond oraz wszystkie zwrócone odpowiedzi. Brak pliku ogranicza niezależną kontrolę poszczególnych wywołań natywnych.

## Nierozstrzygnięte

- Dokładny wrapper Slab i osobny odczyt jego rodzica były niedostępne; nie zastąpiono tożsamości. Wcześniejsze zgłoszenia readbacku nie rozstrzygają bieżącej wartości dziecka.
- Różnica view pierwszej belki, własność zapisu i ewentualne współdzielenie składowania pozostają nieustalone. Równe wartości nie dowodzą wspólnego składowania ani skuteczności zapisu.
- ID 4388 nie figuruje w aktualnym wyniku inspekcji, a los archiwalnego rekordu nie jest tu ustalony. Pierwotne surowe dane prób Slab i ich execution_id nie zostały znalezione w dostępnych podsumowaniach.
- Odczyt nie jest testem zapisu ani trwałości. Pominięcie atrybutu nie dowodzi jego nieistnienia.
