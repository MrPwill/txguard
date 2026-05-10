import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/app/txguard-api")

from prefect import flow, task
from api.database import SessionLocal
from api.models.transaction import Transaction
from api.models.alert import Alert


@task
def check_pending_alerts():
    db = SessionLocal()
    try:
        count = db.query(Alert).filter(
            Alert.investigation_status.in_(["PENDING", "IN_PROGRESS"])
        ).count()
        return count
    finally:
        db.close()


@task
def score_recent_transactions():
    db = SessionLocal()
    try:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        unscored = db.query(Transaction).filter(
            Transaction.status == "PENDING",
            Transaction.risk_score.is_(None)
        ).all()
        return len(unscored)
    finally:
        db.close()


@task
def get_score_distribution():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        rows = (
            db.query(Transaction.risk_tier, db.func.count())
            .filter(Transaction.risk_score.isnot(None))
            .filter(Transaction.timestamp >= week_ago)
            .group_by(Transaction.risk_tier)
            .all()
        )
        return {tier: count for tier, count in rows}
    finally:
        db.close()


@task
def detect_model_drift():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        window_7d = now - timedelta(days=7)
        window_14d = now - timedelta(days=14)

        current = [r[0] for r in
            db.query(Transaction.risk_score)
            .filter(Transaction.risk_score.isnot(None))
            .filter(Transaction.timestamp >= window_7d)
            .all()
        ]
        baseline = [r[0] for r in
            db.query(Transaction.risk_score)
            .filter(Transaction.risk_score.isnot(None))
            .filter(Transaction.timestamp >= window_14d)
            .filter(Transaction.timestamp < window_7d)
            .all()
        ]

        if not current or not baseline:
            return {"drift_detected": False, "current_mean": 0, "baseline_mean": 0, "drift_pct": 0}

        curr_mean = sum(current) / len(current)
        base_mean = sum(baseline) / len(baseline)
        drift_pct = abs((curr_mean - base_mean) / base_mean) * 100 if base_mean > 0 else 0

        return {
            "drift_detected": drift_pct > 15.0,
            "current_mean": round(curr_mean, 4),
            "baseline_mean": round(base_mean, 4),
            "drift_pct": round(drift_pct, 4),
        }
    finally:
        db.close()


@flow(name="txguard-nightly-pipeline", log_prints=True)
def nightly_pipeline():
    run_time = datetime.now(timezone.utc).isoformat()

    pending_alerts = check_pending_alerts()
    unscored = score_recent_transactions()
    distribution = get_score_distribution()
    drift = detect_model_drift()

    print(f"=== TxGuard Nightly Pipeline - {run_time} ===")
    print(f"Pending alerts: {pending_alerts}")
    print(f"Unscored transactions: {unscored}")
    print(f"Score distribution (7d): {distribution}")
    print(f"Drift status: {drift}")

    if drift["drift_detected"]:
        print("WARNING: Model drift detected. Retraining recommended.")
        print(f"  Current mean: {drift['current_mean']}, Baseline: {drift['baseline_mean']}, Drift: {drift['drift_pct']:.2f}%")

    return {
        "run_time": run_time,
        "pending_alerts": pending_alerts,
        "unscored_transactions": unscored,
        "score_distribution": distribution,
        "drift_status": drift,
    }


if __name__ == "__main__":
    nightly_pipeline()