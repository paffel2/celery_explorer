from django.urls import path
from task_creator.views import MakeTaskAPIView



urlpatterns = [
    path("test",MakeTaskAPIView.as_view(), name="test_task" )
]