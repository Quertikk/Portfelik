# Plan wdrożenia Portfelika

Lista kontrolna do odznaczania: `[ ]` do zrobienia, `[x]` zrobione. Wymagania i kryteria akceptacji: [wymagania.md](wymagania.md). Przy każdym zadaniu podano ID wymagania, wykonawcę i szacunek w dniach roboczych.

Każda pozycja kodowa spełnia Definition of Done. Praca idzie na gałęzi `feature/<ID>`, a PR recenzuje druga osoba. Nowa logika ma test automatyczny, a scenariusz trafia do `docs/testy.md`. Widok na telefonie jest sprawdzony, backlog zaktualizowany.

Skróty: **V** Valentyn, **D** Daria, **F** Filip.

---

## Etap 0: fundament (06–08.11)

### Proces i repozytorium
- [ ] Tablica GitHub Projects z kolumnami: Backlog, Sprint, W toku, Review, Zrobione (V)
- [ ] Jedna Issue na każdą pozycję F i NF, z etykietą sprintu i osobą (V, D)
- [ ] Dwa błędy zgłoszone przez Filipa w sprincie 0 (uruchomienie na Windows, widok na telefonie) wpisane jako Issues ze statusem „” (F)
- [ ] Ochrona gałęzi `main`: wymagany PR i jedna recenzja (V)
- [ ] Szablon PR z listą Definition of Done w `.github/pull_request_template.md` (V)
- [ ] Specyfikacja przeniesiona do `docs/specyfikacja.md`, pozostałe pliki z `specs/` zachowane (D)
- [ ] Pisemne potwierdzenie prowadzącego, że nowy temat jest zaakceptowany (e-mail), dopisane do `docs/postepy.md` (V)

### Testy
- [ ] `pytest` w `requirements.txt` (F)
- [ ] `tests/conftest.py` z tymczasową bazą (nadpisanie `db.DB_PATH`) i klientem Flask (F)
- [ ] Testy `parse_amount`: poprawne formaty, `0`, liczba ujemna, `inf`, `nan`, tekst (F)
- [ ] Testy `parse_month`, `shift_month`, filtra `zl` (F)
- [ ] Workflow `.github/workflows/tests.yml` uruchamiający `pytest` przy każdym PR (F)

### Migracje i bezpieczeństwo
- [ ] `db.py`: lista `MIGRATIONS` stosowana według `PRAGMA user_version`, migracja 1 to obecny schemat (V)
- [ ] NF8: `app.secret_key` z `SECRET_KEY` (lokalnie plik w `.gitignore`) (F)
- [ ] NF8: `SESSION_COOKIE_HTTPONLY` i `SESSION_COOKIE_SAMESITE="Lax"` (F)
- [ ] NF8: `parse_amount` łapie także `OverflowError` (F)
- [ ] NF8: Flask-WTF `CSRFProtect` i `{{ csrf_token() }}` w każdym formularzu POST (F)

---

## Sprint 1 (06–19.11): konta, wspólny portfel, zatwierdzanie, limity

### F6 Logowanie i rejestracja (F, 1,5 dnia)
- [ ] Migracja 2: `users.email` (UNIQUE) i `users.password_hash`; scalona do `main` pierwszego dnia
- [ ] `auth.py` (Blueprint): `/rejestracja`, `/logowanie`, `/wyloguj`
- [ ] Hasła przez `werkzeug.security`, minimum 8 znaków
- [ ] Komunikat błędnego logowania nie ujawnia, co jest błędne
- [ ] `load_user` w `app.py` zastąpiony sprawdzeniem sesji z przekierowaniem na logowanie
- [ ] Usunięty `/user` i selektor „” z `base.html`
- [ ] Szablony `login.html` i `register.html`
- [ ] Seed demo tylko w trybie deweloperskim, hasło demo opisane w README
- [ ] Testy: rejestracja, logowanie, złe hasło, dostęp bez logowania

### NF4 Izolacja danych (F, razem z F6 i F7)
- [ ] Test: użytkownik A dostaje 404 dla portfela użytkownika B (osobistego i wspólnego)

