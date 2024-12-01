from celery import shared_task
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


@shared_task
def test_task():
    print("TEST VALUE")


@shared_task
def test_task_with_args(a: int, b: str):
    print(f"{a} + {b}")


@shared_task
def test_task_with_default_args(a: int = 0, b: str = "string"):
    print(f"{a} + {b}")


class MakeTaskAPIView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        task_id = test_task.apply_async()
        print(f"{task_id=}")
        return Response("OK")
