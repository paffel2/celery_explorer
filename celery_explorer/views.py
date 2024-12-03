import celery
from django.shortcuts import render
import inspect
from itertools import zip_longest
import celery.result
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Parameter, IN_QUERY
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class ShowTaskListAPIView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        tasks = celery.current_app.tasks
        result = []
        for key, value in tasks.items():
            if "celery." in key:
                continue
            signature = inspect.signature(value)
            result.append(f"{key}{signature}")

        return JsonResponse({"tasks": result})


class GetFullTaskInfoAPIView(GenericAPIView):

    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                "name",
                IN_QUERY,
                type="string",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        if name:
            task = celery.current_app.tasks.get(name)
            if task:
                arg_specs = inspect.getfullargspec(task)
                return JsonResponse({"task": name, "specs": arg_specs.args})

        return Response(status=404)


class ExecuteTaskAPIView(GenericAPIView):
    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                "name",
                IN_QUERY,
                type="string",
            ),
            Parameter(
                "args",
                IN_QUERY,
                type="string",
            ),
            Parameter(
                "countdown",
                IN_QUERY,
                type="int",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        args = request.query_params.get("args", "")
        countdown = 0
        try:
            countdown = int(request.query_params.get("countdown", 0))
        except TypeError:
            return JsonResponse({"error": "bad countdown value"}, status=400)
        if name:
            task = celery.current_app.tasks.get(name)
            if task:
                task_signature = inspect.signature(task)
                signature_params = task_signature.parameters
                task_id = None
                status = "NOT STARTED"
                if not args and not signature_params:
                    task_id = str(task.apply_async(countdown=countdown))
                    status = "STARTED"
                elif signature_params:
                    params = []
                    list_of_params = args.split(",") if args else []
                    if len(list_of_params) > len(signature_params):
                        return JsonResponse({"error": "too much parameters"}, status=400)

                    for str_param, param in zip_longest(list_of_params, signature_params.values()):
                        param_type = param.annotation
                        value = None
                        if str_param is None and param.default is not inspect._empty:
                            value = param.default
                        else:
                            try:
                                value = param_type(str_param)
                            except (TypeError, ValueError):
                                return JsonResponse({"error": f"bad type of {param.name}"}, status=400)
                        params.append(value)
                    task_id = str(task.apply_async(params, countdown=countdown))
                    status = "STARTED"

                else:
                    status = "WRONG PARAMETERS"
                return JsonResponse({"task": name, "task_id": task_id, "status": status})
            else:
                return JsonResponse({"error": "task not founded"}, status=400)

        return Response(status=404)


class CheckTaskStatusAPIView(GenericAPIView):
    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                "task_id",
                IN_QUERY,
                type="string",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        task_id = request.query_params.get("task_id")
        if task_id:
            res = celery.result.AsyncResult(task_id).state
            return JsonResponse({"result": res})
        else:
            return JsonResponse({"error": "task not founded"}, status=400)


def task_list_index(request):
    tasks = celery.current_app.tasks
    result = []
    for key, value in tasks.items():
        if "celery." in key:
            continue
        task = {}
        task["name"] = key
        result.append(task)

    return render(template_name="task_list.html")
