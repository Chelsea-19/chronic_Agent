from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import ReportOut, ReportRequest
from chronic_agent.features.reports.service import ReportService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(prefix='/reports', tags=['reports'])


@router.post('/generate', response_model=ReportOut, dependencies=[Depends(require_bearer_token)])
def generate_report(payload: ReportRequest, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return ReportService(db, patient_id).generate(payload)


@router.get('', response_model=list[ReportOut], dependencies=[Depends(require_bearer_token)])
def list_reports(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return ReportService(db, patient_id).list_reports()


@router.get('/{report_id}/export', dependencies=[Depends(require_bearer_token)])
def export_report(report_id: int, fmt: str = 'pdf', db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    try:
        path = ReportService(db, patient_id).export(report_id, fmt)
    except ValueError as e:
        raise HTTPException(status_code=404 if 'not found' in str(e) else 400, detail=str(e))
    media = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'html': 'text/html',
    }[fmt]
    return FileResponse(path, media_type=media, filename=path.name)
