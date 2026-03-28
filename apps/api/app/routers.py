from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from apps.api.app.deps import get_session, get_settings
from chronic_agent.core.contracts import (
    ChatRequest,
    ChatResponse,
    DigestOut,
    HealthCheckOut,
    HealthEventOut,
    MedicationCreate,
    MedicationOut,
    ReminderOccurrenceOut,
    ReminderStatusUpdate,
    SummaryOut,
)
from chronic_agent.features.clinician_digest.service import ClinicianDigestService
from chronic_agent.features.companion.chat.service import CompanionChatService
from chronic_agent.features.health.service import HealthTrackingService
from chronic_agent.features.medications.service import MedicationService
from chronic_agent.features.reminders.service import ReminderService
from chronic_agent.platform.repositories import HealthRepository, MedicationRepository, ReminderRepository
from chronic_agent.platform.security import require_bearer_token

router = APIRouter()


@router.get("/healthz", response_model=HealthCheckOut)
def healthz(settings=Depends(get_settings)):
    return HealthCheckOut(status="ok", app=settings.app_name, env=settings.app_env)


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_bearer_token)])
def chat(payload: ChatRequest, db: Session = Depends(get_session)):
    service = CompanionChatService(db)
    return service.handle_message(payload.message)


@router.get("/messages", dependencies=[Depends(require_bearer_token)])
def list_messages(db: Session = Depends(get_session)):
    service = CompanionChatService(db)
    rows = service.list_messages()
    return [{"id": r.id, "role": r.role, "content": r.content, "created_at": r.created_at.isoformat()} for r in rows]


@router.get("/health-events", response_model=list[HealthEventOut], dependencies=[Depends(require_bearer_token)])
def health_events(db: Session = Depends(get_session)):
    rows = HealthTrackingService(db).list_recent()
    return [
        HealthEventOut(
            id=r.id,
            event_type=r.event_type,
            value_text=r.value_text,
            value_num1=r.value_num1,
            value_num2=r.value_num2,
            unit=r.unit,
            source=r.source,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/medications", response_model=MedicationOut, dependencies=[Depends(require_bearer_token)])
def create_medication(payload: MedicationCreate, db: Session = Depends(get_session)):
    row = MedicationService(db).create(**payload.model_dump())
    return MedicationOut(id=row.id, medicine_name=row.medicine_name, dose=row.dose, schedule=row.schedule, notes=row.notes, active=row.active)


@router.get("/medications", response_model=list[MedicationOut], dependencies=[Depends(require_bearer_token)])
def list_medications(db: Session = Depends(get_session)):
    rows = MedicationService(db).list_active()
    return [MedicationOut(id=r.id, medicine_name=r.medicine_name, dose=r.dose, schedule=r.schedule, notes=r.notes, active=r.active) for r in rows]


@router.delete("/medications/{med_id}", dependencies=[Depends(require_bearer_token)])
def delete_medication(med_id: int, db: Session = Depends(get_session)):
    MedicationService(db).deactivate(med_id)
    return {"ok": True}


@router.post("/reminders/generate-today", dependencies=[Depends(require_bearer_token)])
def generate_today(db: Session = Depends(get_session)):
    rows = ReminderService(db).generate_today()
    return {"created": len(rows)}


@router.get("/reminders", response_model=list[ReminderOccurrenceOut], dependencies=[Depends(require_bearer_token)])
def list_today_reminders(db: Session = Depends(get_session)):
    rows = ReminderService(db).list_today()
    return [
        ReminderOccurrenceOut(
            id=r.id,
            medication_id=r.medication_id,
            medicine_name=r.medication.medicine_name,
            schedule_label=r.schedule_label,
            scheduled_for=r.scheduled_for,
            status=r.status,
        )
        for r in rows
    ]


@router.post("/reminders/{occurrence_id}", dependencies=[Depends(require_bearer_token)])
def update_reminder(occurrence_id: int, payload: ReminderStatusUpdate, db: Session = Depends(get_session)):
    row = ReminderService(db).update_status(occurrence_id, payload.status)
    if row is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"ok": True}


@router.post("/digest", response_model=DigestOut, dependencies=[Depends(require_bearer_token)])
def generate_digest(db: Session = Depends(get_session)):
    row = ClinicianDigestService(db).generate()
    return DigestOut(id=row.id, window_days=row.window_days, markdown=row.content_markdown)


@router.get("/summary", response_model=SummaryOut, dependencies=[Depends(require_bearer_token)])
def summary(db: Session = Depends(get_session)):
    health_repo = HealthRepository(db)
    med_repo = MedicationRepository(db)
    reminder_repo = ReminderRepository(db)
    events = health_repo.list_recent(limit=50)
    latest_bp = next((e for e in events if e.event_type == "blood_pressure" and e.value_num1 and e.value_num2), None)
    latest_fg = next((e for e in events if e.event_type == "fasting_glucose" and e.value_num1 is not None), None)
    return SummaryOut(
        date=__import__("datetime").date.today(),
        latest_blood_pressure=(f"{latest_bp.value_num1:.0f}/{latest_bp.value_num2:.0f} mmHg" if latest_bp else None),
        latest_fasting_glucose=(latest_fg.value_num1 if latest_fg else None),
        active_medications=len(med_repo.list_active()),
        pending_reminders=reminder_repo.pending_count(),
    )


def attach_static(app: FastAPI):
    base = Path(__file__).resolve().parent
    static_dir = base / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index():
        return (static_dir / "index.html").read_text(encoding="utf-8")
