from fastapi import APIRouter

from .chat import router as chat_router
from .health import router as health_router
from .medications import router as medications_router
from .reminders import router as reminders_router
from .digest import router as digest_router
from .companion import router as companion_router
from .meals import router as meals_router
from .workflows import router as workflows_router
from .reports import router as reports_router
from .patients import router as patients_router
from .system import router as system_router, attach_static

router = APIRouter()
for child in [system_router, chat_router, health_router, medications_router, reminders_router, digest_router, companion_router, meals_router, workflows_router, reports_router, patients_router]:
    router.include_router(child)
