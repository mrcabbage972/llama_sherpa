from fastapi import APIRouter, Depends
from requests import Session
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.db.db import User, get_db
from app.dependencies import get_current_active_superuser

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get('/list_users')
def login(request: Request, sess: Session = Depends(get_db), user=Depends(get_current_active_superuser)):
    users = sess.query(User).all()

    return templates.TemplateResponse("list_users.html", context={"request": request, 'users': users})