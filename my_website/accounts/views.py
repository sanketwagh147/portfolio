from django.contrib import messages
from django.shortcuts import redirect, render
from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile

# Create your views here.


def registerUser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using form
            # user = form.save(commit=False)
            # password = form.cleaned_data["password"]
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create user using create_user method
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()
            print("User is created using create user method")
            messages.success(request, "your account is registered successfully")
            return redirect("registerUser")
        else:
            print("invalid form")
            print(form.errors)
            messages.error(request, "Oops something went wrong")
            context = {"form": form}
            return render(request, "accounts/registerUser.html", context=context)

    else:
        form = UserForm()
        context = {"form": form}
        return render(request, "accounts/registerUser.html", context=context)


def registerVendor(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(
                request,
                "Your account has been registered successfully! Please wait to get it approved",
            )
            return redirect("registerVendor")

        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
        vendor_form = VendorForm()
        context = {"form": form, "vendor_form": vendor_form}
        return render(request, "accounts/registerVendor.html", context=context)
