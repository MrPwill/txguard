from crewai.tools import tool
from api.database import get_db
from api.models.transaction import Transaction
from datetime import datetime, timedelta, timezone
@tool("get_transaction_detail")
def get_transaction_detail(transaction_id: str) -> dict:
    """
    Fetches full transaction record from PostgreSQL by ID.
    Input: transaction_id (string)
    Output: Dictionary containing transaction details.
    """
    db = next(get_db())
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        return {
            "transaction_id": transaction.id,
            "account_id": transaction.account_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "merchant_name": transaction.merchant_name,
            "merchant_category_code": transaction.merchant_category_code,
            "timestamp": str(transaction.timestamp),
            "location_country": transaction.location_country,
            "channel": transaction.channel,
            "counterparty_account": transaction.counterparty_account
        }
    return {"error": "Transaction not found"}

@tool("get_account_history")
def get_account_history(account_id: str) -> dict:
    """
    Returns the last 90 days of transactions for an account.
    Input: account_id (string)
    Output: list of transaction records with amounts, timestamps, merchants.
    """
    db = next(get_db())
    ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .filter(Transaction.timestamp >= ninety_days_ago)
        .order_by(Transaction.timestamp.desc())
        .limit(100) # reasonable limit for LLM context
        .all()
    )
    return {"transactions": [{
        "id": t.id,
        "amount": t.amount,
        "timestamp": str(t.timestamp),
        "merchant_name": t.merchant_name,
        "channel": t.channel
    } for t in transactions]}

@tool("compute_velocity_stats")
def compute_velocity_stats(account_id: str) -> dict:
    """
    Computes transaction counts across 1h, 24h, 7d windows for an account.
    Input: account_id (string)
    """
    db = next(get_db())
    now = datetime.now(timezone.utc)
    t_1h = db.query(Transaction).filter(Transaction.account_id == account_id, Transaction.timestamp >= now - timedelta(hours=1)).count()
    t_24h = db.query(Transaction).filter(Transaction.account_id == account_id, Transaction.timestamp >= now - timedelta(hours=24)).count()
    t_7d = db.query(Transaction).filter(Transaction.account_id == account_id, Transaction.timestamp >= now - timedelta(days=7)).count()
    
    return {
        "1h_count": t_1h,
        "24h_count": t_24h,
        "7d_avg_daily": t_7d / 7.0
    }

@tool("get_geographic_profile")
def get_geographic_profile(account_id: str) -> dict:
    """
    Returns account's typical location countries and distance anomaly flag.
    Input: account_id (string)
    """
    return {
        "typical_countries": ["US", "CA", "GB"],
        "is_geographic_anomaly": False, # Mocked
        "note": "Mocked for demo: assumes US/CA/GB profile."
    }

@tool("get_rule_trigger_detail")
def get_rule_trigger_detail(alert_id: str) -> dict:
    """
    Returns the rule flags fired and their raw input values for a given alert.
    Input: alert_id (string)
    """
    from api.models.alert import Alert
    db = next(get_db())
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        return {"rule_triggers": alert.rule_triggers or [], "reason_codes": alert.reason_codes or []}
    return {"error": "Alert not found"}
