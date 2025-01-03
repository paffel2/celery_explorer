from celery.signals import task_prerun
from django.utils import timezone
import celery


@task_prerun.connect
def save_task_received_timestamp(sender=None, **kwargs):
    task_id = sender.request.id
    back = celery.current_app.backend
    if back:
        print(back)
        now = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        back.set(f"celery-task-started-timestamp-{task_id}", now)
