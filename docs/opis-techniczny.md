# Opis techniczny

Stan po sprincie 3. Instalacja i wdrożenie: [instrukcja-administratora.md](instrukcja-administratora.md). Architektura i model danych: [specyfikacja](specyfikacja.md#4-architektura), diagramy: [uml.md](uml.md).

## Pliki

| Plik | Zawartość |
|---|---|
| `app.py` | Aplikacja Flask: konfiguracja, trasy, zapytania do sum, walidacja formularza wydatku, filtr `zl` |
| `auth.py` | Blueprint: `/rejestracja`, `/logowanie`, `/wyloguj`; hasła przez `werkzeug.security` |
| `budget.py` | Logika bez Flaska i bazy, na groszach: `limit_state`, `saver_mode` (F10), `average` (F12), `due_soon` (F13), `settle` (F17), `month_done`, `achievements`, `PENALTIES` (F14, F15) |
| `receipts.py` | Odczyt paragonu (F11): `read_receipt(bajty, mime)`, dostawca Gemini w `PROVIDERS`, rozpoznanie JPG/PNG po zawartości |
| `db.py` | Schemat jako lista `MIGRATIONS` (wersja w `PRAGMA user_version`), kategorie, dane demonstracyjne |
| `wsgi.py` | Punkt wejścia na serwerze |
| `scripts/backup_db.py` | Kopia bazy z rotacją 14 kopii |
| `scripts/receipt_spike.py` | Próbka F11: porównanie odczytu modelu z arkuszem `prawda.csv` |
| `scripts/perf_check.py` | NF7: generuje 1000 wydatków w tymczasowej bazie i mierzy ładowanie portfela (limit 1 s) |
| `start.bat` | Uruchomienie lokalne na Windows: instalacja zależności, przeglądarka, `python app.py` |
| `templates/` | `base.html` (nagłówek, baner subskrypcji), `wallet.html`, `edit.html`, `subscriptions.html`, `login.html`, `register.html` |
| `static/style.css` | Style; układ mobilny w `@media (max-width: 700px)` |
| `tests/` | Testy `pytest`; `conftest.py` daje tymczasową bazę i zalogowanego klienta |

## Trasy

| Trasa | Metoda | Funkcja |
|---|---|---|
| `/portfel/<id>` | GET | Widok miesiąca: sumy, kategorie ze średnią i limitami, rozliczenie, lista (parametr `m=RRRR-MM`; `amount`, `category_id`, `description`, `spent_on` wypełniają formularz) |
| `/portfel/<id>/dodaj` | POST | Dodanie wydatku, status wg progu |
| `/portfel/<id>/paragon` | POST | F11: zdjęcie w pamięci, odpowiedź modelu, przekierowanie z wypełnionym formularzem |
| `/portfel/<id>/eksport.csv` | GET | F18: wydatki miesiąca, średnik jako separator, UTF-8 z BOM |
| `/portfel/<id>/limity`, `/prog` | POST | Ustawienia właściciela (F10, F8) |
| `/portfel/<id>/zaproszenie`, `/dolacz/<kod>` | POST, GET | F7 |
| `/wydatek/<id>/edytuj`, `/usun`, `/zatwierdz`, `/odrzuc` | GET/POST | F19, F5, F8 |
| `/subskrypcje`, `/subskrypcje/<id>/usun` | GET/POST, POST | F13 |
| `/portfele/nowy` | POST | F7: nowy wspólny portfel, twórca jest właścicielem |
| `/rejestracja`, `/logowanie`, `/wyloguj` | GET/POST, GET/POST, POST | F6 (`auth.py`) |
| `/` | GET | Przekierowanie na pierwszy portfel użytkownika (osobisty) |

## Baza danych

SQLite, jeden plik `portfelik.db`. Schemat to lista `MIGRATIONS` w `db.py` stosowana według `PRAGMA user_version`; każda migracja działa w transakcji razem z podniesieniem wersji, a starych nie edytuje się. Kwoty są w groszach (`INTEGER`). Daty to teksty `RRRR-MM-DD`, a znaczniki czasu zaproszeń używają `datetime('now')` (UTC).

| Tabela | Kolumny | Uwagi |
|---|---|---|
| `users` | `id`, `name` (UNIQUE), `email` (unikalny indeks), `password_hash` | Hasło jako skrót `werkzeug.security` |
| `wallets` | `id`, `name`, `kind` (`personal`/`shared`), `owner_id`, `approval_threshold` | Próg w groszach, domyślnie 20000 |
| `wallet_members` | `wallet_id`, `user_id` (klucz złożony) | Podstawa uprawnień: `get_wallet` wpuszcza tylko członków |
| `categories` | `id`, `name` (UNIQUE), `icon` | 8 stałych kategorii z `db.CATEGORIES` |
| `expenses` | `wallet_id`, `user_id`, `category_id`, `amount` (>0), `description`, `comment`, `spent_on`, `status`, `decided_by`, `decided_at`, `created_at` | `status`: `pending`, `approved`, `rejected` |
| `category_limits` | `wallet_id`, `category_id`, `amount` | Limit miesięczny kategorii w portfelu |
| `invitations` | `wallet_id`, `code`, `expires_at` | Kod z `secrets.token_urlsafe`, ważny 7 dni |
| `subscriptions` | `user_id`, `name`, `amount`, `day_of_month` (1–31) | Prywatne dla użytkownika |
| `piggy_deposits` | `wallet_id`, `month` (`RRRR-MM`), `amount` (>0) | Klucz złożony: jedno przeniesienie na portfel i miesiąc; saldo skarbonki to suma. Osiągnięcia i kary nie mają tabeli, liczą się przy każdym otwarciu portfela |

Migracje: 1 schemat początkowy, 2 logowanie (e-mail, hasło), 3 zaproszenia, 4 zatwierdzanie, 5 limity, 6 komentarz, 7 subskrypcje, 8 skarbonka.

## Zmienne środowiskowe

| Zmienna | Znaczenie | Domyślnie |
|---|---|---|
| `SECRET_KEY` | Klucz sesji | lokalnie plik `secret_key.txt` |
| `GEMINI_API_KEY` | Klucz API modelu do odczytu paragonów (NF9); bez niego upload daje komunikat o braku konfiguracji | brak |
| `GEMINI_MODEL` | Model Gemini | `gemini-3.5-flash-lite` |
| `RECEIPT_PROVIDER` | Klucz w `receipts.PROVIDERS` | `gemini` |
| `PORT` | Port trybu deweloperskiego | `5000` |

## Decyzje

- **Zdjęcie paragonu (NF6):** `request.files[...].read()` do pamięci, bez `save`. Limit 5 MB to `MAX_CONTENT_LENGTH`; błąd 413 zamienia się w komunikat. Typ pliku wynika z pierwszych bajtów, nie z nazwy.
- **Model do paragonów (F11):** domyślny `gemini-3.5-flash-lite`. Wybrany 10.11.2026 z dokumentacji Google (strony modeli i cen) i zestawień limitów. Warunki: model stabilny (nie preview), darmowy plan, wejście obrazowe, nie wycofany. Limity darmowego planu, które sprawdzono: `gemini-3.8-flash` i `gemini-3.6-flash` mają 20 zapytań dziennie i 5 na minutę, a `gemini-3.5-flash-lite` i `gemini-3.1-flash-lite` 500 dziennie i 15 na minutę. Google nie publikuje tych liczb w dokumentacji (są w AI Studio, zakładka Rate limits, dla danego projektu), więc wartości z zestawień mogą się różnić. Poprzedni wybór `gemini-2.5-flash` jest wycofany dla nowych kluczy (HTTP 404, przekierowanie na `gemini-3.5-flash-lite` od 1.12.2026), a `gemini-3.8-flash` wyczerpał limit 20 zapytań podczas testu. Jakość odczytu potwierdza test akceptacyjny (8 z 10 kwot). Jeśli lite go nie zda, następny kandydat to `gemini-3.1-flash-lite`, a dopiero potem `gemini-3.6-flash` z limitem 20 dziennie.
- **Paragon nie zapisuje wydatku:** odpowiedź modelu trafia do parametrów adresu strony portfela, a formularz zapisuje zwykła trasa `/dodaj`, więc próg zatwierdzania i walidacja działają tak samo jak przy ręcznym wpisie.
- **Walidacja odpowiedzi modelu:** kwota przez `parse_amount`, data przez `date.fromisoformat`, kategoria musi istnieć w tabeli `categories`. Błędne pole jest pomijane, błędna kwota daje komunikat.
- **Średnia z 3 miesięcy (F12):** suma zatwierdzonych wydatków kategorii z 3 poprzednich miesięcy podzielona przez liczbę tych miesięcy, które zaczęły się nie wcześniej niż pierwszy wydatek portfela. Brak historii oznacza brak znacznika.
- **Subskrypcje (F13):** baner liczy `due_soon` przy każdym renderze strony (`context_processor`). Płatność przypada od dnia płatności minus 2 dni do samego dnia płatności.
- **Rozliczenie (F17):** reszta groszy z równego podziału obciąża osoby, które zapłaciły najwięcej, więc salda sumują się do zera.
- **CSV (F18):** separator `;` i przecinek dziesiętny, bo w ten sposób polski Excel otwiera plik od razu w kolumnach. Komórki zaczynające się od `=`, `+`, `-`, `@`, tabulatora lub CR dostają apostrof.

## Bezpieczeństwo

- **Hasła i sesje:** skrót hasła, minimum 8 znaków, ten sam komunikat dla złego e-maila i złego hasła, nowa sesja po zalogowaniu. Ciasteczko sesji ma `HttpOnly` i `SameSite=Lax`. `SECRET_KEY` pochodzi ze środowiska.
- **CSRF:** `CSRFProtect` obejmuje każdy formularz POST (`{{ csrf_token() }}`).
- **Uprawnienia (NF4):** każdy dostęp do portfela przechodzi przez `get_wallet`, a obcy portfel daje 404, jakby nie istniał. Zatwierdzanie sprawdza członkostwo i to, że decyduje ktoś inny niż autor. Edycja i usuwanie wydatku tylko dla autora. Próg i limity tylko dla właściciela portfela (403).
- **Dane wejściowe:** `parse_amount` odrzuca `0`, liczby ujemne, `inf`, `nan` i `1e999`. Przekierowanie po logowaniu (`next`) tylko w obrębie aplikacji (`safe_next`). Zapytania SQL są parametryzowane, szablony Jinja2 escapują HTML.
- **Paragon:** typ pliku po pierwszych bajtach, limit 5 MB, zdjęcie tylko w pamięci, klucz API tylko ze środowiska (NF6, NF9).

## Testy i jakość

`pytest` (232 testy, ok. 25 s) uruchamia się lokalnie i w GitHub Actions. `tests/conftest.py` podmienia `db.DB_PATH` na bazę tymczasową, więc testy nie dotykają `portfelik.db`. Pokrycie linii mierzone narzędziem `coverage`: `budget.py`, `receipts.py` i `auth.py` 100%, `app.py` 98%, `db.py` 98%. Scenariusze opisuje [testy.md](testy.md).

## Wydajność (NF7)

Widok miesiąca wykonuje kilkanaście zapytań SQL i wypisuje wszystkie wydatki miesiąca bez stronicowania. `scripts/perf_check.py` (i test `tests/test_perf.py`) wstawia 1000 wydatków do bieżącego miesiąca wspólnego portfela, czyli najgorszy przypadek, i mierzy 10 pobrań strony. Wynik 10.11.2026: mediana 28 ms, maksimum 30 ms (limit 1000 ms). Pomiar nie obejmuje sieci i pobierania CSS.
