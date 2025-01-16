import celery
from django import template
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime
import json


import inspect
from itertools import zip_longest
import celery.result
from django.http import JsonResponse, HttpResponseNotFound


@require_GET
def get_task_detail(request, *args, **kwargs):
    name = request.GET.get("name")
    if name:
        task = celery.current_app.tasks.get(name)
        if task:
            signature = str(inspect.signature(task))[1:-1]
            description = inspect.getdoc(task)
            return JsonResponse(
                {"task": name, "signature": signature, "description": description}
            )

    return HttpResponseNotFound()


@require_GET
def check_task_status(request, *args, **kwargs):
    task_id = request.GET.get("task_id")
    if task_id:
        async_result = celery.result.AsyncResult(task_id)
        result = async_result._get_task_meta().get("result")
        if isinstance(result, Exception):
            result = f"{type(result).__name__}({str(result)})"
        result_dict = {
            "task_id": task_id,
            "task_name": async_result.name,
            "status": async_result.state,
            "queue": async_result.queue,
            "result": result,
            "date_done": (
                async_result.date_done.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                if async_result.date_done
                else None
            ),
            "traceback": async_result.traceback,
            "args": async_result.args,
            "kwargs": async_result.kwargs,
        }
        backend = celery.current_app.backend
        if backend:
            received = backend.get(f"celery-task-received-timestamp-{task_id}")
            started = backend.get(f"celery-task-started-timestamp-{task_id}")
            if received:
                result_dict["received"] = datetime.strptime(
                    received.decode("UTF-8"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            if started:
                started_datetime = datetime.strptime(
                    started.decode("UTF-8"), "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                result_dict["started"] = started_datetime.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                result_dict["runtime"] = (
                    f"{async_result.date_done.timestamp() - started_datetime.timestamp()}s"
                )
        return render(
            request, "task_info.html", result_dict
        )  # JsonResponse({"result": result_dict})
    else:
        return JsonResponse({"error": "task not founded"}, status=400)


def task_index(request):
    from celery_explorer.forms import TaskForm

    template_path = "task_explorer.html"

    if request.method == "GET":
        form = TaskForm()
        context = {}
        context["form"] = form
        return render(request, template_path, context=context)

    elif request.method == "POST":
        form = TaskForm(request.POST)
        context = {}
        context["form"] = form
        if form.is_valid():
            cleaned_data = form.cleaned_data
            name = cleaned_data.get("task_name")
            context["task_name"] = name
            task = celery.current_app.tasks.get(name)
            if task:
                task_signature = inspect.signature(task)
                signature_params = task_signature.parameters
                args = cleaned_data.get("params")
                countdown = cleaned_data.get("countdown")
                task_id = None
                error = True
                status = "NOT STARTED"
                if not args and not signature_params:
                    task_id = str(task.apply_async(countdown=countdown))
                    status = "STARTED"
                    error = False
                elif signature_params:
                    params = []
                    list_of_params = args.split(",") if args else []
                    if len(list_of_params) > len(signature_params):
                        context["status"] = "too much parameters"
                        context["task_id"] = None
                        context["error"] = True
                        return render(request, template_path, context=context)

                    for str_param, param in zip_longest(
                        list_of_params, signature_params.values()
                    ):
                        param_type = param.annotation
                        value = None
                        if str_param is None and param.default is not inspect._empty:
                            value = param.default
                        else:
                            try:
                                value = param_type(str_param)
                            except (TypeError, ValueError):
                                context["status"] = f"bad type of {param.name}"
                                context["task_id"] = None
                                context["error"] = True
                                return render(request, template_path, context=context)
                        params.append(value)
                    task_id = str(task.apply_async(params, countdown=countdown))
                    status = "STARTED"
                    error = False
                else:
                    status = "WRONG PARAMETERS"
                context["status"] = status
                context["task_id"] = task_id
                context["error"] = error
                return render(request, template_path, context=context)
            else:
                context["status"] = "TASK NOT FOUND"
                context["task_id"] = None
                context["error"] = True
                return render(request, template_path, context=context)


def get_tasks_list(request):
    page_param = request.GET.get("page")
    page = 1
    page_size = 10
    start = 0
    end = page_size - 1
    if page_param and page_param.isdigit():
        page = int(page_param)
        start = (page - 1) * page_size
        end = page * page_size - 1
    backend = celery.current_app.backend.client
    task_ids_list = [
        task_id.decode("UTF-8")
        for task_id in backend.lrange("celery-task-history", start, end)
    ]
    meta_task_ids_list = [f"celery-task-meta-{task_id}" for task_id in task_ids_list]
    num_of_tasks = backend.llen("celery-task-history")

    num_of_pages = num_of_tasks // page_size + 1

    values = backend.mget(keys=meta_task_ids_list)
    tasks_list = []
    for value in values:
        if value:
            dict_value = json.loads(value)
            tasks_list.append(
                {
                    "task_name": dict_value["name"],
                    "task_id": dict_value["task_id"],
                    "status": dict_value["status"],
                }
            )

    context = {
        "tasks_list": tasks_list,
        "num_of_pages": num_of_pages,
        "current_page": page,
    }
    print(context)
    template_path = "task_list.html"
    return render(request, template_path, context=context)
