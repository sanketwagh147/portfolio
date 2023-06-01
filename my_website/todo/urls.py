from django.urls import path

from . import views

urlpatterns = [
    path("", views.todo_home, name="todo_home"),
    path("add_task/", views.add_task, name="add_task"),
]
