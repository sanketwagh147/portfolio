from django.http import HttpResponse
from django.shortcuts import render
from vendor.models import Vendor

# Create your views here.


def tomato_home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {"vendors": vendors}
    return render(request, "tomato/index.html", context)
