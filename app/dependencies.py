from fastapi import Depends
from fastapi import HTTPException
from starlette.requests import Request

from app.auth import manager
from app.settings import get_settings


def get_current_active_superuser(
        current_user=Depends(manager)):
    if not current_user['is_superuser']:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_user_for_job_submit(request: Request):
    if get_settings().require_login_for_submit:
        return await manager.__call__(request)
    else:
        return None
