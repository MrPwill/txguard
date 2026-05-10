import os
import sys
import joblib
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import precision_score, recall_score

# Allow imports when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.synthetic_gen import generate_dataset
from ml.features import FeatureEngineer

def train_models():
    print("Loading synthetic data...")
    df = generate_dataset(num_accounts=2000, txns_per_account=15)
    
    print("Engineering features...")
    fe = FeatureEngineer()
    fe.fit(df)
    X = fe.transform(df)
    
    # Isolation Forest
    print("Training Isolation Forest...")
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    iso_forest.fit(X)
    
    # Local Outlier Factor
    print("Training Local Outlier Factor...")
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05, novelty=True)
    lof.fit(X)
    
    # Evaluate
    # -1 is anomaly, 1 is normal
    y_pred_iso = iso_forest.predict(X)
    y_pred_lof = lof.predict(X)
    
    is_anomaly_iso = y_pred_iso == -1
    is_anomaly_lof = y_pred_lof == -1
    
    y_true = df['is_fraud'].values
    
    precision_iso = precision_score(y_true, is_anomaly_iso, zero_division=0)
    recall_iso = recall_score(y_true, is_anomaly_iso, zero_division=0)
    print(f"Isolation Forest - Precision: {precision_iso:.2f}, Recall: {recall_iso:.2f}")
    
    precision_lof = precision_score(y_true, is_anomaly_lof, zero_division=0)
    recall_lof = recall_score(y_true, is_anomaly_lof, zero_division=0)
    print(f"Local Outlier Factor - Precision: {precision_lof:.2f}, Recall: {recall_lof:.2f}")
    
    # Save models
    save_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    os.makedirs(save_dir, exist_ok=True)
    
    joblib.dump(fe, os.path.join(save_dir, "feature_engineer.joblib"))
    joblib.dump(iso_forest, os.path.join(save_dir, "isolation_forest.joblib"))
    joblib.dump(lof, os.path.join(save_dir, "lof.joblib"))
    
    metadata = {
        "version": "1.0",
        "training_date": pd.Timestamp.utcnow().isoformat(),
        "training_set_size": len(X),
        "features": list(X.columns),
        "metrics": {
            "isolation_forest": {
                "precision": float(precision_iso),
                "recall": float(recall_iso)
            },
            "lof": {
                "precision": float(precision_lof),
                "recall": float(recall_lof)
            }
        }
    }
    
    with open(os.path.join(save_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("Models and metadata saved successfully in 'saved_models'.")

if __name__ == "__main__":
    train_models()
