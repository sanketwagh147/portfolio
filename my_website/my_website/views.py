"""
Home Page root check
"""


from django.contrib.staticfiles import finders
from django.http import HttpRequest
from django.shortcuts import render
from employees.models import Employee

result = finders.find("css/base.css")
searched_locations = finders.searched_locations


def home(request: HttpRequest):
    employees = Employee.objects.all()
    print(employees)
    context = {"employees": employees}
    return render(request, "home.html", context=context)


def index(request: HttpRequest):
    return render(request, "home.html")
    # return "Work in progress"
