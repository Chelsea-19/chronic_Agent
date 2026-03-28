from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import MedicationCreate, MedicationOut
from chronic_agent.features.medications.service import MedicationService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(tags=['medications'])


@router.post('/medications', response_model=MedicationOut, dependencies=[Depends(require_bearer_token)])
def create_medication(payload: MedicationCreate, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    row = MedicationService(db, patient_id).create(**payload.model_dump())
    return MedicationOut.model_validate(row, from_attributes=True)


@router.get('/medications', response_model=list[MedicationOut], dependencies=[Depends(require_bearer_token)])
def list_medications(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return [MedicationOut.model_validate(r, from_attributes=True) for r in MedicationService(db, patient_id).list_active()]


@router.delete('/medications/{med_id}', dependencies=[Depends(require_bearer_token)])
def delete_medication(med_id: int, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    MedicationService(db, patient_id).deactivate(med_id)
    return {'ok': True}
