"""F11: próbka odczytu paragonu przez Gemini. Jedno wywołanie modelu na zdjęcie, wynik porównany z arkuszem.

Uruchomienie:
    export GEMINI_API_KEY=...            # PowerShell: $env:GEMINI_API_KEY = "..."
    python scripts/receipt_spike.py <katalog_ze_zdjęciami> [arkusz.csv]

Arkusz (domyślnie <katalog>/prawda.csv, UTF-8, nagłówek): plik,kwota,data,sklep
Zdjęcia i arkusz trzymaj poza repozytorium (dane zakupów). Model zmienisz zmienną GEMINI_MODEL.
"""
import csv
import json
import mimetypes
import os
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import receipts  # noqa: E402
from receipts import CATEGORIES, SCHEMA  # noqa: E402,F401  (SCHEMA i CATEGORIES sprawdza test)

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")


def grosze(text):
    """'12,50' / '12.5 zł' -> 1250; None przy błędnej kwocie."""
    try:
        return round(float(str(text).lower().replace("zł", "").replace("pln", "").replace(" ", "").replace(",", ".")) * 100)
    except ValueError:
        return None


def describe(cause):
    """Przyczyna błędu z API: dla HTTPError kod i początek odpowiedzi Google (bez klucza)."""
    if isinstance(cause, urllib.error.HTTPError):
        return f"HTTP {cause.code}: {cause.read().decode('utf-8', 'replace')[:400]!r}"
    return repr(cause)


def check(result, truth):
    """Porównanie z arkuszem: kwota co do grosza, data co do dnia, sklep bez rozróżniania wielkości liter."""
    return {"amount": grosze(result.get("amount")) == grosze(truth["kwota"]),
            "date": result.get("date") == truth["data"],
            "shop": truth["sklep"].strip().lower() in result.get("shop", "").lower()}


def main(folder, sheet):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("Brak zmiennej GEMINI_API_KEY.")
    with open(sheet, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    correct = 0
    for row in rows:
        try:
            path = folder / row["plik"]
            result = json.loads(receipts.gemini(path.read_bytes(), mimetypes.guess_type(path)[0] or "image/jpeg"))
        except (receipts.ReceiptError, json.JSONDecodeError, OSError) as e:
            print(f"{row['plik']}: BŁĄD {e!r}")
            print(f"    przyczyna: {describe(e.__cause__)}")  # ogólny komunikat ReceiptError ukrywa, co poszło nie tak
            if getattr(e.__cause__, "code", None) == 429:  # limit zapytań: kolejne próby tylko go zużywają
                print("Limit zapytań wyczerpany, przerywam. Spróbuj później albo z innym modelem (GEMINI_MODEL).")
                break
            continue
        ok = check(result, row)
        correct += ok["amount"]
        flags = " ".join(f"{k}={'OK' if v else 'ZLE'}" for k, v in ok.items())
        print(f"{row['plik']}: {flags} | model: {result} | arkusz: {row['kwota']} {row['data']} {row['sklep']}")
    print(f"Poprawne kwoty: {correct} z {len(rows)} (cel: 8 z 10), model {MODEL}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1])
    main(folder, Path(sys.argv[2]) if len(sys.argv) > 2 else folder / "prawda.csv")
