from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.models import Category, Vendor

from .forms import VendorForm

# Create your views here.


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
                "vendor": vendor,
            }
        return render(request, "vendor/vprofile.html", context=context)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
        context = {
            "profile_form": profile_form,
            "vendor_form": vendor_form,
            "profile": profile,
            "vendor": vendor,
        }
        return render(request, "vendor/vprofile.html", context=context)


def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor)
    print(categories)
    context = {"categories": categories}
    return render(request, "vendor/menu_builder.html", context)
