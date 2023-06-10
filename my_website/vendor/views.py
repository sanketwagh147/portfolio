import re
from unicodedata import category

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm
from menu.models import Category, FoodItem, Vendor

from .forms import VendorForm

VENDOR = "vendor"


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


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


def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, f"Category: {category_name} added !")
            return redirect("menu_builder")
        else:
            context = {"form": form}
            return render(request, f"{VENDOR}/add_category.html", context)
    else:
        form = CategoryForm()
        context = {"form": form}
        return render(request, f"{VENDOR}/add_category.html", context)


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


def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category_name = category.category_name
    category.delete()
    messages.success(request, f"Category: {category_name} deleted successfully !")
    return redirect("menu_builder")
