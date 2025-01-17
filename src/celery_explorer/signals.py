from celery.signals import task_prerun, after_task_publish
from django.utils import timezone
import celery
import json


@task_prerun.connect
def save_task_received_timestamp(sender=None, **kwargs):
    task_id = sender.request.id
    backend = celery.current_app.backend
    if backend:
        now = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        backend.set(f"celery-task-started-timestamp-{task_id}", now)


@after_task_publish.connect
def save_tasks_history(sender=None, headers=None, body=None, **kwargs):
    info = headers if "task" in headers else body
    info_dict = {"status": "PENDING", "task_id": info["id"], "name": info["task"]}
    backend = celery.current_app.backend
    if backend:
        backend.set(f"celery-task-meta-{info_dict['task_id']}", json.dumps(info_dict))
        backend.client.rpush("celery-task-history", info_dict["task_id"])
        now = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        backend.set(f"celery-task-received-timestamp-{info_dict['task_id']}", now)
