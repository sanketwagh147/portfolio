from tabnanny import verbose

from accounts.models import User
from django.db import models
from menu.models import FoodItem

# Create your models here.


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #! As user is foreign key instead of str we use unicode
    def __unicode__(self):
        return self.user


class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(
        decimal_places=2, max_digits=4, verbose_name="Tax Percentage (%)"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.tax_type

    class Meta:
        verbose_name_plural = "tax"
