from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def tomato_home(request):
    return render(request, "tomato/index.html")
