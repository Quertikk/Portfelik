"""Portfelik: aplikacja webowa do budżetu osobistego i wspólnych wydatków."""
import os
import secrets
from datetime import date
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect

import db
from auth import bp as auth_bp
from budget import limit_state, saver_mode


def load_secret_key():
    """SECRET_KEY ze środowiska (serwer); lokalnie z pliku w .gitignore, tworzonego przy pierwszym starcie."""
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    path = Path(__file__).with_name("secret_key.txt")
    if not path.exists():
        path.write_text(secrets.token_hex(32))
    return path.read_text().strip()


app = Flask(__name__)
app.secret_key = load_secret_key()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
CSRFProtect(app)
app.register_blueprint(auth_bp)

MONTHS = ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec", "lipiec",
          "sierpień", "wrzesień", "październik", "listopad", "grudzień"]
INVITE_DAYS = 7


@app.template_filter("zl")
def format_zl(grosze):
    zl, gr = divmod(int(grosze), 100)
    return f"{zl:,}".replace(",", " ") + f",{gr:02d} zł"


def parse_amount(text):
    """'12,50' / '12.5' / '12' -> 1250 groszy; None przy błędnej kwocie."""
    try:
        value = round(float(text.replace(" ", "").replace(",", ".")) * 100)
    except (AttributeError, ValueError, OverflowError):  # OverflowError: "inf", "1e999"
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


PUBLIC_ENDPOINTS = {"auth.login", "auth.register", "static"}


@app.before_request
def require_login():
    g.conn = db.connect()
    uid = session.get("user_id")
    g.user = uid and g.conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    if not g.user and request.endpoint not in PUBLIC_ENDPOINTS:
        return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))


@app.teardown_request
def close_db(exc):
    conn = g.pop("conn", None)
    if conn is not None:
        if exc is None:
            conn.commit()
        conn.close()


def user_wallets():
    """Portfele zalogowanego użytkownika: najpierw osobisty, potem wspólne."""
    return g.conn.execute(
        "SELECT w.* FROM wallets w JOIN wallet_members m ON m.wallet_id = w.id"
        " WHERE m.user_id = ? ORDER BY w.kind = 'shared', w.id", (g.user["id"],)).fetchall()


def get_wallet(wallet_id):
    """Portfel tylko dla członka; obcy portfel daje 404, jakby nie istniał (NF4)."""
    wallet = g.conn.execute(
        "SELECT w.* FROM wallets w JOIN wallet_members m ON m.wallet_id = w.id"
        " WHERE w.id = ? AND m.user_id = ?", (wallet_id, g.user["id"])).fetchone()
    if wallet is None:
        abort(404)
    return wallet


# F8: do sum wchodzą tylko zatwierdzone wydatki; każda suma używa tego warunku (alias e = expenses)
APPROVED = "e.status = 'approved'"


def month_total(wallet_id, month):
    return g.conn.execute(
        "SELECT COALESCE(SUM(e.amount), 0) FROM expenses e"
        f" WHERE e.wallet_id = ? AND substr(e.spent_on, 1, 7) = ? AND {APPROVED}",
        (wallet_id, month.strftime("%Y-%m"))).fetchone()[0]


def needs_approval(wallet, amount):
    return wallet["kind"] == "shared" and amount > wallet["approval_threshold"]


@app.get("/")
def index():
    wallets = user_wallets()
    if not wallets:
        abort(404)
    return redirect(url_for("wallet", wallet_id=wallets[0]["id"]))


@app.post("/portfele/nowy")
def new_wallet():
    name = (request.form.get("name") or "").strip()[:60]
    if not name:
        flash("Podaj nazwę portfela.", "error")
        return redirect(request.referrer or url_for("index"))
    wid = g.conn.execute("INSERT INTO wallets (name, kind, owner_id) VALUES (?, 'shared', ?)",
                         (name, g.user["id"])).lastrowid
    g.conn.execute("INSERT INTO wallet_members VALUES (?, ?)", (wid, g.user["id"]))
    flash("Portfel utworzony. Wyślij współlokatorom link zaproszenia.", "ok")
    return redirect(url_for("wallet", wallet_id=wid))


@app.post("/portfel/<int:wallet_id>/zaproszenie")
def invite(wallet_id):
    w = get_wallet(wallet_id)
    if w["kind"] != "shared":
        abort(404)
    g.conn.execute(
        "INSERT INTO invitations (wallet_id, code, expires_at) VALUES (?, ?, datetime('now', ?))",
        (w["id"], secrets.token_urlsafe(16), f"+{INVITE_DAYS} days"))
    flash(f"Nowy link zaproszenia jest ważny {INVITE_DAYS} dni.", "ok")
    return redirect(url_for("wallet", wallet_id=w["id"]))


