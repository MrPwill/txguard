from sqlalchemy import Column, String, Float, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    merchant_name = Column(String)
    merchant_category_code = Column(String)
    channel = Column(String) # online | atm | pos | transfer
    location_country = Column(String)
    location_city = Column(String)
    counterparty_account = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    status = Column(String, default="PENDING") # PENDING | SCORED | FLAGGED | CLEARED | BLOCKED
    risk_score = Column(Float, nullable=True)
    risk_tier = Column(String, nullable=True) # LOW | MEDIUM | HIGH | CRITICAL
    reason_codes = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
