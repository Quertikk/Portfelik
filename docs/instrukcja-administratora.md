# Instrukcja administratora

Dla osoby, która uruchamia Portfelika lokalnie albo na serwerze. Opis plików, tras i tabel: [opis-techniczny.md](opis-techniczny.md). Scenariusze testowe: [testy.md](testy.md).

## 1. Wymagania

- Python 3.10 lub nowszy (na serwerze PythonAnywhere używamy tej samej wersji w środowisku wirtualnym i w zakładce Web).
- Pakiety z `requirements.txt`: Flask, Flask-WTF, pytest.
- Baza SQLite nie wymaga osobnej instalacji. To jeden plik `portfelik.db` obok `app.py`.

## 2. Uruchomienie lokalne (Windows)

1. Pobierz repozytorium.
2. Uruchom `start.bat`. Skrypt instaluje zależności, otwiera przeglądarkę i startuje `python app.py`.
3. Aplikacja działa pod adresem http://127.0.0.1:5000. Inny port ustawia zmienna `PORT`.

Przy pierwszym starcie powstaje `portfelik.db` z kontami demonstracyjnymi: `valentyn@demo.pl`, `daria@demo.pl`, `filip@demo.pl`, hasło `demo1234`. Żeby zacząć od nowa, usuń `portfelik.db` przy zatrzymanej aplikacji.

Klucz sesji powstaje w pliku `secret_key.txt` (jest w `.gitignore`). Usunięcie pliku wyloguje wszystkich.

## 3. Zmienne środowiskowe

| Zmienna | Znaczenie | Domyślnie |
|---|---|---|
| `SECRET_KEY` | Klucz podpisujący sesje. Na serwerze obowiązkowa: bez niej każdy restart losowałby inny klucz z pliku i zrywał sesje | lokalnie plik `secret_key.txt` |
| `GEMINI_API_KEY` | Klucz API do odczytu paragonów. Bez niego reszta aplikacji działa, a formularz paragonu pokazuje komunikat o braku konfiguracji | brak |
| `GEMINI_MODEL` | Model Gemini | `gemini-3.5-flash-lite` |
| `RECEIPT_PROVIDER` | Dostawca odczytu paragonów (klucz w `receipts.PROVIDERS`) | `gemini` |
| `PORT` | Port trybu deweloperskiego (`python app.py`) | `5000` |

Kluczy nie wpisujemy do repozytorium. Na serwerze ustawia się je w pliku WSGI (punkt 4.2), który leży poza repozytorium.

## 4. Wdrożenie na PythonAnywhere

Konto założone ręcznie, adres aplikacji `https://<login>.pythonanywhere.com`. Wdrożona wersja: `bilib.pythonanywhere.com`.

### 4.1. Kod i środowisko

W konsoli Bash:

```bash
git clone https://github.com/Quertikk/Portfelik.git
cd Portfelik && git checkout main
mkvirtualenv --python=python3.13 portfelik   # najnowszy Python z listy konta
pip install -r requirements.txt
```

W zakładce Web: „Add a new web app”, „Manual configuration” i ta sama wersja Pythona (gotowa konfiguracja Flask nadpisuje plik WSGI). Ustaw:

| Pole | Wartość |
|---|---|
| Source code | `/home/<login>/Portfelik` |
| Virtualenv | `/home/<login>/.virtualenvs/portfelik` |
| Static files | URL `/static/`, katalog `/home/<login>/Portfelik/static` |

### 4.2. Plik WSGI i klucze

Wygeneruj klucz sesji: `python -c "import secrets; print(secrets.token_hex(32))"`. Zawartość pliku WSGI z zakładki Web (`/var/www/<login>_pythonanywhere_com_wsgi.py`) zamień na:

```python
import os
import sys

path = "/home/<login>/Portfelik"
if path not in sys.path:
    sys.path.insert(0, path)
os.environ["SECRET_KEY"] = "<wygenerowany klucz>"
os.environ["GEMINI_API_KEY"] = "<klucz API Gemini>"  # opcjonalnie, dla odczytu paragonów

from wsgi import application  # noqa: E402,F401
```

Klucz sesji musi pozostać ten sam po restarcie, inaczej sesje się zerwą. Kliknij „Reload”. Serwer startuje bez kont demonstracyjnych, więc pierwsze konto zakłada się na stronie `/rejestracja`.

### 4.3. HTTPS

Zakładka Web, sekcja „Security”: włącz „Force HTTPS”. Certyfikat dla `*.pythonanywhere.com` jest w cenie konta. Ciasteczko sesji ma flagę `Secure`, więc bez HTTPS logowanie nie zadziała: przeglądarka nie odeśle ciasteczka przez zwykłe http.

### 4.4. Dostęp do API modelu AI

