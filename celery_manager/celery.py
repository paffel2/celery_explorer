import os

from celery import Celery
from src.celery_explorer.signals import save_task_received_timestamp

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery_manager.settings")

app = Celery("celery_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.update(result_extended=True)
