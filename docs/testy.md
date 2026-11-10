# Scenariusze testowe

Każdy scenariusz ma cel, kroki, dane wejściowe i oczekiwany wynik. Kolumna „Test automatyczny” wskazuje test w katalogu `tests/`, który sprawdza ten sam przypadek. Testy automatyczne uruchamia polecenie `pytest`, a w GitHub Actions uruchamiają się przy każdym Pull Requeście.

Dane startowe: baza demonstracyjna tworzona przy uruchomieniu lokalnym (`start.bat`). Konta `valentyn@demo.pl`, `daria@demo.pl` i `filip@demo.pl`, hasło `demo1234`. Właścicielem portfela „Wspólne mieszkanie” jest Valentyn.

## F1–F5 Podstawy: wydatki, portfele, podsumowanie

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F1-01 | Dodanie wydatku | W karcie „Dodaj wydatek” wypełnij pola, kliknij „Dodaj” | Kwota `12,50`, Transport, data `2026-01-15`, opis `bilet` | Wydatek zapisany z kwotą 1250 groszy, autorem i portfelem | `test_basics.py::test_add_expense_saves_all_fields` |
| TC-F1-02 | Domyślna data i pusty opis | Dodaj wydatek tylko z kwotą i kategorią | Kwota `5` | Data dzisiejsza, opis pusty | `test_basics.py::test_add_expense_defaults_date_to_today_and_description_to_empty` |
| TC-F1-03 | Niepoprawne dane | Wyślij formularz z błędną kwotą, datą lub kategorią | `abc`, `0`, `inf`, data `2026-13-45`, kategoria 999 | Komunikat błędu, nic nie zapisane | `test_helpers.py::test_parse_amount_invalid`, `test_permissions.py::test_invalid_date_is_not_saved`, `test_unknown_category_is_not_saved`, `test_security.py::test_infinite_amount_does_not_crash` |
| TC-F2-01 | Lista portfeli | Otwórz stronę główną | Dane demo, Filip | Przekierowanie na portfel osobisty, nad nim lista: osobisty, potem wspólne | `test_wallets.py::test_index_redirects_to_personal_wallet`, `test_basics.py::test_wallet_list_has_personal_first_then_shared` |
| TC-F3-01 | Suma miesiąca i porównanie | Otwórz „Wspólne mieszkanie” | Dane demo | „486,40 zł” i „-4% względem poprzedniego miesiąca (504,14 zł)”; oczekujący wydatek nie wchodzi do sumy | `test_basics.py::test_month_summary_and_comparison_with_previous_month`, `test_pending_does_not_inflate_month_total` |
| TC-F3-02 | Wybór miesiąca | Kliknij strzałkę „‹” | Poprzedni miesiąc | Widok miesiąca z sumą 504,14 zł | `test_basics.py::test_other_month_is_selectable`, `test_helpers.py::test_shift_month` |
| TC-F4-01 | Kto ile zapłacił | Otwórz portfel wspólny | Dane demo | Każdy członek na liście ze swoją sumą zatwierdzonych wydatków | `test_basics.py::test_who_paid_lists_every_member_with_their_total` |
| TC-F5-01 | Usunięcie własnego wydatku | Kliknij ✕ przy swoim wydatku | Wydatek Filipa | Wydatek znika z bazy | `test_permissions.py::test_author_deletes_own_expense` |
| TC-F5-02 | Brak usuwania cudzego wydatku | Jako Daria wyślij usunięcie wydatku Filipa; to samo bez logowania | – | Komunikat „Możesz usuwać tylko własne wydatki.”, wydatek zostaje; bez logowania przekierowanie | `test_permissions.py::test_cannot_delete_someone_elses_expense`, `test_delete_requires_login` |

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
| TC-NF4-03 | Obcy użytkownik nie edytuje, nie zatwierdza i nie dodaje | Jako Daria wyślij żądania dotyczące portfela osobistego Filipa i jego wydatku | Edycja, zatwierdzenie, odrzucenie, dodanie, zaproszenie, limity | Wszędzie 404 | `test_permissions.py::test_member_of_other_wallet_cannot_see_expense_edit_or_decide`, `test_non_member_cannot_add_export_or_invite` |
| TC-NF4-04 | Tylko właściciel zmienia limity i próg | Jako Daria (członek, nie właściciel) zapisz limity | Limit `100` | Odpowiedź 403, limit niezapisany | `test_permissions.py::test_non_owner_cannot_set_limits`, `test_approval.py::test_non_owner_cannot_change_threshold` |

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
| TC-F8-06 | Decyzja tylko raz | Jako Daria zatwierdź, potem odrzuć ten sam wydatek | Wydatek 500 zł | Komunikat „nie czeka już na decyzję”, status pozostaje „zatwierdzony” | `test_permissions.py::test_already_decided_expense_cannot_be_decided_again` |

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

