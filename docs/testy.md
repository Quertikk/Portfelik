# Scenariusze testowe

Każdy scenariusz ma cel, kroki, dane wejściowe i oczekiwany wynik. Kolumna „Test automatyczny” wskazuje test w katalogu `tests/`, który sprawdza ten sam przypadek. Testy automatyczne uruchamia polecenie `pytest`, a w GitHub Actions uruchamiają się przy każdym Pull Requeście.

Dane startowe: baza demonstracyjna tworzona przy uruchomieniu lokalnym (`start.bat`). Konta `valentyn@demo.pl`, `daria@demo.pl` i `filip@demo.pl`, hasło `demo1234`. Właścicielem portfela „Wspólne mieszkanie” jest Valentyn.

## F6 Logowanie i rejestracja

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F6-01 | Rejestracja nowego konta | Otwórz `/rejestracja`, wypełnij formularz, kliknij „Załóż konto” | Nazwa `Ola`, e-mail `ola@example.com`, hasło `tajnehaslo` | Użytkownik jest zalogowany i widzi swój pusty portfel osobisty. W bazie hasło jest zapisane jako skrót, nie jawnym tekstem | `test_auth.py::test_register_creates_user_with_hash_and_personal_wallet` |
| TC-F6-02 | Za krótkie hasło | Jak w TC-F6-01 | Hasło `krotkie` (7 znaków) | Komunikat „Hasło musi mieć co najmniej 8 znaków.”, konto nie powstaje | `test_auth.py::test_register_rejects_invalid_data` |
| TC-F6-03 | Zajęty e-mail | Jak w TC-F6-01 | E-mail `FILIP@demo.pl` | Komunikat „Ta nazwa lub ten e-mail są już zajęte.”, konto nie powstaje | `test_auth.py::test_register_rejects_invalid_data` |
| TC-F6-04 | Logowanie i wylogowanie | Zaloguj się na `/logowanie`, potem kliknij „Wyloguj” | `filip@demo.pl`, `demo1234` | Po zalogowaniu widać portfel i nazwę użytkownika w nagłówku. Po wylogowaniu wejście na adres portfela przenosi do logowania | `test_auth.py::test_login_and_logout` |
| TC-F6-05 | Błędne logowanie nie zdradza, które pole jest złe | Zaloguj się dwa razy: złym hasłem i nieistniejącym e-mailem | `filip@demo.pl` + `zlehaslo1`; `nikt@demo.pl` + `zlehaslo1` | W obu przypadkach ten sam komunikat „Nieprawidłowy e-mail lub hasło.” | `test_auth.py::test_wrong_password_and_unknown_email_give_same_message` |
| TC-F6-06 | Brak dostępu bez logowania | Bez logowania otwórz adres portfela | `/portfel/4` | Przekierowanie na `/logowanie`, po zalogowaniu powrót do portfela | `test_auth.py::test_pages_require_login`, `test_login_redirects_back_to_next` |

## NF4 Izolacja danych

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-NF4-01 | Cudzy portfel osobisty jest niedostępny | Zaloguj się jako Filip, otwórz portfel osobisty Valentyna | `/portfel/1` | Strona 404, także przy próbie dodania wydatku | `test_wallets.py::test_user_gets_404_for_foreign_wallet` |
| TC-NF4-02 | Cudzy portfel wspólny jest niedostępny | Filip tworzy wspólny portfel, Daria otwiera jego adres bez zaproszenia | Adres nowego portfela | Strona 404 | `test_wallets.py::test_user_gets_404_for_foreign_wallet` |

