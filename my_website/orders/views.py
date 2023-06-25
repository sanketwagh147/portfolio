from re import sub
import razorpay
import simplejson as json
from accounts.models import User
from accounts.utils import send_notification
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number
import vendor

print(settings.RAZOR_PAY_KEY_ID)
print(settings.RAZOR_PAY_SECRET)

client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_SECRET))

# client.order.create(data=DATA)


# Create your views here.
@login_required
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if not cart_count:
        return redirect("marketplace")

    vendors_ids = []
    for each in cart_items:
        if each.food_item.vendor.id not in vendors_ids:
            vendors_ids.append(each.food_item.vendor.id)

    get_tax = Tax.objects.filter(is_active=True)
    sub_total = 0
    total_data = {}
    vendor_dict = {}
    for item in cart_items:
        food_item = FoodItem.objects.get(
            pk=item.food_item.id, vendor_id__in=vendors_ids
        )
        v_id = food_item.vendor.id
        if v_id in vendor_dict:
            # sub_total = vendor_dict[v_id]
            sub_total += food_item.price * item.quantity
            vendor_dict[v_id] += sub_total

        else:
            sub_total = food_item.price * item.quantity
            vendor_dict[v_id] = sub_total

        # calcutate tax data
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * sub_total) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        # total data
        total_data.update({food_item.vendor.id: {str(sub_total): str(tax_dict)}})

    print(total_data)

    context = {**get_cart_amount(request)}
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.phone = form.cleaned_data["phone"]
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.pin_code = form.cleaned_data["pin_code"]
            order.user = request.user
            order.total = context["grand_total"]
            order.tax_data = json.dumps(context["taxes"])
            order.total_data = json.dumps(total_data)
            order.total_tax = context["total_tax"]
            order.payment_method = request.POST["payment_method"]
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            # Implement razor pay
            DATA = {
                "amount": float(order.total)
                * 100,  # as razor pay accepts amount in paise
                "currency": "INR",
                "receipt": f"Receipt #{order.order_number}",
                # "notes": {"key1": "value3", "key2": "value2"},
            }
            razor_pay_order = client.order.create(data=DATA)
            razor_pay_id = razor_pay_order["id"]
            # print(razor_pay_order)

            context = context | {
                "order": order,
                "cart_items": cart_items,
                "razor_pay_id": razor_pay_id,
                "razor_key_id": settings.RAZOR_PAY_KEY_ID,
                "razor_pay_amount": float(order.total) * 100,
            }
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)
    return render(request, "orders/place_order.html", context)


@login_required
def payments(request):
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.food_item = item.food_item
            ordered_food.quantity = item.quantity
            ordered_food.price = float(item.food_item.price)
            ordered_food.amount = float(item.food_item.price * item.quantity)
            ordered_food.save()
        mail_subject = "Thank you for ordering from tomato"
        mail_template = "orders/order_confirmation_email.html"
        context = {"user": request.user, "order": order, "to_email": order.email}
        send_notification(
            mail_subject=mail_subject, mail_template=mail_template, context=context
        )
        mail_subject = "You have received and order"
        mail_template = "orders/new_order_received_email.html"
        to_emails = list(set([item.food_item.vendor.user.email for item in cart_items]))
        context = {"user": request.user, "order": order, "to_email": to_emails}
        send_notification(
            mail_subject=mail_subject,
            mail_template=mail_template,
            context=context,
        )
        cart_items.delete()
        response = dict(order_number=order_number, transaction_id=transaction_id)
        return JsonResponse(response)


def order_complete(request):
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")
    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True,
        )
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = sum([item.price for item in ordered_food])
        tax_data = json.loads(order.tax_data)
        context = dict(
            order=order, ordered_food=ordered_food, subtotal=subtotal, tax_data=tax_data
        )
        return render(request, "orders/order_complete.html", context)
    except Exception as err:
        print(err)
        pass