## F11 Paragon (AI)

Testy automatyczne używają atrapy modelu, więc nie wysyłają zdjęć do sieci. Odczyt prawdziwego modelu sprawdza TC-F11-08.

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F11-01 | Poprawny odczyt wypełnia formularz | W karcie „Dodaj wydatek” wybierz zdjęcie i kliknij „Odczytaj paragon” | PNG; model zwraca `12,50 zł`, `2026-11-06`, `Biedronka`, `Transport` | Formularz ma kwotę `12,50`, datę, opis `Biedronka` i wybraną kategorię Transport. Wydatek nie jest zapisany | `test_receipts.py::test_good_answer_fills_form_without_saving` |
| TC-F11-02 | Niepoprawna odpowiedź modelu | Jak wyżej | Odpowiedź `to nie jest json` lub tablica | Komunikat o nieczytelnej odpowiedzi, formularz pusty | `test_receipts.py::test_invalid_json_gives_message`, `test_json_that_is_not_object_gives_message` |
| TC-F11-03 | Zła kwota | Jak wyżej | Kwota `abc`, `0`, `-5`, `inf`, `1e999` | Komunikat „Nie udało się odczytać kwoty”, pole kwoty puste, pozostałe pola wypełnione | `test_receipts.py::test_bad_amount_asks_for_manual_entry_but_keeps_other_fields` |
| TC-F11-04 | Zły typ pliku | Wgraj GIF, PDF, pusty plik lub HTML o nazwie `x.png` | Pliki spoza JPG i PNG | Komunikat o formacie JPG lub PNG, model nie jest wywołany | `test_receipts.py::test_wrong_file_type_is_rejected_before_model`, `test_png_name_does_not_make_html_an_image` |
| TC-F11-05 | Za duży plik | Wgraj plik większy niż 5 MB | Obraz PNG 5 MB + 1 bajt | Komunikat „Plik jest za duży”, model nie jest wywołany | `test_receipts.py::test_too_big_file_is_rejected` |
| TC-F11-06 | Zdjęcie nie trafia na dysk (NF6) | Wgraj poprawne zdjęcie | PNG | Po żądaniu w katalogu bazy nie ma nowych plików | `test_receipts.py::test_nothing_written_to_disk` |
| TC-F11-07 | Klucz API i informacja dla użytkownika (NF9) | Wywołaj dostawcę bez klucza i z kluczem; otwórz portfel | Brak `GEMINI_API_KEY`; klucz `sekret-klucz` | Bez klucza komunikat o braku konfiguracji. Klucz jest w nagłówku, nie w adresie. Przy formularzu jest informacja o zewnętrznym modelu | `test_receipts.py::test_missing_api_key_gives_message`, `test_gemini_sends_key_in_header_and_returns_text`, `test_upload_form_warns_about_external_model` |
| TC-F11-08 | Test akceptacyjny: 8 z 10 paragonów | `python scripts/receipt_spike.py <katalog> ` na 10 zdjęciach z arkuszem `prawda.csv`; potem to samo przez formularz na serwerze | 10 zdjęć różnych sklepów i jakości | Kwota poprawna co do grosza na co najmniej 8 zdjęciach | Ręczny. Wynik 10.11.2026 (lokalnie): 9 z 10 kwot poprawnych, model `gemini-3.5-flash-lite`, zaliczony. Wynik na serwerze do wpisania w `docs/postepy.md` |
| TC-F11-09 | Błąd sieci lub odpowiedź o nieoczekiwanym kształcie | Zasymuluj brak sieci, limit czasu i pustą listę `candidates` | – | Komunikat „Wpisz wydatek ręcznie”, bez błędu 500 | `test_receipts.py::test_gemini_network_errors_become_receipt_error`, `test_gemini_unexpected_reply_shape` |

