from datetime import datetime
from typing import Union

from celery.result import AsyncResult
from pydantic import BaseModel

from app.tasks import TaskResult


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
            self.tasks[task_id].task_result = task_result.result #TaskResult.model_validate(task_result.result)

            if task_result.state == 'PROGRESS':
                self.tasks[task_id].log = task_result.info.get('log', '')


        result_dict = self.tasks[task_id].task_submission.dict()
        result_dict.update({'task_id': task_id})
        if self.tasks[task_id].task_result is not None:
            result_dict.update(self.tasks[task_id].task_result)
        # TODO: this creates duplication
        if self.tasks[task_id].log is not None:
            result_dict.update({'log': self.tasks[task_id].log})
        return result_dict


class SubmitDockerJob(BaseModel):
    image: str = 'ubuntu'
    command: str = 'echo "hello world"'
    gpus: int = 0
    dry_run: bool = False
