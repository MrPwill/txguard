import asyncio
import json
from typing import List, Optional
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.transaction import Transaction
from ..models.alert import Alert
from ..models.audit import AuditLog
from ..models.report import InvestigationReport
from ..schemas.transaction import TransactionCreate, Transaction as TransactionSchema, ScoringResponse
from ..schemas.report import InvestigationReport as InvestigationReportSchema
from ..dependencies import get_scorer, get_explainer
from ..realtime import publish_alert_event
from datetime import datetime
from workers.celery_app import run_investigation

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionSchema])
async def list_transactions(
    tier: Optional[str] = None,
    account_id: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)
    if tier:
        query = query.filter(Transaction.risk_tier == tier)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    return query.order_by(Transaction.timestamp.desc()).limit(limit).all()

@router.post("/ingest", response_model=List[TransactionSchema])
async def ingest_transactions(txns: List[TransactionCreate], db: Session = Depends(get_db)):
    db_txns = []
    for txn in txns:
        db_txn = Transaction(**txn.model_dump())
        db.add(db_txn)
        db_txns.append(db_txn)
        
        # Log ingestion
        audit = AuditLog(
            transaction_id=db_txn.id,
            action_type="INGESTED",
            actor="system",
            payload=txn.model_dump()
        )
        db.add(audit)
        
    db.commit()
    for txn in db_txns:
        db.refresh(txn)
    return db_txns

@router.post("/score")
async def score_transaction_sync(
    txn_id: str,
    stream: bool = False,
    db: Session = Depends(get_db),
    scorer=Depends(get_scorer),
):
    """
    Synchronous scoring for testing. The PRD also asks for SSE streaming version.
    """
    if stream:
        return await score_transaction_stream(txn_id, db, scorer)

    db_txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not db_txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    # Get history for scoring (mocking for now, in real case we'd query DB)
    history = db.query(Transaction).filter(
        Transaction.account_id == db_txn.account_id,
        Transaction.id != db_txn.id
    ).order_by(Transaction.timestamp.desc()).limit(50).all()
    
    import pandas as pd
    history_df = pd.DataFrame([t.__dict__ for t in history]) if history else None
    if history_df is not None:
        history_df = history_df.drop(columns=['_sa_instance_state'], errors='ignore')
        
    result = scorer.score_transaction(db_txn.__dict__, history_df)
    
    # Update transaction
    db_txn.risk_score = result['risk_score']
    db_txn.risk_tier = result['risk_tier']
    db_txn.reason_codes = result['reason_codes']
    db_txn.status = "SCORED"
    
    # Log scoring
    db.add(AuditLog(
        transaction_id=db_txn.id,
        action_type="RULE_EVALUATED",
        actor="system",
        payload={"rule_triggers": result['rule_triggers']}
    ))
    db.add(AuditLog(
        transaction_id=db_txn.id,
        action_type="ML_SCORED",
        actor="system",
        payload={"ml_anomaly_score": result['ml_anomaly_score']}
    ))
    
    # Create alert if needed
    if db_txn.risk_tier in ["HIGH", "CRITICAL"]:
        db_txn.status = "FLAGGED"
        alert = Alert(
            transaction_id=db_txn.id,
            risk_tier=db_txn.risk_tier,
            rule_triggers=result['rule_triggers'],
            ml_anomaly_score=result['ml_anomaly_score'],
            reason_codes=result['reason_codes']
        )
        db.add(alert)
        db.flush()
        db.add(AuditLog(
            transaction_id=db_txn.id,
            action_type="ALERT_CREATED",
            actor="system",
            payload={"alert_id": alert.id, "tier": db_txn.risk_tier}
        ))
        db.add(AuditLog(
            transaction_id=db_txn.id,
            action_type="INVESTIGATION_DISPATCHED",
            actor="system",
            payload={"alert_id": alert.id, "tier": db_txn.risk_tier}
        ))
        publish_alert_event(
            {
                "event_type": "alert_created",
                "alert_id": alert.id,
                "transaction_id": db_txn.id,
                "risk_tier": db_txn.risk_tier,
                "investigation_status": "PENDING",
                "created_at": datetime.utcnow().isoformat(),
            }
        )
        run_investigation.delay(alert.id)
        
    db.commit()
    db.refresh(db_txn)
    
    return result

@router.get("/{id}", response_model=TransactionSchema)
async def get_transaction(id: str, db: Session = Depends(get_db)):
    db_txn = db.query(Transaction).filter(Transaction.id == id).first()
    if not db_txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_txn

@router.get("/{id}/audit")
async def get_transaction_audit(id: str, db: Session = Depends(get_db)):
    audits = db.query(AuditLog).filter(AuditLog.transaction_id == id).order_by(AuditLog.timestamp.asc()).all()
    return audits

@router.get("/{id}/explain")
async def explain_transaction(id: str, db: Session = Depends(get_db), scorer = Depends(get_scorer), explainer = Depends(get_explainer)):
    db_txn = db.query(Transaction).filter(Transaction.id == id).first()
    if not db_txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    # Get history
    history = db.query(Transaction).filter(
        Transaction.account_id == db_txn.account_id,
        Transaction.id != db_txn.id
    ).order_by(Transaction.timestamp.desc()).limit(50).all()
    
    import pandas as pd
    history_df = pd.DataFrame([t.__dict__ for t in history]) if history else None
    if history_df is not None:
        history_df = history_df.drop(columns=['_sa_instance_state'], errors='ignore')
        
    # Transform
    if history_df is not None and not history_df.empty:
        df_eval = pd.concat([history_df, pd.DataFrame([db_txn.__dict__])], ignore_index=True)
        X_eval = scorer.fe.transform(df_eval)
        X_txn = X_eval.iloc[[-1]]
    else:
        df_eval = pd.DataFrame([db_txn.__dict__])
        X_txn = scorer.fe.transform(df_eval)
        
    explanation = explainer.explain_instance(X_txn)
    return explanation

