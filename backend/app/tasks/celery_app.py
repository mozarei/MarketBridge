from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "crosslist",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.jobs"],
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
)
