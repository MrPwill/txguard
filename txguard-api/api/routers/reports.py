from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.report import InvestigationReport
from ..models.alert import Alert
from ..schemas.report import InvestigationReport as ReportSchema

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{txn_id}", response_model=ReportSchema)
async def get_report_by_transaction(txn_id: str, db: Session = Depends(get_db)):
    report = db.query(InvestigationReport).filter(InvestigationReport.transaction_id == txn_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Investigation report not found")
    return report


@router.get("/alert/{alert_id}")
async def get_report_by_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    report = db.query(InvestigationReport).filter(InvestigationReport.alert_id == alert_id).first()
    if not report:
        return {
            "alert_id": alert.id,
            "transaction_id": alert.transaction_id,
            "risk_tier": alert.risk_tier,
            "investigation_status": alert.investigation_status,
        }

    return {
        "id": report.id,
        "alert_id": report.alert_id,
        "transaction_id": report.transaction_id,
        "risk_tier": alert.risk_tier,
        "investigation_status": alert.investigation_status,
        "behavioral_analysis": report.behavioral_analysis,
        "typology_assessment": report.typology_assessment,
        "regulatory_assessment": report.regulatory_assessment,
        "recommended_action": report.recommended_action,
        "confidence_score": report.confidence_score,
        "evidence_citations": report.evidence_citations,
        "agent_run_metadata": report.agent_run_metadata,
        "generated_at": report.generated_at,
    }