@router.get("/{id}/report", response_model=InvestigationReportSchema)
async def get_transaction_report(id: str, db: Session = Depends(get_db)):
    report = (
        db.query(InvestigationReport)
        .filter(InvestigationReport.transaction_id == id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Investigation report not found")
    return report

@router.get("/{id}/score/stream")
async def score_transaction_stream(id: str, db: Session = Depends(get_db), scorer = Depends(get_scorer)):
    """
    SSE streaming version of transaction scoring.
    """
    db_txn = db.query(Transaction).filter(Transaction.id == id).first()
    if not db_txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    async def event_generator():
        # 1. Start evaluation
        yield {"event": "status", "data": "Evaluation started"}
        await asyncio.sleep(0.2)
        
        # Get history
        history = db.query(Transaction).filter(
            Transaction.account_id == db_txn.account_id,
            Transaction.id != db_txn.id
        ).order_by(Transaction.timestamp.desc()).limit(50).all()
        
        import pandas as pd
        history_df = pd.DataFrame([t.__dict__ for t in history]) if history else None
        if history_df is not None:
            history_df = history_df.drop(columns=['_sa_instance_state'], errors='ignore')
            
        # 2. Rule evaluation
        rule_results = scorer.rules_engine.evaluate(db_txn.__dict__, history_df)
        yield {"event": "rules", "data": json.dumps(rule_results)}
        await asyncio.sleep(0.2)
        
        # 3. ML Scoring
        # (This is simplified, reusing the scorer's logic partially to show streaming)
        if history_df is not None and not history_df.empty:
            df_eval = pd.concat([history_df, pd.DataFrame([db_txn.__dict__])], ignore_index=True)
            X_eval = scorer.fe.transform(df_eval)
            X_txn = X_eval.iloc[[-1]]
        else:
            df_eval = pd.DataFrame([db_txn.__dict__])
            X_txn = scorer.fe.transform(df_eval)
            
        iso_scores = scorer.iso_forest.decision_function(X_txn)
        ml_score_raw = 0.5 - iso_scores[0]
        ml_anomaly_score = float(np.clip(ml_score_raw, 0, 1))
        
        yield {"event": "ml", "data": json.dumps({"ml_anomaly_score": ml_anomaly_score})}
        await asyncio.sleep(0.2)
        
        # 4. Final Score
        final_score = (rule_results['rule_score'] * 0.4) + (ml_anomaly_score * 100 * 0.6)
        final_score = float(np.clip(final_score, 0, 100))
        
        tier = "LOW"
        if final_score > 30: tier = "MEDIUM"
        if final_score > 60: tier = "HIGH"
        if final_score > 80: tier = "CRITICAL"
        
        reason_codes = rule_results['rule_triggers'].copy()
        if ml_anomaly_score > 0.6:
            reason_codes.append(f"High ML Anomaly Score ({ml_anomaly_score:.2f})")
        
        result = {
            "risk_score": round(final_score, 2),
            "risk_tier": tier,
            "rule_triggers": rule_results['rule_triggers'],
            "ml_anomaly_score": round(ml_anomaly_score, 4),
            "reason_codes": reason_codes[:3],
            "scored_at": datetime.utcnow().isoformat()
        }
        
# Persist results
        db_txn.risk_score = result['risk_score']
        db_txn.risk_tier = result['risk_tier']
        db_txn.reason_codes = result['reason_codes']
        db_txn.status = "SCORED"
        
        # Audit: rule evaluation
        db.add(AuditLog(
            transaction_id=db_txn.id,
            action_type="RULE_EVALUATED",
            actor="system",
            payload={"rule_triggers": result['rule_triggers']}
        ))
        # Audit: ML scoring
        db.add(AuditLog(
            transaction_id=db_txn.id,
            action_type="ML_SCORED",
            actor="system",
            payload={"ml_anomaly_score": ml_anomaly_score}
        ))
        
        if tier in ["HIGH", "CRITICAL"]:
            db_txn.status = "FLAGGED"
            alert = Alert(
                transaction_id=db_txn.id,
                risk_tier=tier,
                rule_triggers=rule_results['rule_triggers'],
                ml_anomaly_score=ml_anomaly_score,
                reason_codes=result['reason_codes']
            )
            db.add(alert)
            db.flush()
            # Audit: alert creation
            db.add(AuditLog(
                transaction_id=db_txn.id,
                action_type="ALERT_CREATED",
                actor="system",
                payload={"alert_id": alert.id, "tier": tier}
            ))
            # Audit: investigation dispatched
            db.add(AuditLog(
                transaction_id=db_txn.id,
                action_type="INVESTIGATION_DISPATCHED",
                actor="system",
                payload={"alert_id": alert.id, "tier": tier}
            ))
            publish_alert_event(
                {
                    "event_type": "alert_created",
                    "alert_id": alert.id,
                    "transaction_id": db_txn.id,
                    "risk_tier": tier,
                    "investigation_status": "PENDING",
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            run_investigation.delay(alert.id)
            
        db.commit()
        
        yield {"event": "final", "data": json.dumps(result)}

    async def sse_stream():
        async for e in event_generator():
            yield f"event: {e['event']}\ndata: {e['data']}\n\n"

    return StreamingResponse(sse_stream(), media_type="text/event-stream")
