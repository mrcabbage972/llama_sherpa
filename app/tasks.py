import time
from typing import Union

import docker
from celery.app import Celery
from datetime import datetime
import os

from docker.errors import ContainerError, APIError
from pydantic import BaseModel
from requests import ReadTimeout

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)


class TaskResult(BaseModel):
    end_time: Union[datetime, None] = datetime.now()
    stdout: Union[str, None] = None
    success: Union[bool, None] = None


@app.task
def dummy_task():
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")


@app.task(bind=True)
def docker_task(self, image, command, gpus, dry_run, env):
    return_val = None
    if not dry_run:
        client = docker.from_env()

        if gpus > 0:
            gpu_device_request = docker.types.DeviceRequest(device_ids=["0,2"], capabilities=[['gpu']])
            device_requests = [gpu_device_request]
        else:
            device_requests = None

        try:
            container = client.containers.run(image,
                                  command,
                                    environment=env,
                                  device_requests=device_requests,
                                           detach=True)

            while container.status != 'exited':
                container.reload()
                output_accum = container.logs(stdout=True).decode("utf-8")
                self.update_state(state='PROGRESS', meta={'log': output_accum})
                time.sleep(1)
            exit_status = container.wait(timeout=1)['StatusCode']

            if exit_status != 0:
                out = container.logs(stdout=False, stderr=True)
            else:
                out = container.logs(
                    stdout=True, stderr=False, stream=False, follow=False)
            container.remove()

            return_val = TaskResult(stdout=out.decode("utf-8"), success=True)
        except ContainerError | ReadTimeout | APIError as e:
            return_val =  TaskResult(stdout=str(e), success=False)
    else:
        return_val = TaskResult(stdout="", success=True)
    return return_val.model_dump()

@app.task()
def task_list_tasks():
    i = app.control.inspect()

    active_tasks = i.active()
    reserved_tasks = i.reserved()
    revoked_tasks = i.revoked()
    scheduled_tasks = i.scheduled()

    return {
        'active_tasks': active_tasks,
        'reserved_tasks': reserved_tasks,
        'revoked_tasks': revoked_tasks,
        'scheduled_tasks': scheduled_tasks
    }