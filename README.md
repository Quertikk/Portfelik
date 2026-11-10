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

Odczyt paragonów ze zdjęcia wymaga klucza API Gemini w zmiennej `GEMINI_API_KEY` (opcjonalnie `GEMINI_MODEL`). Bez klucza reszta aplikacji działa, a formularz paragonu pokazuje komunikat o braku konfiguracji.

## Testy

```
pip install -r requirements.txt
pytest
python scripts/perf_check.py   # NF7: 1000 wydatków, limit 1 s
```

Testy działają też w GitHub Actions przy każdym Pull Requeście.

## Struktura repozytorium

```
app.py            serwer i obsługa stron
auth.py           rejestracja, logowanie i wylogowanie
budget.py         limity, tryb Oszczędny, średnia, subskrypcje, rozliczenie
receipts.py       odczyt paragonu przez model AI (Gemini)
wsgi.py           punkt wejścia na serwerze (WSGI)
scripts/          kopia bazy (backup_db.py), próbka paragonów (receipt_spike.py), pomiar wydajności (perf_check.py)
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
| [docs/uml.md](docs/uml.md) | Diagramy UML: przypadki użycia, sekwencja odczytu paragonu, stany wydatku |
| [docs/opis-techniczny.md](docs/opis-techniczny.md) | Opis powykonawczy: pliki, trasy, baza, zmienne środowiskowe, bezpieczeństwo, wydajność |
| [docs/instrukcja-uzytkownika.md](docs/instrukcja-uzytkownika.md) | Instrukcja użytkownika |
| [docs/instrukcja-administratora.md](docs/instrukcja-administratora.md) | Instalacja, wdrożenie na PythonAnywhere, zmienne środowiskowe, kopia i przywracanie bazy, aktualizacja |
| [docs/wytyczne.md](docs/wytyczne.md) | Lista kontrolna 15 punktów wytycznych prowadzącego ze stanem realizacji |
| [docs/makiety.md](docs/makiety.md) | Makiety ekranów zatwierdzania (F8) i limitów (F10) do akceptacji Właściciela produktu |

## Status

Sprinty 0–2 zakończone, sprint 3 (jakość i dokumentacja) w toku, zamrożenie funkcji 08.12, oddanie 11.12.2026.

| Obszar | Stan |
|---|---|
| Konta i portfele | Rejestracja, logowanie, portfel osobisty i wspólny z zaproszeniami (F6, F7) |
| Wydatki | Dodawanie, edycja, komentarz, usuwanie, zatwierdzanie powyżej progu, limity i tryb Oszczędny (F1–F5, F8–F10, F19) |
| Analiza | Podsumowanie miesiąca, średnia z 3 miesięcy, rozliczenie, eksport CSV (F3, F12, F17, F18) |
| AI | Dodanie wydatku ze zdjęcia paragonu przez Gemini (F11); test akceptacyjny 8 z 10 paragonów jeszcze do wykonania |
| Subskrypcje | Lista z przypomnieniem 2 dni przed płatnością (F13) |
| Nie zrobione | Skarbonka (F14) i osiągnięcia (F15): opcjonalne, niski priorytet; Telegram (F16) poza zakresem |
| Jakość | 232 testy automatyczne, pokrycie `app.py`, `auth.py`, `budget.py`, `receipts.py` powyżej 95%, ładowanie portfela z 1000 wydatków w ok. 30 ms |
