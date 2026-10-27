# Diagnostyka Allplan MCP 0.41.0 — PASS

PASS wyłącznie dla kompletnego odczytu wskazanego dziecka Slab i osobnego odczytu jego rzeczywistego bezpośredniego rodzica. Wykonano jedną sondę material_comparison, bez ponowienia i bez testu zapisu.

## Warunki i środowisko

- CI: dla commita `f775168aaf8fdb043c269ff09d6ffda9fcea17c9` nowszy przebieg [40550057327](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40550057327) ma zielone ci-required i package. Wcześniejszy przebieg dla tego commita był nieudany.
- Użytkownik potwierdził poprawność CI i ZIP oraz polecił kontynuację od punktu 2. Niezależne potwierdzenie dokładnego zainstalowanego ZIP nie zostało uzyskane; lokalny plik sha256 podaje `ec0df7b1370c36fc42d41aeeab77f9baf28c6219ba6a4153e20eeb800822b751`. Nie zbudowano pakietu zastępczego.
- Health: MCP 0.41.0, bridge 0.41.0, source_commit zgodny; installed_bridge_integrity=verified, mismatches=[].
- Projekt „Kopia MCP_QA_DEMO”, ścieżka `D:\Programy\Allplan\Data\Prj\Kopia MCP_QA_DEMO.prj`; aktywny foreground drawing 101. Trwała tożsamość projektu niezweryfikowana przez API.
- Allplan 2026.1; executable file_version 16.1617.8659.814, product_version 2026.0.1.0; hotfix not_checked; embedded CPython 3.13.13, external Python 3.14.8; runtime_verified=false.
- request_id health `35274aee-6fb3-49de-8bdf-322176ad30e2`, context `f76badb4-7175-4c2e-aace-ad954a326217`, sonda `9ad89ece-031a-4b70-8d3a-e65de93a558a`; probe_id `d7b68f7e6ce645b68a022f76c762d318`.

## Tożsamość i wynik

Target zachował rysunek 101, model `8a693925-ae20-4dda-91d1-3951af3c0a52`, view `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, typ Slab_TypeUUID; nie został zastąpiony przez MultiSlab. identity_resolution.method=`exact_parent_children`; parent_ref zachowuje model `bf097d95-8275-4229-ac74-27bbea26c211`, view `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`, typ MultiSlab_TypeUUID. child_parent_edges potwierdza dokładną krawędź dziecko→rodzic o tych identyfikatorach. Osobno odczytany immediate parent ma tę samą tożsamość. target_in_direct_scan=false jest obserwacją tej sondy; nie ustala ogólnej przyczyny ani zachowania SelectAllElements.

| Odczyt | Slab dziecko | Bezpośredni rodzic MultiSlab |
|---|---|---|
| native_material | `" "` (jedna spacja) | `" "` (jedna spacja) |
| ID 508 ReadAll | `"TEST1"` | `"TEST1"` |
| ID 508 ReadAllAndComputable | `"TEST1"` | `"TEST1"` |

Obie reprezentacje natywne zgłoszono jako `NemAll_Python_ArchElements.SlabElement`, a dostęp do materiału jako `SlabElement.Properties.Material`. Wartości ID 508 mają runtime type `builtins.str`, encoding `json_scalar`. Metadane: nazwa `Materiał`, round-trip nazwa→ID 508, typ SDK `String`, binding matched, runtime `NemAll_Python_BaseElements.AttributeType`. Wartość `" "` nie jest pustym ciągiem `""`.

## Kompletność, widoki i bezpieczeństwo

- representation_count=1, representation_consensus=true, evidence_complete=true; parent_representation_count=1, child_visits=2, child_inventory_complete=true.
- Coverage: scan_complete=true, requested_scope_complete=true, returned_fields_complete=true, returned_fields_not_checked=0; whole_project=false, unloaded_files=not_enumerated, visibility=api_select_all_screen_and_occlusion_not_checked. Pełne coverage i counts są w odpowiedzi.
- source_fingerprint `e0b19a70592aedf376aec41fc3a5d5a2717173e581bcc86e5a608515879f5cd2`; inventory_fingerprint `3372a366350c0cc4ded74e8fcc64b8d8c202c3df8bd3d30c05ad62ad7e60f444`; probe_fingerprint `619574fd1aabde6f3c41016bb24f9b602e045e627700184484b0b82b642c630d`.
- other_view_uuids zawiera `37a3c6a2-d40a-4005-a830-3d212c9bd165`. Odpowiedź nie zgłasza konfliktu reprezentacji; conflicting_model_identities=0, file_state_conflicts=0, duplicate_representations=0. Zachowana krawędź rodzica i osobny odczyt rodzica mają view `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`. Różnica other_view nie dowodzi równoważności widoków.
- read_only=true, model_data_changed=false, usable_for_write=false, setter_calls_started=0; native_selection=not_requested.
- Trace: 365 wpisów w kolejności źródłowej zapisano w `03-trace.jsonl`, ze zgłoszonej ścieżki `Local/.allplan-mcp/logs/m4-native-probe.jsonl`, rozwiniętej jako `C:\Users\dawid\Documents\Nemetschek\Allplan\2026\Usr\Local\.allplan-mcp\logs\m4-native-probe.jsonl`.

Nie ustalono writable ownera, wspólnego składowania ani persistence; nie wywnioskowano równoważności widoków. Odczyt spacji nie stanowi dowodu zapisu. Przyczyna natywna wcześniejszego probe_scope_unavailable pozostaje nieustalona.
