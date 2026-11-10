"""F14 skarbonka, F15 osiągnięcia i wirtualne kary."""
from datetime import date

import db
from app import shift_month
from budget import achievements, month_done
from conftest import WALLET, query

MINE = WALLET["Filip"]
THIS = date.today().replace(day=1)
PREV = shift_month(THIS, -1)


def seed(month, rows, limits=()):
    """rows: (kwota w groszach, kategoria); limits: (kategoria, kwota w groszach) w portfelu Filipa."""
    with db.connect() as conn:
        for cents, cat in rows:
            conn.execute("INSERT INTO expenses (wallet_id, user_id, category_id, amount, spent_on)"
                         " VALUES (?, 3, ?, ?, ?)", (MINE, cat, cents, month.isoformat()))
        for cat, cents in limits:
            conn.execute("INSERT INTO category_limits VALUES (?, ?, ?)", (MINE, cat, cents))


def move(client, month):
    return client.post(f"/portfel/{MINE}/skarbonka?m={month:%Y-%m}", follow_redirects=True).get_data(as_text=True)


# --- budget.py ---------------------------------------------------------------------------------------

def test_month_done():
    assert month_done(date(2026, 10, 1), date(2026, 11, 10))
    assert not month_done(date(2026, 11, 1), date(2026, 11, 29))
    assert month_done(date(2026, 11, 1), date(2026, 11, 30))  # ostatni dzień miesiąca
    assert not month_done(date(2026, 12, 1), date(2026, 11, 30))


def test_achievements_earned_flags():
    assert [a[2] for a in achievements(0, 0, 0, False, 0)] == [False] * 4
    assert [a[2] for a in achievements(1, 3, 0, True, 500)] == [True] * 4
    assert not achievements(1, 3, 1, True, 0)[2][2]  # przekroczony limit blokuje „Pod kontrolą”
    assert not achievements(1, 0, 0, True, 0)[2][2]  # bez limitów nie ma czego kontrolować


# --- F14 ---------------------------------------------------------------------------------------------

def test_piggy_moves_roundups_and_unspent_limits_once(client):
    seed(PREV, [(1250, 1), (1000, 1)], limits=[(1, 10000)])  # zaokrąglenie 0,50 zł + niewydane 77,50 zł
    assert "razem <strong>78,00 zł</strong>" in client.get(f"/portfel/{MINE}?m={PREV:%Y-%m}").get_data(as_text=True)
    assert "Do skarbonki przeniesiono 78,00 zł" in move(client, PREV)
    assert query("SELECT amount FROM piggy_deposits WHERE wallet_id = ?", MINE)[0][0] == 7800
    assert "już przeniesiony" in move(client, PREV)
    assert len(query("SELECT * FROM piggy_deposits")) == 1
    assert "78,00 zł" in client.get(f"/portfel/{MINE}").get_data(as_text=True)  # saldo widać też w bieżącym miesiącu


def test_piggy_nothing_to_move_when_limit_overspent(client):
    seed(PREV, [(5000, 1)], limits=[(1, 3000)])  # limit przekroczony: reszta 0, zaokrąglenie 0
    assert "Nie ma teraz nic do przeniesienia" in move(client, PREV)
    assert query("SELECT * FROM piggy_deposits") == []


def test_piggy_refuses_unfinished_month(client):
    seed(shift_month(THIS, 1), [(1250, 1)])
    assert "Nie ma teraz nic do przeniesienia" in move(client, shift_month(THIS, 1))
    assert query("SELECT * FROM piggy_deposits") == []


def test_piggy_only_for_wallet_member(client):
    assert client.post(f"/portfel/{WALLET['Daria']}/skarbonka?m={PREV:%Y-%m}").status_code == 404


# --- F15 ---------------------------------------------------------------------------------------------

def test_first_achievement_earned_with_demo_expense(client):
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "🏆 Pierwszy krok" in html and "🔒 Skarbnik" in html


def test_all_achievements_after_clean_month_with_piggy(client):
    seed(PREV, [(1250, 1)], limits=[(1, 10000), (2, 10000), (3, 10000)])
    move(client, PREV)
    html = client.get(f"/portfel/{MINE}?m={PREV:%Y-%m}").get_data(as_text=True)
    assert html.count("🏆") == 4 and "Wirtualna kara" not in html


def test_virtual_penalty_for_exceeded_limit(client):
    seed(THIS, [], limits=[(6, 10000)])  # demo: Filip wydał 199 zł na Zakupy
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "Limit „Zakupy” przekroczony. Wirtualna kara:" in html
