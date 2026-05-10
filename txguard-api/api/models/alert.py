from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from ..database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    risk_tier = Column(String, nullable=False) # HIGH | CRITICAL
    rule_triggers = Column(JSONB)
    ml_anomaly_score = Column(Float)
    reason_codes = Column(JSONB)
    investigation_status = Column(String, default="PENDING") # PENDING | IN_PROGRESS | COMPLETE | ESCALATED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
