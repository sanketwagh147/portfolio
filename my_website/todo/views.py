from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import Task

# Create your views here.


def todo_home(request):
    tasks = Task.objects.filter(is_completed=False).order_by("-updated_at")
    context = {"tasks": tasks}
    return render(request, template_name="todo/home.html", context=context)


def add_task(request):
    task = request.POST["task"]
    Task.objects.create(task=task)
    return redirect("todo_home")
