from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import MealAnalyzeRequest, MealRecordOut, MealSummaryOut
from chronic_agent.features.meals.service import MealService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(prefix='/meals', tags=['meals'])


@router.post('/analyze', dependencies=[Depends(require_bearer_token)])
def analyze_meal(payload: MealAnalyzeRequest, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return MealService(db, patient_id).analyze_and_record(payload)


@router.get('/records', response_model=list[MealRecordOut], dependencies=[Depends(require_bearer_token)])
def meal_records(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    rows = MealService(db, patient_id).list_records(limit=50)
    return [MealRecordOut.model_validate(r, from_attributes=True) for r in rows]


@router.get('/daily-summary', response_model=MealSummaryOut, dependencies=[Depends(require_bearer_token)])
def daily_summary(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return MealService(db, patient_id).daily_summary()


@router.get('/weekly-summary', response_model=MealSummaryOut, dependencies=[Depends(require_bearer_token)])
def weekly_summary(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return MealService(db, patient_id).weekly_summary()
