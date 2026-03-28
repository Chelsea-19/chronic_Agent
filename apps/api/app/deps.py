from __future__ import annotations

from fastapi import Header
from sqlalchemy.orm import Session

from chronic_agent.platform.db import get_db
from chronic_agent.platform.settings import settings


def get_settings():
    return settings


def get_session() -> Session:
    yield from get_db()


def get_patient_id(x_patient_id: int | None = Header(default=None)) -> int:
    return x_patient_id or 1
