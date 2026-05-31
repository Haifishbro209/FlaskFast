"""
google_auth.py
--------------
Google OAuth2 helpers.  Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
in the environment (set by init.py).

REDIRECT_URI must match what you registered in the Google Cloud Console.
For local dev: http://localhost:8080/oauth2callback
For production: https://yourdomain.com/oauth2callback
"""

import os

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

load_dotenv()

_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/oauth2callback")

_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def _build_flow() -> Flow:
    client_config = {
        "web": {
            "client_id":     _CLIENT_ID,
            "client_secret": _CLIENT_SECRET,
            "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
            "token_uri":     "https://oauth2.googleapis.com/token",
            "redirect_uris": [_REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=_SCOPES)
    flow.redirect_uri = _REDIRECT_URI
    return flow


def get_authorization_url() -> str:
    """Return the Google OAuth authorization URL to redirect the user to."""
    flow = _build_flow()
    url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )
    return url


def handle_callback(code: str) -> dict:
    """Exchange *code* for user info.

    Returns a dict with keys:
        google_id, email, first_name, last_name, picture
    """
    flow = _build_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials

    service   = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()

    return {
        "google_id":  user_info.get("id"),
        "email":      user_info.get("email"),
        "first_name": user_info.get("given_name"),
        "last_name":  user_info.get("family_name"),
        "picture":    user_info.get("picture"),
    }
