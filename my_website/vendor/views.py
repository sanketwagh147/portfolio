import re
from unicodedata import category

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem, Vendor
from orders.models import Order, OrderedFood

from .forms import OpeningHourForm, VendorForm
from .models import OpeningHour, Vendor

VENDOR = "vendor"
FOOD = "food"


def get_vendor(request):
    return Vendor.objects.get(user=request.user)


@login_required
@user_passes_test(check_role_vendor)
def v_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "You Change is updated !")
            return redirect("vprofile")
        else:
            context = {
                "profile_form": profile_form,
                "vendor_form": vendor_form,
                "profile": profile,
                VENDOR: vendor,
            }
        return render(request, f"{VENDOR}/vprofile.html", context=context)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
        context = {
            "profile_form": profile_form,
            "vendor_form": vendor_form,
            "profile": profile,
            VENDOR: vendor,
        }
        return render(request, f"{VENDOR}/vprofile.html", context=context)


@login_required
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by("created_at")
    print(categories)
    for each in categories:
        print(each.id)
    context = {"categories": categories}
    return render(request, f"{VENDOR}/menu_builder.html", context)


@login_required
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = dict(fooditems=fooditems, category=category)
    return render(request, f"{VENDOR}/fooditems_by_category.html", context)


@login_required
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name) + str(category.id)
            category.save()
            messages.success(request, f"Category: {category_name} added !")
            return redirect("menu_builder")
        else:
            context = {"form": form}
            return render(request, f"{VENDOR}/add_category.html", context)
    else:
        form = CategoryForm()
        context = {"form": form}
        return render(request, f"{VENDOR}/add_category.html", context)


@login_required
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(
                request, f"Category: {category_name} updated successfully !"
            )
            return redirect("menu_builder")
        else:
            context = {"form": form}
    else:
        form = CategoryForm(instance=category)
        context = {"form": form, "category": category}
    return render(request, f"{VENDOR}/edit_category.html", context)


@login_required
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category_name = category.category_name
    category.delete()
    messages.success(request, f"Category: {category_name} deleted successfully !")
    return redirect("menu_builder")


@login_required
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, f"Food item: {food_title} added successfully !")
            return redirect("fooditems_by_category", food.category.id)
        else:
            context = {"form": form}
    else:
        # context = {"form": form, "category": category}
        form = FoodItemForm()

        # only fetch categories from specific vendor
        form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
        context = {"form": form}
        return render(request, f"{VENDOR}/add_food.html", context)
    return render(request, f"{VENDOR}/edit_category.html", context)


@login_required
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)

    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, f"Food: {food_title} updated successfully !")
            return redirect("fooditems_by_category", food.category.id)
        else:
            context = {"form": form}
    else:
        form = FoodItemForm(instance=food)
        # only fetch categories from specific vendor
        form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
        context = {"form": form, "food": food}
    return render(request, f"{VENDOR}/edit_food.html", context)


@login_required
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food_title = food.food_title
    food.delete()
    messages.success(request, f"Category: {food_title} deleted successfully !")
    return redirect("menu_builder")


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = dict(form=form, opening_hours=opening_hours)
    return render(request, "vendor/opening_hours.html", context)


def add_opening_hours(request):
    if not request.user.is_authenticated:
        return
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        day = request.POST.get("day")
        from_hour = request.POST.get("from_hour")
        to_hour = request.POST.get("to_hour")
        is_closed = request.POST.get("is_closed") == "true"
        print(day, from_hour, to_hour, is_closed)
        try:
            if hour := OpeningHour.objects.create(
                vendor=get_vendor(request),
                day=day,
                from_hour=from_hour,
                to_hour=to_hour,
                is_closed=is_closed,
            ):
                day = OpeningHour.objects.get(id=hour.id)
                weekday = str(day.get_day_display()).title()
                if day.is_closed:
                    response = dict(
                        status="SUCCESS",
                        id=hour.id,
                        day=weekday,
                        is_closed="Closed",
                        from_hour="",
                        to_hour="",
                    )
                else:
                    response = dict(
                        status="SUCCESS",
                        id=hour.id,
                        day=weekday,
                        from_hour=hour.from_hour,
                        to_hour=hour.to_hour,
                        is_closed="",
                    )
                return JsonResponse(response)

        except IntegrityError as err:
            return JsonResponse(
                {"status": "FAILED", "error": "This timing exists for this day"}
            )
    else:
        HttpResponse("Invalid Request")


def remove_opening_hours(request, pk):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        hour = get_object_or_404(OpeningHour, pk=pk)
        hour.delete()
        return JsonResponse(dict(status="SUCCESS", id=pk))
    return JsonResponse(dict(status="FAILED", id=pk))


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(
            order=order, food_item__vendor=get_vendor(request)
        )
        print(ordered_food)
        context = dict(ordered_food=ordered_food, order=order)
        return render(request, "vendor/order_detail.html", context)
    except Exception as err:
        return redirect("vendor")
