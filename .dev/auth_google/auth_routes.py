"""
auth_routes.py  ·  Google OAuth
---------------------------------
Copy this file's content into app.py (or import it) after running init.py.
The init script pastes these routes automatically.

Also requires google_auth.py to be present at the project root.
"""

# --------------------------------------------------------------------------
# These imports are already present in app.py – listed here for clarity.
# from flask import request, redirect, url_for, make_response, flash
# from src.database import upsert_google_user, create_session
# from google_auth import get_authorization_url, handle_callback
# --------------------------------------------------------------------------


@app.route("/api/register")
@limiter.limit("20 per minute")
def register_api():
    """Google register – same OAuth flow as login."""
    return redirect(get_authorization_url())


@app.route("/api/login")
@limiter.limit("20 per minute")
def login_api():
    """Start Google OAuth login flow."""
    return redirect(get_authorization_url())


@app.route("/oauth2callback")
@limiter.limit("20 per minute")
def oauth2callback():
    """Google redirects here after the user approves."""
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
