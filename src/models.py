from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True)
    encoded_id  = Column(String, nullable=False, default="")

    # --- filled by google auth ---
    google_id   = Column(String, unique=True, nullable=True)
    first_name  = Column(String, nullable=True)
    last_name   = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # --- filled by username auth ---
    username    = Column(String, unique=True, nullable=True)
    pwd_hash    = Column(String, nullable=True)          # argon2 hash

    # shared
    email       = Column(String, unique=True, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    sessions    = relationship("Session_Cookie", back_populates="user",
                               cascade="all, delete-orphan")


class Session_Cookie(Base):
    __tablename__ = "session_cookies"

    # stored value is the argon2-hash of the raw token
    token_hash  = Column(String(650), primary_key=True, nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    expiry      = Column(DateTime, nullable=False)
    ip_address  = Column(String(46),  nullable=True)
    user_agent  = Column(String(512), nullable=True)

    user        = relationship("User", back_populates="sessions")
