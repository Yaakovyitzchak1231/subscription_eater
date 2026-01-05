from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AuthorizationUrlResponse(BaseModel):
    authorization_url: str
    state: str


class AccountResponse(BaseModel):
    id: int
    email: str
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    subject: Optional[str]
    from_address: Optional[str]
    snippet: Optional[str]
    internal_date: Optional[datetime]
    subscription_keyword: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionEntry(BaseModel):
    account_id: int = Field(..., description="Identifier of the account")
    account_email: str = Field(..., description="Email for the account")
    from_address: Optional[str] = None
    message_count: int
    last_seen: Optional[datetime] = None


class AccountSummary(BaseModel):
    accounts: List[AccountResponse]
    subscription_entries: List[SubscriptionEntry]