### F7 Wspólny portfel i zaproszenia (V, 1,5 dnia, po migracji z F6)
- [ ] Trasy `/portfel/<kind>` zmienione na `/portfel/<int:wallet_id>`
- [ ] `get_wallet(wallet_id)` sprawdza członkostwo przez `wallet_members`
- [ ] `wallet.html`: `kind` zastąpiony przez `wallet.kind`, zakładki zastąpione listą portfeli użytkownika
- [ ] `POST /portfele/nowy` ustawia `owner_id` twórcy
- [ ] Migracja: tabela `invitations` (`code` z `secrets.token_urlsafe`, `expires_at`)
- [ ] `GET /dolacz/<code>` dopisuje zalogowanego użytkownika do `wallet_members`, wygasły kod daje komunikat
- [ ] `index` przekierowuje na portfel osobisty
- [ ] Testy: tworzenie, zaproszenie, wygasły kod, użytkownik w dwóch wspólnych portfelach

### F8 Zatwierdzanie wydatków (V, 2 dni, po F7)
- [ ] Makieta ekranu zatwierdzania zaakceptowana przez Darię (D, przed startem)
- [ ] Migracja: `wallets.approval_threshold` (domyślnie 20000 groszy), `expenses.status`, `expenses.decided_by`, `expenses.decided_at`
- [ ] `add_expense`: wspólny portfel i kwota powyżej progu daje status `pending`
- [ ] `POST /wydatek/<id>/zatwierdz` i `/odrzuc`: członkostwo, inny użytkownik niż autor, status `pending`
- [ ] Wszystkie sumy (`month_total`, `by_category`, `by_person`, `total`) filtrują `status='approved'` przez jedną wspólną stałą SQL
- [ ] Karta „” i status widoczny na liście
- [ ] `POST /portfel/<id>/prog` tylko dla właściciela portfela
- [ ] Testy: TC-F8-01 (powyżej progu daje „”), TC-F8-02 (autor nie zatwierdza), odrzucenie, sumy bez oczekujących

### F10 Limity i tryb Oszczędny (V, 1,5 dnia)
- [ ] Makieta limitów zaakceptowana (D, przed startem)
- [ ] Definicja trybu „” potwierdzona przez Darię
- [ ] Migracja: `category_limits(wallet_id, category_id, amount)`
- [ ] `budget.py`: `limit_state(spent, limit)` (ostrzeżenie od 80%) i `saver_mode(spent_total, limits_total, today)`
- [ ] Formularz ustawiania limitów, baner i kolorowanie pasków w `wallet.html`
- [ ] Testy jednostkowe obu funkcji, w tym granica 80%, brak limitów, koniec miesiąca

### F9 Komentarz i F19 Edycja (F, po 0,5 dnia, po F6)
- [ ] Migracja: `expenses.comment`; pole w formularzu i na liście (F9)
- [ ] Funkcja walidacji formularza wydatku wyciągnięta z `add_expense` i użyta w dodawaniu oraz edycji
- [ ] `GET/POST /wydatek/<id>/edytuj` tylko dla autora (F19)
- [ ] Edycja kwoty zatwierdzonego wydatku powyżej progu cofa status do `pending`
- [ ] Testy: edycja własnego, odmowa edycji cudzego, zmiana statusu po edycji

### NF11 Hosting i trwałość (F, razem z F6)
- [ ] Konto PythonAnywhere, plik WSGI, zmienne środowiskowe (`SECRET_KEY`)
- [ ] HTTPS włączone
- [ ] Zadanie okresowe z kopią `sqlite3 .backup`
- [ ] Test dymny: logowanie, dodanie wydatku, restart aplikacji, dane i sesja zachowane
- [ ] Jednokrotne przywrócenie bazy z kopii wypróbowane
- [ ] Sprawdzone, że serwer pozwala na wywołanie zewnętrznego API modelu AI

### Próbka F11 (V, 0,5 dnia)
- [ ] 10 zdjęć paragonów przygotowanych (różne sklepy, jakość zdjęcia)
- [ ] `scripts/receipt_spike.py`: jedno wywołanie modelu, JSON z kwotą, datą, sklepem i kategorią
- [ ] Wynik: liczba poprawnie odczytanych kwot (cel 8 z 10) zapisany w `docs/postepy.md`
- [ ] Próbka uruchomiona także na serwerze docelowym
- [ ] Decyzja: model (Gemini czy Claude) i klucz API w zmiennej środowiskowej, ustalony limit kosztów

