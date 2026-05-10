import uuid
import random
import datetime
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Blacklisted MCCs for rule testing (e.g., Pawn shops, Financial inst, Gambling)
BLACKLISTED_MCCS = ["5933", "6012", "7995"]  
CHANNELS = ["online", "atm", "pos", "transfer"]
CURRENCIES = ["USD", "EUR", "GBP"]
COUNTRIES = ["US", "GB", "DE", "FR", "CA", "NG"]

def generate_base_account_profile():
    return {
        "account_id": f"ACC-{uuid.uuid4().hex[:8]}",
        "home_country": random.choice(COUNTRIES),
        "typical_channel": random.choice(CHANNELS),
        "typical_amount": round(np.random.lognormal(mean=3, sigma=1), 2),
        "typical_hour": random.randint(8, 20)
    }

def generate_normal_transaction(account):
    hour = int(np.random.normal(account["typical_hour"], 2)) % 24
    date = fake.date_time_between(start_date="-90d", end_date="now")
    date = date.replace(hour=hour)
    
    amount = round(max(1.0, np.random.normal(account["typical_amount"], account["typical_amount"]*0.5)), 2)
    
    return {
        "transaction_id": str(uuid.uuid4()),
        "account_id": account["account_id"],
        "amount": amount,
        "currency": "USD",
        "merchant_name": fake.company(),
        "merchant_category_code": str(random.randint(5000, 5999)),
        "timestamp": date.isoformat() + "Z",
        "location_country": account["home_country"],
        "location_city": fake.city(),
        "channel": account["typical_channel"],
        "counterparty_account": None,
        "is_fraud": False,
        "fraud_type": "None"
    }

def inject_high_velocity(account):
    txns = []
    current_time = fake.date_time_between(start_date="-90d", end_date="now")
    for _ in range(6):
        txns.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": account["account_id"],
            "amount": round(random.uniform(50, 200), 2),
            "currency": "USD",
            "merchant_name": fake.company(),
            "merchant_category_code": str(random.randint(5000, 5999)),
            "timestamp": current_time.isoformat() + "Z",
            "location_country": account["home_country"],
            "location_city": fake.city(),
            "channel": "online",
            "counterparty_account": None,
            "is_fraud": True,
            "fraud_type": "high_velocity"
        })
        current_time += datetime.timedelta(minutes=random.randint(2, 8))
    return txns

def inject_large_round_amount_off_hours(account):
    date = fake.date_time_between(start_date="-90d", end_date="now")
    date = date.replace(hour=random.randint(1, 3)) # Off hours 1am-3am
    return [{
        "transaction_id": str(uuid.uuid4()),
        "account_id": account["account_id"],
        "amount": round(random.choice([5000, 10000, 15000, 20000]) * 1.0, 2),
        "currency": "USD",
        "merchant_name": fake.company(),
        "merchant_category_code": str(random.randint(5000, 5999)),
        "timestamp": date.isoformat() + "Z",
        "location_country": account["home_country"],
        "location_city": fake.city(),
        "channel": "transfer",
        "counterparty_account": f"ACC-{uuid.uuid4().hex[:8]}",
        "is_fraud": True,
        "fraud_type": "large_round_off_hours"
    }]

def inject_rapid_cross_border(account):
    txns = []
    date = fake.date_time_between(start_date="-90d", end_date="now")
    
    countries = random.sample(COUNTRIES, 3)
    for i, country in enumerate(countries):
        txns.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": account["account_id"],
            "amount": round(random.uniform(100, 500), 2),
            "currency": "USD",
            "merchant_name": fake.company(),
            "merchant_category_code": str(random.randint(5000, 5999)),
            "timestamp": (date + datetime.timedelta(hours=i*3)).isoformat() + "Z",
            "location_country": country,
            "location_city": fake.city(),
            "channel": "pos",
            "counterparty_account": None,
            "is_fraud": True,
            "fraud_type": "rapid_cross_border"
        })
    return txns

def inject_blacklisted_merchant(account):
    date = fake.date_time_between(start_date="-90d", end_date="now")
    return [{
        "transaction_id": str(uuid.uuid4()),
        "account_id": account["account_id"],
        "amount": round(random.uniform(500, 2000), 2),
        "currency": "USD",
        "merchant_name": "Crypto Exchange Inc",
        "merchant_category_code": random.choice(BLACKLISTED_MCCS),
        "timestamp": date.isoformat() + "Z",
        "location_country": account["home_country"],
        "location_city": fake.city(),
        "channel": "online",
        "counterparty_account": None,
        "is_fraud": True,
        "fraud_type": "blacklisted_merchant"
    }]

def generate_dataset(num_accounts=1000, txns_per_account=10):
    all_txns = []
    accounts = [generate_base_account_profile() for _ in range(num_accounts)]
    
    for account in accounts:
        for _ in range(txns_per_account):
            all_txns.append(generate_normal_transaction(account))
            
        prob = random.random()
        if prob < 0.03:
            all_txns.extend(inject_high_velocity(account))
        elif prob < 0.06:
            all_txns.extend(inject_large_round_amount_off_hours(account))
        elif prob < 0.09:
            all_txns.extend(inject_rapid_cross_border(account))
        elif prob < 0.12:
            all_txns.extend(inject_blacklisted_merchant(account))
            
    df = pd.DataFrame(all_txns)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    return df

if __name__ == "__main__":
    print("Generating synthetic dataset...")
    df = generate_dataset(num_accounts=1000, txns_per_account=10)
    print(f"Generated {len(df)} transactions.")
    fraud_counts = df['is_fraud'].value_counts()
    print(f"Normal: {fraud_counts.get(False, 0)}, Fraud: {fraud_counts.get(True, 0)}")
    
    import os
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), "synthetic_transactions.csv"), index=False)
    print("Saved to synthetic_transactions.csv")
