from django.shortcuts import render

# Create your views here.


def v_profile(request):
    return render(request, "vendor/vprofile.html")
