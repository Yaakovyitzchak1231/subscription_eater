import json
from datetime import datetime, timezone
from typing import Iterable, Optional
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2.credentials import Credentials
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import get_settings
from .database import SessionLocal
from .models import Account, EmailMessage
from .oauth import build_gmail_service

settings = get_settings()
_scheduler: Optional[BackgroundScheduler] = None

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


SUBSCRIPTION_KEYWORDS = [
    "unsubscribe",
    "subscription",
    "receipt",
    "billing",
    "newsletter",
]


def _header_value(headers: list[dict], name: str) -> Optional[str]:
    for header in headers:
        if header.get("name") == name:
            return header.get("value")
    return None


def _upsert_message(
    db: Session,
    account_id: int,
    message_id: str,
    thread_id: Optional[str],
    subject: Optional[str],
    from_address: Optional[str],
    snippet: Optional[str],
    internal_date: Optional[datetime],
    keyword: Optional[str],
    history_id: Optional[str],
):
    existing = (
        db.query(EmailMessage)
        .filter(EmailMessage.account_id == account_id, EmailMessage.gmail_message_id == message_id)
        .one_or_none()
    )
    if existing:
        existing.subject = subject
        existing.from_address = from_address
        existing.snippet = snippet
        existing.internal_date = internal_date
        existing.subscription_keyword = keyword or existing.subscription_keyword
        existing.thread_id = thread_id
        existing.history_id = history_id
        return

    db.add(
        EmailMessage(
            account_id=account_id,
            gmail_message_id=message_id,
            thread_id=thread_id,
            subject=subject,
            from_address=from_address,
            snippet=snippet,
            internal_date=internal_date,
            subscription_keyword=keyword,
            history_id=history_id,
        )
    )


def _keyword_for_message(subject: Optional[str], snippet: Optional[str]) -> Optional[str]:
    combined = f"{subject or ''} {snippet or ''}".lower()
    for keyword in SUBSCRIPTION_KEYWORDS:
        if keyword in combined:
            return keyword
    return None


def sync_account_messages(db: Session, account: Account) -> None:
    logger.info(f"🔄 Starting sync for account: {account.email}")
    
    token_info = json.loads(account.token_json)
    credentials = Credentials.from_authorized_user_info(token_info)
    
    # Update the token if it's different
    if credentials.token != account.access_token:
        credentials.token = account.access_token
    
    # The refresh_token should be in the token_json already, but ensure expiry is set
    if account.token_expiry:
        credentials.expiry = account.token_expiry

    service = build_gmail_service(credentials)
    query = settings.subscription_query
    message_ids: Iterable[dict] = []

    logger.info(f"📧 Searching for emails with query: {query}")
    
    response = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=50)
        .execute()
    )
    if not response:
        logger.info("No emails found")
        return
    message_ids = response.get("messages", [])
    logger.info(f"Found {len(message_ids)} emails matching the query")

    processed = 0
    for idx, message_info in enumerate(message_ids, 1):
        logger.info(f"Processing email {idx}/{len(message_ids)}: {message_info['id']}")
        
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_info["id"], format="metadata", metadataHeaders=["Subject", "From"])
            .execute()
        )
        headers = message.get("payload", {}).get("headers", [])
        subject = _header_value(headers, "Subject")
        from_address = _header_value(headers, "From")
        snippet = message.get("snippet")
        internal_date_ms = message.get("internalDate")
        internal_date = None
        if internal_date_ms:
            internal_date = datetime.fromtimestamp(int(internal_date_ms) / 1000, tz=timezone.utc)
        keyword = _keyword_for_message(subject, snippet)

        _upsert_message(
            db=db,
            account_id=account.id,
            message_id=message.get("id"),
            thread_id=message.get("threadId"),
            subject=subject,
            from_address=from_address,
            snippet=snippet,
            internal_date=internal_date,
            keyword=keyword,
            history_id=message.get("historyId"),
        )

    account.access_token = credentials.token
    account.token_json = credentials.to_json()
    account.token_expiry = credentials.expiry
    account.last_synced_at = datetime.now(timezone.utc)
    db.commit()
    logger.info(f"✅ Sync completed for {account.email}")


def sync_all_accounts() -> None:
    logger.info("=" * 50)
    logger.info("🚀 Starting gmail sync for all accounts")
    db = SessionLocal()
    try:
        accounts = db.query(Account).all()
        logger.info(f"Found {len(accounts)} account(s) to sync")
        for account in accounts:
            sync_account_messages(db, account)
        logger.info("✨ All accounts synced successfully!")
    except Exception as e:
        logger.error(f"❌ Error during sync: {e}", exc_info=True)
    finally:
        db.close()
    logger.info("=" * 50)


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(sync_all_accounts, "interval", minutes=settings.sync_interval_minutes, id="gmail-sync")
    scheduler.start()
    _scheduler = scheduler
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def subscription_summary(db: Session):
    results = (
        db.query(
            EmailMessage.account_id,
            Account.email.label("account_email"),
            EmailMessage.from_address,
            func.count(EmailMessage.id).label("message_count"),
            func.max(EmailMessage.internal_date).label("last_seen"),
        )
        .join(Account, EmailMessage.account_id == Account.id)
        .group_by(EmailMessage.account_id, Account.email, EmailMessage.from_address)
        .order_by(func.max(EmailMessage.internal_date).desc())
        .all()
    )
    return results
