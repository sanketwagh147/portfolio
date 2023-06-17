from accounts import views as AccountViews
from django.urls import path

from . import views

urlpatterns = [
    path("", AccountViews.custDashboard, name="customer"),
    path("profile", views.c_profile, name="cprofile"),
]
