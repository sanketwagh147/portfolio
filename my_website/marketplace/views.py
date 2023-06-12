from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor

from .context_processors import get_cart_amount, get_cart_counter

# Create your views here.
SUCCESS = "Success"
FAILED = "Failed"


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {"vendors": vendors, "vendor_count": vendor_count}
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {"vendor": vendor, "categories": categories, "cart_items": cart_items}
    return render(request, "marketplace/vendor_detail.html", context)


def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({"status": FAILED, "message": "Invalid Request"})

        # Try if food exists
        food_item = FoodItem.objects.get(id=food_id)
        if not food_item:
            return JsonResponse(
                {"status": FAILED, "message": "This food item does not exists"}
            )

        #  Check if user has already added the same item to the cart
        try:
            check_cart = Cart.objects.get(user=request.user, food_item=food_item)
            check_cart.quantity += 1
            check_cart.save()
            return JsonResponse(
                {
                    "status": SUCCESS,
                    "message": "Increased the cart quantity",
                    "cart_counter": get_cart_counter(request),
                    "qty": check_cart.quantity,
                    "cart_amount": get_cart_amount(request),
                }
            )
        except Exception as err:
            check_cart = Cart.objects.create(
                user=request.user, food_item=food_item, quantity=1
            )
            return JsonResponse(
                {
                    "status": SUCCESS,
                    "message": "Food item added to the cart",
                    "cart_counter": get_cart_counter(request),
                    "qty": check_cart.quantity,
                    "cart_amount": get_cart_amount(request),
                }
            )

    return JsonResponse(
        {"status": "LOGIN_REQUIRED", "message": "Please login to continue"}
    )


def remove_from_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({"status": FAILED, "message": "Invalid Request"})

        # Try if food exists
        food_item = FoodItem.objects.get(id=food_id)
        if not food_item:
            return JsonResponse(
                {"status": FAILED, "message": "This food item does not exists"}
            )

        #  Check if user has already added the same item to the cart
        try:
            check_cart = Cart.objects.get(user=request.user, food_item=food_item)
            if check_cart.quantity > 1:
                check_cart.quantity -= 1
                check_cart.save()
            else:
                check_cart.delete()
                check_cart.quantity = 0
            return JsonResponse(
                {
                    "status": SUCCESS,
                    "message": "Decrease food quantity",
                    "cart_counter": get_cart_counter(request),
                    "qty": check_cart.quantity,
                    "cart_amount": get_cart_amount(request),
                }
            )
        except Exception as err:
            return JsonResponse(
                {
                    "status": FAILED,
                    "message": "You don not have item in your cart",
                }
            )

    return JsonResponse(
        {"status": "LOGIN_REQUIRED", "message": "Please login to continue"}
    )


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    print(cart_items)

    context = dict(cart_items=cart_items)
    context |= get_cart_amount(request)  # type: ignore
    print("cart content", context)
    print(context)
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id):
    print("here 1")
    if request.user.is_authenticated:
        print("here 2")
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({"status": FAILED, "message": "Invalid Request"})
        try:
            print("here 3")

            if cart_items := Cart.objects.get(user=request.user, id=cart_id):
                print("here 4")
                cart_items.delete()

                return JsonResponse(
                    {
                        "status": SUCCESS,
                        "message": "Cart item is deleted",
                        "cart_counter": get_cart_counter(request),
                        "cart_amount": get_cart_amount(request),
                    }
                )
        except Exception as err:
            return JsonResponse(
                {"status": FAILED, "message": "Cart  item does not exist"}
            )


def search(request):
    if "address" not in request.GET:
        return redirect("marketplace")
    address = request.GET["address"]
    latitude = request.GET["lat"]
    longitude = request.GET["lng"]
    radius = request.GET["radius"]
    keyword = request.GET["rest_name"]

    # get vendor id that has food user is searching fo

    vendor_by_food_item = FoodItem.objects.filter(
        food_title__icontains=keyword, is_available=True
    ).values_list("vendor", flat=True)

    vendors = Vendor.objects.filter(
        Q(id__in=vendor_by_food_item)
        | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
    )
    if latitude and longitude and radius:
        pnt = GEOSGeometry(f"POINT({longitude} {latitude})")

        vendors = (
            Vendor.objects.filter(
                Q(id__in=vendor_by_food_item)
                | Q(
                    vendor_name__icontains=keyword,
                    is_approved=True,
                    user__is_active=True,
                ),
                user_profile__location__distance_lte=(pnt, D(km=radius)),
            )
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)
    vendor_count = vendors.count()
    context = {
        "vendors": vendors,
        "vendors_count": vendor_count,
        "source_location": address,
    }
    print(vendors)
    return render(request, "marketplace/listings.html", context)
