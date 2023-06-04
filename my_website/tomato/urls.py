from django.urls import path

from . import views

urlpatterns = [
    path("", views.tomato_home, name="todo_home"),
]
