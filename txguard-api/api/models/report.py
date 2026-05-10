from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from ..database import Base

class InvestigationReport(Base):
    __tablename__ = "investigation_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    
    behavioral_analysis = Column(Text)
    typology_assessment = Column(JSONB)
    regulatory_assessment = Column(Text)
    recommended_action = Column(String) # CLEAR | ESCALATE_TO_SAR | BLOCK_AND_HOLD | MONITOR
    confidence_score = Column(Float)
    evidence_citations = Column(JSONB)
    agent_run_metadata = Column(JSONB) # per-agent name, duration, token usage
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
