import logging
import os
import time
from datetime import datetime

import celery
import docker
from celery.app import Celery
from celery.contrib.abortable import AbortableTask
from docker.errors import ContainerError, APIError
from requests import ReadTimeout

from app.data import TaskResult

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.task
def dummy_task():
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")


class DockerTask(celery.Task):
    def __init__(self):
        super().__init__()
        self.container = None
        self.hi = False

@app.task(bind=True, base=AbortableTask)
def docker_task(self, image, command, gpus, dry_run, env):
    if not dry_run:
        client = docker.from_env()

        if gpus > 0:
            gpu_device_request = docker.types.DeviceRequest(device_ids=["0,2"], capabilities=[['gpu']])
            device_requests = [gpu_device_request]
        else:
            device_requests = None

        try:
            self.container = client.containers.run(image,
                                  command,
                                    environment=env,
                                  device_requests=device_requests,
                                           detach=True)

            is_aborted = False
            while self.container.status != 'exited':
                if self.is_aborted():
                    is_aborted = True
                    break

                self.container.reload()
                output_accum = self.container.logs(stdout=True).decode("utf-8")

                if not self.request.called_directly:
                    self.update_state(state='PROGRESS', meta={'log': output_accum})
                time.sleep(1)

            if is_aborted:
                self.container.stop(timeout=10)
                self.container.remove()
                return_val = TaskResult(stdout=None, success=False, is_aborted=True)
            else:
                exit_status = self.container.wait(timeout=1)['StatusCode']

                if exit_status != 0:
                    out = self.container.logs(stdout=False, stderr=True)
                else:
                    out = self.container.logs(
                        stdout=True, stderr=False, stream=False, follow=False)
                self.container.remove()

                return_val = TaskResult(stdout=out.decode("utf-8"), success=True)
        except (ContainerError, ReadTimeout, APIError) as e:
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
