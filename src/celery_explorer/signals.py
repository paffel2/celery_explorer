from celery.signals import task_prerun, task_received
from django.utils import timezone
import celery


@task_prerun.connect
def save_task_received_timestamp(sender=None, **kwargs):
    task_id = sender.request.id
    backend = celery.current_app.backend
    if backend:
        now = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        backend.set(f"celery-task-started-timestamp-{task_id}", now)
