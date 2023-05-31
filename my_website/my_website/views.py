"""
Home Page root check
"""


from django.contrib.staticfiles import finders
from django.http import HttpRequest
from django.shortcuts import render

result = finders.find("css/base.css")
searched_locations = finders.searched_locations


def home(request: HttpRequest):
    return render(request, "home.html")
