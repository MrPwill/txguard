import sys
import time
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import OperationalError

sys.path.insert(0, "/app/txguard-api")

from api.database import SessionLocal
from api.models.transaction import Transaction
from api.models.alert import Alert
from api.models.audit import AuditLog
from api.models.report import InvestigationReport

CHANNELS = ["online", "atm", "pos", "transfer"]
COUNTRIES = [
    ("US", "New York"),
    ("GB", "London"),
    ("NG", "Lagos"),
    ("DE", "Berlin"),
    ("CA", "Toronto"),
]
MERCHANTS = [
    ("Bluewave Retail", "5411"),
    ("Northstar Electronics", "5732"),
    ("Summit Travel", "4722"),
    ("Metro Fuel", "5541"),
    ("Mercury Transfers", "4829"),
]
BLACKLISTED_MCCS = ["5933", "6012", "7995"]

def wait_for_db(max_attempts=30, sleep_seconds=2):
    for attempt in range(1, max_attempts + 1):
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return
        except Exception:
            if attempt == max_attempts:
                raise
            time.sleep(sleep_seconds)

def seed():
    wait_for_db()
    db = SessionLocal()
    try:
        if db.query(Transaction).count() > 0:
            print("DB already seeded, skipping.")
            return

        now = datetime.now(timezone.utc)
        random.seed(42)

        txns = []
        alert_ids = []

        for i in range(250):
            country, city = random.choice(COUNTRIES)
            merchant_name, mcc = random.choice(MERCHANTS)
            minutes_ago = random.randint(0, 60 * 24 * 7)
            ts = now - timedelta(minutes=minutes_ago)

            risk_score = round(random.uniform(5, 98), 2)
            if risk_score > 80:
                risk_tier = "CRITICAL"
                status = "FLAGGED"
                reasons = ["High ML Anomaly Score", "Velocity spike"]
            elif risk_score > 60:
                risk_tier = "HIGH"
                status = "FLAGGED"
                reasons = ["Rule trigger threshold exceeded"]
            elif risk_score > 30:
                risk_tier = "MEDIUM"
                status = "SCORED"
                reasons = ["Moderate anomaly"]
            else:
                risk_tier = "LOW"
                status = "SCORED"
                reasons = ["Within expected pattern"]

            if random.random() < 0.05:
                mcc = random.choice(BLACKLISTED_MCCS)
                merchant_name = "Blacklisted Merchant"
                reasons = ["Blacklisted merchant MCC: " + mcc] + reasons[:1]
                risk_score = min(98, risk_score + 20)
                risk_tier = "CRITICAL"
                status = "FLAGGED"

            txn = Transaction(
                id=f"TXN-{10000+i}",
                account_id=f"ACC-{100000 + (i % 120)}",
                amount=round(random.uniform(12, 18000), 2),
                currency="USD",
                merchant_name=merchant_name,
                merchant_category_code=mcc,
                channel=random.choice(CHANNELS),
                location_country=country,
                location_city=city,
                counterparty_account=None,
                timestamp=ts,
                status=status,
                risk_score=risk_score,
                risk_tier=risk_tier,
                reason_codes=reasons,
            )
            db.add(txn)
            db.flush()

            db.add(AuditLog(
                transaction_id=txn.id,
                action_type="INGESTED",
                actor="system",
                payload={"source": "seed"}
            ))
            db.add(AuditLog(
                transaction_id=txn.id,
                action_type="RULE_EVALUATED",
                actor="system",
                payload={"rule_triggers": reasons}
            ))
            db.add(AuditLog(
                transaction_id=txn.id,
                action_type="ML_SCORED",
                actor="system",
                payload={"ml_anomaly_score": round(random.uniform(0.1, 0.95), 4)}
            ))

            if risk_tier in ["HIGH", "CRITICAL"]:
                alert = Alert(
                    transaction_id=txn.id,
                    risk_tier=risk_tier,
                    rule_triggers=reasons,
                    ml_anomaly_score=round(risk_score / 100, 4),
                    reason_codes=reasons,
                )
                db.add(alert)
                db.flush()

                db.add(AuditLog(
                    transaction_id=txn.id,
                    action_type="ALERT_CREATED",
                    actor="system",
                    payload={"alert_id": alert.id, "tier": risk_tier}
                ))
                db.add(AuditLog(
                    transaction_id=txn.id,
                    action_type="INVESTIGATION_DISPATCHED",
                    actor="system",
                    payload={"alert_id": alert.id, "tier": risk_tier}
                ))
                alert_ids.append(alert.id)

                if random.random() < 0.4:
                    alert.investigation_status = "COMPLETE"
                    report = InvestigationReport(
                        id=f"REP-{len(alert_ids):05d}",
                        alert_id=alert.id,
                        transaction_id=txn.id,
                        behavioral_analysis=f"Account {txn.account_id} exhibited {risk_tier} risk indicators. Transaction amount ${txn.amount} from {txn.merchant_name} in {txn.location_city}, {txn.location_country} triggered multiple rule flags.",
                        typology_assessment={"matches": ["Rapid cross-border" if "NG" in country else "High velocity", "Blacklisted merchant" if mcc in BLACKLISTED_MCCS else "Structuring"]},
                        regulatory_assessment="Transaction meets CTR reporting threshold of $10,000. SAR filing review required. No sanctions match identified.",
                        recommended_action=random.choice(["ESCALATE_TO_SAR", "BLOCK_AND_HOLD", "MONITOR"]),
                        confidence_score=round(random.uniform(0.7, 0.95), 2),
                        evidence_citations=[{"source": "FATF Recommendation 10", "excerpt": "CDD required for high-risk transactions"}],
                        agent_run_metadata={"agents_run": 4, "total_duration_s": round(random.uniform(15, 90), 1)},
                    )
                    db.add(report)

                    db.add(AuditLog(
                        transaction_id=txn.id,
                        action_type="AGENT_COMPLETED",
                        actor="system",
                        payload={"alert_id": alert.id, "recommended_action": report.recommended_action}
                    ))
                    db.add(AuditLog(
                        transaction_id=txn.id,
                        action_type="REPORT_WRITTEN",
                        actor="system",
                        payload={"report_id": report.id}
                    ))

        db.commit()
        print(f"Seeded 250 transactions, {len(alert_ids)} alerts, reports created.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()