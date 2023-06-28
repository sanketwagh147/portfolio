from decimal import Decimal

from menu.models import FoodItem

from .models import Cart, Tax


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for item in cart_items:
                    cart_count += item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0

    return dict(cart_count=cart_count)


def get_cart_amount(request):
    grand_total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        sub_total = Decimal()
        for item in cart_items:
            food_item = FoodItem.objects.get(pk=item.food_item.id)
            sub_total += food_item.price * item.quantity

        tax = Tax.objects.filter(is_active=True)
        taxes = {}
        for each in tax:
            tax_type = each.tax_type
            tax_percentage = each.tax_percentage
            tax_amount = round((tax_percentage * sub_total) / 100, 2)
            taxes[tax_type] = {str(tax_percentage): tax_amount}

        all_tax = 0
        for key in taxes.values():
            for x in key.values():
                all_tax = all_tax + x

        grand_total = sub_total + all_tax
        return dict(
            sub_total=sub_total, taxes=taxes, grand_total=grand_total, total_tax=all_tax
        )
    return {}