## F7 Wspólny portfel i zaproszenia

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F7-01 | Utworzenie wspólnego portfela | Kliknij „+ Nowy wspólny portfel”, wpisz nazwę, kliknij „Utwórz” | `Wyjazd w góry` | Portfel pojawia się na liście portfeli, twórca jest jego właścicielem | `test_wallets.py::test_create_shared_wallet_sets_owner_and_member` |
| TC-F7-02 | Dołączenie przez link | W nowym portfelu kliknij „Utwórz link zaproszenia”, otwórz link jako Daria | Link `/dolacz/<kod>` | Daria widzi portfel na swojej liście. Ponowne otwarcie linku nie dubluje członkostwa | `test_wallets.py::test_invitation_lets_other_user_join` |
| TC-F7-03 | Link otwarty przed zalogowaniem | Otwórz link zaproszenia w przeglądarce bez sesji, zaloguj się | Link `/dolacz/<kod>` | Po zalogowaniu użytkownik trafia do zaproszenia i dołącza do portfela | `test_wallets.py::test_invitation_link_survives_login` |
| TC-F7-04 | Wygasłe zaproszenie | Otwórz link po terminie ważności (7 dni) | Link z datą ważności w przeszłości | Komunikat „Zaproszenie wygasło lub jest nieprawidłowe.”, brak dostępu do portfela | `test_wallets.py::test_expired_invitation_gives_message` |
| TC-F7-05 | Kilka wspólnych portfeli | Należąc do „Wspólne mieszkanie”, utwórz drugi wspólny portfel i dodaj w nim wydatek | Kwota `10` | Oba portfele są na liście, wydatek trafia tylko do wybranego portfela | `test_wallets.py::test_user_in_two_shared_wallets` |

## F8 Zatwierdzanie wydatków

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F8-01 | Wydatek powyżej progu czeka na zatwierdzenie | We wspólnym portfelu dodaj wydatek | Kwota `200,01` przy progu 200 zł | Status „oczekuje”, wydatek jest w karcie „Do zatwierdzenia” i nie wchodzi do sum | `test_approval.py::test_tc_f8_01_above_threshold_is_pending` |
| TC-F8-02 | Autor nie zatwierdza własnego wydatku | Jako autor wyślij zatwierdzenie | Wydatek z TC-F8-01 | Komunikat o konieczności decyzji innego członka, status bez zmian. Autor nie widzi przycisków decyzji | `test_approval.py::test_tc_f8_02_author_cannot_approve` |
| TC-F8-03 | Zatwierdzenie przez innego członka | Jako Daria kliknij „Zatwierdź” | Wydatek Filipa za 500 zł | Status „zatwierdzony”, zapisane kto i kiedy zdecydował, kwota wchodzi do sum miesiąca | `test_approval.py::test_other_member_approves`, `test_pending_not_in_sums` |
| TC-F8-04 | Odrzucenie | Jako Daria kliknij „Odrzuć” | Wydatek „Telewizor” za 500 zł | Wydatek zostaje na liście z dopiskiem „odrzucony”, nie wchodzi do sum, ponowna decyzja nie zmienia statusu | `test_approval.py::test_rejected_expense_stays_in_history_without_counting` |
| TC-F8-05 | Zmiana progu przez właściciela | Jako Valentyn otwórz „Ustawienia portfela”, wpisz próg | `1000` | Wydatek za 500 zł jest od razu zatwierdzony. Inny członek dostaje 403 przy próbie zmiany progu | `test_approval.py::test_owner_changes_threshold`, `test_non_owner_cannot_change_threshold` |

## F9 Komentarz do wydatku

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F9-01 | Komentarz na liście | Dodaj wydatek z komentarzem | Komentarz `Kupione na promocji` | Komentarz widoczny pod kategorią na liście wydatków | `test_edit.py::test_comment_saved_and_visible` |
| TC-F9-02 | Komentarz przy zatwierdzaniu | Dodaj wydatek powyżej progu z komentarzem, zaloguj się jako inny członek | Kwota `500`, komentarz `Pralka się zepsuła` | Komentarz widoczny w karcie „Do zatwierdzenia” | `test_edit.py::test_comment_visible_when_approving` |
| TC-F9-03 | Opis i komentarz na telefonie | Otwórz portfel na ekranie o szerokości 360 px | Wydatek z opisem i komentarzem | Opis i komentarz są widoczne, strona nie przewija się w poziomie | `test_edit.py::test_description_not_hidden_on_mobile` (reguła CSS); przegląd ręczny |

