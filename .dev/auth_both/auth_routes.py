"""
auth_routes.py  ·  username + password  AND  Google OAuth
-----------------------------------------------------------
Copy this file's content into app.py (or import it) after running init.py.
The init script pastes these routes automatically.
"""

# --------------------------------------------------------------------------
# These imports are already present in app.py – listed here for clarity.
# from flask import request, redirect, url_for, make_response, flash
# from src.database import (create_user_username, verify_user_password,
#                            upsert_google_user, create_session)
# from google_auth import get_authorization_url, handle_callback
# --------------------------------------------------------------------------


# ── username / password ────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
@limiter.limit("5 per minute")
def register_api():
    username  = request.form.get("username", "").strip()
    password  = request.form.get("password", "")
    password2 = request.form.get("password2", "")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("register_page"))

    if password != password2:
        flash("Passwords do not match.", "error")
        return redirect(url_for("register_page"))

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("register_page"))

    try:
        user = create_user_username(username, password)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("register_page"))

    return _login_response(user)


@app.route("/api/login", methods=["POST"])
@limiter.limit("10 per minute")
def login_api():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = verify_user_password(username, password)
    if not user:
        flash("Invalid username or password.", "error")
        return redirect(url_for("login_page"))

    return _login_response(user)


# ── Google OAuth ────────────────────────────────────────────────────────────

@app.route("/api/register/google")
@limiter.limit("20 per minute")
def register_google():
    return redirect(get_authorization_url())


@app.route("/api/login/google")
@limiter.limit("20 per minute")
def login_google():
    return redirect(get_authorization_url())


@app.route("/oauth2callback")
@limiter.limit("20 per minute")
def oauth2callback():
    code = request.args.get("code")
    if not code:
        flash("Google authentication failed.", "error")
        return redirect(url_for("login_page"))

    try:
        info = handle_callback(code)
    except Exception:
        flash("Google authentication failed.", "error")
        return redirect(url_for("login_page"))

    user = upsert_google_user(
        google_id  = info["google_id"],
        email      = info["email"],
        first_name = info["first_name"],
        last_name  = info["last_name"],
        picture    = info["picture"],
    )
    return _login_response(user)


# ── shared helper ───────────────────────────────────────────────────────────

def _login_response(user):
    raw_token = create_session(
        user_id=user.id,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        days=SESSION_LENGTH,
    )
    response = make_response(redirect(url_for("home", encoded_id=user.encoded_id)))
    response.set_cookie(
        "token", raw_token,
        httponly=True,
        samesite="Lax",
        secure=False,   # ← set True in production (HTTPS)
        max_age=SESSION_LENGTH * 86400,
    )
    return response
