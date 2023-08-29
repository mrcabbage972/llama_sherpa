from datetime import datetime
from typing import Union

from celery.result import AsyncResult
from pydantic import BaseModel


class TaskSubmission(BaseModel):
    start_time: datetime = datetime.now()
    image: str = 'python:3.11.2-slim-buster'
    command: str = 'date'
    gpus: int = 0
    dry_run: bool = False
    env: list = []


class TaskResult(BaseModel):
    end_time: Union[datetime, None] = datetime.now()
    stdout: Union[str, None] = None
    success: Union[bool, None] = None
    is_aborted: Union[bool, None] = False


class TaskData(BaseModel):
    status: str = 'SUCCESS'
    task_submission: TaskSubmission = TaskSubmission()
    task_result: Union[TaskResult, None] = None
    log: str = None


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
            if task_result.result is not None and 'is_aborted' in task_result.result and task_result.result['is_aborted']:
                self.tasks[task_id].status = 'ABORTED'

            self.tasks[task_id].task_result = task_result.result #TaskResult.model_validate(task_result.result)

            if task_result.state == 'PROGRESS':
                self.tasks[task_id].log = task_result.info.get('log', '')

        return self.tasks[task_id].model_dump()


class SubmitDockerJob(BaseModel):
    image: str = 'ubuntu'
    command: str = 'echo "hello world"'
    gpus: int = 0
    dry_run: bool = False

