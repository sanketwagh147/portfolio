from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile

# Register your models here.


class CustomerUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "username", "role", "is_active")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, CustomerUserAdmin)
admin.site.register(UserProfile)