Darmowe konto wpuszcza ruch wychodzący tylko do domen z listy dozwolonych. Sprawdzenie w konsoli Bash:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://generativelanguage.googleapis.com/
```

Kod HTTP (np. 404) oznacza, że połączenie przeszło. Błąd proxy lub „403 Forbidden” od proxy oznacza blokadę: wtedy trzeba prosić o dopisanie domeny albo zmienić hosting.

### 4.5. Ważność aplikacji

Darmowa aplikacja wygasa po 3 miesiącach bez kliknięcia „Run until 3 months from today” w zakładce Web.

## 5. Kopia i przywracanie bazy (NF11)

### 5.1. Kopia

`scripts/backup_db.py` robi spójną kopię przez API `sqlite3` (to samo co `.backup`), więc jest bezpieczna przy działającej aplikacji. Kopie trafiają do katalogu `backups/` (lub podanego w argumencie), zostaje 14 najnowszych.

```bash
python scripts/backup_db.py [katalog_docelowy]
```

Na serwerze: zakładka Tasks, zadanie dzienne (darmowe konto ma jedno), np. o 03:00 UTC:

```
/home/<login>/.virtualenvs/portfelik/bin/python /home/<login>/Portfelik/scripts/backup_db.py /home/<login>/backups
```

Przed każdym wdrożeniem uruchom to samo polecenie ręcznie.

### 5.2. Przywracanie

1. Zakładka Web: „Disable” (zatrzymanie aplikacji).
2. W konsoli: `cp ~/backups/portfelik-<data>.db ~/Portfelik/portfelik.db`.
3. Zakładka Web: „Enable” i „Reload”.

Przywrócenie nadpisuje bieżące dane danymi z kopii, więc wcześniej zrób kopię aktualnej bazy. Próbę przywrócenia wykonano 10.11.2026 (TC-NF11-03).

## 6. Aktualizacja do nowej wersji

```bash
cd ~/Portfelik
~/.virtualenvs/portfelik/bin/python scripts/backup_db.py ~/backups   # kopia przed wdrożeniem
git pull
workon portfelik && pip install -r requirements.txt
```

Potem „Reload” w zakładce Web. Migracje bazy stosują się same przy starcie (`db.init_db`, wersja w `PRAGMA user_version`). Migracji nie edytuje się wstecznie, nowe zmiany schematu dopisuje się na końcu listy `MIGRATIONS` w `db.py`.

## 7. Testy i kontrola jakości

```bash
pip install -r requirements.txt
pytest
python scripts/perf_check.py        # NF7: 1000 wydatków, limit 1 s
python scripts/receipt_spike.py <katalog_ze_zdjeciami>   # F11: próbka odczytu paragonów
```

`pytest` uruchamia się też w GitHub Actions przy każdym Pull Requeście i pushu na `main` (`.github/workflows/tests.yml`).

Test dymny po wdrożeniu: zaloguj się, dodaj wydatek, kliknij „Reload” w zakładce Web, odśwież stronę. Wydatek ma zostać, a sesja trwać.

## 8. Rozwiązywanie problemów

| Objaw | Przyczyna i działanie |
|---|---|
| Po każdym restarcie wylogowanie | Brak `SECRET_KEY` w pliku WSGI. Ustaw stały klucz (punkt 4.2) |
| „Odczyt paragonów nie jest skonfigurowany” | Brak `GEMINI_API_KEY`. Ustaw zmienną i kliknij „Reload” |
| „Nie udało się odczytać paragonu” mimo klucza | Domena API zablokowana (punkt 4.4), błędny klucz albo limit zapytań |
| HTTP 404 „model is no longer available” (widać w `scripts/receipt_spike.py`) | Google wycofał model. Ustaw nowy w zmiennej `GEMINI_MODEL` (nazwa z komunikatu błędu lub z AI Studio) i kliknij „Reload”. Domyślny model to `gemini-3.5-flash-lite` |
| Aplikacja nie startuje po aktualizacji | Zakładka Web, link „Error log”; zwykle brakuje pakietu: `pip install -r requirements.txt` |
| `OperationalError: database is locked` | Dwa procesy zapisują naraz. SQLite wystarcza dla małej grupy użytkowników; przy dużym ruchu przejdź na PostgreSQL |
| Po zalogowaniu strona wraca do logowania | Adres zaczyna się od `http://`. Wejdź przez `https://` i włącz „Force HTTPS” (punkt 4.3) |
| Logowanie zwraca 429 | Ponad 10 nieudanych prób na jeden e-mail w 15 minut. Poczekaj albo kliknij „Reload”, bo liczniki są w pamięci procesu |
| Stara baza bez haseł (sprzed F6) | Usuń `portfelik.db`, bo konta z wersji 0.1 nie mają haseł |
