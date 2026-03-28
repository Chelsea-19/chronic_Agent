from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import ReminderOccurrenceOut, ReminderStatusUpdate
from chronic_agent.features.reminders.service import ReminderService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(tags=['reminders'])


@router.post('/reminders/generate-today', dependencies=[Depends(require_bearer_token)])
def generate_today(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    rows = ReminderService(db, patient_id).generate_today()
    return {'created': len(rows)}


@router.get('/reminders', response_model=list[ReminderOccurrenceOut], dependencies=[Depends(require_bearer_token)])
def list_today_reminders(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    rows = ReminderService(db, patient_id).list_today()
    return [ReminderOccurrenceOut(id=r.id, medication_id=r.medication_id, medicine_name=r.medication.medicine_name, schedule_label=r.schedule_label, scheduled_for=r.scheduled_for, status=r.status) for r in rows]


@router.post('/reminders/{occurrence_id}', dependencies=[Depends(require_bearer_token)])
def update_reminder(occurrence_id: int, payload: ReminderStatusUpdate, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    row = ReminderService(db, patient_id).update_status(occurrence_id, payload.status)
    if row is None:
        raise HTTPException(status_code=404, detail='Reminder not found')
    return {'ok': True}
