from fastapi import Header, HTTPException, status

from .settings import settings


async def require_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if settings.app_env == 'dev' and not authorization:
        return 'dev-user'
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing bearer token')
    token = authorization.replace('Bearer ', '', 1).strip()
    if token != settings.auth_bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid bearer token')
    return 'demo-user'
