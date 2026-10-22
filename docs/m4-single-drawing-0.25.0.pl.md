# Próba natywna 0.25.0 — usunięcie, materiał Wall i brakujące W1

> **Archiwalna instrukcja.** Wyniki części tej próby z 22 października 2026
> zapisano w [ograniczonej obserwacji 0.25.0](test-results/m4-owner-observation-0.25.0-2026-10-22.md).
> Nie powtarzaj odczytów tożsamości, raportowanego usunięcia ściany ani
> readbacku W1 dla ściany 200 mm. Kontynuuj wyłącznie nieodebrane zakresy z
> [krótkiej próby 0.26.0](m4-single-drawing-0.26.0.pl.md).

To jest krótka próba na kopii projektu z dokładnym pakietem 0.25.0. CI i
dostawa kandydata muszą być zakończone przed instalacją. Zachowaj manifest,
build Allplana, `allplan_health`, odpowiedzi MCP i ślady. Nie czyść dzienników.
Nie powtarzaj odczytów/atrybutów stropów, REI120, highlightów ani usunięcia
słupa wykonanego wcześniej w UI.

1. **Typowane usunięcie — jeden testowy cel.** W kopii przygotuj jeden jawnie
   rozpoznawalny, tymczasowy element testowy. Preferuj otwarcie
   `WindowDoor_TypeUUID` z dokładną linią `[opening, Wall root]`, bez makro
   przodków; nie może to przekierować usunięcia na Wall. Zachowaj model/view/type
   UUID, całą linię i pełne poddrzewo celu (maksymalnie 256, łącznie z celem).
   Dziecko wskazane osobno ma być pominięte, gdy wybrany root nadrzędny już je
   obejmuje. Wyłączenie dowolnego elementu poddrzewa blokuje cały root. Przejrzyj
   dokładny plan, wykonaj wymagane `highlight` i `revalidate`, a następnie
   pojedynczy Apply z nowym execution ID. Świeży, kompletny skan ma wykazać
   brak celu i potomków oraz obecność nadrzędnej ściany. Brak rodzica, częściowa
   obecność, niepełny skan lub timeout oznacza `unknown`; wykonaj tylko Recover
   tego execution ID. Nie ponawiaj Apply ani nie usuwaj ręcznie dzieci. Następnie
   wykonaj jedno UI Undo i świeżym skanem potwierdź odtworzenie celu/poddrzewa
   oraz niezmienność Wall. Slab child pozostaje zablokowany, chyba że jest
   objęty pełnym poddrzewem jawnie wybranego MultiSlab.
2. **Natywny materiał — jeden prosty Wall.** Wskaż jeden terminalny,
   samodzielny Wall z dokładnie jedną warstwą/tierem, bez potomków
   `WindowDoor_TypeUUID`. W Allplan wybierz i skopiuj dokładną nazwę
   istniejącego materiału. Preview może zawierać wyłącznie
   `target={kind:"native_material", tier_index:1}` i tę wartość tekstową;
   nie zakładaj, że nazwa istnieje w katalogu. Zapisz stan przed Apply:
   materiał oraz wskazane w planie reprezentacje geometrii Polyhedron3D,
   osi, płaszczyzn/powierzchni i właściwości tier/common. Przejrzyj plan,
   wykonaj wymagane `highlight` i `revalidate`, a potem jeden Apply
   z nowym execution ID potwierdź nazwę w UI oraz świeżym odczycie API;
   porównaj pozostałe zapisane niezmienniki. Wykonaj Undo i potwierdź
   odtworzenie poprzedniego materiału oraz niezmienników. Każdy konflikt,
   niezgodność reprezentacji albo nieznany wynik oznacza stop i Recover bez
   ponawiania setterów.
3. **Tożsamość Slab — jeden odczyt read-only.** Tylko jeśli zachowany jest
   dokładny `drawing_file`, model UUID i view UUID Slab z nieudanego probe
   0.24.0, wykonaj dla nich jeden `model_property_probe` z
   `phase=component_identity`. Nie szukaj nowego celu i nie wykonuj zapisu.
   Zachowaj całą odpowiedź i ślad. Odczyt `observed` potwierdza wynik tego
   jednego probe; błąd nadal pozostawia tożsamość nierozstrzygniętą. Sam wynik
   nie dowodzi, że różnica nazw/warstw była pierwotną przyczyną ani nie
   rozstrzyga celów Slab/MultiSlab.
4. **W1 — wyłącznie brakujące no-op i Undo.** Nie wracaj do wcześniej
   zmienianego ani usuniętego słupa. Najpierw użyj innego, jawnie
   zidentyfikowanego słupa testowego na W1; `preview` bez zmiany ma wskazać
   `no_op` i zero setterów. Następnie na odrębnym, odwracalnym słupie z kopii
   projektu wykonaj pojedynczą zmianę warstwy na istniejące W1 według zwykłego
   preview/highlight/revalidate/Apply. Zapisz pierwotny i końcowy ID warstwy,
   wykonaj jedno UI Undo i potwierdź świeżym odczytem powrót do pierwotnego ID.
   Ogranicz wniosek do tego celu i kroku Undo.

Jeżeli brakuje bezpiecznego, jawnego celu dla któregokolwiek punktu, zapisz
`not_run` i przejdź dalej. Nie twórz celu w aktywnym projekcie użytkownika.
Wyniki natywne pozostają oddzielne od testów automatycznych i CI. Ta próba nie
odbiera selekcji natywnej, rodziny sześciu adapterów, dat ani wektorów.
