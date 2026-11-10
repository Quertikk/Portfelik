"""Limit prób w oknie czasu (logowanie, odczyt paragonu), w pamięci procesu.

ponytail: przy kilku procesach serwera każdy liczy osobno; przy większym ruchu użyj Redis albo Flask-Limiter.
"""
import time
from collections import defaultdict, deque

_hits = defaultdict(deque)


def count(key, window):
    """Liczba prób klucza z ostatnich `window` sekund."""
    hits = _hits[key]
    while hits and hits[0] < time.monotonic() - window:
        hits.popleft()
    if not hits:
        del _hits[key]
    return len(hits)


def add(key):
    if len(_hits) > 10_000:  # ogranicza pamięć przy zalewie kluczy; koszt: chwilowe wyzerowanie limitów
        _hits.clear()
    _hits[key].append(time.monotonic())
