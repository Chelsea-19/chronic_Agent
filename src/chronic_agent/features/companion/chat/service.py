from __future__ import annotations

from sqlalchemy.orm import Session

from chronic_agent.agent.chat import ChatAgent
from chronic_agent.features.companion.service import CompanionService
from chronic_agent.features.health.service import HealthTrackingService
from chronic_agent.platform.repositories import ChatRepository


class CompanionChatService:
    def __init__(self, db: Session, patient_id: int):
        self.chat_repo = ChatRepository(db, patient_id)
        self.health_service = HealthTrackingService(db, patient_id)
        self.companion_service = CompanionService(db, patient_id)
        self.agent = ChatAgent()

    def handle_message(self, message: str):
        self.chat_repo.add('user', message)
        if message.strip().startswith('[TRACK]'):
            self.health_service.track_from_chat(message)
            reply = '已记录。你可以继续补充今天的血糖、血压、饮食、体重或症状。'
            self.chat_repo.add('assistant', reply)
            return {'reply': reply, 'tracked': True}

        recent = [(m.role, m.content) for m in self.chat_repo.recent(limit=8)]
        today = self.companion_service.today_view()
        extra_context = (
            f"\n【今日概览】待处理提醒 {today.pending_reminders} 条；"
            f"最近空腹血糖 {today.latest_fasting_glucose or '暂无'}；"
            f"最近血压 {today.latest_blood_pressure or '暂无'}。"
        )
        reply = self.agent.reply(message, recent, extra_context)
        self.chat_repo.add('assistant', reply)
        return {'reply': reply, 'tracked': False}

    def list_messages(self):
        return self.chat_repo.recent(limit=50)
