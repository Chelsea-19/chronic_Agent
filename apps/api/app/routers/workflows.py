from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.deps import get_patient_id, get_session
from chronic_agent.core.contracts import WorkflowRequest, WorkflowRunOut
from chronic_agent.features.workflows.service import WorkflowService
from chronic_agent.platform.security import require_bearer_token

router = APIRouter(prefix='/workflows', tags=['workflows'])


@router.post('/run', response_model=WorkflowRunOut, dependencies=[Depends(require_bearer_token)])
def run_workflow(payload: WorkflowRequest, db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    row = WorkflowService(db, patient_id).run(payload)
    return WorkflowRunOut(id=row.id, patient_id=row.patient_id, workflow_type=row.workflow_type, status=row.status, current_state=row.current_state, summary=row.summary, created_at=row.created_at, updated_at=row.updated_at, log=json.loads(row.log_json or '[]'))


@router.get('/runs', response_model=list[WorkflowRunOut], dependencies=[Depends(require_bearer_token)])
def list_runs(db: Session = Depends(get_session), patient_id: int = Depends(get_patient_id)):
    rows = WorkflowService(db, patient_id).list_runs()
    return [WorkflowRunOut(id=r.id, patient_id=r.patient_id, workflow_type=r.workflow_type, status=r.status, current_state=r.current_state, summary=r.summary, created_at=r.created_at, updated_at=r.updated_at, log=json.loads(r.log_json or '[]')) for r in rows]
