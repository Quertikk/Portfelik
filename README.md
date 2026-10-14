# BoxForFriend

Projekt zespołowy, Uniwersytet im. Adama Mickiewicza w Poznaniu, semestr zimowy 2026/2027.

**BoxForFriend** to para małych urządzeń stojących na biurku. Jedno stoi u nas, drugie u bliskiej osoby (partnera, przyjaciela, rodziców) w innym mieszkaniu lub mieście. Wysyłamy z telefonu zdjęcie lub krótką wiadomość, a po kilku sekundach pojawia się ona na ekranie urządzenia drugiej osoby.

Celem nie jest kolejny komunikator, tylko **fizyczna obecność**: wiadomość nie ginie wśród powiadomień w telefonie, tylko stoi na biurku i jest widoczna.

## Zespół

| Osoba | Rola | Zakres odpowiedzialności |
|---|---|---|
| Valentyn | Lider zespołu, Product Owner | Wizja produktu, decyzje projektowe, elektronika i montaż, kontakt z podwykonawcą, prezentacja postępów |
| Daria | Scrum Master | Harmonogram i tablica zadań, projekt obudowy (model 3D), schematy i diagramy, testy, instrukcja użytkownika |

**Podwykonawca zewnętrzny**

| Osoba | Zakres |
|---|---|
| Aleksander | Druk 3D obudowy na podstawie modelu przygotowanego przez zespół |

**Narzędzia AI wykorzystywane w projekcie**

| Narzędzie | Zastosowanie |
|---|---|
| Claude (Anthropic) | Asystent programisty: kod urządzenia i serwera, konfiguracja serwera, pomoc przy dokumentacji technicznej |
| Gemini (Google) | Wizualizacje koncepcyjne urządzenia, grafiki do instrukcji i prezentacji |

Za wynik pracy narzędzi AI odpowiadają członkowie zespołu: każdy wygenerowany fragment jest sprawdzany i testowany przed włączeniem do projektu.

## Metodyka pracy

Pracujemy w uproszczonym modelu **Scrum**:

- sprint trwa jeden tydzień (od czwartku do czwartku),
- na cotygodniowym spotkaniu z prowadzącym przedstawiamy wykonane prace i plan na kolejny tydzień,
- zadania prowadzimy w repozytorium GitHub (Issues / Projects),
- postępy zapisujemy w [docs/postepy.md](docs/postepy.md).

## Dokumentacja

| Dokument | Zawartość |
|---|---|
| [docs/koncepcja.md](docs/koncepcja.md) | Koncepcja projektu, cele, otwarte problemy do rozwiązania |
| [docs/harmonogram.md](docs/harmonogram.md) | Harmonogram (wykres Gantta), podział prac, macierz RAM |
| [docs/postepy.md](docs/postepy.md) | Dziennik postępów z kolejnych spotkań |

Kolejne dokumenty (specyfikacja wymagań, schematy, diagramy, scenariusze testowe, instrukcje) będą dodawane w trakcie realizacji projektu.

## Planowana struktura repozytorium

```
docs/       dokumentacja projektu
firmware/   oprogramowanie urządzenia (ESP32-C3)
server/     oprogramowanie serwera
hardware/   schematy elektryczne, lista części
case/       model 3D obudowy
```

## Status

Etap: **analiza i koncepcja** (sprint 1).
