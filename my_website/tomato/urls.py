from django.urls import include, path
from marketplace import views as MarketPlaceViews

from . import views

urlpatterns = [
    path("cart/", MarketPlaceViews.cart, name="cart"),
    path("checkout/", MarketPlaceViews.checkout, name="checkout"),
    path("orders/", include("orders.urls")),
    path("search/", MarketPlaceViews.search, name="search"),
    path("", views.tomato_home, name="tomato_home"),
]