## F12 Wykres i średnia z 3 miesięcy

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F12-01 | Średnia z pełnej historii | Otwórz portfel z wydatkami sprzed 3 i 1 miesiąca | Jedzenie: 900 zł (−3 mies.), 300 zł (−1 mies.), nic w −2 mies. | Napis „średnia z 3 miesięcy: 400,00 zł” i kreska na pasku | `test_sprint2.py::test_average_of_three_previous_months` |
| TC-F12-02 | Portfel z krótszą historią | Portfel ma wydatek tylko sprzed 1 miesiąca | 300 zł | Średnia 300,00 zł (dzielnik to 1 miesiąc historii) | `test_sprint2.py::test_average_with_shorter_history_uses_only_months_since_first_expense`, `test_budget.py::test_average` |
| TC-F12-03 | Brak historii | Otwórz portfel, który ma wydatki tylko z bieżącego miesiąca | Dane demo | Brak kreski i legendy | `test_sprint2.py::test_no_average_without_history` |
| TC-F12-04 | Do średniej wchodzą tylko zatwierdzone wydatki z 3 poprzednich miesięcy | Dodaj wydatki sprzed 4 miesięcy, z bieżącego i oczekujący | 9000 zł, 9000 zł, oczekujący 5000 zł | Średnia pochodzi wyłącznie z poprawnych wydatków | `test_sprint2.py::test_average_ignores_pending_older_than_three_months_and_current_month` |
| TC-F12-05 | Kreska mieści się na pasku i widok na 360 px | Otwórz portfel na ekranie 360 px | Średnia wyższa niż wydatki bieżącego miesiąca | Kreska jest w granicach paska, brak przewijania w poziomie | `test_sprint2.py::test_marker_position_is_within_bar`; przegląd ręczny |

## F13 Subskrypcje

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F13-01 | Dodanie i lista | Na `/subskrypcje` wypełnij formularz | Spotify, `23,99`, dzień 15 | Subskrypcja na liście, suma miesięczna | `test_sprint2.py::test_add_and_list_subscription` |
| TC-F13-02 | Błędne dane | Wyślij formularz z błędnymi polami | Pusta nazwa, kwota `abc` lub `0`, dzień `0`, `32`, tekst | Komunikat, nic nie zapisane | `test_sprint2.py::test_invalid_subscription_is_not_saved` |
| TC-F13-03 | Baner 2 dni przed płatnością | Dodaj subskrypcję z dniem za 2 dni, otwórz portfel | Dzień = dziś + 2 | Baner „płatność pojutrze”. W dniu płatności „dziś”. Za 5 dni brak baneru | `test_sprint2.py::test_banner_two_days_before_payment`, `test_banner_today_and_not_for_later_payments` |
| TC-F13-04 | Dzień 31 w krótkim miesiącu | Wywołaj `due_soon` dla 27.02.2027 | Dzień płatności 31 | Płatność przypada na 28.02 | `test_budget.py::test_due_soon_31st_in_short_month` |
| TC-F13-05 | Przełom roku | `due_soon` dla 30.12.2026 | Dzień płatności 1 | Płatność 01.01.2027, dla 29.12 jeszcze brak | `test_budget.py::test_due_soon_across_year_end` |
| TC-F13-06 | Prywatność i usuwanie | Jako Daria spróbuj usunąć lub zobaczyć subskrypcje Filipa | – | Cudzej subskrypcji nie widać ani nie usuniesz | `test_sprint2.py::test_delete_only_own_subscription`, `test_subscriptions_are_private` |

