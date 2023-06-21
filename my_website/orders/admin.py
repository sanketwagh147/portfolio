from django.contrib import admin

from .models import Order, OrderedFood, Payment


class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = [
        "order",
        "payment",
        "user",
        "food_item",
        "quantity",
        "price",
        "amount",
    ]
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "name",
        "phone",
        "email",
        "total",
        "payment_method",
        "status",
        "is_ordered",
    ]
    inlines = [OrderedFoodInline]


# Register your models here.
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderedFood)
