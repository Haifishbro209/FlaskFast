"""
auth_decorator.py
-----------------
Provides the @require_auth decorator.

How it works
~~~~~~~~~~~~
1. Every protected route has an ``encoded_id`` URL parameter, e.g.
       /home/<encoded_id>
2. The decorator decodes the encoded_id to get the real user_id.
3. It reads the raw session token from the ``token`` cookie.
4. It verifies the token against the DB (argon2 comparison).
5. On success it stores the user_id in Flask's ``g`` object so route
   handlers can do ``g.user_id`` without repeating the lookup.
6. On failure it always redirects to /login (no 401 JSON – this is a
   browser-first template).

Security notes
~~~~~~~~~~~~~~
* The encoded_id is HMAC-signed (see encoder.py), so it cannot be
  guessed or tampered with.
* The raw token is never stored in the DB – only its argon2 hash is.
* hmac.compare_digest is used inside verify() so timing attacks are
  not possible.
"""

from functools import wraps

from flask import g, redirect, request, url_for

from src.encoder import decode as decode_id
from src.database import verify_session, get_user_by_id


def require_auth(func):
    """Decorator for routes that require a logged-in user.

    The wrapped route **must** accept ``encoded_id`` as a URL parameter.

    Example
    -------
    @app.route("/home/<encoded_id>")
    @require_auth
    def home(encoded_id):
        user = g.user          # User ORM object
        user_id = g.user_id    # integer
        ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        encoded_id = kwargs.get("encoded_id") or request.view_args.get("encoded_id")

        # --- 1. decode the URL parameter ---
        try:
            user_id = decode_id(encoded_id)
        except (ValueError, TypeError):
            return redirect(url_for("login_page"))

        # --- 2. read cookie ---
        raw_token = request.cookies.get("token")
        if not raw_token:
            return redirect(url_for("login_page"))

        # --- 3. verify against DB ---
        if not verify_session(raw_token, user_id):
            return redirect(url_for("login_page"))

        # --- 4. attach to request context ---
        user = get_user_by_id(user_id)
        if not user:
            return redirect(url_for("login_page"))

        g.user_id = user_id
        g.user    = user

        return func(*args, **kwargs)

    return wrapper
