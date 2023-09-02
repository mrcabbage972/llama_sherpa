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


@router.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})


@router.post('/login')
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = query_user(username)
    if not user:
        raise InvalidCredentialsException
    elif not verify_password(password, user['password']):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data={'sub': username}
    )
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
    manager.set_cookie(response, access_token)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse('/', status_code=302)
    response.delete_cookie(key=manager.cookie_name)
    return response


@router.get('/signup')
def signup(request: Request):
    return templates.TemplateResponse("signup.html", context={"request": request})


@router.post("/signup")
def signup(username: Annotated[str, Form()],
           email: Annotated[str, Form()],
           password: Annotated[str, Form()],
           db: Session = Depends(get_db)):
    # TODO: hash password
    hashed_password = hash_password(password)

    user = User(username=username, email=email, password=hashed_password, is_superuser=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)


@router.get('/change_password/{username}')
def signup(request: Request, username: str):
    return templates.TemplateResponse("change_password.html", context={"request": request, "username": username})

@router.post("/change_password/{username}")
def signup(username: str,
           password: Annotated[str, Form()],
           db: Session = Depends(get_db)):
    user = db.query(User).where(User.username == username).one()
    user.password = hash_password(password)
    db.commit()
    return RedirectResponse('/list_users', status_code=status.HTTP_302_FOUND)