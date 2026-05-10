import os
import joblib
import pandas as pd
import numpy as np

from ml.rules_engine import RulesEngine
from ml.features import FeatureEngineer

class HybridScorer:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
            
        self.fe = joblib.load(os.path.join(model_dir, "feature_engineer.joblib"))
        self.iso_forest = joblib.load(os.path.join(model_dir, "isolation_forest.joblib"))
        self.lof = joblib.load(os.path.join(model_dir, "lof.joblib"))
        self.rules_engine = RulesEngine()
        
    def score_transaction(self, txn: dict, history_df: pd.DataFrame = None):
        """
        Scores a single transaction.
        txn: Transaction dict
        history_df: DataFrame of recent transactions for this account (optional)
        """
        # 1. Rule evaluation
        rule_results = self.rules_engine.evaluate(txn, history_df)
        rule_score = rule_results['rule_score']
        
        # 2. ML Anomaly Score
        if history_df is not None and not history_df.empty:
            df_eval = pd.concat([history_df, pd.DataFrame([txn])], ignore_index=True)
            X_eval = self.fe.transform(df_eval)
            X_txn = X_eval.iloc[[-1]] # Last row is the new txn
        else:
            df_eval = pd.DataFrame([txn])
            X_txn = self.fe.transform(df_eval)
            
        # Get ML scores. isolation forest decision_function returns negative score for anomalies.
        iso_scores = self.iso_forest.decision_function(X_txn)
        
        # Heuristic normalization to 0-1 range (higher = more anomalous)
        # typically iso_scores are in [-0.5, 0.5] range
        ml_score_raw = 0.5 - iso_scores[0]
        ml_anomaly_score = float(np.clip(ml_score_raw, 0, 1))
        
        # 3. Hybrid Score Formula
        # Final Risk Score = (Rule Weight Sum * 0.4) + (ML Anomaly Score * 100 * 0.6)
        final_score = (rule_score * 0.4) + (ml_anomaly_score * 100 * 0.6)
        final_score = float(np.clip(final_score, 0, 100))
        
        # Determine tier
        if final_score <= 30:
            tier = "LOW"
        elif final_score <= 60:
            tier = "MEDIUM"
        elif final_score <= 80:
            tier = "HIGH"
        else:
            tier = "CRITICAL"
            
        # Gather reason codes (top 3)
        reasons = rule_results['rule_triggers'].copy()
        if ml_anomaly_score > 0.6:
            reasons.append(f"High ML Anomaly Score ({ml_anomaly_score:.2f})")
            
        return {
            "risk_score": round(final_score, 2),
            "risk_tier": tier,
            "rule_triggers": rule_results['rule_triggers'],
            "ml_anomaly_score": round(ml_anomaly_score, 4),
            "reason_codes": reasons[:3],
            "scored_at": pd.Timestamp.utcnow().isoformat()
        }
