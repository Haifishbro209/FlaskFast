import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = 'http://localhost:8080/oauth2callback'  # Full callback URL


SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def init_oauth_flow():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return authorization_url

def handle_oauth_callback(code):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    
    flow.fetch_token(code=code)
    
    credentials = flow.credentials

    print(get_user_info(credentials))
    return credentials

def get_user_info(credentials):
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    return user_info
