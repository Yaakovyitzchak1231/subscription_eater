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


class SubscriptionResponse(BaseModel):
    id: int
    service_name: str
    cost: Optional[float]
    currency: str
    billing_cycle: Optional[str]
    category: Optional[str]
    status: str
    renewal_date: Optional[datetime]
    confidence_score: float
    is_confirmed: bool
    manually_edited: bool = False
    is_hidden: bool = False

    # Metadata
    account_email: Optional[str] = None
    source_email_subject: Optional[str] = None
    source_email_from: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    cost: Optional[float] = None
    currency: Optional[str] = None
    billing_cycle: Optional[str] = None
    category: Optional[str] = Field(
        None, 
        description="Category of subscription. Valid values: Entertainment, Software, Utilities, Shopping, News, Health, Food, Other"
    )
    status: Optional[str] = Field(
        None,
        description="Status of subscription. Valid values: active, cancelled, detected"
    )
    renewal_date: Optional[str] = Field(None, description="ISO 8601 format date string")
