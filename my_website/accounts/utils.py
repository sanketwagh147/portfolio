from urllib import request

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def detect_user(user):
    if user.role == 1:
        redirect_url = "vendorDashboard"
    elif user.role == 2:
        redirect_url = "custDashboard"
    elif user.role == None and user.is_superadmin:
        redirect_url = "/admin"
    else:
        redirect_url = "/tomato"

    return redirect_url


def send_mail(request, user, mail_subject, template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(
        template,
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()


def send_verification_email(request, user):
    mail_subject = "Please activate your account."
    template = "accounts/emails/account_verification_email.html"
    send_mail(request, user, mail_subject, template)


def send_password_reset_email(request, user):
    mail_subject = "Reset Your password"
    template = "accounts/emails/reset_password.html"
    send_mail(request, user, mail_subject, template)


def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)

    if context.get("to_email"):
        if isinstance(context["to_email"], str):
            to_email = [context["to_email"]]
        else:
            to_email = context["to_email"]
    else:
        to_email = [context["user"].email]

    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()
