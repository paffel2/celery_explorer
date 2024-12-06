import celery
from django.shortcuts import render
from django.views.decorators.http import require_GET

import inspect
from itertools import zip_longest
import celery.result
from django.http import JsonResponse, Http404


@require_GET
def get_task_detail(request, *args, **kwargs):
    name = request.GET.get("name")
    if name:
        task = celery.current_app.tasks.get(name)
        if task:
            signature = str(inspect.signature(task))[1:-1]  # delete brackets
            description = inspect.getdoc(task)
            print(description)
            return JsonResponse({"task": name, "signature": signature, "description": description})

    return Http404()


@require_GET
def check_task_status(request, *args, **kwargs):
    task_id = request.GET.get("task_id")
    if task_id:
        res = celery.result.AsyncResult(task_id).state
        return JsonResponse({"result": res})
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
                elif signature_params:
                    params = []
                    list_of_params = args.split(",") if args else []
                    if len(list_of_params) > len(signature_params):
                        context["status"] = "too much parameters"
                        context["task_id"] = None
                        context["error"] = True
                        return render(request, template_path, context=context)

                    for str_param, param in zip_longest(list_of_params, signature_params.values()):
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
