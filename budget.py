"""Logika budżetu bez Flaska i bazy: limity kategorii i tryb Oszczędny (F10). Kwoty w groszach."""
import calendar

WARN_PERCENT = 80


def limit_state(spent, limit):
    """'ok', 'warn' od 80% limitu, 'over' po przekroczeniu limitu."""
    if spent > limit:
        return "over"
    if spent * 100 >= limit * WARN_PERCENT:
        return "warn"
    return "ok"


def saver_mode(spent_total, limits_total, today):
    """Tryb Oszczędny: wydano ponad 80% sumy limitów, a miesiąc jeszcze trwa (przed jego ostatnim dniem).

    Definicja do potwierdzenia przez Właściciela produktu (specyfikacja, F10).
    """
    if limits_total <= 0:
        return False
    last_day = calendar.monthrange(today.year, today.month)[1]
    return spent_total * 100 > limits_total * WARN_PERCENT and today.day < last_day
