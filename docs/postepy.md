# Dziennik postępów

Po każdym spotkaniu dopisujemy: co zostało zrobione (kto co zrobił), jakie były problemy i plan na kolejny tydzień.

---

## Spotkanie 1 – 06.11.2026 (koniec sprintu 0)

### Kto co zrobił

| Osoba | Wykonane prace |
|---|---|
| Valentyn (Lider) | Uzgodnienie zmiany tematu, organizacja zespołu w nowym składzie i podział ról, wybór technologii, przygotowanie repozytorium, pierwsza wersja aplikacji (z pomocą Claude) |
| Daria (Właściciel produktu) | Koncepcja funkcji aplikacji (portfele, zatwierdzanie wydatków, limity, skarbonka, subskrypcje, grywalizacja), ustalenie priorytetów w backlogu |
| Filip (Zespół) | Dołączenie do zespołu, zapoznanie się z koncepcją, przegląd pierwszej wersji interfejsu, zgłoszenie dwóch błędów (uruchomienie na Windows, widok na telefonie) |

### Zrobione

- Nowy temat: aplikacja webowa do budżetu osobistego i wspólnego.
- Koncepcja ([koncepcja.md](koncepcja.md)) i backlog z priorytetami i szacunkami ([backlog.md](backlog.md)).
- Plan sprintów, wykres Gantta, WBS i macierz RAM ([harmonogram.md](harmonogram.md)).
- Pierwsza działająca wersja aplikacji: portfel osobisty i wspólny, dodawanie i usuwanie wydatków, podsumowanie według kategorii, porównanie z poprzednim miesiącem, „kto ile zapłacił”.

### Problemy

- **Zmiana tematu:** poprzedni temat został odrzucony, przez co sprint 0 był krótszy. Zakres ograniczyliśmy do funkcji o wysokim priorytecie.
- **Za dużo pomysłów na dostępny czas:** funkcje podzieliliśmy na priorytety; grywalizacja i Telegram są na końcu listy.
- **Brak dostępu do danych bankowych:** integracja z bankami wymaga licencji (PSD2). Zamiast tego wydatki dodaje się ręcznie albo ze zdjęcia paragonu przez AI.
- **Logowanie i serwer:** w pierwszej wersji użytkownika wybiera się z listy, a aplikacja działa tylko lokalnie. Potrzebne logowanie z hasłem i serwer dostępny z telefonu.
- **Baza danych:** SQLite wystarcza na start; do sprawdzenia, czy poradzi sobie z wieloma użytkownikami naraz, czy przejść na PostgreSQL.
- **Błąd uruchomienia na Windows:** komunikat z polskimi znakami w konsoli (kodowanie cp1252) powodował awarię przy starcie. Poprawione: komunikat w konsoli bez polskich znaków.
- **Widok na telefonie:** formularz dodawania wydatku wychodził poza ekran. Poprawione w stylach (CSS).

### Plan na kolejny tydzień

- Specyfikacja wymagań i makiety ekranów zatwierdzania i limitów (Daria).
- Baza danych pod użytkowników i wspólne portfele; decyzja: SQLite czy PostgreSQL (Valentyn).
- Logowanie z hasłem i wybór serwera do wdrożenia aplikacji (Filip).

---

## Próbka F11 i test akceptacyjny odczytu paragonów – 10.11.2026

Dziesięć zdjęć prawdziwych paragonów (BUDMED, stacje ANWIM/Moya i ORLEN, Lidl, cukiernia, zajazd; różna jakość: zagniecione, obrócone, nieostre). Wzorzec kwot, dat i sklepów spisał Claude ze zdjęć (bez udziału modelu Gemini), a Filip go potwierdził i poprawił (kwota z kaucją, nazwa zajazdu). Uruchomienie: `python scripts/receipt_spike.py <katalog> <arkusz.csv>`.

| Wynik | Wartość |
|---|---|
| Poprawne kwoty co do grosza | **9 z 10** (cel: 8 z 10), test zaliczony |
| Poprawne daty | 10 z 10 |
| Nazwa sklepu zgodna z arkuszem | 7 z 10 (model podaje markę stacji „Moya” zamiast spółki „ANWIM” i nazwę z pozycji zamiast nazwy baru) |
| Model | `gemini-3.5-flash-lite` |

**Błąd:** paragon Lidl z kaucją za opakowania (SUMA 72,20, DO ZAPŁATY 73,20) model odczytał jako 72,20, bo prompt prosił o „SUMA PLN”. Prompt poprawiony: kwota to pozycja „DO ZAPŁATY”, a gdy jej nie ma, „SUMA PLN”. Poprawkę trzeba potwierdzić ponownym uruchomieniem.

### Problemy po drodze

- **Model wycofany:** `gemini-2.5-flash` zwracał HTTP 404 dla nowego klucza. Domyślny model zmieniony po sprawdzeniu dokumentacji Google (patrz `docs/opis-techniczny.md`, sekcja Decyzje).
- **Przeciążenie (HTTP 503) i timeouty:** `receipts.gemini` ponawia teraz żądanie do 3 razy.
- **Limit darmowego planu:** `gemini-3.8-flash` ma 20 zapytań dziennie i wyczerpał się w teście. `gemini-3.5-flash-lite` ma ok. 500 dziennie.
- **Limit zdjęcia 5 MB:** jedno zdjęcie z telefonu (5,7 MB) przekraczało limit aplikacji; do testu zostało zmniejszone. Zdjęcia z nowych telefonów mogą przekraczać 5 MB, co jest ograniczeniem aplikacji.

### Do zrobienia

- Uruchomić próbkę na serwerze PythonAnywhere (klucz w pliku WSGI, dostęp do `generativelanguage.googleapis.com`).
- ~~Ustalić limit kosztów.~~ Decyzja 10.11.2026: model Gemini 3.5 Flash-Lite, darmowy plan (koszt 0, limit dzienny wystarcza), bez płatnych rozliczeń.

