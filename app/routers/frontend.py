from typing import Annotated

from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter, Depends
from fastapi import Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.auth import query_user, manager
from app.data import TaskSubmission
from app.db.db import SessionLocal
from app.db.db import TaskSubmission as TaskSubmissionDB
from app.tasks import docker_task

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request,
                                                            "result": request.app.state.task_registry.get_tasks()})


@router.get('/task_info/{task_id}')
def task_info(request: Request, task_id: str):
    task = request.app.state.task_registry.get_task(task_id, update=True)
    abort_url = f'/abort/{task_id}'
    resubmit_url = f'/submit?task_id={task_id}'
    context_dict = {"request": request, "result": task, 'abort_url': abort_url, 'resubmit_url': resubmit_url}
    return templates.TemplateResponse("task_info.html", context=context_dict)


@router.get("/submit")
def submit_job(request: Request, task_id: str = None):
    # TODO: use depends for this
    if task_id is None:
        task = TaskSubmission()
    else:
        session = SessionLocal()
        task = session.query(TaskSubmissionDB).filter(TaskSubmissionDB.id == task_id).one()
    return templates.TemplateResponse("submit_job.html", context={"request": request, "task": task})


@router.post("/submit")
def submit_job(request: Request, image: Annotated[str, Form()],
               command: Annotated[str, Form()],
               env: Annotated[str, Form()],
               dry_run: Annotated[bool, Form()] = False):
    num_gpus = 0  # TODO: add to form
    env = env.split(';')
    task = docker_task.delay(image, command, num_gpus, dry_run, env)
    request.app.state.task_registry.add_task(task, TaskSubmission(image=image, command=command, dry_run=dry_run,
                                                                  gpus=num_gpus, env=env))
    return RedirectResponse(
        '/',
        status_code=status.HTTP_302_FOUND)


@router.get("/abort/{task_id}")
def abort(request: Request, task_id: str):
    AbortableAsyncResult(task_id).abort()
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
