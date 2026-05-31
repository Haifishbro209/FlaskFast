"""
pwd_hasher.py
-------------
Thin wrapper around argon2-cffi.

Used for:
  * hashing user passwords (username auth)
  * hashing session tokens before storing in the DB

Both use the same hasher so the same verify() call works for both.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

_ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
#  ↑  OWASP 2023 recommended minimum for argon2id


def hash_value(plaintext: str) -> str:
    """Return an argon2id hash of *plaintext*."""
    return _ph.hash(plaintext)


def verify(plaintext: str, hashed: str) -> bool:
    """Return True if *plaintext* matches *hashed*, False otherwise.

    Never raises – invalid / mismatched hashes both return False.
    """
    try:
        return _ph.verify(hashed, plaintext)
    except (VerifyMismatchError, InvalidHashError, Exception):
        return False
