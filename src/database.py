"""
database.py
-----------
All database operations for FastFlask.

Keeps SQLAlchemy session management in one place so app.py stays clean.
Every public function opens its own session and closes it in a finally-block.
"""

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, User, Session_Cookie
from src.encoder import encode as encode_id
from src.pwd_hasher import hash_value, verify
from src.token_gen import generate_token

# ---------------------------------------------------------------------------
# Engine / Session factory  (created once at import time)
# ---------------------------------------------------------------------------
_DB_URL = os.getenv("DB_URL")
if not _DB_URL:
    raise RuntimeError("DB_URL environment variable is not set.")

engine = create_engine(
    _DB_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
)

Base.metadata.create_all(engine)
_Session = sessionmaker(bind=engine)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _new_session():
    return _Session()


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def get_user_by_id(user_id: int) -> User | None:
    s = _new_session()
    try:
        return s.query(User).filter(User.id == user_id).first()
    finally:
        s.close()


def get_user_by_encoded_id(encoded_id: str) -> User | None:
    s = _new_session()
    try:
        return s.query(User).filter(User.encoded_id == encoded_id).first()
    finally:
        s.close()


# ---------------------------------------------------------------------------
# Username + password auth
# ---------------------------------------------------------------------------

def create_user_username(username: str, password: str) -> User:
    """Create a new user with username/password.  Raises ValueError if the
    username is already taken."""
    s = _new_session()
    try:
        if s.query(User).filter(User.username == username).first():
            raise ValueError("Username already taken.")
        user = User(username=username, pwd_hash=hash_value(password))
        s.add(user)
        s.flush()
        user.encoded_id = encode_id(user.id)
        s.commit()
        s.refresh(user)
        return user
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def verify_user_password(username: str, password: str) -> User | None:
    """Return the User if credentials are correct, else None."""
    s = _new_session()
    try:
        user = s.query(User).filter(User.username == username).first()
        if user and verify(password, user.pwd_hash or ""):
            return user
        return None
    finally:
        s.close()


# ---------------------------------------------------------------------------
# Google OAuth auth
# ---------------------------------------------------------------------------

def upsert_google_user(google_id: str, email: str,
                       first_name: str | None = None,
                       last_name:  str | None = None,
                       picture:    str | None = None) -> User:
    """Create or update a user that authenticated via Google."""
    s = _new_session()
    try:
        user = s.query(User).filter(User.google_id == google_id).first()
        if user:
            # update mutable fields on every login
            user.email         = email
            user.first_name    = first_name
            user.last_name     = last_name
            user.profile_picture = picture
        else:
            user = User(
                google_id=google_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                profile_picture=picture,
            )
            s.add(user)
            s.flush()
            user.encoded_id = encode_id(user.id)
        s.commit()
        s.refresh(user)
        return user
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


# ---------------------------------------------------------------------------
# Session / token management
# ---------------------------------------------------------------------------

def create_session(user_id: int, ip: str | None,
                   user_agent: str | None,
                   days: int = 7) -> str:
    """Generate a token, hash it, store the hash, return the raw token."""
    raw_token  = generate_token()
    token_hash = hash_value(raw_token)
    expiry     = datetime.utcnow() + timedelta(days=days)

    s = _new_session()
    try:
        cookie = Session_Cookie(
            token_hash=token_hash,
            user_id=user_id,
            expiry=expiry,
            ip_address=ip,
            user_agent=user_agent,
        )
        s.add(cookie)
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()

    return raw_token   # only time the raw token leaves this module


def verify_session(raw_token: str, user_id: int) -> bool:
    """Return True if *raw_token* is valid and not expired for *user_id*."""
    s = _new_session()
    try:
        now     = datetime.utcnow()
        cookies = (
            s.query(Session_Cookie)
             .filter(
                 Session_Cookie.user_id == user_id,
                 Session_Cookie.expiry  >  now,
             )
             .all()
        )
        return any(verify(raw_token, c.token_hash) for c in cookies)
    finally:
        s.close()


def delete_session(raw_token: str, user_id: int) -> None:
    """Invalidate a specific session (logout)."""
    s = _new_session()
    try:
        now     = datetime.utcnow()
        cookies = (
            s.query(Session_Cookie)
             .filter(
                 Session_Cookie.user_id == user_id,
                 Session_Cookie.expiry  >  now,
             )
             .all()
        )
        for c in cookies:
            if verify(raw_token, c.token_hash):
                s.delete(c)
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def cleanup_expired_sessions() -> int:
    """Delete all expired sessions.  Returns number of rows deleted."""
    s = _new_session()
    try:
        n = (
            s.query(Session_Cookie)
             .filter(Session_Cookie.expiry <= datetime.utcnow())
             .delete()
        )
        s.commit()
        return n
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
