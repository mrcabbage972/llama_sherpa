import base64
from io import BytesIO

import matplotlib.pyplot as plt
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from gpu_tracker import GpuTracker

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

gpu_tracker = GpuTracker()


@router.get("/metrics", response_class=HTMLResponse)
async def read_gpu_usage(request: Request):

    gpu_usages = gpu_tracker.get_gpu_usage()  # Get GPU usage data from the GpuTracker class

    x = [f"GPU {i}" for i in range(len(gpu_usages))]
    y = gpu_usages

    plt.figure(figsize=(8, 6))
    plt.bar(x, y)
    plt.xlabel("GPU")
    plt.ylabel("Usage (%)")
    plt.title("GPU Usage")
    plt.xticks(rotation=45)

    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    plt.close()

    img_data = base64.b64encode(img_stream.getvalue()).decode()
    return templates.TemplateResponse("metrics.html", context={"img_data": img_data})