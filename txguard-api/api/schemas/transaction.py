from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TransactionBase(BaseModel):
    account_id: str
    amount: float
    currency: str
    merchant_name: Optional[str] = None
    merchant_category_code: Optional[str] = None
    channel: str # online | atm | pos | transfer
    location_country: str
    location_city: str
    counterparty_account: Optional[str] = None
    timestamp: datetime

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: str
    status: str
    risk_score: Optional[float] = None
    risk_tier: Optional[str] = None
    reason_codes: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScoringResponse(BaseModel):
    risk_score: float
    risk_tier: str
    rule_triggers: List[str]
    ml_anomaly_score: float
    reason_codes: List[str]
    scored_at: datetime