## F17 Rozliczenie

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F17-01 | Dwie osoby | Wywołaj `settle` | Ala 30 zł, Bob 10 zł | Ala +10 zł, Bob −10 zł, przelew Bob → Ala 10 zł | `test_budget.py::test_settle_two_people` |
| TC-F17-02 | Trzy osoby | Wywołaj `settle` | Ala 90 zł, pozostali 0 | Ala +60 zł, pozostali −30 zł, dwa przelewy do Ali | `test_budget.py::test_settle_three_people_one_paid_all` |
| TC-F17-03 | Wszyscy po równo i nikt nic | Wywołaj `settle` | 5 zł × 3; 0 zł × 2 | Salda zerowe, brak przelewów | `test_budget.py::test_settle_everyone_paid_equally`, `test_settle_nobody_paid_and_empty` |
| TC-F17-04 | Reszta groszy | Wywołaj `settle` | Ala 1 zł, dwie osoby 0 zł | Salda sumują się do zera, przelewy je wyrównują | `test_budget.py::test_settle_balances_sum_to_zero_and_transfers_clear_them` |
| TC-F17-05 | Karta w portfelu | Otwórz portfel wspólny i osobisty | Dane demo | Karta „Rozliczenie” z przelewem tylko we wspólnym; oczekujące wydatki nie zmieniają rozliczenia; przy równych kwotach „Wszyscy są rozliczeni” | `test_sprint2.py::test_settlement_card_on_shared_wallet`, `test_settlement_ignores_pending`, `test_no_settlement_on_personal_wallet`, `test_settlement_all_even` |

## F18 Eksport CSV

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-F18-01 | Zawartość pliku | Kliknij „Pobierz CSV” przy liście wydatków | Wydatek `12,50`, opis `Żółć gęślą` | Plik zaczyna się od BOM, nagłówek: data, kategoria, kwota, opis, osoba, status; polskie znaki zachowane | `test_sprint2.py::test_export_has_bom_header_and_polish_characters` |
| TC-F18-02 | Ochrona przed formułami | Dodaj wydatek z formułą w opisie, pobierz CSV | Opis `=HYPERLINK("http://zle.pl")`, `+1+1`, `-2`, `@SUM(A1)` | Komórki poprzedzone apostrofem, żadna nie zaczyna się od `=`, `+`, `-`, `@` | `test_sprint2.py::test_formula_in_description_gets_apostrophe` |
| TC-F18-03 | Pusty miesiąc i wybór miesiąca | Pobierz CSV dla `m=2000-01` oraz dla poprzedniego miesiąca | – | Pusty miesiąc: tylko nagłówek. Plik zawiera wydatki wybranego miesiąca, wraz ze statusem „oczekuje” | `test_sprint2.py::test_empty_month_gives_header_only`, `test_export_only_chosen_month`, `test_export_includes_pending_with_status` |
| TC-F18-04 | Uprawnienia | Pobierz CSV cudzego portfela i bez logowania | – | 404 oraz przekierowanie na logowanie | `test_sprint2.py::test_export_of_foreign_wallet_is_404`, `test_export_requires_login` |
| TC-F18-05 | Otwarcie w Excelu | Pobierz plik na komputerze z polskim Excelem i otwórz dwuklikiem | Wydatek z polskimi znakami | Kolumny rozdzielone, polskie znaki poprawne, kwota jako liczba z przecinkiem | Ręczny, do wykonania |