@app.get("/dolacz/<code>")
def join(code):
    inv = g.conn.execute("SELECT wallet_id FROM invitations WHERE code = ? AND expires_at > datetime('now')",
                         (code,)).fetchone()
    if inv is None:
        flash("Zaproszenie wygasło lub jest nieprawidłowe. Poproś o nowy link.", "error")
        return redirect(url_for("index"))
    g.conn.execute("INSERT OR IGNORE INTO wallet_members VALUES (?, ?)", (inv["wallet_id"], g.user["id"]))
    flash("Dołączono do wspólnego portfela.", "ok")
    return redirect(url_for("wallet", wallet_id=inv["wallet_id"]))


@app.get("/portfel/<int:wallet_id>")
def wallet(wallet_id):
    w = get_wallet(wallet_id)
    month = parse_month(request.args.get("m"))
    ym = month.strftime("%Y-%m")
    expenses = g.conn.execute(
        "SELECT e.*, c.name AS category, c.icon, u.name AS who FROM expenses e"
        " JOIN categories c ON c.id = e.category_id JOIN users u ON u.id = e.user_id"
        " WHERE e.wallet_id = ? AND substr(e.spent_on, 1, 7) = ?"
        " ORDER BY e.spent_on DESC, e.id DESC", (w["id"], ym)).fetchall()
    # kategorie z wydatkami lub z limitem; lim to limit miesięczny albo NULL
    by_category = [dict(r, state=r["lim"] and limit_state(r["total"], r["lim"])) for r in g.conn.execute(
        "SELECT c.id, c.name, c.icon, COALESCE(s.total, 0) AS total, l.amount AS lim FROM categories c"
        " LEFT JOIN (SELECT e.category_id, SUM(e.amount) AS total FROM expenses e"
        f"   WHERE e.wallet_id = ? AND substr(e.spent_on, 1, 7) = ? AND {APPROVED}"
        "   GROUP BY e.category_id) s ON s.category_id = c.id"
        " LEFT JOIN category_limits l ON l.category_id = c.id AND l.wallet_id = ?"
        " WHERE s.total IS NOT NULL OR l.amount IS NOT NULL"
        " ORDER BY total DESC, c.id", (w["id"], ym, w["id"]))]
    limited = [c for c in by_category if c["lim"]]
    saver = month == date.today().replace(day=1) and saver_mode(
        sum(c["total"] for c in limited), sum(c["lim"] for c in limited), date.today())
    by_person = g.conn.execute(
        "SELECT u.name, COALESCE(SUM(e.amount), 0) AS total FROM wallet_members m"
        " JOIN users u ON u.id = m.user_id"
        " LEFT JOIN expenses e ON e.user_id = u.id AND e.wallet_id = m.wallet_id"
        f"   AND substr(e.spent_on, 1, 7) = ? AND {APPROVED}"
        " WHERE m.wallet_id = ? GROUP BY u.id ORDER BY total DESC", (ym, w["id"])).fetchall()
    pending = g.conn.execute(
        "SELECT e.*, c.name AS category, c.icon, u.name AS who FROM expenses e"
        " JOIN categories c ON c.id = e.category_id JOIN users u ON u.id = e.user_id"
        " WHERE e.wallet_id = ? AND e.status = 'pending' ORDER BY e.spent_on, e.id", (w["id"],)).fetchall()
    total = month_total(w["id"], month)
    prev_total = month_total(w["id"], shift_month(month, -1))
    invitation = w["kind"] == "shared" and g.conn.execute(
        "SELECT code, expires_at FROM invitations WHERE wallet_id = ? AND expires_at > datetime('now')"
        " ORDER BY id DESC LIMIT 1", (w["id"],)).fetchone()
    return render_template(
        "wallet.html", wallet=w, wallets=user_wallets(), invitation=invitation,
        expenses=expenses, pending=pending, total=total, saver=saver,
        limits={c["id"]: c["lim"] for c in limited},
        prev_total=prev_total, by_category=by_category, by_person=by_person,
        categories=g.conn.execute("SELECT * FROM categories ORDER BY id").fetchall(),
        month=month, month_name=f"{MONTHS[month.month - 1]} {month.year}",
        prev_m=shift_month(month, -1).strftime("%Y-%m"),
        next_m=shift_month(month, 1).strftime("%Y-%m"),
        today=date.today().isoformat())


