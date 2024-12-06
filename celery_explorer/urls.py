from django.urls import path
from django.conf import settings
from celery_explorer.views import check_task_status, get_task_detail, task_index, tasks_list, get_task_list


urlpatterns = (
    [
        path("task_detail", get_task_detail, name="task_detail"),
        path("check_task_status", check_task_status, name="check_task_status"),
        path("", task_index, name="task_explorer"),
        path("tasks_list", tasks_list, name="tasks_list"),
        path("tasks_list_by_name", get_task_list, name="tasks_list_by_name"),
    ]
    if settings.CELERY_MANAGER_ENABLED or settings.DEBUG
    else []
)
