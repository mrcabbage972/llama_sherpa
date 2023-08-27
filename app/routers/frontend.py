from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.auth import query_user, manager
from app.data import TaskSubmission
from app.tasks import docker_task

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request, "result": request.app.state.task_registry.get_tasks()})


@router.get('/task_info/{task_id}')
def task_info(request: Request, task_id: str):
    task = request.app.state.task_registry.get_task(task_id, update=True)
    return templates.TemplateResponse("task_info.html", context={"request": request, "result": task})

@router.get("/submit")
def submit_job(request: Request):
    return templates.TemplateResponse("submit_job.html", context={"request": request})



@router.post("/submit")
def submit_job(request: Request, image: Annotated[str, Form()],
               command: Annotated[str, Form()],
               env: Annotated[str, Form()],
               dry_run: Annotated[bool, Form()] = False):
    num_gpus = 0 # TODO: add to form
    env = env.split(';')
    task = docker_task.delay(image, command, num_gpus, dry_run, env)
    request.app.state.task_registry.add_task(task, TaskSubmission(image=image, command=command, dry_run=dry_run, gpus=num_gpus, env=env))
    return RedirectResponse(
        '/',
        status_code=status.HTTP_302_FOUND)

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
    elif password != user['password']:
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