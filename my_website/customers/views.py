from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.


@login_required
def c_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile updated")
            return redirect("cprofile")
        else:
            print(profile_form.errors)
            print(user_form.errors)

    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    context = {"profile_form": profile_form, "user_form": user_form, "profile": profile}
    return render(request, "customers/cprofile.html", context)
