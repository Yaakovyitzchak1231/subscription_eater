import json
import base64
from datetime import datetime, timezone
from typing import Iterable, Optional
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from google.oauth2.credentials import Credentials
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import get_settings
from .database import SessionLocal
from .models import Account, EmailMessage, Subscription
from .oauth import build_gmail_service
from .parser import SubscriptionParser

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

def _extract_body(payload: dict) -> str:
    """Extracts plain text body from Gmail payload."""
    body_text = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    body_text += base64.urlsafe_b64decode(data).decode("utf-8")
    elif "body" in payload and payload["body"].get("data"):
         # Some messages are just flat bodies without parts
         data = payload["body"]["data"]
         body_text = base64.urlsafe_b64decode(data).decode("utf-8")

    return body_text


def _upsert_message(
    db: Session,
    account_id: int,
    message_id: str,
    thread_id: Optional[str],
    subject: Optional[str],
    from_address: Optional[str],
    snippet: Optional[str],
    body_text: Optional[str],
    internal_date: Optional[datetime],
    keyword: Optional[str],
    history_id: Optional[str],
):
    existing = (
        db.query(EmailMessage)
        .filter(EmailMessage.account_id == account_id, EmailMessage.gmail_message_id == message_id)
        .one_or_none()
    )

    email_obj = existing
    if existing:
        existing.subject = subject
        existing.from_address = from_address
        existing.snippet = snippet
        if body_text:
            existing.body_text = body_text
        existing.internal_date = internal_date
        existing.subscription_keyword = keyword or existing.subscription_keyword
        existing.thread_id = thread_id
        existing.history_id = history_id
    else:
        email_obj = EmailMessage(
            account_id=account_id,
            gmail_message_id=message_id,
            thread_id=thread_id,
            subject=subject,
            from_address=from_address,
            snippet=snippet,
            body_text=body_text,
            internal_date=internal_date,
            subscription_keyword=keyword,
            history_id=history_id,
        )
        db.add(email_obj)
        db.flush() # get ID

    # Run parser
    parser = SubscriptionParser()
    # Use body_text if available, else snippet
    content_to_parse = body_text or snippet or ""

    parsed_data = parser.parse_email(
        subject=subject or "",
        body=content_to_parse,
        sender=from_address or ""
    )

    if parsed_data:
        # Check if subscription already exists for this email
        sub = db.query(Subscription).filter(Subscription.email_message_id == email_obj.id).one_or_none()
        if sub:
            # Update only if not manually edited by user
            if not sub.manually_edited:
                sub.service_name = parsed_data["service_name"]
                sub.cost = parsed_data["cost"]
                sub.currency = parsed_data["currency"]
                sub.billing_cycle = parsed_data["billing_cycle"]
                sub.category = parsed_data.get("category", "Other")
            # Always update these if parser runs again? Maybe confidence score changes.
            sub.confidence_score = parsed_data["confidence_score"]
        else:
            # Create
            sub = Subscription(
                account_id=account_id,
                email_message_id=email_obj.id,
                service_name=parsed_data["service_name"],
                cost=parsed_data["cost"],
                currency=parsed_data["currency"],
                billing_cycle=parsed_data["billing_cycle"],
                category=parsed_data.get("category", "Other"),
                status=parsed_data["status"],
                confidence_score=parsed_data["confidence_score"],
                renewal_date=internal_date # Rough guess: renewal is around the email date
            )
            db.add(sub)


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
        
        try:
            message = (
                service.users()
                .messages()
                .get(userId="me", id=message_info["id"], format="full")
                .execute()
            )
            payload = message.get("payload", {})
            headers = payload.get("headers", [])
            subject = _header_value(headers, "Subject")
            from_address = _header_value(headers, "From")
            snippet = message.get("snippet")
            body_text = _extract_body(payload)

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
                body_text=body_text,
                internal_date=internal_date,
                keyword=keyword,
                history_id=message.get("historyId"),
            )
        except Exception as e:
            logger.error(f"Error processing message {message_info['id']}: {e}")
            continue

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
