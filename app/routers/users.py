from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.auth import manager

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})


@router.post('/login')
def login_post(request: Request, data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    request.app.state.user_manager.authenticate(username, password)

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
def signup_post(request: Request,
                username: Annotated[str, Form()],
                email: Annotated[str, Form()],
                password: Annotated[str, Form()]):
    request.app.state.user_manager.create_user(username, email, password)
    return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)


@router.get('/change_password/{username}')
def change_password(request: Request, username: str):
    return templates.TemplateResponse("change_password.html", context={"request": request, "username": username})


@router.post("/change_password/{username}")
def change_password_post(request: Request,
                    username: str,
                    password: Annotated[str, Form()]):
    request.app.state.user_manager.change_password(username, password)
    return RedirectResponse('/list_users', status_code=status.HTTP_302_FOUND)


@router.get('/delete_user/{username}')
def delete_user(request: Request,
                username: str):
    request.app.state.user_manager.delete_user(username)
    return RedirectResponse('/list_users', status_code=status.HTTP_302_FOUND)


@router.get('/make_superuser/{username}')
def make_superuser(request: Request,
                   username: str):
    request.app.state.user_manager.make_superuser(username)
    return RedirectResponse('/list_users', status_code=status.HTTP_302_FOUND)
