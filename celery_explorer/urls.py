from django.urls import path
from celery_explorer.views import ShowTaskListAPIView, GetFullTaskInfoAPIView, ExecuteTaskAPIView, CheckTaskStatusAPIView


urlpatterns = [
    path("show_tasks_list", ShowTaskListAPIView.as_view(), name="show_tasks_list"),
    path("task_detail", GetFullTaskInfoAPIView.as_view(), name="task_detail"),
    path("execute_task", ExecuteTaskAPIView.as_view(), name="execute_task"),
    path("check_task_status", CheckTaskStatusAPIView.as_view(), name="check_task_status"),
    # path("task_explorer/", TaskApplyView.as_view(), name="task_explorer"),
]
