from django.urls import path
from task_creator.views import start_task


urlpatterns = [path("test", start_task, name="test_task")]
