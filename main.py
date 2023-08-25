from typing import Annotated, Union

import fastapi
import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.openapi.models import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from auth import query_user, manager
from tasks import docker_task, task_list_tasks, TaskResult
from datetime import datetime, timedelta


class TaskSubmission(BaseModel):
    start_time: datetime = datetime.now()
    image: str = 'python:3.11.2-slim-buster'
    command: str = 'date'
    gpus: int = 0
    dry_run: bool = False
    env: list = []

class TaskData(BaseModel):
    status: str = 'SUCCESS'
    task_submission: TaskSubmission = TaskSubmission()
    task_result: Union[TaskResult, None] = None

class TaskRegistry:
    def __init__(self):
        self.tasks = {'a': TaskData()} # TODO: set to empty dict

    def add_task(self, celery_task, task_submission: TaskSubmission):
        self.tasks[celery_task.id] = TaskData(status=celery_task.status, task_submission=task_submission)

    def get_tasks(self):
        return self.tasks

    def get_task(self, task_id, update=False):
        # TODO: refactor, this is ugly
        if update:
            task_result = AsyncResult(task_id)
            self.tasks[task_id].status = task_result.status
            self.tasks[task_id].task_result = task_result.result #TaskResult.model_validate(task_result.result)

        result_dict = self.tasks[task_id].task_submission.dict()
        result_dict.update({'task_id': task_id})
        if self.tasks[task_id].task_result is not None:
            result_dict.update(self.tasks[task_id].task_result)
        return result_dict


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.state.task_registry = TaskRegistry()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request, "result": app.state.task_registry.get_tasks()})


@app.get('/task_info/{task_id}')
def task_info(request: Request, task_id: str):
    task = app.state.task_registry.get_task(task_id, update=True)
    return templates.TemplateResponse("task_info.html", context={"request": request, "result": task})

@app.get("/submit")
def submit_job(request: Request):
    return templates.TemplateResponse("submit_job.html", context={"request": request})



@app.post("/submit")
def submit_job(request: Request, image: Annotated[str, Form()],
               command: Annotated[str, Form()],
               env: Annotated[str, Form()],
               dry_run: Annotated[bool, Form()] = False):
    num_gpus = 0 # TODO: add to form
    env = env.split(';')
    task = docker_task.delay(image, command, num_gpus, dry_run, env)
    app.state.task_registry.add_task(task, TaskSubmission(image=image, command=command, dry_run=dry_run, gpus=num_gpus, env=env))
    return fastapi.responses.RedirectResponse(
        '/',
        status_code=status.HTTP_302_FOUND)
    #return templates.TemplateResponse("submit_job.html", context={"request": request, "result": task.id})


class SubmitDockerJob(BaseModel):
    image: str = 'ubuntu'
    command: str = 'echo "hello world"'
    gpus: int = 0
    dry_run: bool = False

@app.post("/tasks", status_code=201)
def submit_docker_job(payload: SubmitDockerJob):
    task = docker_task.delay(payload.image, payload.command, payload.gpus, payload.dry_run)
    return {"task_id": task.id}


@app.get("/task_status/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status and task_result.result['success'],
        "task_result": task_result.result['stdout'],
        "task_end_time": task_result.result['end_time']
    }
    return result

@app.get('/list_tasks')
def list_tasks():
    return task_list_tasks.run()


@app.post('/login')
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
    response = JSONResponse({'access_token': access_token})
    manager.set_cookie(response, access_token)
    return response

@app.get('/protected')
def protected_route(user=Depends(manager)):
    return {'user': user}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)