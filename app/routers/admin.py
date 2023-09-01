from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from requests import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.auth import query_user, manager, verify_password, hash_password
from app.db.db import User, get_db

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get('/list_users')
def login(request: Request, sess: Session = Depends(get_db), user=Depends(manager)):
    users = sess.query(User).all()

    return templates.TemplateResponse("list_users.html", context={"request": request, 'users': users})