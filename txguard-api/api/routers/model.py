from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.transaction import Transaction
from ..schemas.model import ModelStatusResponse

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    window_7d = now - timedelta(days=7)
    window_14d = now - timedelta(days=14)

    current_scores = [
        row[0]
        for row in db.query(Transaction.risk_score)
        .filter(Transaction.risk_score.isnot(None))
        .filter(Transaction.timestamp >= window_7d)
        .all()
    ]
    baseline_scores = [
        row[0]
        for row in db.query(Transaction.risk_score)
        .filter(Transaction.risk_score.isnot(None))
        .filter(Transaction.timestamp >= window_14d)
        .filter(Transaction.timestamp < window_7d)
        .all()
    ]

    current_mean = float(sum(current_scores) / len(current_scores)) if current_scores else 0.0
    baseline_mean = float(sum(baseline_scores) / len(baseline_scores)) if baseline_scores else current_mean
    drift_pct = (
        abs((current_mean - baseline_mean) / baseline_mean) * 100.0
        if baseline_mean > 0
        else 0.0
    )

    return ModelStatusResponse(
        drift_detected=drift_pct > 15.0,
        current_mean_risk_score=round(current_mean, 4),
        baseline_mean_risk_score=round(baseline_mean, 4),
        drift_pct=round(drift_pct, 4),
        updated_at=now,
        models=[
            {
                "name": "Isolation Forest",
                "version": "v1",
                "precision": 0.85,
                "recall": 0.84,
                "status": "HEALTHY" if drift_pct <= 15.0 else "DRIFT",
            },
            {
                "name": "Local Outlier Factor",
                "version": "v1",
                "precision": 0.82,
                "recall": 0.8,
                "status": "HEALTHY" if drift_pct <= 15.0 else "DRIFT",
            },
        ],
    )
