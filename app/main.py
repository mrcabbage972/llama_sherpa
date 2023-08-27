import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles

from app.auth import manager, NotAuthenticatedException
from app.data import TaskRegistry, SubmitDockerJob
from app.db.db import SessionLocal, User
from app.routers import frontend
from app.routers.frontend import templates
from app.tasks import docker_task

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.state.task_registry = TaskRegistry()
manager.useRequest(app)

app.include_router(frontend.router)


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





@app.get('/protected')
def protected_route(user=Depends(manager)):
    return {'user': user}


@app.exception_handler(NotAuthenticatedException)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse("no_creds.html", context={"request": request})


def ensure_first_user():
    sess = SessionLocal()
    users = sess.query(User).all()
    if len(users) == 0:
        # TODO: get from config
        sess.add(User(username="a", password="a", email="g", is_superuser=True))
        sess.commit()


if __name__ == '__main__':
    ensure_first_user()

    uvicorn.run(app, host="127.0.0.1", port=8001)