## NF8 Bezpieczeństwo i NF11 Trwałość

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-NF8-01 | Formularz bez tokenu CSRF jest odrzucany | Wyślij POST bez pola `csrf_token` | Logowanie, dodanie wydatku | Odpowiedź 400 | `test_security.py::test_login_without_csrf_token_is_rejected`, `test_post_without_csrf_token_is_rejected` |
| TC-NF8-02 | Przekierowanie po logowaniu tylko w obrębie aplikacji | Zaloguj się z parametrem `next` wskazującym inną domenę | `https://evil.example`, `//evil.example` | Przekierowanie na stronę główną aplikacji | `test_auth.py::test_login_ignores_external_next` |
| TC-NF11-01 | Kopia bazy | Uruchom `python scripts/backup_db.py` | Baza z danymi | W `backups/` powstaje kopia z kompletem danych, zostaje 14 najnowszych kopii | `test_backup.py::test_backup_copies_data_and_rotates` |
| TC-NF11-02 | Dane i sesja przeżywają restart aplikacji na serwerze | Zaloguj się, dodaj wydatek, w zakładce Web kliknij „Reload”, odśwież stronę | Wydatek `TEST-DYMNY` | Wydatek nadal jest na liście, użytkownik pozostaje zalogowany | Ręczny, wykonany 10.11.2026 na bilib.pythonanywhere.com: zaliczony |
| TC-NF11-03 | Przywrócenie bazy z kopii | Zrób kopię (`scripts/backup_db.py`), dodaj wydatek `DO USUNIĘCIA`, „Disable”, skopiuj kopię na `portfelik.db`, „Enable” i „Reload” | Kopia z `~/backups` | Wydatku `DO USUNIĘCIA` nie ma, wcześniejsze dane (`TEST-DYMNY`) są | Ręczny, wykonany 10.11.2026 na bilib.pythonanywhere.com: zaliczony |

## NF1, NF2, NF3, NF5, NF6, NF7, NF9, NF10 Wymagania niefunkcjonalne

| ID | Cel | Kroki | Dane wejściowe | Oczekiwany wynik | Test automatyczny |
|---|---|---|---|---|---|
| TC-NF1-01 | Układ na telefonie i komputerze | Otwórz portfel osobisty i wspólny (z rozwiniętymi ustawieniami), edycję wydatku, subskrypcje i rejestrację w oknie 360 px i 1366 px | Dane demo + wydatek z długim opisem i komentarzem | Brak poziomego przewijania (`scrollWidth` nie przekracza okna), opis i komentarz widoczne, żaden element nie wychodzi poza ekran | `test_edit.py::test_description_not_hidden_on_mobile` (reguła CSS); przegląd ręczny wykonany 10.11.2026 (pomiar DOM w ramkach 360 i 1366 px): zaliczony |
| TC-NF1-02 | Cele dotykowe | Sprawdź wysokość przycisków i pól na ekranie 360 px | – | Przyciski formularzy mają min. 44 px; małe przyciski „✎” i „✕” w wierszu listy mają 25 px wysokości przy szerokości 44 px (świadomie, żeby wiersz nie rósł) | Przegląd ręczny, wykonany 10.11.2026 |
| TC-NF2-01 | Kwoty w groszach | Wywołaj `parse_amount` i filtr `zl` | `12,50`, `12.5`, `12`, ` 1 234,56 `; 123456 groszy | 1250, 1250, 1200, 123456; „1 234,56 zł” | `test_helpers.py::test_parse_amount_valid`, `test_format_zl` |
| TC-NF3-01 | Uruchomienie jednym plikiem | Na czystym Windows z Pythonem 3.10+ uruchom `start.bat` | – | Aplikacja startuje, przeglądarka otwiera stronę logowania, konta demo działają | Ręczny, do wykonania na czystym komputerze |
| TC-NF5-01 | Dodanie wydatku w 3 kliknięciach | Po zalogowaniu (strona główna to portfel osobisty z formularzem) wpisz kwotę, wybierz kategorię, kliknij „Dodaj” | Dwie osoby testowe | Wydatek dodany w co najwyżej 3 kliknięciach od strony głównej: pole kwoty, kategoria, „Dodaj” | Formularz jest na stronie głównej: `test_wallets.py::test_index_redirects_to_personal_wallet`; test użyteczności ręczny, do wykonania (Daria) |
| TC-NF6-01 | Zdjęcie nie jest zapisywane | Patrz TC-F11-06 | PNG | Brak nowych plików | `test_receipts.py::test_nothing_written_to_disk` |
| TC-NF7-01 | Ładowanie przy 1000 wydatków | `python scripts/perf_check.py` | 1000 wydatków w bieżącym miesiącu portfela wspólnego | Maksymalny czas 10 pobrań poniżej 1 s (10.11.2026: mediana 28 ms, maksimum 30 ms) | `test_perf.py::test_wallet_with_1000_expenses_loads_under_one_second` |
| TC-NF9-01 | Klucz API i informacja o modelu zewnętrznym | Patrz TC-F11-07 | – | Klucz tylko ze środowiska, przy formularzu informacja o wysyłce obrazu | `test_receipts.py::test_missing_api_key_gives_message`, `test_upload_form_warns_about_external_model` |
| TC-NF10-01 | Testy w jednym poleceniu i w CI | Uruchom `pytest`; otwórz Pull Request | – | Wszystkie testy przechodzą lokalnie i w GitHub Actions (`.github/workflows/tests.yml`) | Sam zestaw `tests/` |