@app.post("/portfel/<int:wallet_id>/dodaj")
def add_expense(wallet_id):
    w = get_wallet(wallet_id)
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
        status = "pending" if needs_approval(w, amount) else "approved"
        g.conn.execute(
            "INSERT INTO expenses (wallet_id, user_id, category_id, amount, description, spent_on, status)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (w["id"], g.user["id"], category, amount, description, spent_on, status))
        flash("Wydatek czeka na zatwierdzenie przez innego członka portfela." if status == "pending"
              else "Wydatek dodany.", "ok")
    return redirect(url_for("wallet", wallet_id=w["id"], m=(spent_on or "")[:7] or None))


def decide(expense_id, status):
    """Zatwierdza lub odrzuca oczekujący wydatek; decyduje członek portfela inny niż autor."""
    e = g.conn.execute(
        "SELECT e.* FROM expenses e JOIN wallet_members m ON m.wallet_id = e.wallet_id AND m.user_id = ?"
        " WHERE e.id = ?", (g.user["id"], expense_id)).fetchone()
    if e is None:
        abort(404)
    if e["user_id"] == g.user["id"]:
        flash("Własny wydatek musi zatwierdzić inny członek portfela.", "error")
    elif e["status"] != "pending":
        flash("Ten wydatek nie czeka już na decyzję.", "error")
    else:
        g.conn.execute(
            "UPDATE expenses SET status = ?, decided_by = ?, decided_at = datetime('now') WHERE id = ?",
            (status, g.user["id"], expense_id))
        flash("Wydatek zatwierdzony." if status == "approved" else "Wydatek odrzucony.", "ok")
    return redirect(request.referrer or url_for("wallet", wallet_id=e["wallet_id"]))


@app.post("/wydatek/<int:expense_id>/zatwierdz")
def approve_expense(expense_id):
    return decide(expense_id, "approved")


@app.post("/wydatek/<int:expense_id>/odrzuc")
def reject_expense(expense_id):
    return decide(expense_id, "rejected")


@app.post("/portfel/<int:wallet_id>/prog")
def set_threshold(wallet_id):
    w = get_wallet(wallet_id)
    if w["owner_id"] != g.user["id"]:
        abort(403)
    amount = parse_amount(request.form.get("threshold"))
    if amount is None:
        flash("Podaj poprawny próg, np. 200.", "error")
    else:
        g.conn.execute("UPDATE wallets SET approval_threshold = ? WHERE id = ?", (amount, w["id"]))
        flash("Próg zatwierdzania zapisany.", "ok")
    return redirect(url_for("wallet", wallet_id=w["id"]))


@app.post("/portfel/<int:wallet_id>/limity")
def set_limits(wallet_id):
    """Pole limit_<id kategorii>: puste usuwa limit, kwota go ustawia; błędna kwota nie zmienia limitu."""
    w = get_wallet(wallet_id)
    if w["owner_id"] != g.user["id"]:
        abort(403)
    invalid = []
    for c in g.conn.execute("SELECT id, name FROM categories ORDER BY id"):
        text = (request.form.get(f"limit_{c['id']}") or "").strip()
        amount = parse_amount(text)
        if not text:
            g.conn.execute("DELETE FROM category_limits WHERE wallet_id = ? AND category_id = ?", (w["id"], c["id"]))
        elif amount is None:
            invalid.append(c["name"])
        else:
            g.conn.execute(
                "INSERT INTO category_limits (wallet_id, category_id, amount) VALUES (?, ?, ?)"
                " ON CONFLICT (wallet_id, category_id) DO UPDATE SET amount = excluded.amount",
                (w["id"], c["id"], amount))
    if invalid:
        flash("Niepoprawna kwota limitu: " + ", ".join(invalid) + ". Pozostałe limity zapisane.", "error")
    else:
        flash("Limity zapisane.", "ok")
    return redirect(url_for("wallet", wallet_id=w["id"]))


@app.post("/wydatek/<int:expense_id>/usun")
def delete_expense(expense_id):
    deleted = g.conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, g.user["id"])).rowcount
    flash("Wydatek usunięty." if deleted else "Możesz usuwać tylko własne wydatki.",
          "ok" if deleted else "error")
    return redirect(request.referrer or url_for("index"))


db.init_db()

if __name__ == "__main__":  # tryb deweloperski; serwer importuje app przez WSGI i nie dostaje kont demo
    db.init_db(demo=True)
    port = int(os.environ.get("PORT", 5000))
    print(f"Portfelik: http://127.0.0.1:{port}")  # ASCII: konsola Windows (cp1252)
    app.run(host="127.0.0.1", port=port)
