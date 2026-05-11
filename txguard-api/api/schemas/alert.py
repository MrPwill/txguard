from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class AlertBase(BaseModel):
    transaction_id: str
    risk_tier: str
    rule_triggers: List[str]
    ml_anomaly_score: float
    reason_codes: List[str]
    investigation_status: str = "PENDING"

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
