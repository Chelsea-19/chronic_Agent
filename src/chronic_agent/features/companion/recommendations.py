from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta

from chronic_agent.platform.repositories import HealthRepository, MedicationRepository, ReminderRepository, PatientRepository

@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    priority: int  # 1 (High) to 3 (Low)
    action_type: str  # 'input', 'workflow', 'view'
    action_payload: dict

class RecommendationService:
    def __init__(self, db: Session, patient_id: int):
        self.db = db
        self.patient_id = patient_id
        self.health_repo = HealthRepository(db, patient_id)
        self.med_repo = MedicationRepository(db, patient_id)
        self.reminder_repo = ReminderRepository(db, patient_id)

    def get_recommendations(self) -> List[Recommendation]:
        recs = []
        today = date.today()
        
        # 1. Check for missing data (Blood Pressure / Glucose)
        recent_events = self.health_repo.list_recent(limit=50)
        today_events = [e for e in recent_events if e.created_at.date() == today]
        
        has_today_bp = any(e.event_type == 'blood_pressure' for e in today_events)
        if not has_today_bp:
            recs.append(Recommendation(
                id="missing_bp",
                title="补录今日血压",
                description="今日尚未记录血压，规律监测有助于稳定控压。",
                priority=1,
                action_type="input",
                action_payload={"placeholder": "血压 130/85"}
            ))

        has_today_fg = any(e.event_type == 'fasting_glucose' for e in today_events)
        if not has_today_fg:
            recs.append(Recommendation(
                id="missing_fg",
                title="补录今日空腹血糖",
                description="早起空腹血糖是评估基础糖代谢的关键指标。",
                priority=1,
                action_type="input",
                action_payload={"placeholder": "空腹血糖 6.5"}
            ))

        # 2. Check medication adherence
        pending_reminders = self.reminder_repo.list_today()
        if any(r.status == 'pending' for r in pending_reminders):
            recs.append(Recommendation(
                id="adherence_check",
                title="检查今日用药",
                description="尚有未确认的服药提醒，请确保按时服药。",
                priority=1,
                action_type="view",
                action_payload={"tab": "reminders"}
            ))

        # 3. Predict need for Pre-visit Digest if follow-up is near (within 3 days)
        patient_repo = PatientRepository(self.db)
        patient = patient_repo.get(self.patient_id)
        followups = patient_repo.list_followups(self.patient_id) if hasattr(patient_repo, 'list_followups') else []
        # Wait, let's use the DB query directly if repo is limited
        from chronic_agent.platform.models import FollowUp
        near_followup = self.db.query(FollowUp).filter(
            FollowUp.patient_id == self.patient_id,
            FollowUp.status == 'planned',
            FollowUp.scheduled_for >= today,
            FollowUp.scheduled_for <= today + timedelta(days=3)
        ).first()

        if near_followup:
            recs.append(Recommendation(
                id="previsit_prep",
                title="生成门诊前摘要",
                description=f"您在 {near_followup.scheduled_for} 有一次复诊，建议提前准备临床摘要。",
                priority=2,
                action_type="workflow",
                action_payload={"workflow": "previsit_digest"}
            ))
        
        # 4. Meal risk analysis (If recent meals had multiple risks)
        meal_events = [e for e in recent_events if e.event_type == 'meal_risk']
        if len(meal_events) >= 2:
            recs.append(Recommendation(
                id="diet_warning",
                title="添加低盐/低脂饮食提醒",
                description="近期多次记录到高盐或高脂饮食，建议加强饮食干预。",
                priority=2,
                action_type="input",
                action_payload={"placeholder": "提醒我：下次聚餐少点红烧肉"}
            ))

        # Default fallback if empty
        if not recs:
            recs.append(Recommendation(
                id="all_clear",
                title="保持良好状态",
                description="今日表现非常棒！继续保持规律的监测和用药。",
                priority=3,
                action_type="view",
                action_payload={}
            ))

        return sorted(recs, key=lambda x: x.priority)
