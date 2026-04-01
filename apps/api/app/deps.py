from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from chronic_agent.platform.db import get_db
from chronic_agent.platform.settings import settings


@dataclass
class LLMConfig:
    """Holds per-request LLM credentials forwarded from the browser."""
    api_key: str
    base_url: str
    model: str


def get_settings():
    return settings


def get_session() -> Session:
    yield from get_db()


def get_patient_id(x_patient_id: int | None = Header(default=None)) -> int:
    return x_patient_id or 1


def get_llm_config(
    x_llm_api_key: str | None = Header(default=None),
    x_llm_base_url: str | None = Header(default=None),
    x_llm_model: str | None = Header(default=None),
) -> LLMConfig:
    """Extract LLM configuration from request headers.

    If the server-side flag `enable_fake_llm` is True, missing headers are
    tolerated and the service layer will use fake responses instead.
    Otherwise a clear HTTP 400 is raised asking the user to configure their
    API key first.
    """
    if not settings.enable_fake_llm:
        if not x_llm_api_key or not x_llm_base_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='请先在前端页面的"设置"中配置 LLM API Key 和 Base URL。',
            )
    return LLMConfig(
        api_key=x_llm_api_key or '',
        base_url=x_llm_base_url or '',
        model=x_llm_model or settings.default_llm_model,
    )
