from datetime import datetime, timezone
from typing import List
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, engine, get_db
from .gmail_sync import shutdown_scheduler, start_scheduler, subscription_summary, sync_all_accounts
from .models import Account, Subscription
from .oauth import exchange_code_for_credentials, generate_authorization_url
from .schemas import AccountResponse, AccountSummary, AuthorizationUrlResponse, SubscriptionEntry, SubscriptionResponse

settings = get_settings()

app = FastAPI(title="Subscription Eater Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    shutdown_scheduler()


# API Routes
@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/auth/google/start", response_model=AuthorizationUrlResponse)
def auth_start() -> AuthorizationUrlResponse:
    authorization_url, state = generate_authorization_url()
    return AuthorizationUrlResponse(authorization_url=authorization_url, state=state)


@app.get("/api/auth/google/callback")
def auth_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    try:
        credentials = exchange_code_for_credentials(code, state)
    except ValueError as exc:  # includes invalid state or missing refresh token
        return RedirectResponse(url=f"/?auth=error&message={str(exc)}", status_code=302)

    try:
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress")

        if not email:
            return RedirectResponse(url="/?auth=error&message=Unable to resolve account email", status_code=302)

        account = db.query(Account).filter(Account.email == email).one_or_none()

        if account:
            account.access_token = credentials.token
            account.refresh_token = credentials.refresh_token
            account.token_json = credentials.to_json()
            account.token_expiry = credentials.expiry
            account.updated_at = datetime.now(timezone.utc)
        else:
            account = Account(
                email=email,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_json=credentials.to_json(),
                token_expiry=credentials.expiry,
            )
            db.add(account)

        db.commit()
        
        # Redirect back to dashboard with success message
        return RedirectResponse(url=f"/?auth=success&email={email}", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/?auth=error&message={str(e)}", status_code=302)


@app.get("/api/accounts", response_model=AccountSummary)
def list_accounts(db: Session = Depends(get_db)):
    accounts: List[Account] = db.query(Account).order_by(Account.email).all()
    summary_rows = subscription_summary(db)
    subscription_entries = [
        SubscriptionEntry(
            account_id=row.account_id,
            account_email=row.account_email,
            from_address=row.from_address,
            message_count=row.message_count,
            last_seen=row.last_seen,
        )
        for row in summary_rows
    ]
    return AccountSummary(accounts=accounts, subscription_entries=subscription_entries)


@app.get("/api/subscriptions", response_model=List[SubscriptionResponse])
def list_subscriptions(db: Session = Depends(get_db)):
    subs = db.query(Subscription).join(Account).all()

    # Enrich with metadata that isn't directly on Subscription model (via relationships)
    response = []
    for sub in subs:
        resp = SubscriptionResponse.from_orm(sub)
        resp.account_email = sub.account.email
        if sub.source_email:
            resp.source_email_subject = sub.source_email.subject
            resp.source_email_from = sub.source_email.from_address
        response.append(resp)

    return response


@app.post("/api/sync", status_code=202)
def trigger_sync():
    sync_all_accounts()
    return {"status": "sync-started"}


# Serve dashboard HTML for root path
@app.get("/")
def serve_dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"error": "Dashboard not found"}


@app.get("/{full_path:path}")
def serve_static(full_path: str):
    """Serve static files and fallback to index.html for SPA routes"""
    file_path = os.path.join(os.path.dirname(__file__), "..", full_path)
    
    # Only serve files that actually exist
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise serve index.html for SPA routing
    html_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    
    return {"error": "Not found"}
