"""Logika budżetu bez Flaska i bazy: limity kategorii i tryb Oszczędny (F10). Kwoty w groszach."""
import calendar
from datetime import date

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


def average(total, months):
    """F12: średnia miesięczna z sumy kilku miesięcy; None, gdy portfel nie ma jeszcze historii."""
    return round(total / months) if months else None


def due_soon(subs, today, days=2):
    """F13: subskrypcje płatne dziś lub w ciągu `days` dni jako (subskrypcja, data płatności).

    Dzień płatności dłuższy niż miesiąc (31 w lutym) przypada na ostatni dzień miesiąca.
    """
    result = []
    for sub in subs:
        for offset in (0, 1):  # ten miesiąc i następny: przełom miesiąca i roku
            i = today.year * 12 + today.month - 1 + offset
            year, month = i // 12, i % 12 + 1
            due = date(year, month, min(sub["day_of_month"], calendar.monthrange(year, month)[1]))
            if 0 <= (due - today).days <= days:
                result.append((sub, due))
                break
    return sorted(result, key=lambda r: r[1])


def settle(paid):
    """F17: równy podział wydatków. paid: {osoba: wydane grosze}, także 0 dla osób, które nic nie zapłaciły.

    Zwraca (salda, przelewy): saldo dodatnie to nadpłata, ujemne to dług, suma sald to 0;
    przelewy to lista (kto, komu, grosze) wyrównująca salda. Reszta z dzielenia (grosze) obciąża osoby,
    które zapłaciły najwięcej (przy remisie wg nazwy), więc wynik nie zależy od kolejności wejścia.
    """
    if not paid:
        return {}, []
    base, extra = divmod(sum(paid.values()), len(paid))
    order = sorted(paid, key=lambda p: (-paid[p], p))
    balance = {p: paid[p] - base - (i < extra) for i, p in enumerate(order)}
    debtors = sorted((p for p in balance if balance[p] < 0), key=lambda p: (balance[p], p))
    creditors = sorted((p for p in balance if balance[p] > 0), key=lambda p: (-balance[p], p))
    owed = {p: -balance[p] for p in debtors}
    due = {p: balance[p] for p in creditors}
    transfers = []
    while debtors and creditors:
        d, c = debtors[0], creditors[0]
        amount = min(owed[d], due[c])
        transfers.append((d, c, amount))
        owed[d] -= amount
        due[c] -= amount
        if not owed[d]:
            debtors.pop(0)
        if not due[c]:
            creditors.pop(0)
    return balance, transfers


def month_done(month, today):
    """F14/F15: miesiąc (pierwszy dzień) jest zakończony: minął albo dziś jest jego ostatni dzień."""
    first = today.replace(day=1)
    return month < first or (month == first and today.day == calendar.monthrange(today.year, today.month)[1])


def achievements(approved_expenses, limits, over, done, piggy):
    """F15: lista (nazwa, opis, zdobyte). Tylko zapisy w aplikacji, żadnych prawdziwych płatności.

    approved_expenses: liczba zatwierdzonych wydatków portfela; limits: liczba kategorii z limitem;
    over: liczba przekroczonych limitów w wybranym miesiącu; done: czy miesiąc się zakończył; piggy: saldo skarbonki.
    """
    return [
        ("Pierwszy krok", "Dodaj pierwszy zatwierdzony wydatek.", approved_expenses > 0),
        ("Zaplanowany budżet", "Ustaw limity w co najmniej 3 kategoriach.", limits >= 3),
        ("Pod kontrolą", "Zakończ wybrany miesiąc z limitami i bez przekroczenia żadnego.",
         done and limits > 0 and over == 0),
        ("Skarbnik", "Przenieś pierwsze pieniądze do skarbonki.", piggy > 0),
    ]


# F15: humorystyczne, wirtualne „kary” za przekroczony limit; kolejna kategoria dostaje kolejną karę
PENALTIES = ["Kawa dla całego mieszkania (na niby).", "Wyniesienie śmieci przez cały tydzień.",
             "Jeden dzień bez zamawiania jedzenia.", "Umycie naczyń po wszystkich.",
             "Dziesięć pompek przed następnym zakupem."]
