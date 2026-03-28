from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from apps.api.app.deps import get_settings
from chronic_agent.core.contracts import HealthCheckOut

router = APIRouter()


@router.get('/healthz', response_model=HealthCheckOut)
def healthz(settings=Depends(get_settings)):
    return HealthCheckOut(status='ok', app=settings.app_name, env=settings.app_env)


def attach_static(app: FastAPI):
    base = Path(__file__).resolve().parent.parent / 'static'
    app.mount('/static', StaticFiles(directory=str(base)), name='static')

    @app.get('/', response_class=HTMLResponse)
    def index():
        return (base / 'index.html').read_text(encoding='utf-8')
