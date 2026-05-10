from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from ..database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, index=True)
    action_type = Column(String, nullable=False) # INGESTED | RULE_EVALUATED | ML_SCORED | ALERT_CREATED | INVESTIGATION_DISPATCHED | AGENT_COMPLETED | REPORT_WRITTEN
    actor = Column(String) # "system" | agent name
    payload = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
