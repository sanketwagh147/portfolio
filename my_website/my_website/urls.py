"""
URL configuration for my_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

print(settings.MEDIA_URL)
print(settings.MEDIA_ROOT)
urlpatterns = [
    path("", views.index),
    path("admin/", admin.site.urls),
    path("dev", views.home, name="home_test"),
    path("employees/", include("employees.urls")),
    path("todo/", include("todo.urls")),
    path("tomato/", include("tomato.urls")),
    path("tomato/", include("accounts.urls")),
    path("tomato/marketplace/", include("marketplace.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
