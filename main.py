import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI
from pydantic import BaseModel

from worker import docker_task

app = FastAPI()


class SubmitDockerJob(BaseModel):
    image: str = 'ubuntu'
    command: str = 'nvidia-smi'
    gpus: int = 0
    dry_run: bool = False


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/tasks", status_code=201)
def submit_docker_job(payload: SubmitDockerJob):
    task = docker_task.delay(payload.image, payload.command, payload.gpus)
    return {"task_id": task.id}


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
