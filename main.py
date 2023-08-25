from typing import Annotated

import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI, Request, Form
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from tasks import docker_task, task_list_tasks
from datetime import datetime

class TaskRegistry:
    def __init__(self):
        self.tasks = {'a': {'status': 'SUCCESS', 'result': 'a', 'start_time': datetime.now()}}

    def add_task(self, task):
        self.tasks[task.id] = {'status': task.status, 'result': task.result, 'start_time': datetime.now()}

    def get_tasks(self):
        return self.tasks

    def get_task(self, task_id, update=False):
        if update:
            task_result = AsyncResult(task_id)
            self.tasks[task_id].update({'status': task_result.status, 'result': task_result.result})
        return self.tasks[task_id]



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
    return templates.TemplateResponse("submit_job.html", context={"request": request, "result": None})



@app.post("/submit")
def submit_job(request: Request, image: Annotated[str, Form()],
               command: Annotated[str, Form()],
               env: Annotated[str, Form()],
               dry_run: Annotated[bool, Form()] = False):
    task = docker_task.delay(image, command, 0, dry_run, env.split(';'))
    app.state.task_registry.add_task(task)
    return templates.TemplateResponse("submit_job.html", context={"request": request, "result": task.id})


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
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result

@app.get('/list_tasks')
def list_tasks():
    return task_list_tasks.run()

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)