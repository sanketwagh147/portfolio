from django.urls import path

from accounts import views as AccountViews

from . import views

urlpatterns = [
    path("", AccountViews.vendorDashboard, name="vendor"),
    path("profile/", views.v_profile, name="vprofile"),
    path("menu-builder/", views.menu_builder, name="menu_builder"),
]
