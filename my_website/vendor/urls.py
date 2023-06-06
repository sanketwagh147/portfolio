from accounts import views as AccountViews
from django.urls import path

from . import views

urlpatterns = [
    path("", AccountViews.vendorDashboard, name="vendor"),
    path("profile/", views.v_profile, name="vprofile"),
]
