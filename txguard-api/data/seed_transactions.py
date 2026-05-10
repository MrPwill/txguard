from __future__ import annotations

import random
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import OperationalError

from api.database import SessionLocal
from api.models.transaction import Transaction


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


def wait_for_db(max_attempts: int = 30, sleep_seconds: int = 2) -> None:
    for attempt in range(1, max_attempts + 1):
        db = SessionLocal()
        try:
            db.execute(Transaction.__table__.select().limit(1))
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(sleep_seconds)
        finally:
            db.close()


def generate_transactions(count: int = 250) -> list[Transaction]:
    random.seed(42)
    now = datetime.now(timezone.utc)
    txns: list[Transaction] = []

    for i in range(count):
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

        txns.append(
            Transaction(
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
        )

    return txns


def main() -> None:
    wait_for_db()

    db = SessionLocal()
    try:
        existing_count = db.query(Transaction).count()
        if existing_count > 0:
            print(f"Seed skipped: transactions table already has {existing_count} rows.")
            return

        txns = generate_transactions()
        db.add_all(txns)
        db.commit()
        print(f"Seed complete: inserted {len(txns)} transactions.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
