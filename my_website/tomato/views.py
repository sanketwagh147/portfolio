from typing import List

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.http import HttpResponse
from django.shortcuts import render
from vendor.models import Vendor

# Create your views here.


def get_or_set_current_location(request):
    if "lat" in request.session:
        lat = request.session["lat"]
        lng = request.session["lng"]
        return lng, lat
    elif "lat" in request.GET:
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        request.session["lat"] = lat
        request.session["lng"] = lng
        return lng, lat
    else:
        return None, None


def tomato_home(request):
    print(request.path)
    longitude, latitude = get_or_set_current_location(request)
    print(longitude, latitude)
    if latitude and longitude:
        pnt = GEOSGeometry(f"POINT({longitude} {latitude})")

        vendors = (
            Vendor.objects.filter(
                user_profile__location__distance_lte=(pnt, D(km=25)),
            )
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {"vendors": vendors}
    return render(request, "tomato/index.html", context)
