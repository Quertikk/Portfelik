"""F6: rejestracja, logowanie i wylogowanie."""
import sqlite3

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import db
import throttle

bp = Blueprint("auth", __name__)

MIN_PASSWORD = 8
MAX_PASSWORD = 128  # dłuższe hasło tylko wydłuża kosztowne liczenie skrótu
LOGIN_TRIES, LOGIN_WINDOW = 10, 900  # nieudane próby na adres e-mail w 15 minut


def safe_next(url):
    """Przekierowanie po logowaniu tylko w obrębie aplikacji (bez open redirect)."""
    # isprintable: tabulator w "/<TAB>/evil.com" zamieniał się w nagłówku w "//evil.com", a nowa linia dawała błąd 500
    if url and url.startswith("/") and not url.startswith(("//", "/\\")) and url.isprintable():
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
    elif not MIN_PASSWORD <= len(password) <= MAX_PASSWORD:
        flash(f"Hasło musi mieć od {MIN_PASSWORD} do {MAX_PASSWORD} znaków.", "error")
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
    email = (request.form.get("email") or "").strip().lower()[:254]
    next_url = request.form.get("next", "")
    if throttle.count(email, LOGIN_WINDOW) >= LOGIN_TRIES:
        flash("Zbyt wiele nieudanych prób logowania. Spróbuj za kilkanaście minut.", "error")
        return render_template("login.html", next=next_url, email=email), 429
    user = g.conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    # skrót liczymy także dla nieznanego e-maila, by czas odpowiedzi nie zdradzał, czy konto istnieje
    if check_password_hash(user["password_hash"] if user else db.demo_hash(), request.form.get("password") or "") and user:
        log_in(user["id"])
        return redirect(safe_next(next_url))
    throttle.add(email)
    flash("Nieprawidłowy e-mail lub hasło.", "error")  # celowo bez wskazania, które pole jest złe
    return render_template("login.html", next=next_url, email=email), 401


@bp.post("/wyloguj")
def logout():
    session.clear()
    flash("Wylogowano.", "ok")
    return redirect(url_for("auth.login"))
