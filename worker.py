import docker
from celery.app import Celery
from datetime import datetime
import os

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
def docker_task(image, command, gpus):
    client = docker.from_env()
    gpu_device_request = docker.types.DeviceRequest(device_ids=["0,2"], capabilities=[['gpu']])
    client.containers.run('ubuntu',
                          "nvidia-smi",
                          device_requests=[
                              gpu_device_request])