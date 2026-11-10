"""F11: odczyt paragonu ze zdjęcia przez zewnętrzny model. Zdjęcie żyje tylko w pamięci (NF6).

Dostawca to funkcja (bajty, mime) -> tekst JSON; nowego dodaje się do PROVIDERS i wybiera zmienną RECEIPT_PROVIDER.
Klucz API tylko ze zmiennej środowiskowej (NF9).
"""
import base64
import json
import os
import re
import time
import urllib.request

import db
from budget import parse_amount

CATEGORIES = [name for name, _ in db.CATEGORIES]
MAX_BYTES = 5 * 1024 * 1024
TRANSIENT = (500, 502, 503, 504)  # HTTP: przeciążenie dostawcy; 429 (limit dzienny) nie ma sensu ponawiać
TRIES = 3
PROMPT = ("Odczytaj paragon ze zdjęcia. amount: kwota faktycznie zapłacona jako tekst, np. \"12,50\": pozycja \"DO ZAPŁATY\", a gdy jej nie ma, \"SUMA PLN\". "
          "date: data zakupu w formacie RRRR-MM-DD. shop: nazwa sklepu. "
          f"category: dokładnie jedna z: {', '.join(CATEGORIES)}. "
          "Gdy pola nie da się odczytać, zwróć pusty tekst.")
SCHEMA = {"type": "OBJECT",
          "properties": {"amount": {"type": "STRING"}, "date": {"type": "STRING"},
                         "shop": {"type": "STRING"}, "category": {"type": "STRING", "enum": CATEGORIES}},
          "required": ["amount", "date", "shop", "category"]}
# rozpoznanie po początku pliku, nie po nazwie ani nagłówku z przeglądarki
SIGNATURES = {b"\xff\xd8\xff": "image/jpeg", b"\x89PNG\r\n\x1a\n": "image/png"}


class ReceiptError(Exception):
    """Błąd odczytu; komunikat nadaje się do pokazania użytkownikowi."""


def receipt_amount(text):
    """'12,50 zł' / '1 234,00 PLN' -> grosze; None przy błędnej kwocie."""
    return parse_amount(re.sub(r"(?i)\s*(zł|pln)\s*$", "", text.strip()))


def image_mime(data):
    """'image/jpeg' lub 'image/png' po zawartości; None dla innych plików."""
    return next((mime for sig, mime in SIGNATURES.items() if data.startswith(sig)), None)


def gemini(image_bytes, mime):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ReceiptError("Odczyt paragonów nie jest skonfigurowany. Wpisz wydatek ręcznie.")
    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    body = {"contents": [{"parts": [
                {"inlineData": {"mimeType": mime, "data": base64.b64encode(image_bytes).decode()}},
                {"text": PROMPT}]}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": SCHEMA, "temperature": 0}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(TRIES):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp)["candidates"][0]["content"]["parts"][0]["text"]
        except (OSError, KeyError, IndexError, ValueError) as e:  # URLError i TimeoutError to OSError
            # przeciążenie (503) i przekroczenie czasu bywają chwilowe; inne błędy kończą od razu
            transient = isinstance(e, TimeoutError) or getattr(e, "code", None) in TRANSIENT
            if not transient or attempt == TRIES - 1:
                raise ReceiptError("Nie udało się odczytać paragonu. Wpisz wydatek ręcznie.") from e
            time.sleep(2 * (attempt + 1))


PROVIDERS = {"gemini": gemini}


def read_receipt(image_bytes, mime):
    """Słownik z surowymi polami amount, date, shop, category (teksty); walidację robi wywołujący."""
    provider = PROVIDERS[os.environ.get("RECEIPT_PROVIDER", "gemini")]
    text = provider(image_bytes, mime)
    try:
        data = json.loads(text)
    except (TypeError, ValueError) as e:
        raise ReceiptError("Model zwrócił nieczytelną odpowiedź. Wpisz wydatek ręcznie.") from e
    if not isinstance(data, dict):
        raise ReceiptError("Model zwrócił nieczytelną odpowiedź. Wpisz wydatek ręcznie.")
    return {k: str(data.get(k) or "") for k in ("amount", "date", "shop", "category")}
