from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from chronic_agent.agent.chat import LLMParams
from chronic_agent.platform.repositories import ChatRepository

class CompanionChatService:
    def __init__(self, db: Session, patient_id: int, llm_params: Optional[LLMParams] = None):
        self.db = db
        self.patient_id = patient_id
        self.chat_repo = ChatRepository(db, patient_id)
        self.llm_params = llm_params

    def handle_message(self, message: str):
        from chronic_agent.agent.orchestrator import Orchestrator
        # 1. Store user message
        self.chat_repo.add('user', message)
        
        # 2. Get history
        recent = [(m.role, m.content) for m in self.chat_repo.recent(limit=8)]
        
        # 3. Handle with orchestrator
        orch = Orchestrator(self.db, self.patient_id)
        result = orch.handle_message(message, recent, llm_params=self.llm_params)
        
        # 4. Store assistant response
        self.chat_repo.add('assistant', result["reply"])
        
        return {
            "reply": result["reply"],
            "tracked": result.get("has_tool_use", False),
            "trace": result.get("trace", [])
        }

    def list_messages(self):
        return self.chat_repo.recent(limit=50)
