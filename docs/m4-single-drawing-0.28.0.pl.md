# Krótka próba natywna 0.28.0 — usunięcie Column na W1

Ta próba ma objąć wyłącznie nowe zachowanie wiązania rodzica potomka dla
usunięcia Column. Kandydat 0.28.0 implementuje dopasowanie tożsamości rodzica
według rysunku, model UUID i typu, zachowując rzeczywisty view UUID rodzica w
`child_parent_edges` i `descendant_parent_edges` związanych z podglądem i
ponowną walidacją. Dokładny view UUID wybranego celu nadal musi być związany
z planem. Nie zmieniać blokad własności zapisu Slab/MultiSlab.

W tym środowisku nie ma natywnego Allplana; wykonanie próby wymaga właściciela.
Przed próbą użyj wyłącznie dokładnego kandydata 0.28.0 po przejściu pełnego CI
i weryfikacji pakietu. Focused checks dla kodu kandydata przeszły; nie są
wynikiem CI. Zachowaj manifest instalacji, build Allplana, `allplan_health`, pełne
surowe odpowiedzi MCP i logi. Pracuj na kopii projektu. Nie ponawiaj wcześniej
zaakceptowanego usunięcia Wall 240 mm, zmian warstwy, zapisów atrybutów,
lookupu nazwy ani diagnostyki materiału.

## Zgłoszony wynik właściciela — 23 października 2026

Właściciel zgłosił PASS dla punktów 1, 2, 3 i 5 oraz FAIL dla punktu 4.
Trzy Column na W1 zostały podświetlone, preview objął trzy cele (każdy z
podrzędnym kontenerem atrybutów, bez innych wykrytych zależności), a po
potwierdzonym usunięciu świeży odczyt zgłosił brak wszystkich trzech. Jedno UI
Undo przywróciło tylko jeden Column; dalsze Undo nie było dostępne. Oczekiwanie
jednego Undo przywracającego całą grupę nie zostało spełnione. Opcjonalny
read-only probe zgłoszono jako PASS, lecz log nie zawiera jego wyniku.

Oryginalny [log rozmowy](test-results/evidence/allplan-chat-log-0.28.0-2026-10-23.md)
i [ograniczona obserwacja właściciela](test-results/m4-owner-observation-0.28.0-2026-10-23.md)
nie zachowują manifestu instalacji, dokładnego ZIP-a, builda Allplana, surowych
odpowiedzi MCP ani UUID celów. Dlatego punkty 1–3 i 5 są ograniczonymi
obserwacjami owner-reported, a punkt 4 pozostaje FAIL; nie wnioskować o
atomowości ani przyczynie braku dalszego Undo. Próba nie daje pełnej akceptacji
natywnej usuwania Column.

## Zakres

1. **Ustal dokładne cele Column na W1.** Odczytaj identyfikatory rysunku,
   model UUID, view UUID, typ i warstwę dla dokładnie tych celów, które
   zamierzasz usunąć. Log 0.27.0 zgłosił trzy Columns na W1, ale nie zachował
   identyfikatorów; nie zakładaj, że bieżące cele są tymi samymi elementami.
   Jeśli identyczność nie jest jednoznaczna, zatrzymaj próbę.
2. **Podgląd usunięcia.** Wykonaj jedno preview dla dokładnego zaznaczonego
   celu lub jawnej, ograniczonej grupy. W odpowiedzi zachowaj
   `changes[].resource.delete_ownership.value`, w tym `target`, `descendants`,
   `child_parent_edges`, `descendant_parent_edges`, model/view UUID, typ,
   kompletność poddrzewa oraz plan/hash. Preview nie zwraca pola
   `component_ownership`. Potwierdź, że dokładny wybrany target view UUID jest
   zachowany, a krawędzie potomków wiążą ich rzeczywisty rodzicielski view UUID.
   `child_parent_edges` opisuje dzieci root, a `descendant_parent_edges` cały
   zbiór krawędzi poddrzewa. Nie kontynuuj przy uciętym odczycie, brakującej
   krawędzi, konflikcie tożsamości ani nieznanym potomku.
3. **Zatwierdzenie i wykonanie.** Po przejrzeniu dokładnego planu potwierdź
   usunięcie zgodnie z kontraktem. Wykonanie ma wysłać natywny setter raz dla
   dokładnego targetu. Zachowaj pełny wynik dla każdego targetu i potomka;
   wynik `unknown` wymaga odzyskania pod tym samym execution ID, nigdy
   ponownego setteru.
4. **Świeży odczyt i Undo.** Wykonaj świeży kompletny skan i potwierdź brak
   wybranego Column oraz wszystkich związanych potomków. Potwierdź, że
   niezależne elementy pozostały. W UI wykonaj dokładnie jedno Undo na jeden
   element usunięty przez dany krok i po każdym kroku wykonaj świeży odczyt
   tożsamości oraz potomków. Nie zakładaj, że jedno Undo przywraca całą grupę.
5. **Opcjonalny read-only probe.** Jeśli ponownie wystąpi rozbieżność wrapperów,
   zachowaj osobny read-only probe rodzica i potomka z rysunkiem, model UUID,
   view UUID, typem i kierunkiem relacji. Nie zmieniaj celu ani planu na
   podstawie bounds i nie zapisuj do Slab/MultiSlab.

## Wynik i granice

Zapisz każdy etap jako PASS, BLOCKED albo NOT RUN z dokładnym targetem,
manifestem, buildem, surową odpowiedzią oraz świeżym odczytem. Przerwij przy
niejednoznaczności, niekompletności, zmianie celu lub wyniku `unknown`; nie
ponawiaj setteru. Jeśli preview ponownie zwróci
`component_child_owner_mismatch`, zachowaj całą krawędź i zatrzymaj się.

Ta próba nie obejmuje zapisu natywnego materiału, selekcji, no-op warstwy,
ponownych zapisów, Slab/MultiSlab setterów, dat/wektorów ani szerszej macierzy
rodzin. Nie powtarzaj zaakceptowanego Wall subtree delete ani dwóch zmian Beam
na W1 z logu 0.27.0.
