from celery import Celery
from app.core.config import settings

# Create the Celery app
celery_app = Celery(
    "app",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["app.tasks.batch_tasks"],
)

# Optional: Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,  # Don't prefetch more than one task
)

if __name__ == "__main__":
    celery_app.start()
