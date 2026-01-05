from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .config import get_settings

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

_state_store: Dict[str, datetime] = {}
_STATE_TTL_MINUTES = 15


def _build_flow(state: str | None = None) -> Flow:
    settings = get_settings()
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.oauth_redirect_uri],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=GMAIL_SCOPES, state=state)
    flow.redirect_uri = settings.oauth_redirect_uri
    return flow


def generate_authorization_url() -> Tuple[str, str]:
    flow = _build_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    _state_store[state] = datetime.now(timezone.utc) + timedelta(minutes=_STATE_TTL_MINUTES)
    return authorization_url, state


def exchange_code_for_credentials(code: str, state: str) -> Credentials:
    expiry = _state_store.get(state)
    if not expiry or expiry < datetime.now(timezone.utc):
        raise ValueError("Invalid or expired OAuth state")

    flow = _build_flow(state=state)
    flow.fetch_token(code=code)
    _state_store.pop(state, None)
    credentials: Credentials = flow.credentials
    if not credentials.refresh_token:
        raise ValueError("Missing refresh token from Google; ensure consent screen requests offline access")
    return credentials


def build_gmail_service(credentials: Credentials):
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)
