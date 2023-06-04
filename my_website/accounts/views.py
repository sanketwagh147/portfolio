from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile
from .utils import detect_user

# Create your views here.

# restrict vendor from accessing customer from accessing customer page and vice-versa


def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged in")
        return redirect("myAccount")

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
    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged in")
        return redirect("myAccount")
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


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already Logged in")
        return redirect("myAccount")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("myAccount")
        else:
            messages.error(request, "Invalid Login credentials")
            return redirect("login")
    return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are now logged out")
    return redirect("login")


@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, "accounts/custDashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")
