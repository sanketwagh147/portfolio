from email import message

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode
from vendor.forms import VendorForm
from vendor.models import Vendor

from .forms import UserForm
from .models import User, UserProfile
from .utils import detect_user, send_password_reset_email, send_verification_email

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
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
                phone_number=phone_number,
            )
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            send_verification_email(request, user)

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
            vendor_name = vendor_form.cleaned_data["vendor_name"] + str(user.id)
            vendor.vendor_slug = slugify(vendor_name)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(
                request,
                "Your account has been registered successfully! Please wait to get it approved",
            )
            send_verification_email(request, user)
            return redirect("registerVendor")

        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
        vendor_form = VendorForm()
        context = {"form": form, "vendor_form": vendor_form}
        return render(request, "accounts/registerVendor.html", context=context)


def activate(request, uidb64, token):
    # Activate user by setting is active true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulatiosn your account is activated")
        return redirect("myAccount")
    else:
        messages.error(request, "Invalid activation Link")
        return redirect("myAccount")


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


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send resetting password email
            send_password_reset_email(request, user)
            messages.success(
                request, "Password reset link has been sent to your email address"
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    uid = None
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # validate user token
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password !")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has been expired")
        return redirect("myAccount")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Passwords Do not match")
            return redirect("reset_password")

    return render(request, "accounts/reset_password.html")
