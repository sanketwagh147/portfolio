from accounts import views as AccountViews
from django.urls import path

from . import views

urlpatterns = [
    path("", AccountViews.custDashboard, name="customer"),
    path("profile", views.c_profile, name="cprofile"),
    path("my_orders", views.my_orders, name="customer_orders"),
    path("order_detail/<int:order_number>", views.order_detail, name="order_detail"),
]
