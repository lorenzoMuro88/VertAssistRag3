from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import json
import hashlib

auth_bp = Blueprint("auth", __name__)

USERS_DB = "users.json"

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

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
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

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()

        if username == os.getenv("ADMIN_USER") and password == os.getenv("ADMIN_PASS"):
            session["authenticated"] = True
            session["role"] = "admin"
            return redirect(url_for("admin"))

        user = users.get(username)
        if user and user["password"] == hash_password(password):
            session["authenticated"] = True
            session["role"] = user["role"]
            return redirect(url_for("core.home"))

        flash("Credenziali errate", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))