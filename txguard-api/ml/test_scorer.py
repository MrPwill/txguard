import os
import sys
import uuid
import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.scorer import HybridScorer

def test():
    print("Initializing Scorer...")
    scorer = HybridScorer()
    
    # 1. Normal transaction
    normal_txn = {
        "transaction_id": str(uuid.uuid4()),
        "account_id": "ACC-12345",
        "amount": 45.50,
        "currency": "USD",
        "merchant_name": "Local Coffee Shop",
        "merchant_category_code": "5814",
        "timestamp": datetime.datetime.utcnow().replace(hour=14).isoformat() + "Z",
        "location_country": "US",
        "location_city": "New York",
        "channel": "pos",
        "counterparty_account": None
    }
    
    res1 = scorer.score_transaction(normal_txn)
    print("\n--- Normal Transaction Result ---")
    print(res1)
    
    # 2. Highly Fraudulent transaction (Large round amount, off hours, blacklisted MCC)
    fraud_txn = {
        "transaction_id": str(uuid.uuid4()),
        "account_id": "ACC-12345",
        "amount": 10000.00,
        "currency": "USD",
        "merchant_name": "Crypto Exchange Inc",
        "merchant_category_code": "6012",
        "timestamp": datetime.datetime.utcnow().replace(hour=2).isoformat() + "Z",
        "location_country": "NG",
        "location_city": "Lagos",
        "channel": "online",
        "counterparty_account": "ACC-99999"
    }
    
    # History dataframe to trigger velocity or geo anomaly
    # Let's say the user usually is in US
    history = []
    base_time = datetime.datetime.utcnow().replace(hour=2)
    for i in range(5):
        history.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": "ACC-12345",
            "amount": 20.0,
            "currency": "USD",
            "merchant_name": "Grocery Store",
            "merchant_category_code": "5411",
            "timestamp": (base_time - datetime.timedelta(minutes=10*(i+1))).isoformat() + "Z",
            "location_country": "US",
            "location_city": "New York",
            "channel": "pos",
            "counterparty_account": None
        })
    history_df = pd.DataFrame(history)
    
    res2 = scorer.score_transaction(fraud_txn, history_df)
    print("\n--- Fraudulent Transaction Result ---")
    print(res2)

if __name__ == "__main__":
    test()
