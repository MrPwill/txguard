from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class InvestigationReportBase(BaseModel):
    alert_id: str
    transaction_id: str
    behavioral_analysis: str
    typology_assessment: List[Dict[str, Any]]
    regulatory_assessment: str
    recommended_action: str
    confidence_score: float
    evidence_citations: List[Dict[str, str]]
    agent_run_metadata: List[Dict[str, Any]]

class InvestigationReportCreate(InvestigationReportBase):
    pass

class InvestigationReport(InvestigationReportBase):
    id: str
    generated_at: datetime

    class Config:
        from_attributes = True
