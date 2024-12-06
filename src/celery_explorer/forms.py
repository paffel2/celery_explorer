from django import forms
import celery


def get_task_list():
    tasks = celery.current_app.tasks
    result = ["------"]
    for key, value in tasks.items():
        if "celery." in key:
            continue
        result.append(key)
    return zip(result, result)


class TaskForm(forms.Form):
    task_name = forms.ChoiceField(choices=get_task_list(), initial="------")
    countdown = forms.IntegerField(required=False, initial=0)
    params = forms.CharField(required=False)
