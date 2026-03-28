from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import DigestOut
from chronic_agent.features.clinician_digest.service import ClinicianDigestService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(tags=['digest'])


@router.post('/digest', response_model=DigestOut, dependencies=[Depends(require_bearer_token)])
def generate_digest(window_days: int = Query(default=14, ge=1, le=90), db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    row = ClinicianDigestService(db, patient_id).generate(window_days)
    return DigestOut(id=row.id, patient_id=row.patient_id, window_days=row.window_days, markdown=row.content_markdown)
