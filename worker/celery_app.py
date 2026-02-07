import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url,
from worker.tasks.upscale_task import upscale_image
from worker.tasks.rip_task import rip_separation
from worker.main import pipeline_task

# Ensure tasks are registered
celery_app.conf.update(
    include=["worker.tasks.upscale_task", "worker.tasks.rip_task", "worker.main"]
)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
