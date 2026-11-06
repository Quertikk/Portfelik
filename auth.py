"""F6: rejestracja, logowanie i wylogowanie."""
import sqlite3

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__)

MIN_PASSWORD = 8


def safe_next(url):
    """Przekierowanie po logowaniu tylko w obrębie aplikacji (bez open redirect)."""
    if url and url.startswith("/") and not url.startswith(("//", "/\\")):
        return url
    return url_for("index")


def log_in(user_id):
    session.clear()  # nowa sesja po zalogowaniu
    session["user_id"] = user_id


@bp.route("/rejestracja", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", next=request.args.get("next", ""))
    name = (request.form.get("name") or "").strip()[:50]
    email = (request.form.get("email") or "").strip().lower()[:254]
    password = request.form.get("password") or ""
    if not name or "@" not in email:
        flash("Podaj nazwę i poprawny adres e-mail.", "error")
    elif len(password) < MIN_PASSWORD:
        flash(f"Hasło musi mieć co najmniej {MIN_PASSWORD} znaków.", "error")
    else:
        try:
            uid = g.conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))).lastrowid
        except sqlite3.IntegrityError:
            flash("Ta nazwa lub ten e-mail są już zajęte.", "error")
        else:
            wid = g.conn.execute(
                "INSERT INTO wallets (name, kind, owner_id) VALUES (?, 'personal', ?)",
                (f"Portfel: {name}", uid)).lastrowid
            g.conn.execute("INSERT INTO wallet_members VALUES (?, ?)", (wid, uid))
            log_in(uid)
            flash("Konto założone. Witaj w Portfeliku!", "ok")
            return redirect(safe_next(request.form.get("next")))
    return render_template("register.html", next=request.form.get("next", ""),
                           name=name, email=email), 400


@bp.route("/logowanie", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", next=request.args.get("next", ""))
    email = (request.form.get("email") or "").strip().lower()
    user = g.conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user and check_password_hash(user["password_hash"], request.form.get("password") or ""):
        log_in(user["id"])
        return redirect(safe_next(request.form.get("next")))
    flash("Nieprawidłowy e-mail lub hasło.", "error")  # celowo bez wskazania, które pole jest złe
    return render_template("login.html", next=request.form.get("next", ""), email=email), 401


@bp.post("/wyloguj")
def logout():
    session.clear()
    flash("Wylogowano.", "ok")
    return redirect(url_for("auth.login"))
