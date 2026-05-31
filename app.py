import os

from dotenv import load_dotenv
from flask import Flask, make_response, redirect, render_template, request, url_for, flash, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# src imports
from src.auth_decorator import require_auth
from src.database import (
    create_session,
    create_user_username,
    delete_session,
    upsert_google_user,
    verify_user_password,
)

# ── optional Google auth (only present when init.py copied it) ──────────────
try:
    from google_auth import get_authorization_url, handle_callback
    _GOOGLE_AVAILABLE = True
except ImportError:
    _GOOGLE_AVAILABLE = False

# ---------------------------------------------------------------------------
load_dotenv()

SESSION_LENGTH = int(os.getenv("SESSION_LENGTH", 7))   # days

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],          # no global limit – applied per route
    storage_uri=os.getenv("LIMITER_STORAGE_URI", "memory://"),
)

# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def landingpage():
    return render_template("landingpage.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/home/<encoded_id>")
@require_auth
def home(encoded_id):
    return render_template("home.html", user=g.user)


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@app.route("/logout")
def logout():
    raw_token = request.cookies.get("token")
    if raw_token and hasattr(g, "user_id"):
        delete_session(raw_token, g.user_id)

    response = make_response(redirect(url_for("login_page")))
    response.delete_cookie("token")
    return response


# ---------------------------------------------------------------------------
# Auth routes  ← inserted here by init.py
# ---------------------------------------------------------------------------

# FASTFLASK_AUTH_ROUTES_PLACEHOLDER


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
