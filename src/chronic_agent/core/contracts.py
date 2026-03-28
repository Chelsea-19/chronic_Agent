from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str
    tracked: bool = False


class MedicationCreate(BaseModel):
    medicine_name: str
    dose: str = ''
    schedule: str = '早餐后'
    notes: str = ''


class MedicationOut(BaseModel):
    id: int
    patient_id: int
    medicine_name: str
    dose: str
    schedule: str
    notes: str
    active: bool


class ReminderOccurrenceOut(BaseModel):
    id: int
    medication_id: int
    medicine_name: str
    schedule_label: str
    scheduled_for: date
    status: str


class ReminderStatusUpdate(BaseModel):
    status: Literal['pending', 'done', 'skipped']


class HealthEventOut(BaseModel):
    id: int
    patient_id: int
    event_type: str
    value_text: str
    value_num1: Optional[float] = None
    value_num2: Optional[float] = None
    unit: str = ''
    source: str = 'chat'
    created_at: datetime


class SummaryOut(BaseModel):
    date: date
    latest_blood_pressure: Optional[str] = None
    latest_fasting_glucose: Optional[float] = None
    active_medications: int
    pending_reminders: int


class DigestOut(BaseModel):
    id: int
    patient_id: int
    window_days: int
    markdown: str


class HealthCheckOut(BaseModel):
    status: str
    app: str
    env: str


class CompanionTodayOut(BaseModel):
    date: date
    latest_blood_pressure: Optional[str] = None
    latest_fasting_glucose: Optional[float] = None
    meal_risk_tags: list[str] = []
    pending_reminders: int
    coach_message: str


class MealAnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)
    meal_time: str = 'auto'
    source: str = 'text'


class MealRecordOut(BaseModel):
    id: int
    patient_id: int
    meal_time: str
    description: str
    risk_tags: str
    estimated_carbs: Optional[float] = None
    estimated_sodium_mg: Optional[float] = None
    source: str
    created_at: datetime


class MealSummaryOut(BaseModel):
    window: str
    total_records: int
    top_risk_tags: list[str]
    avg_estimated_carbs: Optional[float] = None
    avg_estimated_sodium_mg: Optional[float] = None


class WorkflowRequest(BaseModel):
    workflow_type: Literal['daily_review', 'medication_reconciliation', 'previsit_digest']
    payload: dict = Field(default_factory=dict)


class WorkflowRunOut(BaseModel):
    id: int
    patient_id: int
    workflow_type: str
    status: str
    current_state: str
    summary: str
    created_at: datetime
    updated_at: datetime
    log: list[dict] = []


class ReportRequest(BaseModel):
    report_type: Literal['patient_weekly', 'clinician_previsit', 'adherence_overview']
    window_days: int = 7


class ReportOut(BaseModel):
    id: int
    patient_id: int
    report_type: str
    window_days: int
    title: str
    markdown: str
    created_at: datetime


class PatientCreate(BaseModel):
    name: str
    gender: str = ''
    age: Optional[int] = None
    diagnosis_summary: str = '2型糖尿病合并高血压'
    phone: str = ''


class PatientOut(BaseModel):
    id: int
    name: str
    gender: str
    age: Optional[int] = None
    diagnosis_summary: str
    phone: str
    created_at: datetime


class FollowUpCreate(BaseModel):
    scheduled_for: date
    purpose: str = '复诊'
    notes: str = ''
    status: str = 'planned'


class FollowUpOut(BaseModel):
    id: int
    patient_id: int
    scheduled_for: date
    purpose: str
    notes: str
    status: str
    created_at: datetime


class TimelineItemOut(BaseModel):
    item_type: str
    occurred_at: datetime
    title: str
    detail: str

