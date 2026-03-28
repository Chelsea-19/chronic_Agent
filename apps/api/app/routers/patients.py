from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_session
from chronic_agent.core.contracts import FollowUpCreate, FollowUpOut, PatientCreate, PatientOut, TimelineItemOut
from chronic_agent.features.patients.service import PatientService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(prefix='/patients', tags=['patients'])


@router.post('', response_model=PatientOut, dependencies=[Depends(require_bearer_token)])
def create_patient(payload: PatientCreate, db: Session = Depends(get_session)):
    return PatientService(db).create_patient(payload)


@router.get('', response_model=list[PatientOut], dependencies=[Depends(require_bearer_token)])
def list_patients(db: Session = Depends(get_session)):
    return PatientService(db).list_patients()


@router.get('/{patient_id}', response_model=PatientOut, dependencies=[Depends(require_bearer_token)])
def get_patient(patient_id: int, db: Session = Depends(get_session)):
    return PatientService(db).get_patient(patient_id)


@router.post('/{patient_id}/followups', response_model=FollowUpOut, dependencies=[Depends(require_bearer_token)])
def create_followup(patient_id: int, payload: FollowUpCreate, db: Session = Depends(get_session)):
    return PatientService(db).create_followup(patient_id, payload)


@router.get('/{patient_id}/followups', response_model=list[FollowUpOut], dependencies=[Depends(require_bearer_token)])
def list_followups(patient_id: int, db: Session = Depends(get_session)):
    return PatientService(db).list_followups(patient_id)


@router.get('/{patient_id}/timeline', response_model=list[TimelineItemOut], dependencies=[Depends(require_bearer_token)])
def timeline(patient_id: int, db: Session = Depends(get_session)):
    return PatientService(db).timeline(patient_id)