## F14 Skarbonka i F15 Osiągnięcia

| ID | Scenariusz | Kroki | Dane | Oczekiwany wynik | Test |
|---|---|---|---|---|---|
| TC-F14-01 | Przeniesienie raz na miesiąc | Otwórz zakończony miesiąc, kliknij „Przenieś do skarbonki” dwa razy | Wydatki 12,50 i 10,00 zł w kategorii z limitem 100 zł | Propozycja 78,00 zł (zaokrąglenie 0,50 + niewydane 77,50); jeden zapis, drugie kliknięcie daje komunikat; saldo widać w bieżącym miesiącu | `test_gamification.py::test_piggy_moves_roundups_and_unspent_limits_once` |
| TC-F14-02 | Nic do przeniesienia | Przenieś miesiąc z przekroczonym limitem i pełnymi złotymi | Wydatek 50 zł, limit 30 zł | Komunikat, brak zapisu | `test_gamification.py::test_piggy_nothing_to_move_when_limit_overspent` |
| TC-F14-03 | Miesiąc niezakończony | Wyślij przeniesienie dla przyszłego miesiąca | – | Komunikat, brak zapisu | `test_gamification.py::test_piggy_refuses_unfinished_month`, `test_month_done` |
| TC-F14-04 | Uprawnienia | Jako Filip wyślij przeniesienie do portfela Darii | – | 404 | `test_gamification.py::test_piggy_only_for_wallet_member` |
| TC-F15-01 | Co najmniej 3 osiągnięcia | Otwórz portfel z danymi demo, potem po czystym miesiącu z 3 limitami i skarbonką | – | „Pierwszy krok” zdobyty, „Skarbnik” zablokowany; później wszystkie 4 zdobyte, bez kary | `test_gamification.py::test_first_achievement_earned_with_demo_expense`, `test_all_achievements_after_clean_month_with_piggy`, `test_achievements_earned_flags` |
| TC-F15-02 | Wirtualna kara | Ustaw limit niższy niż wydatki kategorii | Zakupy 199 zł, limit 100 zł | Komunikat „Wirtualna kara” przy kategorii, bez żadnej płatności | `test_gamification.py::test_virtual_penalty_for_exceeded_limit` |

F16 (Telegram) jest poza zakresem.
