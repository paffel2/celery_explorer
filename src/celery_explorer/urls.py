from django.urls import path
from celery_explorer.views import check_task_status, get_task_detail, task_index


urlpatterns = [
    path("task_detail", get_task_detail, name="task_detail"),
    path("check_task_status", check_task_status, name="check_task_status"),
    path("", task_index, name="task_explorer"),
]
