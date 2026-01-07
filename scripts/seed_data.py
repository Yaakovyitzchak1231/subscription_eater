import os
import sys
from datetime import datetime, timezone

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.database import SessionLocal, engine, Base
from backend.models import Account, EmailMessage, Subscription
from backend.gmail_sync import _upsert_message
from backend.parser import SubscriptionParser

def seed_data():
    # Reset Database for Development/Testing
    print("Resetting database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Create a dummy account
    email = "test@example.com"
    account = Account(
        email=email,
        access_token="dummy",
        refresh_token="dummy",
        token_json="{}",
        token_expiry=datetime.now()
    )
    db.add(account)
    db.commit()
    print(f"Created account {email}")

    # Sample Emails (Raw Text)
    samples = [
        {
            "id": "msg1",
            "subject": "Your Netflix Subscription",
            "from": "Netflix <info@mailer.netflix.com>",
            "snippet": "We hope you are enjoying Netflix...",
            "body": """
Hello,
We hope you are enjoying Netflix.

This email is to confirm that we have received your payment.
Total: $15.99
Date: January 25, 2025

Your subscription will automatically renew next month.
            """,
            "date": datetime.now(timezone.utc)
        },
        {
            "id": "msg2",
            "subject": "Spotify Premium Receipt",
            "from": "Spotify <no-reply@spotify.com>",
            "snippet": "Here is your receipt for Spotify Premium...",
            "body": """
Spotify Premium

Receipt for your subscription.
You have been charged $11.99 for your monthly subscription.

Payment Method: Visa ending 1234
            """,
            "date": datetime.now(timezone.utc)
        },
        {
            "id": "msg3",
            "subject": "Invoice for Adobe Creative Cloud",
            "from": "Adobe Systems <billing@adobe.com>",
            "snippet": "Your invoice is ready...",
            "body": """
Adobe Creative Cloud

Amount: $54.99
Billing Cycle: Monthly

Thank you for your business.
            """,
            "date": datetime.now(timezone.utc)
        },
        {
            "id": "msg4",
            "subject": "Your Amazon Prime Membership",
            "from": "Amazon.com <prime@amazon.com>",
            "snippet": "Your membership renews soon...",
            "body": """
Hello,

Your Amazon Prime membership will renew on Jan 20, 2026.
You will be charged $139.00 for the next year.

Thanks,
Amazon
            """,
            "date": datetime.now(timezone.utc)
        }
    ]

    print("Seeding emails and running parser...")
    for sample in samples:
        _upsert_message(
            db=db,
            account_id=account.id,
            message_id=sample["id"],
            thread_id=sample["id"],
            subject=sample["subject"],
            from_address=sample["from"],
            snippet=sample["snippet"],
            body_text=sample["body"],
            internal_date=sample["date"],
            keyword="subscription",
            history_id="100"
        )
        print(f"Processed {sample['subject']}")

    db.commit()

    # Check results
    subs = db.query(Subscription).all()
    print(f"\nTotal Subscriptions Found: {len(subs)}")
    for sub in subs:
        print(f"- {sub.service_name}: {sub.currency} {sub.cost} ({sub.billing_cycle})")

    db.close()

if __name__ == "__main__":
    seed_data()
