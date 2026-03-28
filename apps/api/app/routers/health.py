from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import HealthEventOut, SummaryOut
from chronic_agent.features.companion.service import CompanionService
from chronic_agent.features.health.service import HealthTrackingService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(tags=['health'])


@router.get('/health-events', response_model=list[HealthEventOut], dependencies=[Depends(require_bearer_token)])
def health_events(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    rows = HealthTrackingService(db, patient_id).list_recent()
    return [HealthEventOut.model_validate(r, from_attributes=True) for r in rows]


@router.get('/summary', response_model=SummaryOut, dependencies=[Depends(require_bearer_token)])
def summary(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return CompanionService(db, patient_id).summary()
