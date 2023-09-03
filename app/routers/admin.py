from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.dependencies import get_current_active_superuser

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get('/list_users')
def list_users(request: Request, user=Depends(get_current_active_superuser)):
    users = request.app.state.user_manager.get_users()

    return templates.TemplateResponse("list_users.html", context={"request": request, 'users': users})
