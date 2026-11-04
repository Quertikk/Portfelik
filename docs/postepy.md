# Dziennik postępów

Po każdym spotkaniu dopisujemy: co zostało zrobione (kto co zrobił), jakie były problemy i plan na kolejny tydzień.

---

## Spotkanie 1 – 06.11.2026 (koniec sprintu 0)

### Kto co zrobił

| Osoba | Wykonane prace |
|---|---|
| Valentyn (Lider) | Uzgodnienie zmiany tematu, organizacja zespołu w nowym składzie i podział ról, wybór technologii, przygotowanie repozytorium, pierwsza wersja aplikacji (z pomocą Claude) |
| Daria (Właściciel produktu) | Koncepcja funkcji aplikacji (portfele, zatwierdzanie wydatków, limity, skarbonka, subskrypcje, grywalizacja), ustalenie priorytetów w backlogu |
| Filip (Zespół) | Dołączenie do zespołu, zapoznanie się z koncepcją, przegląd pierwszej wersji interfejsu i lista uwag |

### Zrobione

- Nowy temat: aplikacja webowa do budżetu osobistego i wspólnego.
- Koncepcja ([koncepcja.md](koncepcja.md)) i backlog z priorytetami i szacunkami ([backlog.md](backlog.md)).
- Plan sprintów, wykres Gantta, WBS i macierz RAM ([harmonogram.md](harmonogram.md)).
- Pierwsza działająca wersja aplikacji: portfel osobisty i wspólny, dodawanie i usuwanie wydatków, podsumowanie według kategorii, porównanie z poprzednim miesiącem, „kto ile zapłacił”.

### Problemy

- **Zmiana tematu:** poprzedni temat został odrzucony, przez co sprint 0 był krótszy. Zakres ograniczyliśmy do funkcji o wysokim priorytecie.
- **Za dużo pomysłów na dostępny czas:** funkcje podzieliliśmy na priorytety; grywalizacja i Telegram są na końcu listy.
- **Brak dostępu do danych bankowych:** integracja z bankami wymaga licencji (PSD2). Zamiast tego wydatki dodaje się ręcznie albo ze zdjęcia paragonu przez AI.
- **Logowanie:** w pierwszej wersji użytkownika wybiera się z listy; pełne logowanie w sprincie 1.

### Plan na kolejny tydzień

- Specyfikacja wymagań funkcjonalnych i niefunkcjonalnych (Daria).
- Logowanie i rejestracja użytkowników (Valentyn).
- Scenariusze testowe dla pierwszej wersji (Filip).
