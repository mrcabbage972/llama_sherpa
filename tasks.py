import docker
from celery.app import Celery
from datetime import datetime
import os

from celery.bin.control import inspect
from docker.errors import ContainerError, APIError

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)


@app.task
def dummy_task():
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")


@app.task()
def docker_task(image, command, gpus, dry_run, env):
    if not dry_run:
        client = docker.from_env()

        if gpus > 0:
            gpu_device_request = docker.types.DeviceRequest(device_ids=["0,2"], capabilities=[['gpu']])
            device_requests = [gpu_device_request]
        else:
            device_requests = None

        try:
            result = client.containers.run(image,
                                  command,
                                    environment=env,
                                  device_requests=device_requests)
        except ContainerError as e:
            return {'stdout': str(e), 'success': False, 'end_time': datetime.now()}
        except APIError as e:
            return {'stdout': str(e), 'success': False, 'end_time': datetime.now()}
        return {'stdout': result.decode("utf-8"), 'success': True, 'end_time': datetime.now()}

    else:
        return {'stdout': "", 'success': True, 'end_time': datetime.now()}

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