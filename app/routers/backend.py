from celery.result import AsyncResult
from fastapi import Depends, APIRouter

from app.auth import manager
from app.data import SubmitDockerJob
from app.tasks import docker_task

router = APIRouter()


@router.post("/tasks", status_code=201)
def submit_docker_job(payload: SubmitDockerJob):
    task = docker_task.delay(payload.image, payload.command, payload.gpus, payload.dry_run)
    return {"task_id": task.id}


@router.get("/task_status/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status and task_result.result['success'],
        "task_result": task_result.result['stdout'],
        "task_end_time": task_result.result['end_time']
    }
    return result


@router.get('/protected')
def protected_route(user=Depends(manager)):
    return {'user': user}
