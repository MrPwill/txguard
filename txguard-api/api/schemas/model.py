from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ModelStatusResponse(BaseModel):
    drift_detected: bool
    current_mean_risk_score: float
    baseline_mean_risk_score: float
    drift_pct: float
    updated_at: datetime
    models: list[dict[str, Any]]
