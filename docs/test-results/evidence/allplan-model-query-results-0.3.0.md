# Wyniki odczytów Allplan

Wszystkie opisane wywołania `model_query` były tylko do odczytu. Nie wykonano żadnych zmian w modelu.

## 1. Zapytanie początkowe

**Żądanie:** `action=query`, `drawing_files=[1,2]`, `include_passive=true`, `visibility=api_select_all`, pola `display_name` i `layer_id`, `attribute_ids=[498]`, `page_size=1`.

**Odpowiedź:**

- `selection_id`: `e910d848887d4a00b2c5013d0db8072d`
- `query_session_id`: `077351e5c7764c13bc8649452085755b`
- `request_id`: `40c7a7c5-85e3-4312-9339-713a45038761`
- `host_session_id`: `f1a18063-8eae-43a7-b708-19e849110651`
- `runtime_verified`: `false`; `read_only`: `true`; `usable_for_write`: `false`
- Zakres: plik 1 `active_foreground`, plik 2 `passive_background`; oba z `write_eligibility=not_checked`.
- Liczniki: 2 adaptery odwiedzone, 2 w zakresie, 2 dopasowane identyfikatory modelu, brak niedopasowań, konfliktów, duplikatów i identyfikatorów `not_checked`.
- Pokrycie: skan i żądany zakres kompletne; zwrócone pola kompletne; nie cały projekt; pliki niezaładowane nieenumerowane; widoczność ekranu/zasłonięcia nie sprawdzona; liczba oznacza unikalne `file_model_uuid`, nie komponenty najwyższego poziomu; liczby komponentów natywnych oraz jednostki/geometria/offset nie sprawdzone.
- `omissions=[]`; `not_checked_samples=[]`.
- Zwrócony element (pierwsza strona): plik 1, model UUID `5c7abf7c-10bd-477f-bd4c-e6becdcafe5c`, type UUID `ac9415e3-4337-4860-8cd4-2f0d48596f12`, view UUID `8c4f3865-1689-4e5b-93a9-eb58da9447da`, `durable_identity_verified=false`.
- Pola: `display_name` = zaobserwowano `Słup`; `layer_id` = zaobserwowano `3736`; `type_name` = `Column_TypeUUID`; `type_uuid` = `ac9415e3-4337-4860-8cd4-2f0d48596f12`; `attribute:498` = zaobserwowano surowy tekst `Słup` (nie interpretować jako znaku wiązania).
- Odcisk źródła elementu: `9981702425625dacc5c4c4c0684a8898efc68cb4c6a8e5a3161409f5232a53b9`.
- Strona: offset 0, zwrócono 1, następny kursor `66404442cea6414a870a95f165f5b05e`, `complete=false`, `is_full_selection=false`.
- Odcisk źródła selekcji: `3f19e0eba5adc17d425a8465cdf7426b9b3f0161503aeda94dc78ad9b5180b15`.

## 2. Pozostała strona i podsumowanie pełnej selekcji

### Pozostała strona

**Żądanie:** `action=page`, ta sama selekcja, kursor `66404442cea6414a870a95f165f5b05e`, `page_size=1`.

- Odczyt powiódł się; `request_id=480ac5ee-ee22-4846-9543-2c55b80df7da`.
- Zwrócony element: plik 2, model UUID `5be600e7-0ea6-477d-8ef2-b8257613c097`, type UUID `ac9415e3-4337-4860-8cd4-2f0d48596f12`, view UUID `97ebf740-99ed-45cb-b272-95905029d1f0`, `durable_identity_verified=false`.
- Podpisane numery plików rysunkowych: `[-2]`.
- Pola: `display_name=Słup`, `layer_id=3736`, `type_name=Column_TypeUUID`, `type_uuid=ac9415e3-4337-4860-8cd4-2f0d48596f12`; `attribute:498` ma status `missing`, wartość `null`.
- Odcisk źródła elementu: `79bb7543c62118ae8055a64d8a0b531da5b1b212edfa0fd836fe14980823a031`.
- Strona: offset 1, zwrócono 1, `next_cursor=null`, `complete=true`, `is_full_selection=false`.
- Liczniki/coverage pozostały takie jak w pierwszej odpowiedzi: 2 dopasowane identyfikatory; skan i zakres kompletne; `omissions=[]`; `not_checked_samples=[]`; `usable_for_write=false`.

