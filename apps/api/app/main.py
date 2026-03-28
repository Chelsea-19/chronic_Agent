from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.routers import attach_static, router
from chronic_agent.platform.settings import settings

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, '*'] if settings.app_env == 'dev' else [settings.frontend_origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
attach_static(app)
app.include_router(router, prefix=settings.api_prefix)