## F10 Limity i tryb Oszczędny

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F10-01 | Ustawienie i usunięcie limitu | W „Ustawieniach portfela” wpisz limity i zapisz, potem wyczyść jedno pole | Jedzenie `300`, Restauracje `50,50` | Limity zapisane; puste pole usuwa limit | `test_limits.py::test_owner_sets_and_clears_limit` |
| TC-F10-02 | Ostrzeżenie od 80% limitu | Ustaw limit, dodaj wydatek w tej kategorii | Limit 100 zł, wydatek 85 zł | Pasek w kolorze ostrzeżenia i napis „85% limitu” | `test_limits.py::test_warning_at_80_percent`, `test_budget.py::test_limit_state` |
| TC-F10-03 | Przekroczenie limitu | Jak wyżej | Limit 10 zł, wydatek 12,50 zł | Czerwony pasek i napis „Limit przekroczony o 2,50 zł” | `test_limits.py::test_over_limit_message` |
| TC-F10-04 | Tryb Oszczędny | W bieżącym miesiącu wydaj ponad 80% sumy limitów przed ostatnim dniem miesiąca | Limity łącznie 100 zł, wydatki 81 zł | Baner „Tryb Oszczędny” nad podsumowaniem. W poprzednich miesiącach i bez limitów baneru nie ma | `test_budget.py::test_saver_mode`, `test_limits.py::test_saver_banner*` |
| TC-F10-05 | Oczekujące wydatki nie zużywają limitu | Ustaw limit Zakupy 400 zł we wspólnym portfelu z oczekującym wydatkiem 349 zł | Limit `400` | Brak ostrzeżenia, dopóki wydatek nie zostanie zatwierdzony | `test_limits.py::test_pending_expense_does_not_count_toward_limit` |

## F19 Edycja wydatku

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F19-01 | Edycja własnego wydatku | Kliknij ✎ przy swoim wydatku, zmień pola, zapisz | Kwota `12,34`, inna kategoria, data `2026-01-15`, nowy opis i komentarz | Wszystkie pola zmienione | `test_edit.py::test_edit_own_expense` |
| TC-F19-02 | Odmowa edycji cudzego wydatku | Jako Daria otwórz adres edycji wydatku Filipa | `/wydatek/<id>/edytuj` | Strona 404, wydatek bez zmian | `test_edit.py::test_cannot_edit_someone_elses_expense` |
| TC-F19-03 | Ponowne zatwierdzenie po zmianie kwoty | Zatwierdzony wydatek za 500 zł we wspólnym portfelu zmień na 600 zł | Kwota `600` | Status wraca do „oczekuje”, a poprzednia decyzja zostaje usunięta | `test_edit.py::test_raising_approved_amount_above_threshold_needs_approval_again` |
| TC-F19-04 | Zmiana opisu nie cofa zatwierdzenia | Zmień tylko opis zatwierdzonego wydatku | Opis `inny opis` | Status pozostaje „zatwierdzony” | `test_edit.py::test_editing_description_only_keeps_approval` |
| TC-F19-05 | Błędna kwota przy edycji | Wpisz niepoprawną kwotę | `abc` | Komunikat błędu, wydatek bez zmian | `test_edit.py::test_invalid_edit_changes_nothing` |

## NF8 Bezpieczeństwo i NF11 Trwałość

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-NF8-01 | Formularz bez tokenu CSRF jest odrzucany | Wyślij POST bez pola `csrf_token` | Logowanie, dodanie wydatku | Odpowiedź 400 | `test_security.py::test_login_without_csrf_token_is_rejected`, `test_post_without_csrf_token_is_rejected` |
| TC-NF8-02 | Przekierowanie po logowaniu tylko w obrębie aplikacji | Zaloguj się z parametrem `next` wskazującym inną domenę | `https://evil.example`, `//evil.example` | Przekierowanie na stronę główną aplikacji | `test_auth.py::test_login_ignores_external_next` |
| TC-NF11-01 | Kopia bazy | Uruchom `python scripts/backup_db.py` | Baza z danymi | W `backups/` powstaje kopia z kompletem danych, zostaje 14 najnowszych kopii | `test_backup.py::test_backup_copies_data_and_rotates` |
