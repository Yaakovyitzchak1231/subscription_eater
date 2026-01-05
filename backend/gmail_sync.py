import json
import logging
from datetime import datetime, timezone
from typing import Iterable, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from google.auth.exceptions import GoogleAuthError, RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import get_settings
from .database import SessionLocal
from .models import Account, EmailMessage
from .oauth import build_gmail_service

logger = logging.getLogger(__name__)

settings = get_settings()
_scheduler: Optional[BackgroundScheduler] = None


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
    """Sync messages for a single account with comprehensive error handling."""
    logger.info(f"Starting sync for account {account.email} (ID: {account.id})")

    try:
        token_info = json.loads(account.token_json)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse token JSON for account {account.email}: {e}")
        return

    try:
        credentials = Credentials.from_authorized_user_info(token_info)
        credentials.token = account.access_token
        credentials.refresh_token = account.refresh_token
        credentials.expiry = account.token_expiry

        service = build_gmail_service(credentials)
        query = settings.subscription_query
        message_ids: Iterable[dict] = []

        # Fetch message list with error handling
        try:
            response = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=50)
                .execute()
            )
        except HttpError as e:
            if e.resp.status == 401:
                logger.error(f"Authentication failed for {account.email}. Token may be expired or revoked.")
            elif e.resp.status == 403:
                logger.error(f"Permission denied for {account.email}. Check Gmail API scopes.")
            elif e.resp.status == 429:
                logger.warning(f"Rate limit exceeded for {account.email}. Will retry on next sync.")
            else:
                logger.error(f"Gmail API error for {account.email}: {e.resp.status} - {e}")
            return
        except (GoogleAuthError, RefreshError) as e:
            logger.error(f"OAuth error for {account.email}: {e}")
            return
        except Exception as e:
            logger.error(f"Unexpected error listing messages for {account.email}: {e}")
            return

        if not response:
            logger.info(f"No response from Gmail API for {account.email}")
            return

        message_ids = response.get("messages", [])
        logger.info(f"Found {len(message_ids)} messages to process for {account.email}")

        # Process messages with individual error handling
        processed_count = 0
        error_count = 0

        for message_info in message_ids:
            try:
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
                processed_count += 1

            except HttpError as e:
                error_count += 1
                logger.warning(f"Failed to fetch message {message_info['id']} for {account.email}: {e.resp.status}")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing message {message_info['id']} for {account.email}: {e}")
                continue

        # Update account metadata and commit
        try:
            account.access_token = credentials.token
            account.token_json = credentials.to_json()
            account.token_expiry = credentials.expiry
            account.last_synced_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Sync completed for {account.email}: {processed_count} messages processed, {error_count} errors")
        except SQLAlchemyError as e:
            logger.error(f"Database error committing sync for {account.email}: {e}")
            db.rollback()
            raise

    except Exception as e:
        logger.error(f"Unexpected error syncing account {account.email}: {e}")
        db.rollback()
        raise


def sync_all_accounts() -> None:
    """Sync all accounts with error isolation - failures in one account don't affect others."""
    db = SessionLocal()
    try:
        accounts = db.query(Account).all()
        logger.info(f"Starting sync for {len(accounts)} account(s)")

        success_count = 0
        error_count = 0

        for account in accounts:
            try:
                sync_account_messages(db, account)
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Critical error syncing account {account.email}: {e}", exc_info=True)
                # Continue to next account - don't let one failure stop all syncs
                continue

        logger.info(f"Sync batch completed: {success_count} successful, {error_count} failed")

    except Exception as e:
        logger.error(f"Critical error in sync_all_accounts: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """Start the background scheduler for periodic Gmail syncs."""
    global _scheduler
    if _scheduler:
        logger.info("Scheduler already running")
        return _scheduler

    logger.info(f"Starting background scheduler with {settings.sync_interval_minutes} minute interval")
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(sync_all_accounts, "interval", minutes=settings.sync_interval_minutes, id="gmail-sync")
    scheduler.start()
    _scheduler = scheduler
    logger.info("Background scheduler started successfully")
    return scheduler


def shutdown_scheduler() -> None:
    """Shutdown the background scheduler gracefully."""
    global _scheduler
    if _scheduler:
        logger.info("Shutting down background scheduler...")
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Background scheduler stopped")


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
