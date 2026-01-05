from datetime import datetime, timezone
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, engine, get_db
from .gmail_sync import shutdown_scheduler, start_scheduler, subscription_summary, sync_all_accounts
from .models import Account
from .oauth import exchange_code_for_credentials, generate_authorization_url
from .schemas import AccountResponse, AccountSummary, AuthorizationUrlResponse, SubscriptionEntry

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


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/auth/google/start", response_model=AuthorizationUrlResponse)
def auth_start() -> AuthorizationUrlResponse:
    authorization_url, state = generate_authorization_url()
    return AuthorizationUrlResponse(authorization_url=authorization_url, state=state)


@app.get("/auth/google/callback", response_model=AccountResponse)
def auth_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    try:
        credentials = exchange_code_for_credentials(code, state)
    except ValueError as exc:  # includes invalid state or missing refresh token
        raise HTTPException(status_code=400, detail=str(exc))

    service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
    profile = service.users().getProfile(userId="me").execute()
    email = profile.get("emailAddress")

    if not email:
        raise HTTPException(status_code=400, detail="Unable to resolve account email from Google")

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
    db.refresh(account)
    return AccountResponse.from_orm(account)


@app.get("/accounts", response_model=AccountSummary)
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


@app.post("/sync", status_code=202)
def trigger_sync():
    sync_all_accounts()
    return {"status": "sync-started"}
