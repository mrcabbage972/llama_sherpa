from fastapi import Depends
from fastapi import HTTPException

from app.auth import manager


def get_current_active_superuser(
        current_user=Depends(manager)):
    if not current_user['is_superuser']:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
