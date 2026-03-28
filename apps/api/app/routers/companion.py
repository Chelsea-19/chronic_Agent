from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import CompanionTodayOut
from chronic_agent.features.companion.service import CompanionService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(prefix='/companion', tags=['companion'])


@router.get('/today', response_model=CompanionTodayOut, dependencies=[Depends(require_bearer_token)])
def today(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return CompanionService(db, patient_id).today_view()


@router.get('/insights', dependencies=[Depends(require_bearer_token)])
def insights(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return CompanionService(db, patient_id).insights()
