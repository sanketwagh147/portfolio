from django import forms
from pyexpat import model

from .models import Order


class OrderForms(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
        )
