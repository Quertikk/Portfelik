# Portfelik

Projekt zespołowy, Uniwersytet im. Adama Mickiewicza w Poznaniu, 2026/2027.

**Portfelik** to aplikacja webowa do prowadzenia budżetu osobistego i wspólnych wydatków (para, współlokatorzy, rodzina). Każdy użytkownik ma **portfel osobisty**, a grupa ma **portfel wspólny** z podsumowaniem, kto ile zapłacił. Większe wspólne wydatki wymagają zatwierdzenia przez drugą osobę, a AI pozwala dodać wydatek na podstawie zdjęcia paragonu.

## Zespół

| Osoba | Rola w Scrum | Zakres |
|---|---|---|
| Valentyn | Lider (ScrumMaster) | Organizacja pracy, kontakt z prowadzącym, backlog sprintu, architektura aplikacji i baza danych |
| Daria | Właściciel produktu | Wymagania i ich priorytety, koncepcja funkcji, akceptacja wykonanych zadań, instrukcja użytkownika |
| Filip Kellner | Zespół | Logowanie i wdrożenie na serwer, testy, scenariusze testowe, opis techniczny |

**Narzędzia AI wykorzystywane w projekcie**

| Narzędzie | Zastosowanie |
|---|---|
| Claude (Anthropic) | Asystent programisty: kod aplikacji, pomoc przy dokumentacji technicznej |
| Gemini (Google) | Grafiki i prezentacje; planowany model do rozpoznawania paragonów |

Za wynik pracy narzędzi AI odpowiadają członkowie zespołu: wygenerowany kod jest przeglądany i testowany przed włączeniem do projektu.

## Technologie

- Python 3 + Flask (serwer aplikacji)
- SQLite (baza danych, jeden plik)
- HTML + CSS (szablony Jinja2), interfejs dopasowany do telefonu i komputera

## Uruchomienie (Windows)

Wymagany Python 3.10 lub nowszy.

1. Pobierz repozytorium.
2. Uruchom `start.bat`. Skrypt zainstaluje Flask, uruchomi aplikację i otworzy przeglądarkę.
3. Aplikacja działa pod adresem http://127.0.0.1:5000

Przy pierwszym uruchomieniu tworzona jest baza `portfelik.db` z danymi demonstracyjnymi. Żeby zacząć od nowa, wystarczy usunąć ten plik. Bazę sprzed wprowadzenia logowania też trzeba usunąć, bo jej konta nie mają haseł.

Konta demonstracyjne (hasło `demo1234`): `valentyn@demo.pl`, `daria@demo.pl`, `filip@demo.pl`. Powstają tylko przy uruchomieniu lokalnym (`start.bat` lub `python app.py`). Na serwerze aplikacja startuje przez WSGI bez kont demonstracyjnych, a użytkownicy zakładają konta na stronie rejestracji.

Klucz sesji (`SECRET_KEY`) pochodzi ze zmiennej środowiskowej. Lokalnie aplikacja tworzy plik `secret_key.txt` (jest w `.gitignore`).

## Testy

```
pip install -r requirements.txt
pytest
```

## Struktura repozytorium

```
app.py            serwer i obsługa stron
auth.py           rejestracja, logowanie i wylogowanie
budget.py         limity kategorii i tryb Oszczędny
wsgi.py           punkt wejścia na serwerze (WSGI)
scripts/          kopia bazy danych (backup_db.py)
db.py             migracje bazy danych i dane demonstracyjne
tests/            testy automatyczne (pytest)
templates/        szablony stron (HTML)
static/           style (CSS)
docs/             dokumentacja projektu
start.bat         uruchomienie na Windows
requirements.txt  zależności Pythona
```

## Dokumentacja

| Dokument | Zawartość |
|---|---|
| [docs/koncepcja.md](docs/koncepcja.md) | Koncepcja, cele, zakres, ograniczenia |
| [docs/specyfikacja.md](docs/specyfikacja.md) | Specyfikacja wymagań: kryteria akceptacji, architektura |
| [docs/backlog.md](docs/backlog.md) | Zaległości produktowe: wymagania funkcjonalne i niefunkcjonalne, priorytety, szacunki |
| [docs/harmonogram.md](docs/harmonogram.md) | Sprinty, wykres Gantta, podział prac (WBS), macierz RAM |
| [docs/postepy.md](docs/postepy.md) | Dziennik postępów z cotygodniowych spotkań |
| [docs/testy.md](docs/testy.md) | Scenariusze testowe z odwołaniem do testów automatycznych |
| [docs/makiety.md](docs/makiety.md) | Makiety ekranów zatwierdzania (F8) i limitów (F10) do akceptacji Właściciela produktu |

## Status

Sprint 0 zakończony: działa pierwsza wersja (portfel osobisty i wspólny, dodawanie wydatków, podsumowanie miesiąca).
