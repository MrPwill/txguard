from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.report import InvestigationReport
from ..schemas.report import InvestigationReport as ReportSchema

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{txn_id}", response_model=ReportSchema)
async def get_report_by_transaction(txn_id: str, db: Session = Depends(get_db)):
    report = db.query(InvestigationReport).filter(InvestigationReport.transaction_id == txn_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Investigation report not found")
    return report
