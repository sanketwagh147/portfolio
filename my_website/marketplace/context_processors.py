from menu.models import FoodItem

from .models import Cart


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
        sub_total: float = 0
        for item in cart_items:
            food_item = FoodItem.objects.get(pk=item.food_item.id)
            sub_total += float(food_item.price * item.quantity)

        tax = 0.1 * sub_total
        grand_total = sub_total + tax
        return dict(sub_total=sub_total, tax=tax, grand_total=grand_total)
