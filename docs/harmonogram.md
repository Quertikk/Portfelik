# Harmonogram i podział prac

Pracujemy w sprintach dwutygodniowych (zgodnie z modyfikacją metody Scrum przyjętą na zajęciach). Co tydzień, w czwartek, odbywa się spotkanie z prowadzącym podsumowujące prace.

| Sprint | Termin | Cel |
|---|---|---|
| 0 | 29.10 – 05.11.2026 | Zmiana tematu, koncepcja, backlog, pierwsza działająca wersja |
| 1 | 06.11 – 19.11.2026 | Logowanie, wspólny portfel z zapraszaniem, zatwierdzanie wydatków, limity |
| 2 | 20.11 – 03.12.2026 | AI: paragony, wykresy, subskrypcje |
| 3 | 04.12 – 11.12.2026 | Skarbonka, osiągnięcia, testy, dokumentacja końcowa |

| Spotkanie | Data | Co pokazujemy |
|---|---|---|
| 1 | 06.11.2026 | Nowy temat, role, backlog, pierwsza wersja aplikacji |
| 2 | 13.11.2026 | Logowanie, specyfikacja wymagań |
| 3 | 20.11.2026 | Zatwierdzanie wydatków, limity; przegląd sprintu 1 |
| 4 | 27.11.2026 | Rozpoznawanie paragonów przez AI |
| 5 | 04.12.2026 | Wykresy, subskrypcje; przegląd sprintu 2 |
| 6 | 11.12.2026 | Wersja końcowa, testy, dokumentacja |

## Wykres Gantta

```mermaid
gantt
    title Harmonogram projektu Portfelik
    dateFormat YYYY-MM-DD
    axisFormat %d.%m

    section Spotkania
    Spotkanie 1                    :milestone, 2026-11-06, 0d
    Spotkanie 2                    :milestone, 2026-11-13, 0d
    Spotkanie 3                    :milestone, 2026-11-20, 0d
    Spotkanie 4                    :milestone, 2026-11-27, 0d
    Spotkanie 5                    :milestone, 2026-12-04, 0d
    Spotkanie 6                    :milestone, 2026-12-11, 0d

    section Sprint 0
    Koncepcja i backlog            :done, 2026-10-29, 5d
    Pierwsza wersja aplikacji      :done, 2026-11-01, 4d

    section Sprint 1
    Specyfikacja wymagań           :2026-11-06, 7d
    Logowanie i rejestracja        :2026-11-06, 5d
    Wspólny portfel i zaproszenia  :2026-11-10, 5d
    Zatwierdzanie wydatków         :2026-11-13, 6d
    Limity i tryb Oszczędny        :2026-11-14, 5d

    section Sprint 2
    AI: rozpoznawanie paragonów    :2026-11-20, 9d
    Wykresy i porównania           :2026-11-24, 5d
    Subskrypcje i przypomnienia    :2026-11-27, 6d

    section Sprint 3
    Skarbonka i osiągnięcia        :2026-12-04, 4d
    Testy i poprawki               :2026-12-04, 7d
    Dokumentacja końcowa           :2026-12-01, 10d
```

## Pakiety zadań (WBS)

| Pakiet | Zadanie | Odpowiedzialny | Czas | Osoby zaangażowane |
|---|---|---|---|---|
| 1. Analiza | 1.1 Koncepcja funkcji aplikacji | Daria | 2 dni | Daria, Valentyn |
| | 1.2 Backlog i priorytety | Daria | 1 dzień | Daria, Valentyn |
| | 1.3 Specyfikacja wymagań (F/NF) | Daria | 2 dni | Daria, Filip |
| | 1.4 Makiety nowych ekranów (zatwierdzanie, limity) | Daria | 1 dzień | Daria, Valentyn |
| 2. Organizacja | 2.1 Zmiana tematu, kontakt z prowadzącym | Valentyn | 1 dzień | Valentyn |
| | 2.2 Role, repozytorium, plan sprintów | Valentyn | 1 dzień | Valentyn, Daria, Filip |
| 3. Aplikacja | 3.1 Pierwsza wersja: portfele, wydatki, podsumowanie | Valentyn | 3 dni | Valentyn, Claude |
| | 3.2 Baza danych pod użytkowników i wspólne portfele | Valentyn | 1,5 dnia | Valentyn, Claude |
| | 3.3 Logowanie i wdrożenie aplikacji na serwer | Filip | 2,5 dnia | Filip, Valentyn, Claude |
| | 3.4 Zatwierdzanie wydatków i limity | Valentyn | 3,5 dnia | Valentyn, Daria, Claude |
| | 3.5 AI: rozpoznawanie paragonów | Valentyn | 3 dni | Valentyn, Claude |
| | 3.6 Wykresy, subskrypcje | Valentyn | 2,5 dnia | Valentyn, Claude |
| | 3.7 Skarbonka, osiągnięcia | Valentyn | 2,5 dnia | Valentyn, Daria, Claude |
| 4. Jakość | 4.1 Przegląd interfejsu (ergonomia) | Filip | ciągle | Filip, Daria |
| | 4.2 Scenariusze testowe | Filip | 2 dni | Filip |
| | 4.3 Testy i zgłaszanie błędów | Filip | ciągle | Filip, Valentyn |
| 5. Dokumentacja | 5.1 Diagramy UML i architektura | Filip | 2 dni | Filip, Valentyn |
| | 5.2 Instrukcja użytkownika | Daria | 2 dni | Daria, Gemini |
| | 5.3 Instrukcja administratora, opis techniczny | Filip | 2 dni | Filip, Valentyn, Claude |
| | 5.4 Prezentacje na spotkania | Valentyn | co tydzień | wszyscy |

## Macierz RAM

**R** – odpowiedzialny, **C** – konsultowany, **I** – informowany.

| Zadanie | Valentyn | Daria | Filip |
|---|---|---|---|
| 1.1 Koncepcja funkcji | C | R | I |
| 1.2 Backlog i priorytety | C | R | I |
| 1.3 Specyfikacja wymagań | C | R | C |
| 1.4 Makiety nowych ekranów | C | R | I |
| 2.1 Zmiana tematu | R | I | I |
| 2.2 Role, repozytorium, plan | R | C | C |
| 3.1–3.2, 3.4–3.7 Aplikacja | R | C | I |
| 3.3 Logowanie i wdrożenie na serwer | C | I | R |
| 4.1 Przegląd interfejsu | I | C | R |
| 4.2 Scenariusze testowe | C | C | R |
| 4.3 Testy | C | I | R |
| 5.1 Diagramy UML | C | I | R |
| 5.2 Instrukcja użytkownika | I | R | C |
| 5.3 Instrukcja administratora, opis techniczny | C | I | R |
| 5.4 Prezentacje | R | C | C |

Narzędzia AI (Claude, Gemini) nie są osobami odpowiedzialnymi: wspierają zadania, a za wynik odpowiada osoba oznaczona literą R.
