from datetime import datetime
from typing import Union, Optional

from celery.result import AsyncResult
from pydantic import BaseModel
from app.db.db import TaskSubmission as TaskSubmissionDB, SessionLocal


class TaskSubmission(BaseModel):
    start_time: datetime = datetime.now()
    image: str = 'python:3.11.2-slim-buster'
    command: str = 'date'
    gpus: int = 0
    dry_run: bool = False
    env: Optional[list] = None


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
        # populate from db
        self.tasks = {}
        self.session = SessionLocal()
        query_result = self.session.query(TaskSubmissionDB).all()
        for task_submission_db in query_result:
            env = task_submission_db.env.split(';')
            task_submission = TaskSubmission(start_time=task_submission_db.start_time,
                                            image=task_submission_db.image, command=task_submission_db.command,
                                            gpus=task_submission_db.gpus, dry_run=task_submission_db.dry_run,
                                            env=env)
            # TODO: currently not populating
            self.tasks[task_submission_db.id] = TaskData(status='UNKNOWN', task_submission=task_submission)

    def add_task(self, celery_task, task_submission: TaskSubmission):
        self.tasks[celery_task.id] = TaskData(status=celery_task.status, task_submission=task_submission)
        self.session.add(TaskSubmissionDB(id=celery_task.id, start_time=datetime.now(), image=task_submission.image,
                            command=task_submission.command, gpus=task_submission.gpus, dry_run=task_submission.dry_run,
                            env=';'.join(task_submission.env)))
        self.session.commit()


    def get_tasks(self):
        return self.tasks

    def get_task(self, task_id, update=False):
        if update:
            self.update_task(task_id)

        return self.tasks[task_id].model_dump()

    def update_task(self, task_id):
        task_result = AsyncResult(task_id)
        self.tasks[task_id].status = task_result.status
        if task_result.result is not None:
            if 'is_aborted' in task_result.result and task_result.result['is_aborted']:
                self.tasks[task_id].status = 'ABORTED' # TODO: create/reuse enum for states
            elif 'success' in task_result.result and not task_result.result['success']:
                self.tasks[task_id].status = 'FAILURE'
        self.tasks[task_id].task_result = task_result.result
        if task_result.state == 'PROGRESS':
            self.tasks[task_id].log = task_result.info.get('log', '')

    def update_all(self):
        for task_id in self.tasks:
            self.update_task(task_id)


class SubmitDockerJob(BaseModel):
    image: str = 'ubuntu'
    command: str = 'echo "hello world"'
    gpus: int = 0
    dry_run: bool = False

