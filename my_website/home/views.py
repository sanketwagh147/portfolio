from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "home/index.html")
    # return "Work in progress"

def resume(request):
    return render(request, "home/resume.html")
