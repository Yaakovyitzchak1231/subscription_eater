from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func, Float, Boolean
from sqlalchemy.orm import relationship

from .database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_json = Column(Text, nullable=False)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_synced_at = Column(DateTime, nullable=True)

    messages = relationship("EmailMessage", back_populates="account", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="account", cascade="all, delete-orphan")


class EmailMessage(Base):
    __tablename__ = "email_messages"
    __table_args__ = (UniqueConstraint("account_id", "gmail_message_id", name="uq_account_message"),)

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    gmail_message_id = Column(String, nullable=False, index=True)
    thread_id = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    from_address = Column(String, nullable=True, index=True)
    snippet = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)  # New field for full text
    internal_date = Column(DateTime, nullable=True)
    subscription_keyword = Column(String, nullable=True)
    history_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    account = relationship("Account", back_populates="messages")
    subscription = relationship("Subscription", back_populates="source_email", uselist=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    email_message_id = Column(Integer, ForeignKey("email_messages.id"), unique=True, nullable=True)

    service_name = Column(String, nullable=False)
    cost = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    billing_cycle = Column(String, nullable=True)  # "monthly", "yearly"
    status = Column(String, default="active")  # "active", "cancelled", "detected"
    renewal_date = Column(DateTime, nullable=True)

    confidence_score = Column(Float, default=0.0)
    is_confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    account = relationship("Account", back_populates="subscriptions")
    source_email = relationship("EmailMessage", back_populates="subscription")
