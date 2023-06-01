from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Task

# Create your views here.


def todo_home(request):
    tasks = Task.objects.filter(is_completed=False).order_by("-updated_at")
    completed_tasks = Task.objects.filter(is_completed=True).order_by("-updated_at")
    context = {"tasks": tasks, "completed_tasks": completed_tasks}
    return render(request, template_name="todo/home.html", context=context)


def add_task(request):
    task = request.POST["task"]
    Task.objects.create(task=task)
    return redirect("todo_home")


def mark_as_done(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = True
    task.save()
    return redirect("todo_home")


def mark_as_undone(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = False
    task.save()
    return redirect("todo_home")


def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        new_task = request.POST["task"]
        task.task = new_task
        task.save()

        return redirect("todo_home")
    else:
        context = {
            "task": task,
        }
        return render(request, template_name="todo/edit.html", context=context)


def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect("todo_home")
