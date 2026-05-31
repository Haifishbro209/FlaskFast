"""
encoder.py
----------
Encodes / decodes a user's integer primary key into a URL-safe string.

Security model
~~~~~~~~~~~~~~
The raw integer is base62-encoded, then an HMAC-SHA256 signature
(truncated to 8 chars) is appended.  This means:

* An attacker cannot guess another user's encoded_id by incrementing a counter.
* Any tampering with the string is detected on decode.

The HMAC key is read from the environment variable ENCODING_SECRET.
Set it to any long random string in your .env file.

Usage
~~~~~
    from src.encoder import encode, decode

    uid  = encode(42)          # → e.g. "g_9e4f1a2b"
    orig = decode("g_9e4f1a2b") # → 42  (or raises ValueError on bad input)
"""

import hashlib
import hmac
import os

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_CHARS   = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_BASE    = len(_CHARS)          # 62
_SIG_LEN = 8                    # characters taken from the HMAC digest


def _secret() -> bytes:
    """Return the HMAC key as bytes.  Falls back to a hard-coded dev key so the
    app starts without .env, but logs a warning."""
    key = os.getenv("ENCODING_SECRET")
    if not key:
        import warnings
        warnings.warn(
            "ENCODING_SECRET is not set – using insecure default. "
            "Set it in your .env file before going to production.",
            stacklevel=3,
        )
        key = "dev-insecure-secret-change-me"
    return key.encode()


# ---------------------------------------------------------------------------
# Base-62 helpers
# ---------------------------------------------------------------------------
def _b62_encode(n: int) -> str:
    if n == 0:
        return _CHARS[0]
    s = []
    while n:
        n, r = divmod(n, _BASE)
        s.append(_CHARS[r])
    return "".join(reversed(s))


def _b62_decode(s: str) -> int:
    n = 0
    for c in s:
        idx = _CHARS.find(c)
        if idx == -1:
            raise ValueError(f"Invalid character in encoded id: {c!r}")
        n = n * _BASE + idx
    return n


# ---------------------------------------------------------------------------
# HMAC signature
# ---------------------------------------------------------------------------
def _sign(payload: str) -> str:
    sig = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    return sig[:_SIG_LEN]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def encode(user_id: int) -> str:
    """Return a signed, URL-safe string for *user_id*."""
    b62 = _b62_encode(user_id)
    sig  = _sign(b62)
    return f"{b62}_{sig}"


def decode(token: str) -> int:
    """Decode *token* back to an integer user id.

    Raises
    ------
    ValueError
        If the token is malformed or the signature does not match.
    """
    try:
        b62, sig = token.rsplit("_", 1)
    except ValueError:
        raise ValueError("Malformed encoded id")

    if not hmac.compare_digest(_sign(b62), sig):
        raise ValueError("Invalid encoded id signature")

    return _b62_decode(b62)
