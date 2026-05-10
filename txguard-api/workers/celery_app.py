from celery import Celery
from api.config import settings
from agents.crew import create_investigation_crew
from api.database import SessionLocal
from api.models.alert import Alert
from api.models.report import InvestigationReport
from api.models.audit import AuditLog
import uuid
import json
from api.realtime import publish_alert_event


def _extract_report_payload(raw_output: str) -> dict:
    try:
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw_output[start : end + 1])
    except Exception:
        pass
    return {}

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
        parsed = _extract_report_payload(output_text)
        
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
            behavioral_analysis=parsed.get("decision_rationale", "Investigation completed."),
            typology_assessment={"key_risk_factors": parsed.get("key_risk_factors", [])},
            regulatory_assessment=parsed.get("executive_summary", "No regulatory summary provided."),
            recommended_action=parsed.get("recommended_action", action),
            confidence_score=float(parsed.get("confidence_score", 0.75)),
            evidence_citations=parsed.get("evidence_citations", []),
            agent_run_metadata={"crew_output": output_text, "next_actions": parsed.get("next_actions", [])},
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
        db.add(
            AuditLog(
                transaction_id=alert.transaction_id,
                action_type="REPORT_WRITTEN",
                actor="system",
                payload={"alert_id": alert.id, "report_id": report.id},
            )
        )
        db.commit()
        
        publish_alert_event(
            {
                "event_type": "investigation_complete",
                "alert_id": alert.id,
                "transaction_id": alert.transaction_id,
                "investigation_status": "COMPLETE",
                "recommended_action": report.recommended_action,
            }
        )
        
        return {"status": "success", "alert_id": alert_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