### Dokumentacja sprintu 1
- [ ] Kryteria akceptacji F8 i F10 dopracowane przez Darię (D)
- [ ] Scenariusze testowe F6–F10, F19 w `docs/testy.md` (F)
- [ ] Statusy w `docs/backlog.md` zaktualizowane (D)
- [ ] Wpis spotkania 2 (13.11) i 3 (20.11) w `docs/postepy.md` (V)
- [ ] Retrospektywa sprintu 1 w `docs/postepy.md` (wszyscy)
- [ ] Struktura kooperacyjna (zależności zadań) i zaktualizowany podział pracy w `docs/harmonogram.md` (V, D)

### Punkt kontrolny 19.11
- [ ] Logowanie, wspólny portfel z zaproszeniem, zatwierdzanie i limity działają na serwerze
- [ ] `pytest` przechodzi w GitHub Actions
- [ ] Wynik próbki AI znany i zapisany

---

## Sprint 2 (20.11–03.12): AI, wykresy, subskrypcje, rozliczenia

### F11 Paragon (V, 3 dni)
- [ ] `receipts.py`: `read_receipt(image_bytes, mime)` za jednym interfejsem dostawcy
- [ ] `POST /portfel/<id>/paragon`: `MAX_CONTENT_LENGTH` 5 MB, tylko JPG i PNG
- [ ] Plik wczytany do pamięci, nigdzie nie zapisywany (NF6)
- [ ] Odpowiedź modelu walidowana: kwota przez `parse_amount`, data przez `date.fromisoformat`, kategoria z `CATEGORIES` lub „”
- [ ] Formularz wypełniony do edycji, zapis dopiero po zatwierdzeniu
- [ ] Błąd odczytu daje komunikat i ręczne wprowadzanie
- [ ] Klucz API tylko ze zmiennej środowiskowej, nie w repozytorium (NF9)
- [ ] Informacja dla użytkownika o wysyłce obrazu do zewnętrznego modelu (NF9)
- [ ] Testy z atrapą modelu: poprawna odpowiedź, niepoprawny JSON, zła kwota, zły typ pliku, za duży plik
- [ ] Test akceptacyjny: co najmniej 8 z 10 paragonów z poprawną kwotą

### F12 Wykres i średnia z 3 miesięcy (F, 1 dzień)
- [ ] Zapytanie o średnią z 3 poprzednich miesięcy z użyciem `shift_month`
- [ ] Znacznik średniej na istniejącym pasku `.bar` w `static/style.css`
- [ ] Widok sprawdzony na ekranie 360 px
- [ ] Test obliczenia średniej (w tym portfel z krótszą historią)

### F13 Subskrypcje (F, 1,5 dnia)
- [ ] Migracja: `subscriptions(user_id, name, amount, day_of_month)`
- [ ] Strona `/subskrypcje`: lista, dodawanie, usuwanie
- [ ] `due_soon(subs, today)` uwzględnia krótkie miesiące
- [ ] Baner w `base.html` na 2 dni przed płatnością
- [ ] Testy `due_soon`: 31 w lutym, przełom miesiąca i roku

### F17 Rozliczenie (V, 1 dzień, po F8)
- [ ] `settle(totals)` w `budget.py`: równy podział zatwierdzonych wydatków, saldo osoby, lista przelewów wyrównujących
- [ ] Karta „” we wspólnym portfelu
- [ ] Testy: dwie osoby, trzy osoby, wszyscy zapłacili po równo, jedna osoba nie zapłaciła nic

### F18 Eksport CSV (D z V, 0,5 dnia)
- [ ] `GET /portfel/<id>/eksport.csv` przez moduł `csv`, UTF-8 z BOM
- [ ] Komórki zaczynające się od `=`, `+`, `-`, `@` poprzedzone apostrofem
- [ ] Test otwarcia pliku w Excelu: polskie znaki poprawne
- [ ] Testy: wydatek z formułą w opisie, pusty miesiąc

### Dokumentacja sprintu 2
- [ ] Diagramy UML w `docs/uml.md`: przypadki użycia, sekwencji „”, stanów wydatku (F)
- [ ] Szkic `docs/opis-techniczny.md`: pliki, tabele, zmienne środowiskowe (F)
- [ ] Szkic `docs/instrukcja-uzytkownika.md` (D)
- [ ] Scenariusze testowe F11–F13, F17, F18 w `docs/testy.md` (F)
- [ ] Wpisy spotkań 4 (27.11) i 5 (04.12) oraz retrospektywa sprintu 2 w `docs/postepy.md`
- [ ] Statusy w `docs/backlog.md` zaktualizowane

