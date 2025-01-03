import celery
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime


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
        print(type(async_result.result))
        result = async_result.result
        if isinstance(result, Exception):
            result = f"{type(result).__name__}({str(result)})"
        result_dict = {
            "task_id": task_id,
            "task_name": async_result.name,
            "status": async_result.state,
            "queue": async_result.queue,
            "result": result,
            "date_done": async_result.date_done.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "traceback": async_result.traceback,
            "args": async_result.args,
            "kwargs": async_result.kwargs,
        }
        back = celery.current_app.backend
        if back:
            received = back.get(f"celery-task-received-timestamp-{task_id}")
            started = back.get(f"celery-task-started-timestamp-{task_id}")
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

    template_path = "task_list.html"

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
                    back = celery.current_app.backend
                    if back:
                        print(back)
                        now = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        back.set(f"celery-task-received-timestamp-{task_id}", now)
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
                    back = celery.current_app.backend
                    if back:
                        print(back)
                        now = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        back.set(f"celery-task-received-timestamp-{task_id}", now)
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
