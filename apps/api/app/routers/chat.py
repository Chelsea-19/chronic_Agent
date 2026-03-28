from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import ChatRequest, ChatResponse
from chronic_agent.features.companion.chat.service import CompanionChatService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(tags=['chat'])


@router.post('/chat', response_model=ChatResponse, dependencies=[Depends(require_bearer_token)])
def chat(payload: ChatRequest, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    return CompanionChatService(db, patient_id).handle_message(payload.message)


@router.get('/messages', dependencies=[Depends(require_bearer_token)])
def list_messages(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    rows = CompanionChatService(db, patient_id).list_messages()
    return [{'id': r.id, 'role': r.role, 'content': r.content, 'created_at': r.created_at.isoformat()} for r in rows]