### Punkt kontrolny 03.12
- [ ] Wszystkie funkcje o priorytecie W i Ś gotowe i wdrożone na serwerze
- [ ] Test akceptacyjny F11 zaliczony
- [ ] Brak otwartych błędów krytycznych

---

## Sprint 3 (04–11.12): jakość, bez nowych funkcji

### Testy i poprawki
- [ ] NF7: skrypt generuje 1000 wydatków, pomiar ładowania strony poniżej 1 s (F)
- [ ] NF1: przegląd wszystkich ekranów na 360 px i 1366 px, brak poziomego przewijania (F, D)
- [ ] NF5: test użyteczności dodania wydatku w maksymalnie 3 kliknięciach (D)
- [ ] Uzupełnione testy uprawnień i zatwierdzania, pokrycie logiki w `budget.py`, `receipts.py`, `auth.py` (F)
- [ ] Wszystkie błędy ze zgłoszeń zamknięte lub świadomie odroczone z uzasadnieniem
- [ ] **Zamrożenie funkcji 08.12**

### Dokumentacja końcowa
- [ ] `docs/instrukcja-uzytkownika.md` kompletna, ze zrzutami ekranu (D)
- [ ] `docs/instrukcja-administratora.md`: instalacja, wdrożenie, zmienne środowiskowe, kopia i przywracanie bazy, aktualizacja (F)
- [ ] `docs/opis-techniczny.md` kompletny: opis plików, bazy, konfiguracji (F)
- [ ] `docs/koncepcja.md`: sekcja „” uzupełniona o narzędzia i biblioteki (wytyczna 10) (V)
- [ ] `docs/harmonogram.md`: Gantt, WBS i macierz RAM zgodne ze stanem faktycznym (V, D)
- [ ] `docs/testy.md` kompletny, każde F i NF ma co najmniej jeden scenariusz (F)
- [ ] README zaktualizowany: status, uruchomienie, lista dokumentów (V)
- [ ] Wpis „” dla układów elektronicznych i mechanicznych (wytyczna 7) (D)

### Opcjonalne, tylko przy wolnym czasie
- [ ] F14 Skarbonka (V)
- [ ] F15 Osiągnięcia (D)

### Oddanie
- [ ] Lista 15 punktów wytycznych sprawdzona punkt po punkcie
- [ ] Test dymny na serwerze po ostatnim wdrożeniu
- [ ] Kopia bazy i repozytorium wykonana
- [ ] Próba generalna prezentacji 10.12 (V)
- [ ] Spotkanie 6 i oddanie 11.12

---

## Kalendarz

| Termin | Zdarzenie | Odpowiedzialny |
|---|---|---|
| 06.11 | Spotkanie 1, start etapu 0 | Wszyscy |
| 08.11 | Migracje, testy i NF8 w `main`; migracja `users`; potwierdzenie tematu od prowadzącego | V, F |
| 13.11 | Spotkanie 2: logowanie, F7 w toku, specyfikacja | F, V, D |
| 19.11 | Koniec sprintu 1, retrospektywa | Wszyscy |
| 20.11 | Spotkanie 3: zatwierdzanie i limity | V |
| 27.11 | Spotkanie 4: rozpoznawanie paragonów | V |
| 03.12 | Koniec sprintu 2, retrospektywa | Wszyscy |
| 04.12 | Spotkanie 5: wykresy i subskrypcje | F |
| 08.12 | Zamrożenie funkcji | Wszyscy |
| 11.12 | Spotkanie 6: wersja końcowa i oddanie | Wszyscy |

## Obciążenie (dni kodowania, bez dokumentacji)

| Osoba | Sprint 1 | Sprint 2 | Sprint 3 |
|---|---|---|---|
| Valentyn | F7 1,5; F8 2; F10 1,5; próbka F11 0,5 = 5,5 | F11 3; F17 1; F18 0,5 = 4,5 | F14 (opcjonalnie) |
| Filip | F6 + hosting 2,5; F9 0,5; F19 0,5; NF8 0,5 = 4 | F12 1; F13 1,5 = 2,5 | testy i poprawki |
| Daria | makiety, kryteria akceptacji | F18 0,5 (wspólnie z V) | F15 (opcjonalnie) |

Jeśli sprint 1 się opóźni: F10 przechodzi do sprintu 2, a F13 staje się opcjonalne.