### Podsumowanie

**Żądanie:** `action=summary` dla `selection_id=e910d848887d4a00b2c5013d0db8072d`.

- Odczyt powiódł się; `request_id=67109d56-1f37-45c4-a03d-3d6844c80d76`.
- `summary_uses_full_selection=true`.
- Podsumowanie według pliku: plik 1 = 1, plik 2 = 1.
- Podsumowanie według typu: `Column_TypeUUID` = 2.
- Liczba unikalnych UUID z obu stron = 2; zgodna z `matched_model_identities=2` i podsumowaniem.
- Selekcja: `e910d848887d4a00b2c5013d0db8072d`; sesja zapytania: `077351e5c7764c13bc8649452085755b`; host: `f1a18063-8eae-43a7-b708-19e849110651`.
- Skan i żądany zakres kompletne; nie cały projekt; pliki niezaładowane nieenumerowane; widoczność ekranu/zasłonięcia, liczby komponentów natywnych i jednostki/geometria/offset nie sprawdzone. `runtime_verified=false`, `usable_for_write=false`, bez pominięć i próbek `not_checked`.

## 3. Świeże zapytania filtrowane

### Dokładny typ i warstwa, pasywne wykluczone

**Żądanie:** nowe `action=query`, `drawing_files=[1,2]`, `include_passive=false`, `visibility=api_select_all`; predykat `all` z `type_uuid eq ac9415e3-4337-4860-8cd4-2f0d48596f12` oraz `layer_id eq 3736`; `page_size=1`.

- Odczyt powiódł się; `selection_id=1df6930e490b4618bf1d64a9a6eb1d4f`; `request_id=7f3f1403-1506-44ac-b140-d02b0b3c2bde`.
- Dopasowanie: 1, w pliku 1; model UUID `5c7abf7c-10bd-477f-bd4c-e6becdcafe5c`; nazwa `Słup`; warstwa 3736; typ `Column_TypeUUID`, type UUID `ac9415e3-4337-4860-8cd4-2f0d48596f12`.
- Plik 2 pominięty z powodu `passive_excluded`. `raw_adapters_visited=2`, `in_scope_adapters=1`, `matched_model_identities=1`; zero niedopasowań, błędów tożsamości lub konfliktów.
- Skan zakończony, ale `requested_scope_complete=false` z powodu wyłączenia pliku pasywnego. `omissions=[{drawing_file:2,reason:passive_excluded}]`; `not_checked_samples=[]`.
- Pozostałe ograniczenia: `runtime_verified=false`; `write_eligibility=not_checked`; pliki niezaładowane nieenumerowane; widoczność ekranu/zasłonięcia nie sprawdzona; `native_component_counts` oraz `geometry_units_offset` nie sprawdzone; `usable_for_write=false`.

### Równość atrybutu 498 do zaobserwowanej wartości

Wartość atrybutu 498 była zaobserwowana jako tekst `Słup`, więc wykonano zapytanie tylko dla pliku 1 z predykatem `attribute:498 eq "Słup"`.

- Odczyt powiódł się; `selection_id=9fd8fb6d1f6d4745923bd122fe45e27c`; `request_id=60d1145f-1b50-472f-b43c-ae9bcce31835`.
- Dopasowanie: 1, w pliku 1; UUID modelu `5c7abf7c-10bd-477f-bd4c-e6becdcafe5c`; `attribute:498` zaobserwowano jako `Słup` (wartość surowa, nie znak wiązania).
- Skan i żądany zakres kompletne; bez pominięć i próbek `not_checked`; `runtime_verified=false`; `write_eligibility=not_checked`; pliki niezaładowane nieenumerowane; widoczność ekranu/zasłonięcia nie sprawdzona; liczby komponentów natywnych i jednostki/geometria/offset nie sprawdzone; `usable_for_write=false`.
- Odcisk źródła elementu: `9981702425625dacc5c4c4c0684a8898efc68cb4c6a8e5a3161409f5232a53b9`, zgodny z odczytem początkowym elementu z atrybutem 498.

## Niezmienność modelu

Wykonane wywołania były zapytaniami tylko do odczytu i nie zmieniały modelu. W zapytaniu filtrowanym po atrybucie 498 ten sam UUID modelu w pliku 1 i ten sam odcisk źródła co w początkowym odczycie potwierdzają zgodność obserwacji.

