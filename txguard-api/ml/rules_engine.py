import pandas as pd

BLACKLISTED_MCCS = ["5933", "6012", "7995"]

class RulesEngine:
    def __init__(self):
        pass
        
    def evaluate(self, txn: dict, history_df: pd.DataFrame = None) -> dict:
        """
        Evaluates a transaction dictionary against predefined rules.
        txn: dict containing transaction details
        history_df: DataFrame containing the account's recent transaction history
        """
        score = 0
        triggers = []
        
        # 1. High Velocity
        if history_df is not None and not history_df.empty:
            times = pd.to_datetime(history_df['timestamp'])
            txn_time = pd.to_datetime(txn['timestamp'])
            recent_1h = history_df[(txn_time - times).dt.total_seconds() <= 3600]
            # Since txn itself is not in history_df, check if >= 5 previous ones exist in last hour
            if len(recent_1h) >= 5:
                score += 30
                triggers.append("High velocity: >5 transactions in 60m")
        
        # 2. Large Round Amount
        amount = txn.get('amount', 0)
        if amount > 5000 and amount % 100 == 0:
            score += 15
            triggers.append(f"Large round amount: ${amount}")
            
        # 3. Geographic Anomaly
        txn_country = txn.get('location_country')
        if history_df is not None and not history_df.empty:
            last_10 = history_df.tail(10)
            if txn_country not in last_10['location_country'].values and len(last_10) >= 1:
                score += 25
                triggers.append(f"Geographic anomaly: new country {txn_country}")
                
        # 4. Blacklisted Merchant
        mcc = str(txn.get('merchant_category_code', ''))
        if mcc in BLACKLISTED_MCCS:
            score += 40
            triggers.append(f"Blacklisted merchant MCC: {mcc}")
            
        # 5. Off-Hours Transaction
        txn_time = pd.to_datetime(txn['timestamp'])
        if 1 <= txn_time.hour <= 4:
            score += 10
            triggers.append(f"Off-hours transaction: {txn_time.hour} AM")
            
        # 6. Rapid Cross-Border
        if history_df is not None and not history_df.empty:
            recent_24h = history_df[(txn_time - pd.to_datetime(history_df['timestamp'])).dt.total_seconds() <= 86400]
            countries_24h = set(recent_24h['location_country'].values)
            countries_24h.add(txn_country)
            if len(countries_24h) > 2:
                score += 35
                triggers.append("Rapid cross-border: >2 countries in 24h")
                
        return {
            "rule_score": score,
            "rule_triggers": triggers
        }
