from typing import Annotated

import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI, Request, Form
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from tasks import docker_task, task_list_tasks

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.get("/submit")
def submit_job(request: Request):
    return templates.TemplateResponse("submit_job.html", context={"request": request, "result": None})



@app.post("/submit")
def submit_job(request: Request, image: Annotated[str, Form()], command: Annotated[str, Form()]):
    result = {'a': 'b', 'c': 'd'}
    return templates.TemplateResponse("submit_job.html", context={"request": request, "result": result})


class SubmitDockerJob(BaseModel):
    image: str = 'ubuntu'
    command: str = 'echo "hello world"'
    gpus: int = 0
    dry_run: bool = False


@app.get("/")
def read_root():
    return {"Hello": "World"}


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