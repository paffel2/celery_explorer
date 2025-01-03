from celery import shared_task
from django.http import JsonResponse


@shared_task
def test_task():
    """task description"""
    print("TEST VALUE")


@shared_task
def test_task_with_args(a: int, b: str):
    """task description"""
    print(f"{a} + {b}")


@shared_task
def test_task_with_default_args(a: int = 0, b: str = "string"):
    print(f"{a} + {b}")


def start_task(self, request, *args, **kwargs):
    task_id = test_task.apply_async()
    print(f"{task_id=}")
    return JsonResponse({"status": "OK"})
