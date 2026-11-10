# Zaległości produktowe (product backlog)

Lista wymagań z priorytetami i szacowanym czasem realizacji w dniach pracy. Priorytety ustala Właściciel produktu (Daria). Lista jest aktualizowana po każdym spotkaniu.

**Priorytet:** W – wysoki, Ś – średni, N – niski.

## Wymagania funkcjonalne

| ID | Wymaganie | Priorytet | Szacunek (dni) | Sprint | Status |
|---|---|---|---|---|---|
| F1 | Dodawanie wydatku: kwota, kategoria, data, opis | W | 1 | 0 | Zrobione |
| F2 | Portfel osobisty i wspólny, przełączanie między nimi | W | 1 | 0 | Zrobione |
| F3 | Podsumowanie miesiąca według kategorii i porównanie z poprzednim miesiącem | W | 1 | 0 | Zrobione |
| F4 | Wspólny portfel: kto ile zapłacił w danym miesiącu | Ś | 0,5 | 0 | Zrobione |
| F5 | Usuwanie własnych wydatków | Ś | 0,5 | 0 | Zrobione |
| F6 | Rejestracja i logowanie z hasłem | W | 1,5 | 1 | Zrobione, czeka na review |
| F7 | Tworzenie wspólnego portfela i zapraszanie osób | W | 1,5 | 1 | Zrobione, czeka na review |
| F8 | Próg zatwierdzania i statusy wydatku: oczekuje / zatwierdzony / odrzucony | W | 2 | 1 | Zrobione, czeka na review |
| F9 | Komentarz do wydatku (np. uzasadnienie zakupu) | Ś | 0,5 | 1 | Zrobione, czeka na review |
| F10 | Limity miesięczne na kategorie, ostrzeżenie i tryb „Oszczędny” (>80% budżetu) | W | 1,5 | 1 | Zrobione, czeka na review |
| F19 | Edycja własnego wydatku (kwota, kategoria, data, opis; zmiana kwoty liczy status od nowa) | Ś | 1 | 1 | Zrobione, czeka na review |
| F11 | **AI:** dodanie wydatku ze zdjęcia paragonu | W | 3 | 2 | Zrobione, czeka na review |
| F12 | Wykres wydatków i porównanie ze średnią z 3 miesięcy | Ś | 1 | 2 | Zrobione, czeka na review |
| F13 | Menedżer subskrypcji z przypomnieniem 2 dni przed płatnością | Ś | 1,5 | 2 | Zrobione, czeka na review |
| F17 | Rozliczenie we wspólnym portfelu: równy podział, salda, przelewy wyrównujące | Ś | 1 | 2 | Zrobione, czeka na review |
| F18 | Eksport wydatków miesiąca do CSV (UTF-8 z BOM, ochrona przed formułami) | Ś | 0,5 | 2 | Zrobione, czeka na review |
| F14 | Skarbonka z zaokrąglaniem wydatków i przenoszeniem niewydanych środków | N | 1 | 3 | Do zrobienia |
| F15 | Osiągnięcia i „kary” za przekroczenie limitów | N | 1,5 | 3 | Do zrobienia |
| F16 | Powiadomienia przez Telegram | N | 2 | – | Poza zakresem (jeśli zostanie czas) |

## Wymagania niefunkcjonalne

| ID | Wymaganie | Priorytet | Sprint | Status |
|---|---|---|---|---|
| NF1 | Interfejs po polsku, czytelny na telefonie i komputerze | W | 0 | Zrobione (przegląd 360 i 1366 px: 10.11.2026) |
| NF2 | Kwoty przechowywane w groszach (bez błędów zaokrągleń) | W | 0 | Zrobione |
| NF3 | Uruchomienie aplikacji jednym plikiem (`start.bat`) | Ś | 0 | Zrobione |
| NF4 | Hasła przechowywane jako skrót (hash); użytkownik widzi tylko swoje portfele | W | 1 | Zrobione, czeka na review |
| NF8 | Bezpieczeństwo aplikacji: `secret_key` ze zmiennej środowiskowej, ochrona CSRF, ciasteczka sesji z `HttpOnly` i `SameSite` | W | 0 | Zrobione |
| NF5 | Dodanie wydatku zajmuje maksymalnie 3 kliknięcia od strony głównej | Ś | 1 | Formularz na stronie głównej; test użyteczności na 2 osobach do wykonania |
| NF6 | Zdjęcie paragonu nie jest przechowywane dłużej niż potrzeba do odczytu | Ś | 2 | Zrobione, czeka na review |
| NF9 | Klucz API modelu AI tylko w zmiennej środowiskowej; informacja o wysyłce obrazu do zewnętrznego modelu | W | 2 | Zrobione, czeka na review |
| NF7 | Strona ładuje się poniżej 1 s przy 1000 wydatków w portfelu | Ś | 3 | Zrobione (maksimum 30 ms, `scripts/perf_check.py`) |
