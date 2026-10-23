# Ograniczona próba native material M4 0.31.0

Zakres obejmuje wyłącznie nową ścieżkę native material dla samodzielnego
Wall z jednym tierem i bez opening. Nie powtarzać prób 1–3 z 0.30.0, czterech
zapisów/Undo z próby 5 ani zaakceptowanego grouped delete/Undo Column z
0.29.0. Przeszło 87 unique focused checks: 86 affected/dependent checks,
w tym trzy regresje parent-wrapper, oraz jeden package version/lock check.
Zobacz [rekord focused verification](../evaluation-packages/0.31.0/focused-verification.json).
Oba full CI unittest jobs przeszły na Windows i Ubuntu Python 3.12 w
[run 40012042481](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40012042481).
CI 40012042481 przeszedł: 625 testów Ubuntu Python 3.12.15, 625 testów
Windows Python 3.12.10 i package job. Oryginalny CI artifact 12527730616 był
niedostępny. Jeden fallback ZIP z czystego detached exact source
(`source_modified=false`) przeszedł weryfikację: 201 payload files, 43 bridge
hashes, SHA-256
`4047e7bb58eff28c8f87fdc488d0e787ad1a048cf05aae7b7d537646826fbbcb`.
Próba native 0.31.0 pozostaje do wykonania.

Użyj zweryfikowanego [fallback ZIP](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip)
z dokładnego źródła 0.31.0 i zachowaj [rekord ZIP](../evaluation-packages/0.31.0/package-verification.json)
oraz [checksum](../evaluation-packages/0.31.0/allplan-mcp-0.31.0-windows-evaluation.zip.sha256).

Wykonaj próbę na kopii projektu z dokładnym kandydatem i zapisz manifest
instalacji, build Allplana, `allplan_health`, dokładne drawing/model/view UUID
Wall i tier, requesty oraz surowe odpowiedzi MCP. Wall musi być samodzielnym
rootem z dokładnie jednym bezpośrednim `WallTier_TypeUUID` child. Tier nie może
mieć własnych children; Wall nie może mieć opening ani innych children.
Wymagany jest pełny istniejący preservation snapshot. Nie twórz ani nie
zmieniaj fikstur, aby spełnić warunki.

Użyj dokładnej wartości `Żelbet`, jeśli nadal jest wartością żądaną; w innym
razie zastosuj wyłącznie wartość native material podaną przez właściciela.
Nie stosuj fuzzy/catalog resolution ani nie zakładaj, że sama nazwa jest
poprawna. Jeśli fixture, wartość lub guard nie kwalifikuje celu, zapisz
`BLOCKED` albo `fixture_missing` wraz z dokładnym diagnostic; nie wysyłaj
Apply.

1. Odczytaj tożsamość Wall i tier oraz świeży stan materiału i zachowywanych
   właściwości. Zapisz rzeczywiste view UUID root i view UUID parent widziany
   przez tier.
2. Wykonaj guarded preview dla jednego konkretnego targetu. Wymagaj
   `apply_available=true`, dokładnego target binding oraz preservation snapshot,
   który zachowuje rzeczywiście zaobserwowany parent wrapper i przechodzi
   revalidation. Upewnij się, że w snapshotcie istnieje dokładnie jeden tier,
   brak opening i żadnych zmian geometrii/hierarchii.
3. Wykonaj oddzielny highlight, następnie revalidate. Zweryfikuj, że plan i
   target identity nie zmieniły się oraz wszystkie Apply guardy nadal
   kwalifikują się. Zapisz jawne potwierdzenie pracy na kopii projektu.
4. Wyślij Apply dokładnie raz. Wykonaj świeży native-material readback i
   sprawdź zachowanie geometrii, tier count, hierarchii, osi i pozostałych
   wartości preservation. Wykonaj jedno UI Undo i świeży odczyt potwierdzający
   przywrócenie materiału oraz invariants.
5. Jeśli preview/revalidate jest blocked, nie wykonuj Apply. Zachowaj dokładny
   diagnostic, target identities oraz `changes`, `usable_for_write` i
   `setter_calls_started`. W szczególności drugi 0.30.0 wynik
   `component_child_owner_mismatch` pozostaje nierozstrzygnięty; nie traktuj
   poprawki parent-view matching jako naprawy tego przypadku.

Jeśli odpowiedź Apply jest unknown, nie ponawiaj zapisu. Użyj oryginalnego
execution ID i istniejącego recovery/inspection flow, zbierz świeży stan i
pozostaw niepewny wynik nierozliczony, dopóki nie zostanie rozstrzygnięty.
Nie wykonuj drugiego Apply ani automatycznego rollbacku.

Próba akceptuje wyłącznie konkretną Wall material ścieżkę, dla której
wykonano Apply, readback i Undo. Nie zamyka native selection, właściciela
Slab/MultiSlab, date/vector payloadów, innych rodzin/typów ani szerszych
priorytetów M4. Rejestrować tylko obserwacje z dostarczonego kandydata; nie
wiązać wyniku z dokładnym ZIP-em bez manifestu i jego checksumy.

## Dostarczony wynik sesji 0.31.0

Właściciel podał późniejszy log z Allplan 2026.1 i mostka 0.31.0. Wall 240 mm
(model UUID `06d71e4d-193b-483e-8a32-344ade3d612c`) miał root view UUID
`2d33e5a6-b4e8-444b-94e8-d4d0ae75d622`, jeden tier 240 mm oraz parent view
UUID tieru równy temu root view UUID. Odczytany materiał to `Beton`; preview
`Silikat` został zablokowany przez `wall_material_tier_hierarchy_unsupported`
(`material_tier_hierarchy`, `ValueError`), `changes=[]`,
`usable_for_write=false` i zero setterów. Apply nie wykonano.

Osobny Wall 200 mm o model UUID
`545bb0a2-a054-4c91-ac6c-ec552d5b0c18` miał materiał `Cegła`; preview
`Silikat` został zablokowany przez `component_child_owner_mismatch`
(`child_parent_identity`, `ValueError`), również bez zmian, setterów ani
Apply. Ten drugi przypadek pozostaje nierozstrzygnięty i poza potwierdzonym
zakresem poprawki parent-wrapper. Dostarczony log jest rozmową, bez raw MCP
response i bez manifestu/checksumy ZIP-a. Zobacz [ograniczoną obserwację](test-results/m4-owner-observation-0.31.0-2026-10-24.md)
oraz [kopie dowodów](test-results/evidence/0.31.0-2026-10-24/). Native material
ścieżka w 0.31.0 pozostaje BLOCKED; żaden z tych wyników nie stanowi Apply,
readback ani Undo materiału.
