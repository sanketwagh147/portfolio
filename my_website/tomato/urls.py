from django.urls import path
from marketplace import views as MarketPlaceViews

from . import views

urlpatterns = [
    path("cart/", MarketPlaceViews.cart, name="cart"),
    path("search/", MarketPlaceViews.search, name="search"),
    path("", views.tomato_home, name="tomato_home"),
]
