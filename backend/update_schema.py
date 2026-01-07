from typing import Optional
from pydantic import BaseModel, Field

class SubscriptionUpdate(BaseModel):
    cost: Optional[float] = None
    currency: Optional[str] = None
    billing_cycle: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    renewal_date: Optional[str] = None # Accepts ISO format string or None
