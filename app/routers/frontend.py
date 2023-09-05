from collections import OrderedDict
from typing import Annotated
from typing import Optional

from celery.contrib.abortable import AbortableAsyncResult
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Request
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.data import TaskSubmission
from app.db.db import SessionLocal
from app.db.db import TaskSubmission as TaskSubmissionDB
from app.dependencies import get_user_for_job_submit
from app.settings import get_settings
from app.tasks import docker_task

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request):
    request.app.state.task_registry.update_all()

    task_dict = request.app.state.task_registry.get_tasks()
    sorted_tasks = OrderedDict(sorted(task_dict.items(), key=lambda x: x[1].task_submission.start_time, reverse=True))

    return templates.TemplateResponse("home.html", context={"request": request,
                                                            "result": sorted_tasks})


@router.get('/task_info/{task_id}')
def task_info(request: Request, task_id: str):
    task = request.app.state.task_registry.get_task(task_id, update=True)
    abort_url = f'/abort/{task_id}'
    resubmit_url = f'/submit?task_id={task_id}'
    context_dict = {"request": request, "result": task, 'abort_url': abort_url, 'resubmit_url': resubmit_url}
    return templates.TemplateResponse("task_info.html", context=context_dict)


@router.get("/submit")
def submit_job(request: Request, task_id: str = None, predefined_job: str = None,
               user=Depends(get_user_for_job_submit)
               ):
    if predefined_job is not None:
        job = get_settings().predefined_jobs[predefined_job]
        ports = ';'.join([f'{k}:{v}' for k, v in job.ports.items()])
        task = TaskSubmission(image=job.image, command=job.command, env=job.env, ports=ports).model_dump()
    elif task_id is None:
        task = TaskSubmission().model_dump()
        task['env'] = ''
        task['ports'] = ''
    else:
        session = SessionLocal()
        task = session.query(TaskSubmissionDB).filter(TaskSubmissionDB.id == task_id).one()
    return templates.TemplateResponse("submit_job.html", context={"request": request, "task": task})


@router.post("/submit")
def submit_job_post(
        request: Request, image: Annotated[str, Form()],
        command: Annotated[str, Form()],
        env: Optional[str] = Form(None),
        ports: Optional[str] = Form(None),
        gpus: Optional[int] = Form(None),
        dry_run: Annotated[bool, Form()] = False,
        user=Depends(get_user_for_job_submit)):
    num_gpus = 0 if gpus is None else gpus
    if env is not None:
        env = env.split(';')
    else:
        env = []

    if ports is not None:
        ports_dict = {(x.split(':')[0] + '/tcp'): x.split(':')[1] for x in ports.split(';') if x != ''}
    else:
        ports_dict = {}
    task = docker_task.delay(image, command, num_gpus, dry_run, env, ports_dict)

    if user is None:
        username = 'unknown'
    else:
        username = user['username']

    submission = TaskSubmission(image=image, user=username, command=command, dry_run=dry_run, gpus=num_gpus, env=env)
    request.app.state.task_registry.add_task(task, submission)
    return RedirectResponse(
        '/',
        status_code=status.HTTP_302_FOUND)


@router.get("/abort/{task_id}")
def abort(request: Request, task_id: str):
    AbortableAsyncResult(task_id).abort()
    return RedirectResponse(
        '/',
        status_code=status.HTTP_302_FOUND)


@router.get("/job_templates")
def job_templates(request: Request):
    return templates.TemplateResponse("job_templates.html", context={"request": request,
                                                                     "job_templates": get_settings().predefined_jobs})
