"""
token_gen.py
------------
Generates cryptographically-secure session tokens.
"""

import secrets


def generate_token(nbytes: int = 48) -> str:
    """Return a URL-safe base64 token (~64 printable characters).

    The raw token is stored in the user's cookie.
    Only its argon2 hash is stored in the database.
    """
    return secrets.token_urlsafe(nbytes)
