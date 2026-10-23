# Ograniczona próba native material M4 0.31.0

Zakres obejmuje wyłącznie nową ścieżkę native material dla samodzielnego
Wall z jednym tierem i bez opening. Nie powtarzać prób 1–3 z 0.30.0, czterech
zapisów/Undo z próby 5 ani zaakceptowanego grouped delete/Undo Column z
0.29.0. Przeszło 87 unique focused checks: 86 affected/dependent checks,
w tym trzy regresje parent-wrapper, oraz jeden package version/lock check.
Zobacz [rekord focused verification](../evaluation-packages/0.31.0/focused-verification.json).
Full CI, package build i native acceptance są pending.

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
