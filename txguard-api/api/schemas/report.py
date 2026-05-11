from pydantic import BaseModel, ConfigDict
from typing import Any
from datetime import datetime

class InvestigationReportBase(BaseModel):
    alert_id: str
    transaction_id: str
    behavioral_analysis: str
    typology_assessment: Any
    regulatory_assessment: str
    recommended_action: str
    confidence_score: float
    evidence_citations: Any
    agent_run_metadata: Any

class InvestigationReportCreate(InvestigationReportBase):
    pass

class InvestigationReport(InvestigationReportBase):
    id: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
