"""Portfelik: aplikacja webowa do budżetu osobistego i wspólnych wydatków."""
import os
import secrets
from datetime import date

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

import db

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

MONTHS = ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec", "lipiec",
          "sierpień", "wrzesień", "październik", "listopad", "grudzień"]


@app.template_filter("zl")
def format_zl(grosze):
    zl, gr = divmod(int(grosze), 100)
    return f"{zl:,}".replace(",", " ") + f",{gr:02d} zł"


def parse_amount(text):
    """'12,50' / '12.5' / '12' -> 1250 groszy; None przy błędnej kwocie."""
    try:
        value = round(float(text.replace(" ", "").replace(",", ".")) * 100)
    except (AttributeError, ValueError):
        return None
    return value if 0 < value <= 100_000_000 else None


def parse_month(text):
    try:
        y, m = map(int, (text or "").split("-"))
        return date(y, m, 1)
    except ValueError:
        return date.today().replace(day=1)


def shift_month(d, delta):
    i = d.year * 12 + d.month - 1 + delta
    return date(i // 12, i % 12 + 1, 1)


@app.before_request
def load_user():
    g.conn = db.connect()
    g.users = g.conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    uid = session.get("user_id")
    g.user = next((u for u in g.users if u["id"] == uid), g.users[0])


@app.teardown_request
def close_db(exc):
    conn = g.pop("conn", None)
    if conn is not None:
        if exc is None:
            conn.commit()
        conn.close()


def get_wallet(kind):
    if kind == "personal":
        sql = "SELECT * FROM wallets WHERE kind = 'personal' AND owner_id = ?"
    elif kind == "shared":
        sql = ("SELECT w.* FROM wallets w JOIN wallet_members m ON m.wallet_id = w.id"
               " WHERE w.kind = 'shared' AND m.user_id = ? ORDER BY w.id")
    else:
        abort(404)
    wallet = g.conn.execute(sql, (g.user["id"],)).fetchone()
    if wallet is None:
        abort(404)
    return wallet


def month_total(wallet_id, month):
    return g.conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        " WHERE wallet_id = ? AND substr(spent_on, 1, 7) = ?",
        (wallet_id, month.strftime("%Y-%m"))).fetchone()[0]


@app.post("/user")
def switch_user():
    session["user_id"] = request.form.get("user_id", type=int)
    return redirect(request.referrer or url_for("index"))


@app.get("/")
def index():
    return redirect(url_for("wallet", kind="personal"))


@app.get("/portfel/<kind>")
def wallet(kind):
    w = get_wallet(kind)
    month = parse_month(request.args.get("m"))
    ym = month.strftime("%Y-%m")
    expenses = g.conn.execute(
        "SELECT e.*, c.name AS category, c.icon, u.name AS who FROM expenses e"
        " JOIN categories c ON c.id = e.category_id JOIN users u ON u.id = e.user_id"
        " WHERE e.wallet_id = ? AND substr(e.spent_on, 1, 7) = ?"
        " ORDER BY e.spent_on DESC, e.id DESC", (w["id"], ym)).fetchall()
    by_category = g.conn.execute(
        "SELECT c.name, c.icon, SUM(e.amount) AS total FROM expenses e"
        " JOIN categories c ON c.id = e.category_id"
        " WHERE e.wallet_id = ? AND substr(e.spent_on, 1, 7) = ?"
        " GROUP BY c.id ORDER BY total DESC", (w["id"], ym)).fetchall()
    by_person = g.conn.execute(
        "SELECT u.name, COALESCE(SUM(e.amount), 0) AS total FROM wallet_members m"
        " JOIN users u ON u.id = m.user_id"
        " LEFT JOIN expenses e ON e.user_id = u.id AND e.wallet_id = m.wallet_id"
        "   AND substr(e.spent_on, 1, 7) = ?"
        " WHERE m.wallet_id = ? GROUP BY u.id ORDER BY total DESC", (ym, w["id"])).fetchall()
    total = sum(e["amount"] for e in expenses)
    prev_total = month_total(w["id"], shift_month(month, -1))
    return render_template(
        "wallet.html", wallet=w, kind=kind, expenses=expenses, total=total,
        prev_total=prev_total, by_category=by_category, by_person=by_person,
        categories=g.conn.execute("SELECT * FROM categories ORDER BY id").fetchall(),
        month=month, month_name=f"{MONTHS[month.month - 1]} {month.year}",
        prev_m=shift_month(month, -1).strftime("%Y-%m"),
        next_m=shift_month(month, 1).strftime("%Y-%m"),
        today=date.today().isoformat())


@app.post("/portfel/<kind>/dodaj")
def add_expense(kind):
    w = get_wallet(kind)
    amount = parse_amount(request.form.get("amount"))
    category = request.form.get("category_id", type=int)
    spent_on = request.form.get("spent_on") or date.today().isoformat()
    description = (request.form.get("description") or "").strip()[:200]
    valid_cat = g.conn.execute("SELECT 1 FROM categories WHERE id = ?", (category,)).fetchone()
    try:
        date.fromisoformat(spent_on)
    except ValueError:
        spent_on = None
    if amount is None or not valid_cat or spent_on is None:
        flash("Podaj poprawną kwotę, kategorię i datę.", "error")
    else:
        g.conn.execute(
            "INSERT INTO expenses (wallet_id, user_id, category_id, amount, description, spent_on)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (w["id"], g.user["id"], category, amount, description, spent_on))
        flash("Wydatek dodany.", "ok")
    return redirect(url_for("wallet", kind=kind, m=(spent_on or "")[:7] or None))


@app.post("/wydatek/<int:expense_id>/usun")
def delete_expense(expense_id):
    deleted = g.conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, g.user["id"])).rowcount
    flash("Wydatek usunięty." if deleted else "Możesz usuwać tylko własne wydatki.",
          "ok" if deleted else "error")
    return redirect(request.referrer or url_for("index"))


db.init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Portfelik: http://127.0.0.1:{port}")  # ASCII: konsola Windows (cp1252)
    app.run(host="127.0.0.1", port=port)
