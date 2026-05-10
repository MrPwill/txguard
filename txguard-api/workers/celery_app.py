from celery import Celery
from api.config import settings
from agents.crew import create_investigation_crew
from api.database import SessionLocal
from api.models.alert import Alert
from api.models.report import InvestigationReport
from api.models.audit import AuditLog
import uuid
import json

celery_app = Celery(
    "txguard_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="run_investigation")
def run_investigation(alert_id: str):
    """
    Executes the multi-agent investigation pipeline for an alert.
    """
    db = SessionLocal()
    try:
        # Update alert status
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {"error": "Alert not found"}
            
        alert.investigation_status = "IN_PROGRESS"
        db.commit()

        # Instantiate crew
        crew = create_investigation_crew(alert.id, alert.transaction_id)
        
        # Run the crew
        result = crew.kickoff()
        output_text = str(result)
        
        # Determine the recommended action from the result text
        action = "MONITOR"
        if "ESCALATE_TO_SAR" in output_text: action = "ESCALATE_TO_SAR"
        elif "BLOCK_AND_HOLD" in output_text: action = "BLOCK_AND_HOLD"
        elif "CLEAR" in output_text: action = "CLEAR"
        
        # Create InvestigationReport
        report = InvestigationReport(
            id=str(uuid.uuid4()),
            alert_id=alert.id,
            transaction_id=alert.transaction_id,
            behavioral_analysis="Extracted behavioral analysis summary.",
            typology_assessment={"summary": "Extracted typology assessment."},
            regulatory_assessment="Extracted regulatory assessment.",
            recommended_action=action,
            confidence_score=0.85,
            evidence_citations={"output": output_text},
            agent_run_metadata={"crew_output": output_text}
        )
        db.add(report)
        
        # Update alert
        alert.investigation_status = "COMPLETE"
        
        # Audit Log
        payload = {
            "alert_id": alert.id, 
            "recommended_action": action,
            "crew_output": output_text
        }
        if hasattr(result, 'token_usage'):
            payload["token_usage"] = result.token_usage
            
        audit = AuditLog(
            transaction_id=alert.transaction_id,
            action_type="AGENT_COMPLETED",
            actor="system",
            payload=payload
        )
        db.add(audit)
        db.commit()
        
        # Broadcast completion to WebSocket via internal publish mechanism if configured
        
        return {"status": "success", "alert_id": alert_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
