from flask import Blueprint, request, render_template, redirect, url_for, session, flash
import os
import json
import hashlib
from config import config

USERS_DB = "users.json"

auth_bp = Blueprint("auth", __name__)

def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    if not require_auth:
        return redirect(url_for("core.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()

        # Accesso amministratore
        if username == config.ADMIN_USER and password == config.ADMIN_PASS:
            session["authenticated"] = True
            session["role"] = "admin"
            return redirect(url_for("admin.admin_dashboard", token=config.ADMIN_TOKEN))

        # Accesso utente registrato
        user = users.get(username)
        if user and user["password"] == hash_password(password):
            session["authenticated"] = True
            session["role"] = user.get("role", "user")
            return redirect(url_for("core.home"))

        flash("Credenziali errate", "error")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    if not require_auth:
        return redirect(url_for("core.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not password or not confirm:
            flash("Tutti i campi sono obbligatori", "error")
        elif password != confirm:
            flash("Le password non coincidono", "error")
        else:
            users = load_users()
            if username in users:
                flash("Utente già esistente", "error")
            else:
                users[username] = {
                    "password": hash_password(password),
                    "role": "user"
                }
                save_users(users)
                flash("Registrazione completata. Puoi accedere ora.", "success")
                return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))